import sqlite3
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class MemoryManager:
    """Quản lý ký ức SQLite với tự dọn dẹp"""
    
    def __init__(self, config):
        self.config = config
        self.db_path = config.DB_PATH
        self.init_database()
    
    def init_database(self):
        """Khởi tạo database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tạo bảng stream_logs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stream_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    user_name TEXT,
                    emotion_tag TEXT,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tạo bảng context_window
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS context_window (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    message_index INTEGER,
                    user_name TEXT,
                    content TEXT,
                    emotion_tag TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Database khởi tạo tại {self.db_path}")
        except Exception as e:
            logger.error(f"Lỗi khởi tạo database: {e}")
    
    def insert_interaction(self, platform: str, user_name: str, emotion_tag: str, content: str) -> bool:
        """Ghi lại một lượt tương tác thành công"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO stream_logs (platform, user_name, emotion_tag, content)
                VALUES (?, ?, ?, ?)
            ''', (platform, user_name, emotion_tag, content))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Lỗi ghi lại tương tác: {e}")
            return False
    
    def get_recent_context(self, limit: int = None) -> List[Dict[str, Any]]:
        """Lấy context gần đây (5 lượt chat cuối cùng)"""
        limit = limit or self.config.CONTEXT_WINDOW_SIZE
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT platform, user_name, emotion_tag, content, timestamp
                FROM stream_logs
                ORDER BY id DESC
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            context = []
            for row in results:
                context.append({
                    'platform': row[0],
                    'user_name': row[1],
                    'emotion_tag': row[2],
                    'content': row[3],
                    'timestamp': row[4]
                })
            
            return list(reversed(context))  # Đảo ngược để có thứ tự đúng
        except Exception as e:
            logger.error(f"Lỗi lấy context: {e}")
            return []
    
    def cleanup_if_needed(self) -> bool:
        """Tự động dọn dẹp nếu database vượt quá ngưỡng"""
        try:
            import os
            file_size = os.path.getsize(self.db_path)
            
            if file_size > self.config.DB_SIZE_THRESHOLD:
                logger.info(f"Database vượt quá ngưỡng ({file_size} bytes). Dọn dẹp...")
                return self._perform_cleanup()
        except Exception as e:
            logger.error(f"Lỗi kiểm tra kích thước: {e}")
        
        return False
    
    def _perform_cleanup(self) -> bool:
        """Thực hiện dọn dẹp database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Lấy số bản ghi hiện tại
            cursor.execute('SELECT COUNT(*) FROM stream_logs')
            total_records = cursor.fetchone()[0]
            
            # Xóa 200 bản ghi cũ nhất
            cursor.execute('''
                DELETE FROM stream_logs WHERE id IN (
                    SELECT id FROM stream_logs ORDER BY id ASC LIMIT ?
                )
            ''', (self.config.DB_CLEANUP_LIMIT,))
            
            # VACUUM để giải phóng không gian
            cursor.execute('VACUUM')
            
            conn.commit()
            conn.close()
            
            logger.info(f"Đã xóa {self.config.DB_CLEANUP_LIMIT} bản ghi. Tổng còn lại: {total_records - self.config.DB_CLEANUP_LIMIT}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi dọn dẹp: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Lấy thống kê database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM stream_logs')
            total_logs = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT emotion_tag, COUNT(*) as count 
                FROM stream_logs 
                GROUP BY emotion_tag
            ''')
            emotion_stats = dict(cursor.fetchall())
            
            cursor.execute('''
                SELECT platform, COUNT(*) as count 
                FROM stream_logs 
                GROUP BY platform
            ''')
            platform_stats = dict(cursor.fetchall())
            
            conn.close()
            
            import os
            file_size = os.path.getsize(self.db_path)
            
            return {
                'total_logs': total_logs,
                'file_size_mb': file_size / (1024 * 1024),
                'emotion_distribution': emotion_stats,
                'platform_distribution': platform_stats,
                'threshold_mb': self.config.DB_SIZE_THRESHOLD / (1024 * 1024)
            }
        except Exception as e:
            logger.error(f"Lỗi lấy thống kê: {e}")
            return {}
