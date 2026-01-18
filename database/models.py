"""
資料庫模型定義
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_PATH

Base = declarative_base()
engine = None
SessionLocal = None


class MonitorRule(Base):
    """監控規則"""
    __tablename__ = "monitor_rules"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_type = Column(String(50), nullable=False)  # push_count, boo_count, author, keyword
    board = Column(String(50), nullable=False)  # 看板名稱
    condition_value = Column(String(200), nullable=True)  # 作者名/關鍵字
    threshold = Column(Integer, nullable=True)  # 推文/噓文門檻
    created_at = Column(DateTime, default=datetime.utcnow)  # 建立時間
    last_article_url = Column(String(500), nullable=True)  # 上次爬到的文章 URL
    is_active = Column(Boolean, default=True)  # 是否啟用
    
    def __repr__(self):
        return f"<MonitorRule(id={self.id}, type={self.rule_type}, board={self.board})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "rule_type": self.rule_type,
            "board": self.board,
            "condition_value": self.condition_value,
            "threshold": self.threshold,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active
        }


class NotificationLog(Base):
    """通知記錄（避免重複通知）"""
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(Integer, nullable=False)
    article_url = Column(String(500), nullable=False)
    notified_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<NotificationLog(id={self.id}, rule_id={self.rule_id})>"


class Setting(Base):
    """系統設定"""
    __tablename__ = "settings"
    
    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Setting(key={self.key}, value={self.value})>"


def init_db():
    """初始化資料庫"""
    global engine, SessionLocal
    engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return engine


def get_session():
    """取得資料庫 session"""
    if SessionLocal is None:
        init_db()
    return SessionLocal()

