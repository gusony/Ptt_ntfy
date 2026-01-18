#!/usr/bin/env python3
"""
資料庫測試
測試 SQLite 資料庫功能
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# 加入專案根目錄到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import init_db, get_session, MonitorRule, NotificationLog, Setting


def test_init_db():
    """測試資料庫初始化"""
    print("\n[測試 1] 測試資料庫初始化...")
    
    try:
        init_db()
        print("[OK] 資料庫初始化成功")
        return True
    except Exception as e:
        print(f"[X] 初始化失敗: {e}")
        return False


def test_create_rule():
    """測試建立規則"""
    print("\n[測試 2] 測試建立規則...")
    
    session = get_session()
    try:
        # 建立測試規則
        rule = MonitorRule(
            rule_type="push_count",
            board="Test",
            threshold=99,
            condition_value=None,
            last_article_url="https://test.url"
        )
        session.add(rule)
        session.commit()
        
        rule_id = rule.id
        print(f"[OK] 建立規則成功 (ID: {rule_id})")
        
        # 驗證
        fetched = session.query(MonitorRule).filter_by(id=rule_id).first()
        if fetched and fetched.board == "Test":
            print("[OK] 規則資料正確")
            
            # 清理測試資料
            session.delete(fetched)
            session.commit()
            print("[OK] 測試資料已清理")
            return True
        else:
            print("[X] 規則資料不正確")
            return False
            
    except Exception as e:
        print(f"[X] 測試失敗: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def test_settings():
    """測試系統設定"""
    print("\n[測試 3] 測試系統設定...")
    
    session = get_session()
    try:
        # 建立設定
        setting = Setting(key="test_key", value="test_value")
        session.add(setting)
        session.commit()
        
        # 讀取設定
        fetched = session.query(Setting).filter_by(key="test_key").first()
        if fetched and fetched.value == "test_value":
            print("[OK] 設定讀寫正常")
            
            # 清理
            session.delete(fetched)
            session.commit()
            return True
        else:
            print("[X] 設定資料不正確")
            return False
            
    except Exception as e:
        print(f"[X] 測試失敗: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def test_notification_log():
    """測試通知記錄"""
    print("\n[測試 4] 測試通知記錄...")
    
    session = get_session()
    try:
        # 建立記錄
        log = NotificationLog(
            rule_id=999,
            article_url="https://test.url/article"
        )
        session.add(log)
        session.commit()
        
        log_id = log.id
        
        # 驗證
        fetched = session.query(NotificationLog).filter_by(id=log_id).first()
        if fetched and fetched.rule_id == 999:
            print("[OK] 通知記錄正常")
            
            # 清理
            session.delete(fetched)
            session.commit()
            return True
        else:
            print("[X] 通知記錄不正確")
            return False
            
    except Exception as e:
        print(f"[X] 測試失敗: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def main():
    """執行所有測試"""
    print("=" * 50)
    print("資料庫測試")
    print("=" * 50)
    
    results = [
        ("資料庫初始化", test_init_db()),
        ("建立規則", test_create_rule()),
        ("系統設定", test_settings()),
        ("通知記錄", test_notification_log()),
    ]
    
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
