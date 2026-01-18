"""
定時排程模組
"""
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from database import get_session, MonitorRule, NotificationLog, Setting, init_db
from crawler import PTTCrawler
from notifier import TelegramNotifier
from config import DEFAULT_PARSING_INTERVAL


class PTTScheduler:
    """PTT 爬蟲排程器"""
    
    def __init__(self, notifier: TelegramNotifier):
        self.notifier = notifier
        self.crawler = PTTCrawler()
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    def get_interval(self) -> int:
        """取得爬取間隔（分鐘）"""
        session = get_session()
        try:
            setting = session.query(Setting).filter_by(key="parsing_interval").first()
            return int(setting.value) if setting else DEFAULT_PARSING_INTERVAL
        finally:
            session.close()
    
    async def check_rules(self):
        """檢查所有監控規則"""
        print(f"[{datetime.now()}] 開始檢查監控規則...")
        
        session = get_session()
        try:
            rules = session.query(MonitorRule).filter_by(is_active=True).all()
            if not rules:
                print("  沒有啟用的監控規則")
                return
            
            # 依看板分組
            boards = {}
            for rule in rules:
                if rule.board not in boards:
                    boards[rule.board] = []
                boards[rule.board].append(rule)
            
            # 爬取每個看板
            for board, board_rules in boards.items():
                print(f"  正在檢查看板: {board}")
                try:
                    articles = self.crawler.get_board_articles(board, max_pages=2)
                except Exception as e:
                    print(f"    爬取失敗: {e}")
                    continue
                
                if not articles:
                    print(f"    沒有找到文章")
                    continue
                
                # 檢查每個規則
                for rule in board_rules:
                    await self._check_rule(session, rule, articles)
            
            session.commit()
            print(f"[{datetime.now()}] 檢查完成")
            
        except Exception as e:
            print(f"[ERROR] 檢查規則時發生錯誤: {e}")
            session.rollback()
        finally:
            session.close()
    
    async def _check_rule(self, session, rule: MonitorRule, articles: list):
        """檢查單一規則"""
        matched_articles = []
        
        for article in articles:
            # 如果遇到上次爬過的文章，停止
            if rule.last_article_url and article.url == rule.last_article_url:
                break
            
            # 檢查是否已通知過
            existing = session.query(NotificationLog).filter_by(
                rule_id=rule.id,
                article_url=article.url
            ).first()
            if existing:
                continue
            
            # 檢查是否符合條件
            is_match = False
            
            if rule.rule_type == "push_count":
                is_match = article.push_count >= rule.threshold
            elif rule.rule_type == "boo_count":
                is_match = article.push_count <= -rule.threshold
            elif rule.rule_type == "author":
                is_match = article.author.lower() == rule.condition_value.lower()
            elif rule.rule_type == "keyword":
                is_match = rule.condition_value.lower() in article.title.lower()
            
            if is_match:
                matched_articles.append(article)
        
        # 發送通知
        for article in matched_articles:
            try:
                message = self.notifier.format_notification(
                    board=article.board,
                    title=article.title,
                    url=article.url,
                    push_count=article.push_count
                )
                await self.notifier.send_message(message)
                
                # 記錄已通知
                log = NotificationLog(
                    rule_id=rule.id,
                    article_url=article.url
                )
                session.add(log)
                
                print(f"    ✅ 通知: {article.title}")
            except Exception as e:
                print(f"    ❌ 發送通知失敗: {e}")
        
        # 更新上次爬到的文章
        if articles:
            rule.last_article_url = articles[0].url
    
    def start(self):
        """啟動排程器"""
        if self.is_running:
            return
        
        interval = self.get_interval()
        print(f"啟動排程器，間隔: {interval} 分鐘")
        
        self.scheduler.add_job(
            self.check_rules,
            trigger=IntervalTrigger(minutes=interval),
            id="check_rules",
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
    
    def stop(self):
        """停止排程器"""
        if not self.is_running:
            return
        
        self.scheduler.shutdown()
        self.is_running = False
    
    async def run_once(self):
        """立即執行一次檢查"""
        await self.check_rules()

