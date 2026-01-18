#!/usr/bin/env python3
"""
環境檢查腳本
檢查作業系統、Python 環境、依賴套件等
"""
import sys
import platform
import shutil
import subprocess
from pathlib import Path


def print_header(title):
    """印出標題"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(name, value, status="info"):
    """印出檢查結果"""
    symbols = {"ok": "[OK]", "warn": "[!!]", "error": "[X]", "info": "[i]"}
    symbol = symbols.get(status, "[i]")
    print(f"  {symbol} {name}: {value}")


def check_os():
    """檢查作業系統"""
    print_header("作業系統資訊")
    
    os_name = platform.system()
    os_release = platform.release()
    os_version = platform.version()
    machine = platform.machine()
    
    print_result("作業系統", os_name, "ok")
    print_result("版本", os_release)
    print_result("詳細版本", os_version)
    print_result("架構", machine)
    
    # 特定系統資訊
    if os_name == "Linux":
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        distro = line.split("=")[1].strip().strip('"')
                        print_result("發行版", distro)
                        break
        except FileNotFoundError:
            pass
    elif os_name == "Darwin":
        mac_ver = platform.mac_ver()[0]
        print_result("macOS 版本", mac_ver)
    
    return os_name


def check_python():
    """檢查 Python 環境"""
    print_header("Python 環境")
    
    py_version = platform.python_version()
    py_impl = platform.python_implementation()
    py_path = sys.executable
    
    # 版本檢查
    major, minor = sys.version_info[:2]
    if major >= 3 and minor >= 8:
        print_result("Python 版本", f"{py_version} ({py_impl})", "ok")
    else:
        print_result("Python 版本", f"{py_version} (需要 3.8+)", "error")
        return False
    
    print_result("Python 路徑", py_path)
    print_result("虛擬環境", "是" if sys.prefix != sys.base_prefix else "否")
    
    return True


def check_dependencies():
    """檢查依賴套件"""
    print_header("依賴套件檢查")
    
    required_packages = [
        ("requests", "requests"),
        ("beautifulsoup4", "bs4"),
        ("python-telegram-bot", "telegram"),
        ("SQLAlchemy", "sqlalchemy"),
        ("APScheduler", "apscheduler"),
        ("lxml", "lxml"),
    ]
    
    all_ok = True
    missing = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print_result(package_name, "已安裝", "ok")
        except ImportError:
            print_result(package_name, "未安裝", "error")
            missing.append(package_name)
            all_ok = False
    
    if missing:
        print(f"\n  安裝缺少的套件:")
        print(f"  pip install {' '.join(missing)}")
    
    return all_ok


def check_config():
    """檢查設定檔"""
    print_header("設定檔檢查")
    
    config_ok = True
    
    # 檢查 config.py
    config_path = Path(__file__).parent / "config.py"
    if config_path.exists():
        print_result("config.py", "存在", "ok")
        
        # 檢查 Token 設定
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
            
            if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
                print_result("TELEGRAM_BOT_TOKEN", "未設定", "error")
                config_ok = False
            else:
                print_result("TELEGRAM_BOT_TOKEN", "已設定", "ok")
            
            if TELEGRAM_CHAT_ID == "YOUR_CHAT_ID_HERE":
                print_result("TELEGRAM_CHAT_ID", "未設定", "error")
                config_ok = False
            else:
                print_result("TELEGRAM_CHAT_ID", "已設定", "ok")
        except ImportError as e:
            print_result("設定檔匯入", str(e), "error")
            config_ok = False
    else:
        print_result("config.py", "不存在", "error")
        config_ok = False
    
    # 檢查資料庫
    db_path = Path(__file__).parent / "ptt_ntfy.db"
    if db_path.exists():
        size_kb = db_path.stat().st_size / 1024
        print_result("資料庫", f"存在 ({size_kb:.1f} KB)", "ok")
    else:
        print_result("資料庫", "尚未建立 (首次執行會自動建立)", "info")
    
    return config_ok


def check_network():
    """檢查網路連線"""
    print_header("網路連線檢查")
    
    import requests
    
    tests = [
        ("PTT", "https://www.ptt.cc/bbs/Stock/index.html"),
        ("Telegram API", "https://api.telegram.org"),
    ]
    
    all_ok = True
    
    for name, url in tests:
        try:
            # PTT 需要 over18 cookie
            cookies = {"over18": "1"} if "ptt.cc" in url else {}
            r = requests.get(url, timeout=10, cookies=cookies)
            if r.status_code == 200:
                print_result(name, "連線正常", "ok")
            else:
                print_result(name, f"HTTP {r.status_code}", "warn")
        except requests.RequestException as e:
            print_result(name, f"連線失敗: {e}", "error")
            all_ok = False
    
    return all_ok


def check_systemd_available():
    """檢查 systemd 是否可用 (Linux)"""
    if platform.system() != "Linux":
        return False
    return shutil.which("systemctl") is not None


def print_summary(results):
    """印出檢查摘要"""
    print_header("檢查摘要")
    
    all_ok = all(results.values())
    
    for name, ok in results.items():
        status = "ok" if ok else "error"
        result = "通過" if ok else "需要處理"
        print_result(name, result, status)
    
    print()
    if all_ok:
        print("  [OK] 所有檢查通過！可以啟動程式。")
        print("  執行: python main.py")
    else:
        print("  [!!] 部分檢查未通過，請先解決上述問題。")
    print()


def main():
    """主程式"""
    print("\n" + "=" * 60)
    print("  PTT 爬蟲通知程式 - 環境檢查")
    print("=" * 60)
    
    results = {}
    
    # 1. 檢查作業系統
    os_name = check_os()
    results["作業系統"] = True
    
    # 2. 檢查 Python
    results["Python 環境"] = check_python()
    
    # 3. 檢查依賴套件
    results["依賴套件"] = check_dependencies()
    
    # 4. 檢查設定檔
    results["設定檔"] = check_config()
    
    # 5. 檢查網路 (只有依賴套件都裝好才測)
    if results["依賴套件"]:
        results["網路連線"] = check_network()
    
    # 摘要
    print_summary(results)
    
    # 回傳狀態碼
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
