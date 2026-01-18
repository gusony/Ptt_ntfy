"""
PTT 爬蟲模組
"""
import re
import time
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Optional
from config import PTT_BASE_URL, PTT_BOARD_URL, REQUEST_HEADERS, REQUEST_TIMEOUT


@dataclass
class Article:
    """文章資料結構"""
    title: str
    author: str
    url: str
    board: str
    push_count: int  # 正數為推，負數為噓，0為中立或無
    date: str
    
    def __repr__(self):
        return f"<Article(title={self.title}, push={self.push_count})>"


class PTTCrawler:
    """PTT 爬蟲"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)
        # 設定重試機制
        adapter = requests.adapters.HTTPAdapter(
            max_retries=requests.packages.urllib3.util.Retry(
                total=3,
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def _parse_push_count(self, push_str: str) -> int:
        """
        解析推文數
        - 數字: 直接回傳
        - 爆: 回傳 100
        - X1~X9: 回傳 -10 ~ -90
        - XX: 回傳 -100
        - 空白: 回傳 0
        """
        push_str = push_str.strip()
        if not push_str:
            return 0
        if push_str == "爆":
            return 100
        if push_str == "XX":
            return -100
        if push_str.startswith("X"):
            try:
                return -int(push_str[1]) * 10
            except (ValueError, IndexError):
                return 0
        try:
            return int(push_str)
        except ValueError:
            return 0
    
    def get_board_articles(self, board: str, max_pages: int = 2) -> List[Article]:
        """
        取得看板文章列表
        
        Args:
            board: 看板名稱
            max_pages: 最多爬幾頁
            
        Returns:
            文章列表（最新的在前面）
        """
        articles = []
        url = PTT_BOARD_URL.format(board=board)
        
        for page in range(max_pages):
            try:
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"[ERROR] 無法取得看板 {board}: {e}")
                break
            
            soup = BeautifulSoup(response.text, "lxml")
            
            # 取得文章列表
            entries = soup.select("div.r-ent")
            for entry in entries:
                try:
                    # 標題與連結
                    title_elem = entry.select_one("div.title a")
                    if not title_elem:
                        continue  # 已刪除的文章
                    
                    title = title_elem.text.strip()
                    href = title_elem.get("href", "")
                    article_url = PTT_BASE_URL + href if href else ""
                    
                    # 作者
                    author_elem = entry.select_one("div.meta div.author")
                    author = author_elem.text.strip() if author_elem else ""
                    
                    # 推文數
                    push_elem = entry.select_one("div.nrec span")
                    push_str = push_elem.text.strip() if push_elem else ""
                    push_count = self._parse_push_count(push_str)
                    
                    # 日期
                    date_elem = entry.select_one("div.meta div.date")
                    date = date_elem.text.strip() if date_elem else ""
                    
                    articles.append(Article(
                        title=title,
                        author=author,
                        url=article_url,
                        board=board,
                        push_count=push_count,
                        date=date
                    ))
                except Exception as e:
                    print(f"[ERROR] 解析文章失敗: {e}")
                    continue
            
            # 取得上一頁連結
            prev_link = soup.select_one('div.btn-group-paging a:contains("上頁")')
            if not prev_link:
                # 嘗試另一種選擇器
                paging_links = soup.select("div.btn-group-paging a")
                prev_link = None
                for link in paging_links:
                    if "上頁" in link.text:
                        prev_link = link
                        break
            
            if prev_link and prev_link.get("href"):
                url = PTT_BASE_URL + prev_link["href"]
            else:
                break
        
        return articles
    
    def get_article_detail(self, url: str) -> Optional[dict]:
        """
        取得文章詳細內容（含推噓文數）
        
        Args:
            url: 文章 URL
            
        Returns:
            文章詳細資訊
        """
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERROR] 無法取得文章 {url}: {e}")
            return None
        
        soup = BeautifulSoup(response.text, "lxml")
        
        # 計算推噓文數
        pushes = soup.select("div.push")
        push_count = 0
        boo_count = 0
        neutral_count = 0
        
        for push in pushes:
            tag = push.select_one("span.push-tag")
            if tag:
                tag_text = tag.text.strip()
                if tag_text == "推":
                    push_count += 1
                elif tag_text == "噓":
                    boo_count += 1
                else:
                    neutral_count += 1
        
        return {
            "push_count": push_count,
            "boo_count": boo_count,
            "neutral_count": neutral_count,
            "total": push_count - boo_count
        }


# 簡單測試
if __name__ == "__main__":
    crawler = PTTCrawler()
    print("正在爬取 Stock 看板...")
    articles = crawler.get_board_articles("Stock", max_pages=1)
    
    print(f"\n找到 {len(articles)} 篇文章\n")
    
    # 顯示推文數 >= 20 的文章
    hot_articles = [a for a in articles if a.push_count >= 20]
    print(f"推文數 >= 20 的文章 ({len(hot_articles)} 篇):")
    for article in hot_articles:
        print(f"  [{article.board}] {article.title}")
        print(f"    推文: {article.push_count}, 作者: {article.author}")
        print(f"    連結: {article.url}")
        print()

