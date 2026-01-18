"""
PTT 爬蟲通知程式 - 設定檔範本

使用方式：
1. 複製此檔案並重新命名為 config.py
2. 填入你的 Telegram Bot Token 和 Chat ID
"""
import os

# Telegram 設定
# 從 @BotFather 取得 Bot Token
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
# 你的 Chat ID (先對 Bot 發訊息，再從 getUpdates API 取得)
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")

# 資料庫設定
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "ptt_ntfy.db")

# PTT 設定
PTT_BASE_URL = "https://www.ptt.cc"
PTT_BOARD_URL = "https://www.ptt.cc/bbs/{board}/index.html"

# 爬蟲設定
DEFAULT_PARSING_INTERVAL = 10  # 預設爬取間隔（分鐘）
REQUEST_TIMEOUT = 10  # 請求超時時間（秒）
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": "over18=1"  # PTT 年齡驗證 cookie
}
