#!/usr/bin/env python3
"""
PTT 爬蟲通知程式 - 互動式設定精靈
引導使用者完成所有初始化步驟
"""
import sys
import os
import subprocess
import platform
from pathlib import Path
from datetime import datetime

# 顏色輸出 (支援 Windows 10+)
if platform.system() == "Windows":
    os.system("")  # 啟用 ANSI 轉義序列

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}  {text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_step(step, total, text):
    print(f"{Colors.CYAN}[步驟 {step}/{total}]{Colors.ENDC} {Colors.BOLD}{text}{Colors.ENDC}")


def print_success(text):
    print(f"{Colors.GREEN}[OK]{Colors.ENDC} {text}")


def print_error(text):
    print(f"{Colors.RED}[X]{Colors.ENDC} {text}")


def print_warning(text):
    print(f"{Colors.YELLOW}[!]{Colors.ENDC} {text}")


def print_info(text):
    print(f"{Colors.BLUE}[i]{Colors.ENDC} {text}")


def wait_enter(prompt="按 Enter 繼續..."):
    input(f"\n{Colors.YELLOW}{prompt}{Colors.ENDC}")


def ask_yes_no(prompt, default=True):
    """詢問是/否問題"""
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        answer = input(f"{prompt}{suffix}").strip().lower()
        if answer == "":
            return default
        if answer in ("y", "yes", "是"):
            return True
        if answer in ("n", "no", "否"):
            return False
        print("請輸入 y 或 n")


def check_python_version():
    """檢查 Python 版本"""
    major, minor = sys.version_info[:2]
    version = f"{major}.{minor}"
    
    if major >= 3 and minor >= 8:
        print_success(f"Python 版本: {version}")
        return True
    else:
        print_error(f"Python 版本 {version} 太舊，需要 3.8 以上")
        return False


def check_dependencies():
    """檢查依賴套件"""
    required = [
        ("requests", "requests"),
        ("beautifulsoup4", "bs4"),
        ("python-telegram-bot", "telegram"),
        ("SQLAlchemy", "sqlalchemy"),
        ("APScheduler", "apscheduler"),
        ("lxml", "lxml"),
    ]
    
    missing = []
    for package_name, import_name in required:
        try:
            __import__(import_name)
            print_success(f"{package_name} 已安裝")
        except ImportError:
            print_error(f"{package_name} 未安裝")
            missing.append(package_name)
    
    return missing


def install_dependencies():
    """安裝依賴套件"""
    print_info("正在安裝依賴套件...")
    
    requirements_path = Path(__file__).parent / "requirements.txt"
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_path)
        ])
        print_success("依賴套件安裝完成")
        return True
    except subprocess.CalledProcessError:
        print_error("安裝失敗，請手動執行: pip install -r requirements.txt")
        return False


def show_telegram_bot_guide():
    """顯示如何建立 Telegram Bot 的指南"""
    print(f"""
{Colors.BOLD}如何建立 Telegram Bot:{Colors.ENDC}

  1. 開啟 Telegram，搜尋 {Colors.CYAN}@BotFather{Colors.ENDC}
  
  2. 發送 {Colors.CYAN}/newbot{Colors.ENDC} 指令
  
  3. 輸入 Bot 的{Colors.BOLD}顯示名稱{Colors.ENDC}（例如：PTT 通知機器人）
  
  4. 輸入 Bot 的{Colors.BOLD} username{Colors.ENDC}（必須以 bot 結尾，例如：my_ptt_notify_bot）
  
  5. BotFather 會給你一個 {Colors.GREEN}Token{Colors.ENDC}，格式如下：
     {Colors.CYAN}123456789:ABCdefGHIjklMNOpqrsTUVwxyz{Colors.ENDC}
  
  6. 複製這個 Token
""")


def show_chat_id_guide(token):
    """顯示如何取得 Chat ID 的指南"""
    print(f"""
{Colors.BOLD}如何取得你的 Chat ID:{Colors.ENDC}

  1. 在 Telegram 中{Colors.BOLD}找到你剛建立的 Bot{Colors.ENDC}
  
  2. {Colors.BOLD}發送任意訊息{Colors.ENDC}給 Bot（例如：hello）
  
  3. 發送後，在瀏覽器開啟以下網址：
     
     {Colors.CYAN}https://api.telegram.org/bot{token}/getUpdates{Colors.ENDC}
  
  4. 在回應中找到 {Colors.GREEN}"chat":{{"id": 數字}}{Colors.ENDC}
     那個數字就是你的 Chat ID
""")


