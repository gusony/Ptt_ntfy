#!/usr/bin/env python3
"""
自動啟動設定腳本
根據作業系統自動設定開機啟動
"""
import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path


def get_project_dir():
    """取得專案目錄"""
    return Path(__file__).parent.parent.absolute()


def setup_linux_systemd():
    """設定 Linux systemd 服務"""
    print("\n設定 Linux systemd 服務...")
    
    project_dir = get_project_dir()
    username = os.getenv("USER") or os.getenv("USERNAME")
    
    # 讀取模板
    template_path = project_dir / "scripts" / "ptt-ntfy.service"
    with open(template_path, "r") as f:
        content = f.read()
    
    # 替換變數
    content = content.replace("YOUR_USERNAME", username)
    content = content.replace("/home/YOUR_USERNAME/ptt_ntfy", str(project_dir))
    
    # 寫入暫存檔
    temp_path = Path("/tmp/ptt-ntfy.service")
    with open(temp_path, "w") as f:
        f.write(content)
    
    print(f"  專案目錄: {project_dir}")
    print(f"  使用者: {username}")
    print()
    print("  請執行以下指令完成設定:")
    print()
    print(f"  sudo cp {temp_path} /etc/systemd/system/ptt-ntfy.service")
    print("  sudo systemctl daemon-reload")
    print("  sudo systemctl enable ptt-ntfy")
    print("  sudo systemctl start ptt-ntfy")
    print()
    print("  查看狀態: sudo systemctl status ptt-ntfy")
    print("  查看日誌: sudo journalctl -u ptt-ntfy -f")


def setup_macos_launchd():
    """設定 macOS launchd 服務"""
    print("\n設定 macOS launchd 服務...")
    
    project_dir = get_project_dir()
    username = os.getenv("USER")
    home_dir = Path.home()
    
    # 建立 logs 目錄
    logs_dir = project_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # 讀取模板
    template_path = project_dir / "scripts" / "ptt-ntfy.plist"
    with open(template_path, "r") as f:
        content = f.read()
    
    # 替換變數
    content = content.replace("YOUR_USERNAME", username)
    content = content.replace(f"/Users/{username}/ptt_ntfy", str(project_dir))
    
    # 目標路徑
    launch_agents_dir = home_dir / "Library" / "LaunchAgents"
    launch_agents_dir.mkdir(parents=True, exist_ok=True)
    target_path = launch_agents_dir / "com.ptt-ntfy.plist"
    
    # 寫入檔案
    with open(target_path, "w") as f:
        f.write(content)
    
    print(f"  設定檔已寫入: {target_path}")
    print()
    print("  執行以下指令啟動服務:")
    print()
    print(f"  launchctl load {target_path}")
    print("  launchctl start com.ptt-ntfy")
    print()
    print("  查看狀態: launchctl list | grep ptt-ntfy")
    print(f"  查看日誌: tail -f {logs_dir}/stdout.log")


def setup_windows_task():
    """設定 Windows 工作排程器"""
    print("\n設定 Windows 開機自動啟動...")
    
    project_dir = get_project_dir()
    python_path = project_dir / "venv" / "Scripts" / "python.exe"
    main_path = project_dir / "main.py"
    
    # 如果沒有虛擬環境，使用系統 Python
    if not python_path.exists():
        python_path = sys.executable
    
    # 建立批次檔
    bat_content = f'''@echo off
cd /d "{project_dir}"
"{python_path}" "{main_path}"
'''
    
    bat_path = project_dir / "start_ptt_ntfy.bat"
    with open(bat_path, "w") as f:
        f.write(bat_content)
    
    # 建立 VBS 隱藏視窗啟動腳本
    vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "{bat_path}" & chr(34), 0
Set WshShell = Nothing
'''
    
    vbs_path = project_dir / "start_ptt_ntfy_hidden.vbs"
    with open(vbs_path, "w") as f:
        f.write(vbs_content)
    
    print(f"  已建立啟動腳本:")
    print(f"    - {bat_path}")
    print(f"    - {vbs_path} (隱藏視窗)")
    print()
    print("  設定開機自動啟動的方法:")
    print()
    print("  方法 1: 使用 Windows 工作排程器 (推薦)")
    print("    1. 開啟「工作排程器」(Task Scheduler)")
    print("    2. 建立基本工作")
    print("    3. 觸發程序: 「當使用者登入時」")
    print(f"    4. 動作: 啟動程式 -> {vbs_path}")
    print()
    print("  方法 2: 使用啟動資料夾")
    print("    1. 按 Win+R，輸入 shell:startup")
    print(f"    2. 建立 {vbs_path} 的捷徑到該資料夾")
    print()
    print("  手動啟動測試:")
    print(f"    {bat_path}")


def main():
    """主程式"""
    print("=" * 60)
    print("  PTT 爬蟲通知程式 - 自動啟動設定")
    print("=" * 60)
    
    os_name = platform.system()
    print(f"\n偵測到作業系統: {os_name}")
    
    if os_name == "Linux":
        # 檢查是否有 systemd
        if shutil.which("systemctl"):
            setup_linux_systemd()
        else:
            print("[!] 此系統沒有 systemd，請手動設定開機啟動")
    elif os_name == "Darwin":
        setup_macos_launchd()
    elif os_name == "Windows":
        setup_windows_task()
    else:
        print(f"[!] 不支援的作業系統: {os_name}")
        return 1
    
    print()
    print("=" * 60)
    print("  設定完成！")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
