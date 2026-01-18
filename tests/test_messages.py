#!/usr/bin/env python3
"""
多語言訊息測試
測試 Telegram 是否能正確顯示各種語言和符號
"""
import sys
from pathlib import Path

# 加入專案根目錄到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
except ImportError:
    print("[X] 找不到 config.py")
    print("    請先執行 python setup.py 完成設定")
    sys.exit(1)

import requests


def send_message(text):
    """發送訊息到 Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }, timeout=10)
    return response.json().get("ok", False)


def main():
    """執行多語言測試"""
    print("=" * 50)
    print("多語言訊息測試")
    print("=" * 50)
    
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("[X] 請先設定 Telegram Bot Token")
        return 1
    
    messages = [
        ("英文", "Test: English message - Hello World!"),
        ("繁體中文", "測試: 繁體中文訊息 - 台灣 PTT 股票"),
        ("簡體中文", "测试: 简体中文消息 - 大陆股市"),
        ("日文", "テスト: 日本語メッセージ - こんにちは"),
        ("韓文", "테스트: 한국어 메시지 - 안녕하세요"),
        ("標點符號", "符號: 。，、；：「」【】！？～＠＃"),
        ("特殊符號", "特殊: → ← ↑ ↓ ★ ☆ ● ○ ■ □"),
        ("Emoji", "表情: 😀 🔔 📊 💰 ✅ ❌ ⚠️ 🔥"),
        ("PTT 通知格式", "[Stock] [新聞] 測試標題 (推: 87)\nhttps://www.ptt.cc/bbs/Stock/index.html"),
        ("長文測試", """📊 PTT 熱門文章通知

[Stock] 台積電法說會重點整理 (推: 100)
https://www.ptt.cc/bbs/Stock/M.1234567890.A.ABC.html

[Stock] 美股盤後分析 (推: 85)
https://www.ptt.cc/bbs/Stock/M.1234567891.A.DEF.html

---
監控中看板: Stock, Gossiping
爬取間隔: 10 分鐘"""),
    ]
    
    print(f"\n準備發送 {len(messages)} 則測試訊息...\n")
    
    results = []
    for name, text in messages:
        try:
            success = send_message(text)
            status = "[OK]" if success else "[X]"
            print(f"  {status} {name}")
            results.append(success)
        except Exception as e:
            print(f"  [X] {name}: {e}")
            results.append(False)
    
    # 總結
    passed = sum(results)
    total = len(results)
    
    print(f"\n" + "=" * 50)
    print(f"測試結果: {passed}/{total} 通過")
    print("=" * 50)
    
    if passed == total:
        print("\n✅ 所有訊息發送成功！")
        print("請檢查 Telegram 確認顯示是否正常")
        return 0
    else:
        print("\n❌ 部分訊息發送失敗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