def get_chat_id_from_api(token):
    """嘗試從 API 取得 Chat ID"""
    try:
        import requests
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("ok") and data.get("result"):
            # 取得最新的 chat id
            for update in reversed(data["result"]):
                if "message" in update:
                    return str(update["message"]["chat"]["id"])
        return None
    except Exception:
        return None


def test_telegram_connection(token, chat_id):
    """測試 Telegram 連線"""
    try:
        import requests
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        response = requests.post(url, json={
            "chat_id": chat_id,
            "text": "🎉 PTT 爬蟲通知程式設定成功！\n\n輸入 /start 查看使用說明"
        }, timeout=10)
        
        return response.json().get("ok", False)
    except Exception:
        return False


def create_config_file(token, chat_id):
    """建立 config.py 檔案"""
    config_content = f'''"""
PTT 爬蟲通知程式 - 設定檔
"""
import os

# Telegram 設定
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "{token}")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "{chat_id}")

# 資料庫設定
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "ptt_ntfy.db")

# PTT 設定
PTT_BASE_URL = "https://www.ptt.cc"
PTT_BOARD_URL = "https://www.ptt.cc/bbs/{{board}}/index.html"

# 爬蟲設定
DEFAULT_PARSING_INTERVAL = 10  # 預設爬取間隔（分鐘）
REQUEST_TIMEOUT = 10  # 請求超時時間（秒）
REQUEST_HEADERS = {{
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": "over18=1"  # PTT 年齡驗證 cookie
}}
'''
    
    config_path = Path(__file__).parent / "config.py"
    config_path.write_text(config_content, encoding="utf-8")
    return config_path


def test_ptt_connection():
    """測試 PTT 連線"""
    try:
        import requests
        response = requests.get(
            "https://www.ptt.cc/bbs/Stock/index.html",
            headers={"Cookie": "over18=1"},
            timeout=10
        )
        return response.status_code == 200
    except Exception:
        return False


