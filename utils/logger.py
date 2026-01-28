"""
日志模块 - 按日期创建日志文件，自动添加时间戳，自动清理旧日志
"""
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class TimestampedFileWriter:
    """带时间戳的文件写入器，按日期自动切换文件"""
    
    def __init__(self, log_dir: Path, log_prefix: str = "app", retention_days: int = 14):
        """
        初始化日志写入器
        
        Args:
            log_dir: 日志目录
            log_prefix: 日志文件前缀（例如 "app" 会生成 app-2024-01-28.log）
            retention_days: 保留日志的天数，超过此天数的日志会被自动删除
        """
        self.log_dir = Path(log_dir)
        self.log_prefix = log_prefix
        self.retention_days = retention_days
        
        # 确保日志目录存在
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 当前日志文件
        self.current_date: Optional[str] = None
        self.current_file = None
        
        # 上次清理日志的日期
        self.last_cleanup_date: Optional[str] = None
        
        # 打开今天的日志文件
        self._open_today_log()
        
        # 执行首次清理检查
        self._cleanup_old_logs()
    
    def _get_today_date(self) -> str:
        """获取今天的日期字符串 YYYY-MM-DD"""
        return datetime.now().strftime("%Y-%m-%d")
    
    def _get_log_filename(self, date: str) -> str:
        """获取指定日期的日志文件名"""
        return f"{self.log_prefix}-{date}.log"
    
    def _get_log_path(self, date: str) -> Path:
        """获取指定日期的日志文件路径"""
        return self.log_dir / self._get_log_filename(date)
    
    def _open_today_log(self):
        """打开今天的日志文件"""
        today = self._get_today_date()
        
        # 如果日期改变，关闭旧文件，打开新文件
        if self.current_date != today:
            self._close_current_file()
            
            self.current_date = today
            log_path = self._get_log_path(today)
            
            # 以追加模式打开（如果文件已存在）
            self.current_file = open(log_path, "a", encoding="utf-8")
    
    def _close_current_file(self):
        """关闭当前日志文件"""
        if self.current_file:
            try:
                self.current_file.close()
            except Exception:
                pass
            self.current_file = None
    
    def _cleanup_old_logs(self):
        """清理超过保留天数的旧日志文件"""
        today = self._get_today_date()
        
        # 每天只执行一次清理
        if self.last_cleanup_date == today:
            return
        
        self.last_cleanup_date = today
        
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")
            
            # 遍历日志目录中的所有日志文件
            for log_file in self.log_dir.glob(f"{self.log_prefix}-*.log"):
                try:
                    # 从文件名提取日期
                    # 格式: prefix-YYYY-MM-DD.log
                    filename = log_file.stem  # 去掉 .log 扩展名
                    date_str = filename.replace(f"{self.log_prefix}-", "")
                    
                    # 解析日期
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")
                    
                    # 如果文件日期早于截止日期，删除文件
                    if file_date < cutoff_date:
                        log_file.unlink()
                        # 记录清理操作（带时间戳）
                        self.write(f"[日志清理] 已删除旧日志文件: {log_file.name}", skip_timestamp=False)
                except (ValueError, Exception) as e:
                    # 如果文件名格式不正确，跳过
                    continue
        except Exception as e:
            # 清理失败不影响主程序
            pass
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳（精确到秒）"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def write(self, message: str, skip_timestamp: bool = False):
        """
        写入日志消息
        
        Args:
            message: 日志消息（不应包含换行符）
            skip_timestamp: 是否跳过时间戳（用于内部消息）
        """
        # 检查是否需要切换到新文件（日期改变）
        today = self._get_today_date()
        if self.current_date != today:
            self._open_today_log()
            # 日期改变时执行清理
            self._cleanup_old_logs()
        
        # 添加时间戳
        if skip_timestamp:
            log_line = message
        else:
            timestamp = self._get_timestamp()
            log_line = f"[{timestamp}] {message}"
        
        # 确保消息以换行符结尾
        if not log_line.endswith("\n"):
            log_line += "\n"
        
        # 写入文件
        if self.current_file:
            try:
                self.current_file.write(log_line)
                self.current_file.flush()  # 立即刷新到磁盘
            except Exception:
                pass
    
    def close(self):
        """关闭日志文件"""
        self._close_current_file()


