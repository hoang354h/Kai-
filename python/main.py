import logging
import json
from typing import Optional

logger = logging.getLogger(__name__)

class BekaiEngine:
    """Engine chính của hệ thống Bé Kai"""
    
    def __init__(self):
        logger.info("=" * 60)
        logger.info("🚀 Khởi tạo Bé Kai AI Streamer v4.0")
        logger.info("=" * 60)
        
        try:
            # Import config
            from config.config import *
            self.config = self._get_config()
            
            # Import các module
            from core.input_handler import InputHandler
            from core.safety_shield import SafetyShield
            from core.emotion_tagger import EmotionTagger
            from core.text_normalizer import TextNormalizer
            from core.anti_desync import AntiDesyncProtocol
            from core.memory_manager import MemoryManager
            from core.llm_router import LLMRouter
            from models.tts_handler import TTSHandler
            from models.local_llm_handler import LocalLLMHandler
            from api.gemini_api import GeminiAPIHandler
            
            # Khởi tạo các module
            self.input_handler = InputHandler(self.config)
            self.safety_shield = SafetyShield(self.config)
            self.emotion_tagger = EmotionTagger(self.config)
            self.text_normalizer = TextNormalizer(self.config)
            self.anti_desync = AntiDesyncProtocol(self.config)
            self.memory_manager = MemoryManager(self.config)
            self.tts_handler = TTSHandler(self.config)
            
            # Khởi tạo LLM
            self.local_llm = LocalLLMHandler(self.config)
            self.cloud_llm = GeminiAPIHandler(self.config)
            self.llm_router = LLMRouter(self.config, self.local_llm, self.cloud_llm)
            
            logger.info("✅ Tất cả module khởi tạo thành công")
            logger.info("=" * 60 + "\n")
            
        except Exception as e:
            logger.error(f"❌ Lỗi khởi tạo Engine: {e}")
            raise
    
    def _get_config(self):
        """Lấy object config"""
        import sys
        sys.path.insert(0, 'python/config')
        import config
        return config
    
    def process_message(self, platform: str, user_name: str, payload: str, msg_type: str = "chat"):
        """Xử lý một tin nhắn hoàn chỉnh"""
        
        logger.info(f"\n📥 Nhận tin nhắn: [{platform}] {user_name}: {payload}")
        
        try:
            # 1. Input Handler - Chuẩn hóa và xếp hàng
            from core.input_handler import InputPacket
            packet = InputPacket(platform, user_name, payload, msg_type)
            
            packet_json = json.dumps({
                "platform": platform,
                "user_raw_name": user_name,
                "payload": payload,
                "type": msg_type
            })
            
            if not self.input_handler.process_packet(packet_json):
                logger.warning(f"❌ Packet bị drop")
                return None
            
            # 2. Safety Shield - 3 tầng kiểm duyệt
            passed, msg, layer = self.safety_shield.scan(payload)
            if not passed:
                logger.warning(f"🛡️ Safety Shield blocked (Layer {layer}): {msg}")
                return {"status": "blocked", "reason": msg, "layer": layer}
            
            # 3. Emotion Tagger - Phát hiện cảm xúc
            emotion_tag, confidence = self.emotion_tagger.detect_emotion(payload, msg_type, msg_type == "gift")
            logger.info(f"🎭 Cảm xúc: {emotion_tag} (confidence: {confidence:.2f})")
            
            # 4. Text Normalizer - Chuẩn hóa text
            normalized_text = self.text_normalizer.normalize(payload)
            logger.info(f"📝 Văn bản chuẩn: {normalized_text}")
            
            # 5. LLM Router - Định tuyến và tạo phản hồi
            ai_response = self.llm_router.route_and_generate(payload, msg_type, emotion_tag)
            if not ai_response:
                logger.error("❌ LLM không thể tạo phản hồi")
                return None
            
            # 6. Sanitize user name
            sanitized_name = self.text_normalizer.sanitize_for_name(user_name)
            
            # 7. Replace [NAME] token
            final_response = ai_response.replace("[NAME]", sanitized_name)
            logger.info(f"💬 Phản hồi cuối: {final_response}")
            
            # 8. Anti-Desync Protocol
            desync_data = self.anti_desync.process_for_desync_free_delivery(final_response, emotion_tag)
            
            # 9. TTS
            audio_generated = False
            try:
                audio_data = self.tts_handler.synthesize(final_response, emotion_tag)
                audio_generated = audio_data is not None
                if audio_generated:
                    logger.info(f"🔊 Âm thanh được tạo thành công")
            except Exception as e:
                logger.warning(f"⚠️ Lỗi TTS: {e}")
            
            # 10. Memory Manager
            self.memory_manager.insert_interaction(platform, user_name, emotion_tag, final_response)
            self.memory_manager.cleanup_if_needed()
            
            logger.info(f"📤 Phản hồi hoàn tất\n")
            
            return {
                "status": "success",
                "emotion_tag": emotion_tag,
                "ai_response": final_response,
                "audio_generated": audio_generated,
                "chunks": desync_data.get('chunks', []),
                "total_duration": desync_data.get('total_duration', 0),
                "requires_lip_sync": desync_data.get('requires_lip_sync', False)
            }
        
        except Exception as e:
            logger.error(f"❌ Lỗi xử lý: {e}", exc_info=True)
            return None
    
    def get_system_stats(self):
        """Lấy thống kê hệ thống"""
        return {
            "input_handler": self.input_handler.get_queue_stats(),
            "safety_shield": self.safety_shield.get_stats(),
            "llm_router": self.llm_router.get_stats(),
            "memory": self.memory_manager.get_statistics(),
        }

if __name__ == "__main__":
    import sys
    sys.path.insert(0, 'python')
    
    # Khởi tạo engine
    engine = BekaiEngine()
    
    # Test examples
    test_messages = [
        ("TikTok", "Người xem 1", "Em yêu bé Kai quá", "chat"),
        ("YouTube", "Fan 123", "Bé Kai dễ thương lắm nè", "chat"),
        ("TikTok", "Donate user", "Tặng quà cho bé Kai", "gift"),
    ]
    
    print("\n" + "="*60)
    print("🧪 TEST MESSAGES")
    print("="*60)
    
    for platform, user, msg, msg_type in test_messages:
        result = engine.process_message(platform, user, msg, msg_type)
        if result and result.get("status") == "success":
            print(f"✅ Phản hồi: [{result['emotion_tag']}] {result['ai_response']}")
        else:
            print(f"❌ Lỗi: {result}")
    
    print("\n" + "="*60)
    print("📊 THỐNG KÊ HỆ THỐNG")
    print("="*60)
    stats = engine.get_system_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
