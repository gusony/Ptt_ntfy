"""
PTT 爬蟲通知程式 - 主程式
"""
import asyncio
import sys
import os
import io
import signal
import platform
from pathlib import Path

# 設定 stdout 編碼為 UTF-8 (解決 Windows 終端編碼問題)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from database import init_db
from notifier import TelegramNotifier
from scheduler import PTTScheduler
from config import TELEGRAM_BOT_TOKEN
from utils.logger import setup_logger, close_logger

# PID 檔案路徑
PID_FILE = Path(__file__).parent / "ptt_ntfy.pid"


def get_running_pid() -> int:
    """取得正在執行的程式 PID"""
    if not PID_FILE.exists():
        return None
    
    try:
        pid = int(PID_FILE.read_text().strip())
        return pid
    except (ValueError, IOError):
        return None


def is_process_running(pid: int) -> bool:
    """檢查指定 PID 的程序是否正在執行"""
    if pid is None:
        return False
    
    try:
        if platform.system() == "Windows":
            # Windows: 使用 tasklist 檢查
            import subprocess
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True
            )
            return str(pid) in result.stdout
        else:
            # Linux/macOS: 發送信號 0 檢查程序是否存在
            os.kill(pid, 0)
            return True
    except (OSError, subprocess.SubprocessError):
        return False


def kill_process(pid: int) -> bool:
    """終止指定 PID 的程序"""
    if pid is None:
        return False
    
    try:
        if platform.system() == "Windows":
            import subprocess
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], 
                          capture_output=True)
        else:
            os.kill(pid, signal.SIGTERM)
            # 等待一下讓程序有時間清理
            import time
            time.sleep(1)
            # 如果還在執行，強制終止
            if is_process_running(pid):
                os.kill(pid, signal.SIGKILL)
        return True
    except (OSError, subprocess.SubprocessError) as e:
        print(f"[!] 無法終止程序 {pid}: {e}")
        return False


def write_pid_file():
    """寫入當前程序的 PID"""
    PID_FILE.write_text(str(os.getpid()))


def remove_pid_file():
    """移除 PID 檔案"""
    try:
        PID_FILE.unlink()
    except FileNotFoundError:
        pass


def ensure_single_instance():
    """確保只有一個程式實例在執行"""
    print("\n檢查是否有其他實例正在執行...")
    
    old_pid = get_running_pid()
    
    if old_pid and is_process_running(old_pid):
        print(f"[!] 發現舊的程式實例 (PID: {old_pid})")
        print(f"[!] 正在終止舊程式...")
        
        if kill_process(old_pid):
            print(f"[OK] 已終止舊程式 (PID: {old_pid})")
            # 等待一下確保程序完全終止
            import time
            time.sleep(2)
        else:
            print(f"[!] 無法終止舊程式，請手動終止 PID: {old_pid}")
            sys.exit(1)
    else:
        print("[OK] 沒有其他實例正在執行")
    
    # 寫入新的 PID
    write_pid_file()
    print(f"[OK] 當前程式 PID: {os.getpid()}")


async def main():
    """主程式"""
    # 初始化日志系统（按日期创建日志文件，自动添加时间戳）
    project_root = Path(__file__).parent
    setup_logger(log_dir=project_root / "logs", log_prefix="ptt_ntfy", retention_days=14)
    
    print("=" * 50)
    print("PTT 爬蟲通知程式")
    print("=" * 50)
    
    # 確保單一實例
    ensure_single_instance()
    
    # 檢查設定
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("\n[!] 請先設定 Telegram Bot Token!")
        print("方法 1: 設定環境變數 TELEGRAM_BOT_TOKEN")
        print("方法 2: 直接修改 config.py")
        print("\n取得 Bot Token: 在 Telegram 找 @BotFather 建立 Bot")
        remove_pid_file()
        sys.exit(1)
    
    # 初始化資料庫
    print("\n正在初始化資料庫...")
    init_db()
    print("[OK] 資料庫初始化完成")
    
    # 初始化 Telegram 通知器
    print("\n正在初始化 Telegram Bot...")
    notifier = TelegramNotifier()
    application = notifier.build_application()
    print("[OK] Telegram Bot 初始化完成")
    
    # 初始化排程器
    print("\n正在初始化排程器...")
    scheduler = PTTScheduler(notifier)
    print("[OK] 排程器初始化完成")
    
    # 啟動
    print("\n" + "=" * 50)
    print(">>> 啟動服務...")
    print("=" * 50)
    
    # 啟動排程器
    scheduler.start()
    
    # 立即執行一次檢查
    print("\n執行首次檢查...")
    await scheduler.run_once()
    
    # 啟動 Telegram Bot（會阻塞在這裡）
    print("\n[OK] Telegram Bot 已啟動，等待指令...")
    print("提示: 在 Telegram 中輸入 /start 開始使用")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # 保持運行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n正在關閉...")
    finally:
        scheduler.stop()
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        remove_pid_file()
        print("[OK] 程式已關閉")
        
        # 关闭日志系统
        close_logger()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"[ERROR] 程式異常終止: {e}")
        remove_pid_file()
        close_logger()
        sys.exit(1)