class TimestampedStream:
    """带时间戳的流包装器，拦截 stdout/stderr"""
    
    def __init__(self, original_stream, file_writer: TimestampedFileWriter, output_to_terminal: bool = True):
        self.original_stream = original_stream
        self.file_writer = file_writer
        self.output_to_terminal = output_to_terminal
        self.buffer = ""  # 用于缓冲多行消息
    
    def _is_terminal_connected(self) -> bool:
        """检查是否连接到终端"""
        try:
            # 检查 stdout 是否连接到终端
            return self.original_stream.isatty() if hasattr(self.original_stream, 'isatty') else False
        except Exception:
            return False
    
    def write(self, message: str):
        """写入消息到原始流和日志文件"""
        # 只有在 output_to_terminal=True 且连接到终端时才输出到终端
        if self.output_to_terminal and self._is_terminal_connected():
            try:
                self.original_stream.write(message)
                self.original_stream.flush()
            except Exception:
                pass
        
        # 缓冲消息，按行处理
        self.buffer += message
        
        # 如果包含换行符，处理完整的行
        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            if line.strip():  # 只记录非空行
                # 写入到日志文件（带时间戳）
                self.file_writer.write(line, skip_timestamp=False)
    
    def flush(self):
        """刷新流"""
        if self.output_to_terminal and self._is_terminal_connected():
            try:
                self.original_stream.flush()
            except Exception:
                pass
        # 刷新缓冲区中剩余的内容
        if self.buffer.strip():
            self.file_writer.write(self.buffer, skip_timestamp=False)
            self.buffer = ""
    
    def __getattr__(self, name):
        """代理其他属性到原始流"""
        return getattr(self.original_stream, name)


# 全局日志写入器
_log_writer: Optional[TimestampedFileWriter] = None


def setup_logger(log_dir: Optional[Path] = None, log_prefix: str = "app", retention_days: int = 14, output_to_terminal: Optional[bool] = None):
    """
    设置日志系统
    
    Args:
        log_dir: 日志目录，如果为 None 则使用项目根目录下的 logs 目录
        log_prefix: 日志文件前缀
        retention_days: 保留日志的天数
        output_to_terminal: 是否输出到终端。如果为 None，则自动检测（连接到终端时输出，否则不输出）
    """
    global _log_writer
    
    if _log_writer is not None:
        # 如果已经设置过，先关闭旧的文件
        _log_writer.close()
    
    # 确定日志目录
    if log_dir is None:
        # 默认使用项目根目录下的 logs 目录
        project_root = Path(__file__).parent.parent
        log_dir = project_root / "logs"
    
    # 创建日志写入器
    _log_writer = TimestampedFileWriter(log_dir, log_prefix, retention_days)
    
    # 如果 output_to_terminal 为 None，自动检测是否连接到终端
    if output_to_terminal is None:
        try:
            # 检查 stdout 是否连接到终端
            output_to_terminal = sys.stdout.isatty() if hasattr(sys.stdout, 'isatty') else False
        except Exception:
            output_to_terminal = False
    
    # 包装 stdout 和 stderr
    sys.stdout = TimestampedStream(sys.stdout, _log_writer, output_to_terminal)
    sys.stderr = TimestampedStream(sys.stderr, _log_writer, output_to_terminal)
    
    return _log_writer


def get_logger() -> Optional[TimestampedFileWriter]:
    """获取当前的日志写入器"""
    return _log_writer


def close_logger():
    """关闭日志系统"""
    global _log_writer
    if _log_writer:
        _log_writer.close()
        _log_writer = None
