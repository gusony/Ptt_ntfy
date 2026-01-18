#!/usr/bin/env python3
"""
Telegram 連線測試
測試 Bot Token 和 Chat ID 是否正確設定
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
    print("    或複製 config.example.py 為 config.py 並填入設定")
    sys.exit(1)

import requests


def test_bot_token():
    """測試 Bot Token 是否有效"""
    print("\n[測試 1] 檢查 Bot Token...")
    
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("[X] Bot Token 尚未設定")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("ok"):
            bot_info = data["result"]
            print(f"[OK] Bot Token 有效")
            print(f"     Bot 名稱: {bot_info.get('first_name')}")
            print(f"     Bot Username: @{bot_info.get('username')}")
            return True
        else:
            print(f"[X] Bot Token 無效: {data.get('description')}")
            return False
    except Exception as e:
        print(f"[X] 連線失敗: {e}")
        return False


def test_chat_id():
    """測試 Chat ID 是否正確"""
    print("\n[測試 2] 檢查 Chat ID...")
    
    if TELEGRAM_CHAT_ID == "YOUR_CHAT_ID_HERE":
        print("[X] Chat ID 尚未設定")
        return False
    
    print(f"[OK] Chat ID 已設定: {TELEGRAM_CHAT_ID}")
    return True


def test_send_message():
    """測試發送訊息"""
    print("\n[測試 3] 測試發送訊息...")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    try:
        response = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": "🧪 測試訊息\n\nPTT 爬蟲通知程式 - Telegram 連線測試成功！"
        }, timeout=10)
        
        data = response.json()
        
        if data.get("ok"):
            print("[OK] 訊息發送成功！請檢查 Telegram 是否收到")
            return True
        else:
            print(f"[X] 發送失敗: {data.get('description')}")
            return False
    except Exception as e:
        print(f"[X] 連線失敗: {e}")
        return False


def main():
    """執行所有測試"""
    print("=" * 50)
    print("Telegram 連線測試")
    print("=" * 50)
    
    results = []
    
    results.append(("Bot Token", test_bot_token()))
    results.append(("Chat ID", test_chat_id()))
    
    # 只有前兩項通過才測試發送
    if all(r[1] for r in results):
        results.append(("發送訊息", test_send_message()))
    
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
        print("❌ 部分測試失敗，請檢查設定")
        return 1


if __name__ == "__main__":
    sys.exit(main())
