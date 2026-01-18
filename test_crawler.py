"""
PTT 爬蟲測試腳本
不需要 Telegram 設定，直接測試爬蟲功能
"""
import sys
import io

# 設定 stdout 編碼為 UTF-8 (解決 Windows 終端編碼問題)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from crawler import PTTCrawler


def test_stock_board():
    """測試 Stock 看板爬蟲"""
    print("=" * 60)
    print("PTT Stock 看板爬蟲測試")
    print("=" * 60)
    
    crawler = PTTCrawler()
    
    print("\n正在爬取 Stock 看板（最新2頁）...")
    articles = crawler.get_board_articles("Stock", max_pages=2)
    
    print(f"\n[OK] 成功爬取 {len(articles)} 篇文章\n")
    
    # 找出推文數 >= 20 的文章
    threshold = 20
    hot_articles = [a for a in articles if a.push_count >= threshold]
    
    print(f"[HOT] 推文數 >= {threshold} 的文章 ({len(hot_articles)} 篇):")
    print("-" * 60)
    
    if hot_articles:
        for article in hot_articles:
            # 格式: [看板] 標題名稱 : link
            print(f"[{article.board}] {article.title} (推: {article.push_count})")
            print(f"  {article.url}")
            print()
    else:
        print("目前沒有符合條件的文章")
    
    # 顯示所有文章摘要
    print("\n" + "=" * 60)
    print("所有文章列表（依爬取順序）:")
    print("-" * 60)
    
    for i, article in enumerate(articles[:20], 1):  # 只顯示前20篇
        push_display = f"+{article.push_count}" if article.push_count > 0 else str(article.push_count)
        print(f"{i:2d}. [{push_display:>4}] {article.title[:40]}")
    
    if len(articles) > 20:
        print(f"... 還有 {len(articles) - 20} 篇文章")
    
    print("\n" + "=" * 60)
    print("測試完成！")


def test_custom_board(board: str, threshold: int = 20):
    """測試自訂看板"""
    print(f"\n正在爬取 {board} 看板...")
    
    crawler = PTTCrawler()
    articles = crawler.get_board_articles(board, max_pages=2)
    
    if not articles:
        print(f"❌ 無法取得 {board} 看板的文章，請確認看板名稱是否正確")
        return
    
    print(f"✅ 成功爬取 {len(articles)} 篇文章")
    
    hot_articles = [a for a in articles if a.push_count >= threshold]
    
    print(f"\n推文數 >= {threshold} 的文章 ({len(hot_articles)} 篇):")
    for article in hot_articles:
        print(f"[{article.board}] {article.title} (推: {article.push_count})")
        print(f"  {article.url}")
        print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 可以指定看板和門檻
        # 用法: python test_crawler.py Gossiping 50
        board = sys.argv[1]
        threshold = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        test_custom_board(board, threshold)
    else:
        # 預設測試 Stock 看板
        test_stock_board()

