import logging
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class LLMRouter:
    """Bộ điều phối LLM lai (Local + Cloud)"""
    
    def __init__(self, config, local_llm, cloud_llm):
        self.config = config
        self.local_llm = local_llm
        self.cloud_llm = cloud_llm
        self.local_keywords = self._build_local_keywords()
        self.stats = {"local_count": 0, "cloud_count": 0}
    
    def _build_local_keywords(self) -> set:
        """Từ khóa kích hoạt nhánh Local LLM"""
        return {
            "trêu", "đùa", "tán tỉnh", "thả thính", "rủ chơi", "game",
            "chơi", "vui", "cười", "hi", "hello", "chào", "xin chào",
            "tối", "sáng", "buổi", "như thế nào", "bạn", "bạn nào",
            "gì", "sao", "tại sao", "sao vậy", "á", "ơi"
        }
    
    def should_use_local(self, payload: str, msg_type: str) -> bool:
        """Quyết định sử dụng Local LLM hay Cloud"""
        # Cloud LLM cho gift/donate
        if msg_type == "gift":
            return False
        
        # Cloud LLM cho câu hỏi khoa học/học thuật
        if any(keyword in payload.lower() for keyword in ["khoa học", "toán", "vật lý", "hóa", "sinh", "lịch sử", "kiến thức"]):
            return False
        
        # Local LLM cho các câu hỏi đơn giản
        payload_lower = payload.lower()
        if any(keyword in payload_lower for keyword in self.local_keywords):
            return True
        
        # Mặc định dùng Cloud
        return False
    
    def route_and_generate(self, payload: str, msg_type: str = "chat", emotion_tag: str = "GENKI") -> Optional[str]:
        """Định tuyến và tạo phản hồi"""
        use_local = self.should_use_local(payload, msg_type)
        
        if use_local:
            logger.info("🔀 Routing to Local LLM")
            return self._call_local_llm(payload, emotion_tag)
        else:
            logger.info("🔀 Routing to Cloud LLM")
            return self._call_cloud_llm(payload, emotion_tag)
    
    def _call_local_llm(self, payload: str, emotion_tag: str) -> Optional[str]:
        """Gọi Local LLM với fallback"""
        import time
        start_time = time.time()
        
        try:
            response = self.local_llm.generate_response(payload, emotion_tag)
            elapsed = (time.time() - start_time) * 1000
            
            logger.info(f"⏱️ Local LLM response time: {elapsed:.2f}ms")
            
            if response:
                self.stats["local_count"] += 1
                return response
            
            # Nếu Local fail, chuyển sang Cloud
            logger.warning("⚠️ Local LLM failed, switching to Cloud")
            return self._call_cloud_llm(payload, emotion_tag)
        
        except Exception as e:
            logger.error(f"❌ Local LLM error: {e}")
            # Fallback to Cloud
            return self._call_cloud_llm(payload, emotion_tag)
    
    def _call_cloud_llm(self, payload: str, emotion_tag: str) -> Optional[str]:
        """Gọi Cloud LLM (Gemini)"""
        import time
        start_time = time.time()
        
        try:
            response = self.cloud_llm.generate_response(payload, emotion_tag)
            elapsed = (time.time() - start_time) * 1000
            
            logger.info(f"⏱️ Cloud LLM response time: {elapsed:.2f}ms")
            
            if response:
                self.stats["cloud_count"] += 1
                return response
            
            return None
        
        except Exception as e:
            logger.error(f"❌ Cloud LLM error: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê routing"""
        total = self.stats["local_count"] + self.stats["cloud_count"]
        return {
            "local_count": self.stats["local_count"],
            "cloud_count": self.stats["cloud_count"],
            "total": total,
            "local_ratio": f"{(self.stats['local_count'] / total * 100):.1f}%" if total > 0 else "0%",
            "cloud_ratio": f"{(self.stats['cloud_count'] / total * 100):.1f}%" if total > 0 else "0%"
        }
