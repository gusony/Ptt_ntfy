#!/usr/bin/env python3
"""
執行所有測試
"""
import sys
import subprocess
from pathlib import Path

# 測試檔案列表
TESTS = [
    ("PTT 爬蟲測試", "test_crawler.py"),
    ("資料庫測試", "test_database.py"),
    ("Telegram 連線測試", "test_telegram.py"),
]

# 可選測試（需要使用者確認）
OPTIONAL_TESTS = [
    ("多語言訊息測試", "test_messages.py", "會發送多則測試訊息到 Telegram"),
]


def run_test(test_file):
    """執行單一測試"""
    test_path = Path(__file__).parent / test_file
    result = subprocess.run(
        [sys.executable, str(test_path)],
        capture_output=False
    )
    return result.returncode == 0


def main():
    """執行所有測試"""
    print("=" * 60)
    print("  PTT 爬蟲通知程式 - 測試套件")
    print("=" * 60)
    
    results = []
    
    # 執行基本測試
    print("\n📋 基本測試\n")
    
    for name, test_file in TESTS:
        print(f"\n{'─' * 60}")
        print(f"執行: {name}")
        print(f"{'─' * 60}")
        
        passed = run_test(test_file)
        results.append((name, passed))
    
    # 詢問可選測試
    print(f"\n{'─' * 60}")
    print("📋 可選測試")
    print(f"{'─' * 60}\n")
    
    for name, test_file, description in OPTIONAL_TESTS:
        answer = input(f"執行 {name}？({description}) [y/N]: ").strip().lower()
        if answer in ("y", "yes"):
            print(f"\n執行: {name}")
            passed = run_test(test_file)
            results.append((name, passed))
        else:
            print(f"跳過: {name}")
    
    # 總結
    print("\n" + "=" * 60)
    print("  測試總結")
    print("=" * 60 + "\n")
    
    all_passed = True
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 所有測試通過！")
        return 0
    else:
        print("⚠️  部分測試失敗，請檢查上方輸出")
        return 1


if __name__ == "__main__":
    sys.exit(main())
