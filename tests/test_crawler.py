#!/usr/bin/env python3
"""
PTT 爬蟲測試
測試爬蟲功能是否正常
"""
import sys
from pathlib import Path

# 加入專案根目錄到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from crawler import PTTCrawler


def test_connection():
    """測試 PTT 連線"""
    print("\n[測試 1] 測試 PTT 連線...")
    
    crawler = PTTCrawler()
    
    try:
        articles = crawler.get_board_articles("Stock", max_pages=1)
        if articles:
            print(f"[OK] PTT 連線正常，取得 {len(articles)} 篇文章")
            return True, articles
        else:
            print("[X] 連線成功但沒有取得文章")
            return False, []
    except Exception as e:
        print(f"[X] 連線失敗: {e}")
        return False, []


def test_article_parsing(articles):
    """測試文章解析"""
    print("\n[測試 2] 測試文章解析...")
    
    if not articles:
        print("[X] 沒有文章可供測試")
        return False
    
    article = articles[0]
    
    checks = [
        ("標題", bool(article.title)),
        ("作者", bool(article.author)),
        ("URL", bool(article.url) and "ptt.cc" in article.url),
        ("看板", article.board == "Stock"),
        ("推文數", isinstance(article.push_count, int)),
    ]
    
    all_passed = True
    for name, passed in checks:
        status = "[OK]" if passed else "[X]"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n  範例文章:")
        print(f"    標題: {article.title}")
        print(f"    作者: {article.author}")
        print(f"    推文: {article.push_count}")
    
    return all_passed


def test_push_count_filter(articles):
    """測試推文數過濾"""
    print("\n[測試 3] 測試推文數過濾...")
    
    threshold = 10
    hot_articles = [a for a in articles if a.push_count >= threshold]
    
    print(f"[OK] 找到 {len(hot_articles)} 篇推文數 >= {threshold} 的文章")
    
    if hot_articles:
        print("\n  熱門文章:")
        for article in hot_articles[:3]:
            print(f"    [{article.push_count:>3}] {article.title[:40]}")
    
    return True


def test_multiple_boards():
    """測試多個看板"""
    print("\n[測試 4] 測試多個看板...")
    
    boards = ["Stock", "Gossiping", "NBA"]
    crawler = PTTCrawler()
    
    results = []
    for board in boards:
        try:
            articles = crawler.get_board_articles(board, max_pages=1)
            if articles:
                print(f"  [OK] {board}: {len(articles)} 篇文章")
                results.append(True)
            else:
                print(f"  [X] {board}: 沒有文章")
                results.append(False)
        except Exception as e:
            print(f"  [X] {board}: {e}")
            results.append(False)
    
    return all(results)


def main():
    """執行所有測試"""
    print("=" * 50)
    print("PTT 爬蟲測試")
    print("=" * 50)
    
    results = []
    
    # 測試連線
    passed, articles = test_connection()
    results.append(("PTT 連線", passed))
    
    if passed:
        # 測試解析
        results.append(("文章解析", test_article_parsing(articles)))
        
        # 測試過濾
        results.append(("推文數過濾", test_push_count_filter(articles)))
        
        # 測試多看板
        results.append(("多看板", test_multiple_boards()))
    
    # 總結
    print("\n" + "=" * 50)
    print("測試結果")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "[OK]" if passed else "[X]"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("✅ 所有測試通過！")
        return 0
    else:
        print("❌ 部分測試失敗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
