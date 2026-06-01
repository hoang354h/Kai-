import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class EmotionTagger:
    """Ma trận thẻ cảm xúc động"""
    
    def __init__(self, config):
        self.config = config
        self.emotion_tags = config.EMOTION_TAGS
        self.emotion_keywords = self._build_keyword_map()
    
    def _build_keyword_map(self) -> Dict[str, List[str]]:
        """Xây dựng bản đồ từ khóa -> cảm xúc"""
        return {
            "CUTE": ["khen", "tốt", "đẹp", "yêu", "ngộ", "dễ thương", "buổi tối", "chúc", "chúc mừng"],
            "YANDERE": ["yêu em", "yêu anh", "nhớ", "cần", "muốn", "không rời", "mãi mãi", "thề"],
            "TSUNDERE": ["trêu", "đẩy thuyền", "giận", "ghét", "lừa", "xấu tính"],
            "TROLL": ["hack", "xoáy", "bắt bẻ", "ngu", "dốt", "đủng động", "lệnh"],
            "GENKI": ["game", "chơi", "vui", "cười", "haha", "hoạt động"],
            "SERIOUS": ["khoa học", "học", "toán", "vật lý", "hóa", "sinh", "lịch sử", "kiến thức"],
            "COMFORT": ["buồn", "khổ", "áp lực", "mệt", "chán", "nản"],
            "EXCITED": ["gift", "donate", "quà", "tặng"]
        }
    
    def detect_emotion(self, payload: str, msg_type: str = "chat", is_gift: bool = False) -> Tuple[str, float]:
        """Phát hiện cảm xúc từ payload"""
        payload_lower = payload.lower()
        
        # Gift/Donate có ưu tiên 1
        if msg_type == "gift" or is_gift:
            return "EXCITED", 1.0
        
        # Tính điểm cho từng cảm xúc
        emotion_scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in payload_lower:
                    score += 1
            emotion_scores[emotion] = score
        
        # Tìm cảm xúc có điểm cao nhất
        if max(emotion_scores.values()) > 0:
            best_emotion = max(emotion_scores, key=emotion_scores.get)
            confidence = emotion_scores[best_emotion] / len(self.emotion_keywords[best_emotion])
            return best_emotion, min(confidence, 1.0)
        
        # Mặc định là GENKI nếu không tìm thấy
        return "GENKI", 0.5
    
    def get_voice_style(self, emotion: str) -> Dict[str, any]:
        """Lấy cấu hình kiểu giọng dựa trên cảm xúc"""
        styles = {
            "CUTE": {
                "pitch_shift": 0.1,  # Cao hơn bình thường
                "speed": 0.95,  # Chậm chút
                "energy": 0.7,
                "modifiers": ["nha", "nè", "ưm"],
            },
            "YANDERE": {
                "pitch_shift": -0.05,
                "speed": 0.9,
                "energy": 0.8,
                "modifiers": ["...", "..."],
                "punctuation_emphasis": True,
            },
            "TSUNDERE": {
                "pitch_shift": 0.05,
                "speed": 1.0,
                "energy": 0.9,
                "modifiers": ["hứ", "xì"],
            },
            "TROLL": {
                "pitch_shift": 0.0,
                "speed": 1.05,
                "energy": 1.0,
                "modifiers": ["á à", "lêu lêu", "haha"],
            },
            "GENKI": {
                "pitch_shift": 0.15,
                "speed": 1.1,
                "energy": 1.2,
                "punctuation_emphasis": True,
                "modifiers": ["!"],
            },
            "EXCITED": {
                "pitch_shift": 0.2,
                "speed": 1.0,
                "energy": 1.5,
                "modifiers": ["!"],
                "punctuation_emphasis": True,
            },
            "COMFORT": {
                "pitch_shift": -0.1,
                "speed": 0.85,
                "energy": 0.5,
                "modifiers": ["nha", "...", "nè"],
            },
            "SERIOUS": {
                "pitch_shift": 0.0,
                "speed": 1.0,
                "energy": 0.8,
                "modifiers": [],
            },
        }
        return styles.get(emotion, styles["GENKI"])
