import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class InputHandler:
    """
    Xử lý luồng dữ liệu đầu vào từ các nền tảng (TikTok, YouTube)
    Chuẩn hóa dữ liệu và quản lý hàng đợi bất đồng bộ
    """
    
    def __init__(self, cooldown_period: float = 2.5):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.cooldown_period = cooldown_period
        self.processing = False
        
    async def normalize_input(self, platform: str, user_name: str, 
                            payload: str, msg_type: str) -> Dict[str, Any]:
        """
        Chuẩn hóa gói dữ liệu đầu vào thành định dạng JSON cấu trúc
        
        Args:
            platform: "TikTok" hoặc "YouTube"
            user_name: Tên người dùng thô
            payload: Nội dung tin nhắn
            msg_type: "chat" hoặc "gift"
            
        Returns:
            Dict chứa dữ liệu chuẩn hóa
        """
        normalized_packet = {
            "platform": platform,
            "user_raw_name": user_name,
            "payload": payload,
            "type": msg_type,
            "timestamp": datetime.now().isoformat(),
            "priority": "HIGH" if msg_type == "gift" else "NORMAL",
            "streakable": True if platform == "TikTok" and msg_type == "gift" else False
        }
        return normalized_packet
    
    async def filter_tiktok_gift(self, packet: Dict[str, Any], 
                                combo_count: int, threshold: int = 5) -> bool:
        """
        Kiểm tra quà tặng TikTok - nếu combo < threshold thì DROP
        
        Args:
            packet: Gói dữ liệu
            combo_count: Số lượng combo hiện tại
            threshold: Ngưỡng tối thiểu (mặc định 5)
            
        Returns:
            True = Chấp nhận, False = Bỏ qua
        """
        if packet["platform"] == "TikTok" and packet["type"] == "gift":
            if packet.get("streakable") and combo_count < threshold:
                logger.info(f"DROP TikTok gift - combo count ({combo_count}) < threshold ({threshold})")
                return False
        return True
    
    async def enqueue_packet(self, packet: Dict[str, Any]) -> None:
        """
        Đẩy gói dữ liệu vào hàng đợi bất đồng bộ (FIFO)
        
        Args:
            packet: Gói dữ liệu đã chuẩn hóa
        """
        await self.queue.put(packet)
        logger.info(f"Packet enqueued: {packet['platform']} - {packet['user_raw_name']} - {packet['type']}")
    
    async def dequeue_with_cooldown(self) -> Dict[str, Any]:
        """
        Lấy gói dữ liệu từ hàng đợi với thời gian giãn cách (cooldown)
        Mặc định 2.5 giây để tránh xung đột âm thanh
        
        Returns:
            Gói dữ liệu tiếp theo
        """
        if not self.processing:
            self.processing = True
            packet = await self.queue.get()
            await asyncio.sleep(self.cooldown_period)
            self.processing = False
            return packet
        return None
    
    async def process_youtube_polling(self, fetch_func, frequency: float = 1.0) -> None:
        """
        Quét luồng dữ liệu YouTube với tần suất cố định
        
        Args:
            fetch_func: Hàm fetch dữ liệu từ YouTube API
            frequency: Tần suất quét (giây, mặc định 1s)
        """
        while True:
            try:
                messages = await fetch_func()
                for message in messages:
                    packet = await self.normalize_input(
                        platform="YouTube",
                        user_name=message.get("user"),
                        payload=message.get("message"),
                        msg_type="chat"
                    )
                    await self.enqueue_packet(packet)
                await asyncio.sleep(frequency)
            except Exception as e:
                logger.error(f"YouTube polling error: {str(e)}")
                await asyncio.sleep(frequency)
    
    def get_queue_size(self) -> int:
        """Lấy kích thước hàng đợi hiện tại"""
        return self.queue.qsize()
