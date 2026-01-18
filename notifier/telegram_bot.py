"""
Telegram 通知模組
"""
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from database import get_session, MonitorRule, Setting, init_db
from crawler import PTTCrawler
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, DEFAULT_PARSING_INTERVAL


class TelegramNotifier:
    """Telegram 通知與指令處理"""
    
    def __init__(self, token: str = None, chat_id: str = None):
        self.token = token or TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or TELEGRAM_CHAT_ID
        self.bot = Bot(token=self.token)
        self.application = None
    
    async def send_message(self, message: str, chat_id: str = None):
        """發送訊息"""
        target_chat = chat_id or self.chat_id
        await self.bot.send_message(
            chat_id=target_chat,
            text=message,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    
    def send_message_sync(self, message: str, chat_id: str = None):
        """同步發送訊息（給排程器使用）"""
        asyncio.run(self.send_message(message, chat_id))
    
    def format_notification(self, board: str, title: str, url: str, push_count: int = None) -> str:
        """
        格式化通知訊息
        格式: [看板] 標題名稱 : link
        """
        msg = f"[{board}] {title}"
        if push_count is not None:
            msg += f" (推: {push_count})"
        msg += f"\n{url}"
        return msg
    
    # === Telegram 指令處理 ===
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """處理 /start 指令"""
        help_text = """
🔔 <b>PTT 通知機器人</b>

可用指令：
/add_push [看板] [推文數] - 新增推文數監控
  例: /add_push Stock 20

/add_boo [看板] [噓文數] - 新增噓文數監控
  例: /add_boo Gossiping 50

/add_author [看板] [作者] - 新增作者監控
  例: /add_author Stock abc123

/add_keyword [看板] [關鍵字] - 新增關鍵字監控
  例: /add_keyword Stock 台積電

/list - 列出所有監控規則
/delete [規則ID] - 刪除監控規則
/pause [規則ID] - 暫停監控規則
/resume [規則ID] - 恢復監控規則

/interval [分鐘] - 設定爬取間隔
/status - 查看系統狀態
/help - 顯示此說明
        """
        await update.message.reply_text(help_text, parse_mode="HTML")
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """處理 /help 指令"""
        await self.cmd_start(update, context)
    
    def _get_latest_article_url(self, board: str) -> str:
        """取得看板最新文章的 URL（用於不溯及既往）"""
        try:
            crawler = PTTCrawler()
            articles = crawler.get_board_articles(board, max_pages=1)
            if articles:
                return articles[0].url
        except Exception:
            pass
        return None
    
    async def cmd_add_push(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """新增推文數監控規則"""
        if len(context.args) < 2:
            await update.message.reply_text("❌ 格式錯誤\n用法: /add_push [看板] [推文數]")
            return
        
        board = context.args[0]
        try:
            threshold = int(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ 推文數必須是數字")
            return
        
        # 取得最新文章 URL（不溯及既往）
        await update.message.reply_text(f"正在設定監控 {board} 看板...")
        latest_url = self._get_latest_article_url(board)
        
        session = get_session()
        try:
            rule = MonitorRule(
                rule_type="push_count",
                board=board,
                threshold=threshold,
                last_article_url=latest_url  # 從現在開始，不溯及既往
            )
            session.add(rule)
            session.commit()
            await update.message.reply_text(
                f"✅ 已新增監控規則\n"
                f"ID: {rule.id}\n"
                f"看板: {board}\n"
                f"條件: 推文數 >= {threshold}\n"
                f"📍 從現在開始監控（不溯及既往）"
            )
        finally:
            session.close()
    
    async def cmd_add_boo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """新增噓文數監控規則"""
        if len(context.args) < 2:
            await update.message.reply_text("❌ 格式錯誤\n用法: /add_boo [看板] [噓文數]")
            return
        
        board = context.args[0]
        try:
            threshold = int(context.args[1])
        except ValueError:
            await update.message.reply_text("❌ 噓文數必須是數字")
            return
        
        # 取得最新文章 URL（不溯及既往）
        await update.message.reply_text(f"正在設定監控 {board} 看板...")
        latest_url = self._get_latest_article_url(board)
        
        session = get_session()
        try:
            rule = MonitorRule(
                rule_type="boo_count",
                board=board,
                threshold=threshold,
                last_article_url=latest_url
            )
            session.add(rule)
            session.commit()
            await update.message.reply_text(
                f"✅ 已新增監控規則\n"
                f"ID: {rule.id}\n"
                f"看板: {board}\n"
                f"條件: 噓文數 >= {threshold}\n"
                f"📍 從現在開始監控（不溯及既往）"
            )
        finally:
            session.close()
    
    async def cmd_add_author(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """新增作者監控規則"""
        if len(context.args) < 2:
            await update.message.reply_text("❌ 格式錯誤\n用法: /add_author [看板] [作者]")
            return
        
        board = context.args[0]
        author = context.args[1]
        
        # 取得最新文章 URL（不溯及既往）
        await update.message.reply_text(f"正在設定監控 {board} 看板...")
        latest_url = self._get_latest_article_url(board)
        
        session = get_session()
        try:
            rule = MonitorRule(
                rule_type="author",
                board=board,
                condition_value=author,
                last_article_url=latest_url
            )
            session.add(rule)
            session.commit()
            await update.message.reply_text(
                f"✅ 已新增監控規則\n"
                f"ID: {rule.id}\n"
                f"看板: {board}\n"
                f"條件: 作者 = {author}\n"
                f"📍 從現在開始監控（不溯及既往）"
            )
        finally:
            session.close()
    
    async def cmd_add_keyword(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """新增關鍵字監控規則"""
        if len(context.args) < 2:
            await update.message.reply_text("❌ 格式錯誤\n用法: /add_keyword [看板] [關鍵字]")
            return
        
        board = context.args[0]
        keyword = " ".join(context.args[1:])  # 允許多字關鍵字
        
        # 取得最新文章 URL（不溯及既往）
        await update.message.reply_text(f"正在設定監控 {board} 看板...")
        latest_url = self._get_latest_article_url(board)
        
        session = get_session()
        try:
            rule = MonitorRule(
                rule_type="keyword",
                board=board,
                condition_value=keyword,
                last_article_url=latest_url
            )
            session.add(rule)
            session.commit()
            await update.message.reply_text(
                f"✅ 已新增監控規則\n"
                f"ID: {rule.id}\n"
                f"看板: {board}\n"
                f"條件: 標題含 '{keyword}'\n"
                f"📍 從現在開始監控（不溯及既往）"
            )
        finally:
            session.close()
    
    async def cmd_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """列出所有監控規則"""
        session = get_session()
        try:
            rules = session.query(MonitorRule).all()
            if not rules:
                await update.message.reply_text("📭 目前沒有任何監控規則")
                return
            
            msg = "📋 <b>監控規則列表</b>\n\n"
            for rule in rules:
                status = "✅" if rule.is_active else "⏸️"
                if rule.rule_type == "push_count":
                    condition = f"推文 >= {rule.threshold}"
                elif rule.rule_type == "boo_count":
                    condition = f"噓文 >= {rule.threshold}"
                elif rule.rule_type == "author":
                    condition = f"作者 = {rule.condition_value}"
                elif rule.rule_type == "keyword":
                    condition = f"標題含 '{rule.condition_value}'"
                else:
                    condition = "未知"
                
                msg += f"{status} <b>ID {rule.id}</b>: [{rule.board}] {condition}\n"
            
            await update.message.reply_text(msg, parse_mode="HTML")
        finally:
            session.close()
    
    async def cmd_delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """刪除監控規則"""
        if len(context.args) < 1:
            await update.message.reply_text("❌ 格式錯誤\n用法: /delete [規則ID]")
            return
        
        try:
            rule_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ 規則ID必須是數字")
            return
        
        session = get_session()
        try:
            rule = session.query(MonitorRule).filter_by(id=rule_id).first()
            if not rule:
                await update.message.reply_text(f"❌ 找不到規則 ID {rule_id}")
                return
            
            session.delete(rule)
            session.commit()
            await update.message.reply_text(f"✅ 已刪除規則 ID {rule_id}")
        finally:
            session.close()
    
    async def cmd_pause(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """暫停監控規則"""
        if len(context.args) < 1:
            await update.message.reply_text("❌ 格式錯誤\n用法: /pause [規則ID]")
            return
        
        try:
            rule_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ 規則ID必須是數字")
            return
        
        session = get_session()
        try:
            rule = session.query(MonitorRule).filter_by(id=rule_id).first()
            if not rule:
                await update.message.reply_text(f"❌ 找不到規則 ID {rule_id}")
                return
            
            rule.is_active = False
            session.commit()
            await update.message.reply_text(f"⏸️ 已暫停規則 ID {rule_id}")
        finally:
            session.close()
    
    async def cmd_resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """恢復監控規則"""
        if len(context.args) < 1:
            await update.message.reply_text("❌ 格式錯誤\n用法: /resume [規則ID]")
            return
        
        try:
            rule_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ 規則ID必須是數字")
            return
        
        session = get_session()
        try:
            rule = session.query(MonitorRule).filter_by(id=rule_id).first()
            if not rule:
                await update.message.reply_text(f"❌ 找不到規則 ID {rule_id}")
                return
            
            rule.is_active = True
            session.commit()
            await update.message.reply_text(f"✅ 已恢復規則 ID {rule_id}")
        finally:
            session.close()
    
    async def cmd_interval(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """設定爬取間隔"""
        session = get_session()
        try:
            if len(context.args) < 1:
                # 顯示目前設定
                setting = session.query(Setting).filter_by(key="parsing_interval").first()
                current = setting.value if setting else DEFAULT_PARSING_INTERVAL
                await update.message.reply_text(f"⏱️ 目前爬取間隔: {current} 分鐘")
                return
            
            try:
                interval = int(context.args[0])
                if interval < 1:
                    raise ValueError()
            except ValueError:
                await update.message.reply_text("❌ 間隔必須是正整數（分鐘）")
                return
            
            setting = session.query(Setting).filter_by(key="parsing_interval").first()
            if setting:
                setting.value = str(interval)
            else:
                setting = Setting(key="parsing_interval", value=str(interval))
                session.add(setting)
            session.commit()
            
            await update.message.reply_text(f"✅ 已設定爬取間隔為 {interval} 分鐘\n⚠️ 重啟程式後生效")
        finally:
            session.close()
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """查看系統狀態"""
        session = get_session()
        try:
            rules_count = session.query(MonitorRule).count()
            active_count = session.query(MonitorRule).filter_by(is_active=True).count()
            
            setting = session.query(Setting).filter_by(key="parsing_interval").first()
            interval = setting.value if setting else DEFAULT_PARSING_INTERVAL
            
            msg = (
                "📊 <b>系統狀態</b>\n\n"
                f"監控規則: {rules_count} 個\n"
                f"啟用中: {active_count} 個\n"
                f"爬取間隔: {interval} 分鐘"
            )
            await update.message.reply_text(msg, parse_mode="HTML")
        finally:
            session.close()
    
    def setup_handlers(self, application: Application):
        """設定指令處理器"""
        application.add_handler(CommandHandler("start", self.cmd_start))
        application.add_handler(CommandHandler("help", self.cmd_help))
        application.add_handler(CommandHandler("add_push", self.cmd_add_push))
        application.add_handler(CommandHandler("add_boo", self.cmd_add_boo))
        application.add_handler(CommandHandler("add_author", self.cmd_add_author))
        application.add_handler(CommandHandler("add_keyword", self.cmd_add_keyword))
        application.add_handler(CommandHandler("list", self.cmd_list))
        application.add_handler(CommandHandler("delete", self.cmd_delete))
        application.add_handler(CommandHandler("pause", self.cmd_pause))
        application.add_handler(CommandHandler("resume", self.cmd_resume))
        application.add_handler(CommandHandler("interval", self.cmd_interval))
        application.add_handler(CommandHandler("status", self.cmd_status))
    
    def build_application(self) -> Application:
        """建立 Telegram Application"""
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers(self.application)
        return self.application

