# PTT 爬蟲通知程式

一個可以監控 PTT 看板並透過 Telegram 發送通知的程式。

支援 **Linux (Ubuntu/Mint)**、**macOS**、**Windows** 系統。

---

## 🚀 一鍵設定（推薦新手）

```bash
# 1. Clone 專案
git clone https://github.com/gusony/Ptt_ntfy.git
cd Ptt_ntfy

# 2. 執行設定精靈（會引導你完成所有步驟）
python setup.py
```

設定精靈會引導你：
- ✅ 檢查並安裝依賴套件
- ✅ 建立 Telegram Bot（附詳細教學）
- ✅ 設定 Chat ID（可自動偵測）
- ✅ 測試連線
- ✅ 啟動程式

---

## 目錄

- [功能特色](#功能特色)
- [系統需求](#系統需求)
- [快速開始](#快速開始)
- [詳細安裝步驟](#詳細安裝步驟)
- [設定 Telegram Bot](#設定-telegram-bot)
- [測試程式](#測試程式)
- [啟動服務](#啟動服務)
- [開機自動啟動](#開機自動啟動)
- [Telegram 指令說明](#telegram-指令說明)
- [目錄結構](#目錄結構)
- [常見問題](#常見問題)

---

## 功能特色

| 功能 | 說明 |
|------|------|
| 📊 **推文數監控** | 當文章推文數超過設定門檻時通知 |
| 👎 **噓文數監控** | 當文章噓文數超過設定門檻時通知 |
| 👤 **作者監控** | 當特定作者發文時通知 |
| 🔍 **關鍵字監控** | 當標題出現特定關鍵字時通知 |
| 💾 **設定持久化** | 使用 SQLite 儲存設定，重啟後保留 |
| ⏰ **可調整間隔** | 預設每 10 分鐘爬取一次，可自訂 |
| 🔄 **增量爬取** | 只爬取新文章，不重複通知 |

---

## 系統需求

- **Python**: 3.8 或更新版本
- **作業系統**: Linux (Ubuntu/Mint)、macOS、Windows
- **網路**: 可連線到 PTT 和 Telegram

---

## 快速開始

```bash
# 1. 複製專案
git clone <your-repo-url> ptt_ntfy
cd ptt_ntfy

# 2. 檢查環境
python check_env.py

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 設定 Telegram (編輯 config.py)
# 5. 啟動
python main.py
```

---

## 詳細安裝步驟

### Linux (Ubuntu/Mint)

```bash
# 1. 安裝 Python (如果還沒有)
sudo apt update
sudo apt install python3 python3-pip python3-venv

# 2. 複製專案
cd ~
git clone <your-repo-url> ptt_ntfy
cd ptt_ntfy

# 3. 執行安裝腳本
chmod +x scripts/install.sh
./scripts/install.sh

# 4. 啟動虛擬環境
source venv/bin/activate

# 5. 設定 Telegram (見下一節)

# 6. 檢查環境
python check_env.py
```

### macOS

```bash
# 1. 安裝 Python (使用 Homebrew)
brew install python3

# 2. 複製專案
cd ~
git clone <your-repo-url> ptt_ntfy
cd ptt_ntfy

# 3. 執行安裝腳本
chmod +x scripts/install.sh
./scripts/install.sh

# 4. 啟動虛擬環境
source venv/bin/activate

# 5. 設定 Telegram (見下一節)

# 6. 檢查環境
python check_env.py
```

### Windows

```powershell
# 1. 安裝 Python (從 https://www.python.org/downloads/ 下載)
#    安裝時記得勾選「Add Python to PATH」

# 2. 複製專案 (或下載 ZIP 解壓縮)
cd D:\git
git clone <your-repo-url> ptt_ntfy
cd ptt_ntfy

# 3. 執行安裝腳本
powershell -ExecutionPolicy Bypass -File scripts\install.ps1

# 4. 啟動虛擬環境
.\venv\Scripts\Activate.ps1

# 5. 設定 Telegram (見下一節)

# 6. 檢查環境
python check_env.py
```

---

## 設定 Telegram Bot

### 步驟 1: 建立 Bot

1. 在 Telegram 中搜尋 **@BotFather**
2. 發送 `/newbot`
3. 依照指示設定 Bot 名稱和 username
4. 取得 **Bot Token** (格式: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 步驟 2: 取得 Chat ID

1. 在 Telegram 中找到你剛建立的 Bot，發送任意訊息
2. 在瀏覽器開啟:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. 找到 `"chat":{"id": 123456789}` 中的數字，這就是你的 **Chat ID**

### 步驟 3: 設定 config.py

編輯 `config.py`，填入你的 Token 和 Chat ID:

```python
TELEGRAM_BOT_TOKEN = "你的Bot Token"
TELEGRAM_CHAT_ID = "你的Chat ID"
```

或使用環境變數:

```bash
# Linux/macOS
export TELEGRAM_BOT_TOKEN="你的Bot Token"
export TELEGRAM_CHAT_ID="你的Chat ID"

# Windows PowerShell
$env:TELEGRAM_BOT_TOKEN = "你的Bot Token"
$env:TELEGRAM_CHAT_ID = "你的Chat ID"
```

---

## 測試程式

### 1. 環境檢查

```bash
python check_env.py
```

這會檢查:
- ✓ 作業系統
- ✓ Python 版本
- ✓ 依賴套件
- ✓ 設定檔
- ✓ 網路連線

### 2. 爬蟲測試 (不需要 Telegram)

```bash
# 測試 Stock 看板，找推文數 >= 20 的文章
python test_crawler.py

# 測試其他看板
python test_crawler.py Gossiping 50
python test_crawler.py NBA 30
```

### 3. Telegram 測試

```bash
python test_telegram.py
```

你應該會在 Telegram 收到 3 則測試訊息。

---

## 啟動服務

### 前景執行

```bash
python main.py
```

### 背景執行

#### Linux/macOS

```bash
# 方法 1: 使用 nohup（推薦）
# 注意：程式會自動將日誌寫入 logs/ptt_ntfy-YYYY-MM-DD.log，無需手動重定向
nohup python main.py > /dev/null 2>&1 &

# 方法 2: 使用 screen（適合長時間執行）
screen -S ptt_ntfy
python main.py
# 按 Ctrl+A 然後 D 來 detach

# 方法 3: 使用 tmux（適合長時間執行）
tmux new -s ptt_ntfy
python main.py
# 按 Ctrl+B 然後 D 來 detach
```

#### Windows

```powershell
# 方法 1: 使用 Start-Process（推薦）
Start-Process python -ArgumentList "main.py" -WindowStyle Hidden

# 方法 2: 使用 PowerShell 背景工作
Start-Job -ScriptBlock { python main.py }
```

### 手動啟動（每次開機後）

如果你沒有設定開機自動啟動，每次開機後需要手動啟動程式：

#### Linux/macOS

```bash
# 進入專案目錄
cd ~/ptt_ntfy  # 或你的專案路徑

# 背景執行（推薦）
# 注意：程式會自動將日誌寫入 logs/ptt_ntfy-YYYY-MM-DD.log
nohup python main.py > /dev/null 2>&1 &

# 或前景執行（可以看到即時輸出）
python main.py
```

#### Windows

```powershell
# 進入專案目錄
cd D:\git\ptt_ntfy  # 或你的專案路徑

# 背景執行（推薦）
Start-Process python -ArgumentList "main.py" -WindowStyle Hidden

# 或前景執行（可以看到即時輸出）
python main.py
```

### 檢查程式是否在執行

#### Linux/macOS

```bash
# 查看程序
ps aux | grep main.py

# 查看今日日誌（日誌會自動按日期分割）
tail -f logs/ptt_ntfy-$(date +%Y-%m-%d).log

# 或查看最新的日誌文件
ls -lt logs/ptt_ntfy-*.log | head -1 | awk '{print $NF}' | xargs tail -f
```

#### Windows

```powershell
# 查看程序
Get-Process python

# 查看今日日誌（日誌會自動按日期分割）
$today = Get-Date -Format "yyyy-MM-dd"
Get-Content "logs\ptt_ntfy-$today.log" -Tail 50 -Wait
```

### 日誌系統說明

程式使用自動日誌系統，具有以下特性：

- **按日期分割**：每天自動創建新的日誌文件，格式為 `ptt_ntfy-YYYY-MM-DD.log`
- **時間戳**：每行日誌自動添加時間戳（精確到秒），格式為 `[YYYY-MM-DD HH:MM:SS]`
- **自動清理**：超過 14 天的日誌文件會自動刪除（每天檢查一次）
- **背景執行友好**：即使背景執行，所有輸出都會記錄到日誌文件

日誌文件位置：`logs/ptt_ntfy-YYYY-MM-DD.log`

啟動後，你可以在 Telegram 中對 Bot 發送 `/start` 開始使用。

---

## 開機自動啟動

執行自動設定腳本:

```bash
python scripts/setup_autostart.py
```

腳本會根據你的作業系統提供對應的設定指示。

### Linux (systemd)

```bash
# 複製服務檔案
sudo cp /tmp/ptt-ntfy.service /etc/systemd/system/

# 重新載入 systemd
sudo systemctl daemon-reload

# 啟用開機自動啟動
sudo systemctl enable ptt-ntfy

# 啟動服務
sudo systemctl start ptt-ntfy

# 查看狀態
sudo systemctl status ptt-ntfy

# 查看日誌
sudo journalctl -u ptt-ntfy -f
```

### macOS (launchd)

```bash
# 載入服務
launchctl load ~/Library/LaunchAgents/com.ptt-ntfy.plist

# 啟動服務
launchctl start com.ptt-ntfy

# 查看狀態
launchctl list | grep ptt-ntfy

# 查看日誌
tail -f ~/ptt_ntfy/logs/stdout.log
```

### Windows (工作排程器)

1. 開啟「工作排程器」(Task Scheduler)
2. 點擊「建立基本工作」
3. 名稱: `PTT Notifier`
4. 觸發程序: 「當使用者登入時」
5. 動作: 「啟動程式」
6. 程式: 選擇專案目錄下的 `start_ptt_ntfy_hidden.vbs`
7. 完成

---

## Telegram 指令說明

| 指令 | 說明 | 範例 |
|------|------|------|
| `/start` | 顯示說明 | `/start` |
| `/help` | 顯示說明 | `/help` |
| `/add_push [看板] [推文數]` | 新增推文數監控 | `/add_push Stock 20` |
| `/add_boo [看板] [噓文數]` | 新增噓文數監控 | `/add_boo Gossiping 50` |
| `/add_author [看板] [作者]` | 新增作者監控 | `/add_author Stock abc123` |
| `/add_keyword [看板] [關鍵字]` | 新增關鍵字監控 | `/add_keyword Stock 台積電` |
| `/list` | 列出所有監控規則 | `/list` |
| `/delete [規則ID]` | 刪除監控規則 | `/delete 1` |
| `/pause [規則ID]` | 暫停監控規則 | `/pause 1` |
| `/resume [規則ID]` | 恢復監控規則 | `/resume 1` |
| `/interval [分鐘]` | 設定爬取間隔 | `/interval 5` |
| `/status` | 查看系統狀態 | `/status` |

### 通知格式範例

```
[Stock] 新聞標題 (推: 25)
https://www.ptt.cc/bbs/Stock/M.1234567890.A.ABC.html
```

---

## 目錄結構

```
ptt_ntfy/
├── main.py                 # 主程式入口
├── config.py               # 設定檔
├── requirements.txt        # 依賴套件
├── check_env.py            # 環境檢查腳本
├── test_crawler.py         # 爬蟲測試腳本
├── test_telegram.py        # Telegram 測試腳本
├── ptt_ntfy.db            # SQLite 資料庫 (自動產生)
├── README.md               # 本文件
│
├── database/
│   ├── __init__.py
│   └── models.py           # 資料庫模型
│
├── crawler/
│   ├── __init__.py
│   └── ptt_crawler.py      # PTT 爬蟲
│
├── notifier/
│   ├── __init__.py
│   └── telegram_bot.py     # Telegram 通知
│
├── scheduler/
│   ├── __init__.py
│   └── scheduler.py        # 定時排程
│
├── scripts/
│   ├── install.sh          # Linux/macOS 安裝腳本
│   ├── install.ps1         # Windows 安裝腳本
│   ├── setup_autostart.py  # 自動啟動設定腳本
│   ├── ptt-ntfy.service    # Linux systemd 服務檔
│   └── ptt-ntfy.plist      # macOS launchd 設定檔
│
└── logs/                   # 日誌目錄 (自動產生)
```

---

## 常見問題

### Q: 爬蟲連線失敗?

A: PTT 有時會限制連線。程式內建重試機制，如果持續失敗:
- 檢查網路連線
- 稍後再試
- 確認 PTT 沒有維護中

### Q: 收不到 Telegram 通知?

A: 
1. 確認 Bot Token 和 Chat ID 正確
2. 確認你有對 Bot 發送過訊息 (啟動對話)
3. 執行 `python test_telegram.py` 測試

### Q: 如何備份設定?

A: 只需備份以下檔案:
- `config.py` - 設定檔
- `ptt_ntfy.db` - 資料庫 (含所有監控規則)

### Q: 如何更新程式?

A:
```bash
cd ptt_ntfy
git pull
pip install -r requirements.txt
# 重新啟動服務
```

### Q: 如何停止服務?

A:
```bash
# Linux
sudo systemctl stop ptt-ntfy

# macOS
launchctl stop com.ptt-ntfy

# Windows - 在工作管理員中結束 python.exe
```

---

## 測試

專案包含完整的測試套件，方便驗證功能和進行開發。

### 執行所有測試

```bash
python tests/run_all_tests.py
```

### 個別測試

| 測試 | 指令 | 說明 |
|------|------|------|
| PTT 爬蟲 | `python tests/test_crawler.py` | 測試爬蟲連線與解析 |
| 資料庫 | `python tests/test_database.py` | 測試 SQLite 讀寫 |
| Telegram | `python tests/test_telegram.py` | 測試 Bot 連線 |
| 多語言訊息 | `python tests/test_messages.py` | 測試各種語言顯示 |

### 環境檢查

```bash
python check_env.py
```

---

## License

MIT License