def main():
    """主程式"""
    print_header("PTT 爬蟲通知程式 - 設定精靈")
    
    print(f"""
歡迎使用 PTT 爬蟲通知程式！

這個精靈會引導你完成以下設定：
  • 檢查並安裝必要的套件
  • 建立 Telegram Bot
  • 設定通知接收者
  • 測試連線

預計需要 {Colors.BOLD}5-10 分鐘{Colors.ENDC}
""")
    
    if not ask_yes_no("準備好了嗎？開始設定"):
        print("\n已取消。之後可以再次執行 python setup.py")
        return
    
    total_steps = 6
    
    # ===== 步驟 1: 檢查 Python =====
    print_step(1, total_steps, "檢查 Python 環境")
    
    if not check_python_version():
        print_error("請升級 Python 版本後再試")
        return
    
    print_info(f"作業系統: {platform.system()} {platform.release()}")
    
    # ===== 步驟 2: 檢查/安裝依賴 =====
    print_step(2, total_steps, "檢查依賴套件")
    
    missing = check_dependencies()
    
    if missing:
        print_warning(f"缺少 {len(missing)} 個套件")
        if ask_yes_no("是否自動安裝？"):
            if not install_dependencies():
                return
        else:
            print_info("請手動安裝後再次執行此腳本")
            return
    
    # ===== 步驟 3: 建立 Telegram Bot =====
    print_step(3, total_steps, "設定 Telegram Bot")
    
    config_path = Path(__file__).parent / "config.py"
    if config_path.exists():
        if not ask_yes_no("已存在 config.py，是否重新設定？", default=False):
            print_info("跳過 Telegram 設定")
            token = None
            chat_id = None
        else:
            token = None
    else:
        token = None
    
    if token is None and (not config_path.exists() or ask_yes_no("設定 Telegram？", default=True)):
        show_telegram_bot_guide()
        
        wait_enter("完成上述步驟後，按 Enter 繼續...")
        
        while True:
            token = input(f"\n請貼上你的 {Colors.BOLD}Bot Token{Colors.ENDC}: ").strip()
            
            if not token:
                print_error("Token 不能為空")
                continue
            
            if ":" not in token:
                print_error("Token 格式不正確，應該包含 ':'")
                continue
            
            break
        
        # ===== 步驟 4: 取得 Chat ID =====
        print_step(4, total_steps, "取得 Chat ID")
        
        show_chat_id_guide(token)
        
        wait_enter("對 Bot 發送訊息後，按 Enter 繼續...")
        
        # 嘗試自動取得
        print_info("正在嘗試自動取得 Chat ID...")
        chat_id = get_chat_id_from_api(token)
        
        if chat_id:
            print_success(f"自動偵測到 Chat ID: {chat_id}")
            if not ask_yes_no("使用這個 Chat ID？"):
                chat_id = None
        
        if not chat_id:
            while True:
                chat_id = input(f"\n請輸入你的 {Colors.BOLD}Chat ID{Colors.ENDC}: ").strip()
                
                if not chat_id:
                    print_error("Chat ID 不能為空")
                    continue
                
                if not chat_id.lstrip("-").isdigit():
                    print_error("Chat ID 應該是數字")
                    continue
                
                break
        
        # 建立設定檔
        create_config_file(token, chat_id)
        print_success("已建立 config.py")
    
    # ===== 步驟 5: 測試連線 =====
    print_step(5, total_steps, "測試連線")
    
    # 測試 PTT
    print_info("測試 PTT 連線...")
    if test_ptt_connection():
        print_success("PTT 連線正常")
    else:
        print_warning("PTT 連線失敗（可能是暫時性問題）")
    
    # 測試 Telegram
    if token and chat_id:
        print_info("測試 Telegram 連線...")
        if test_telegram_connection(token, chat_id):
            print_success("Telegram 連線正常，請檢查是否收到測試訊息")
        else:
            print_warning("Telegram 發送失敗，請確認 Token 和 Chat ID")
    
    # ===== 步驟 6: 完成 =====
    print_step(6, total_steps, "設定完成")
    
    print_header("設定完成！")
    
    print(f"""
{Colors.GREEN}恭喜！設定已完成。{Colors.ENDC}

{Colors.BOLD}Telegram 指令：{Colors.ENDC}
  /start          - 查看使用說明
  /add_push Stock 20  - 監控 Stock 板推文數 >= 20
  /add_keyword Stock 台積電  - 監控標題含「台積電」
  /list           - 查看所有監控規則
  /status         - 查看系統狀態

{Colors.BOLD}其他指令：{Colors.ENDC}
  python check_env.py  - 檢查環境
  python test_crawler.py  - 測試爬蟲

{Colors.BOLD}更多說明請參考 README.md{Colors.ENDC}
""")
    
    # 詢問是否設定開機自動啟動
    if ask_yes_no("是否要設定開機自動啟動？", default=False):
        print_info("正在設定開機自動啟動...")
        try:
            autostart_script = Path(__file__).parent / "scripts" / "setup_autostart.py"
            if autostart_script.exists():
                subprocess.run([sys.executable, str(autostart_script)], check=False)
            else:
                print_warning("找不到 setup_autostart.py，請手動執行: python scripts/setup_autostart.py")
        except Exception as e:
            print_error(f"設定開機啟動時發生錯誤: {e}")
            print_info("請手動執行: python scripts/setup_autostart.py")
    
    # 詢問是否要在背景啟動程式
    if ask_yes_no("是否要在背景啟動程式？", default=True):
        print_info("正在背景啟動程式...")
        try:
            project_dir = Path(__file__).parent
            main_py = project_dir / "main.py"
            
            if platform.system() == "Windows":
                # Windows: 使用 Start-Process 在背景執行
                subprocess.Popen(
                    [sys.executable, str(main_py)],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    cwd=str(project_dir)
                )
                print_success("程式已在背景啟動（Windows）")
            else:
                # Linux/macOS: 使用 nohup 在背景執行
                # 注意：日志系统会自动按日期创建日志文件（ptt_ntfy-YYYY-MM-DD.log）
                # 并自动添加时间戳，所以不需要重定向 stdout/stderr
                process = subprocess.Popen(
                    [sys.executable, str(main_py)],
                    cwd=str(project_dir),
                    start_new_session=True
                )
                
                logs_dir = project_dir / "logs"
                today = datetime.now().strftime("%Y-%m-%d")
                log_file = logs_dir / f"ptt_ntfy-{today}.log"
                
                print_success(f"程式已在背景啟動（PID: {process.pid}）")
                print_info(f"日誌目錄: {logs_dir}")
                print_info(f"今日日誌: {log_file.name}")
                print_info(f"查看日誌: tail -f {log_file}")
                print_info("提示: 日誌會自動按日期分割，超過14天的日誌會自動刪除")
        except Exception as e:
            print_error(f"啟動程式時發生錯誤: {e}")
            print_info("請手動執行: python main.py")
    else:
        print_info("你可以稍後手動執行: python main.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消設定。")
        sys.exit(0)
