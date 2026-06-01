import logging
from typing import Optional

logger = logging.getLogger(__name__)

class GeminiAPIHandler:
    """Xử lý API Gemini cho Cloud LLM"""
    
    def __init__(self, config):
        self.config = config
        self.api_key = config.GEMINI_API_KEY
        self._init_gemini()
    
    def _init_gemini(self):
        """Khởi tạo Gemini API"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            logger.info("Gemini API khởi tạo thành công")
        except Exception as e:
            logger.error(f"Lỗi khởi tạo Gemini: {e}")
            self.model = None
    
    def generate_response(self, prompt: str, emotion_tag: str = "GENKI") -> Optional[str]:
        """Tạo phản hồi từ Gemini"""
        if not self.model:
            logger.error("Gemini model không khả dụng")
            return None
        
        try:
            system_prompt = f"""Bạn là Bé Kai, một AI streamer vui vẻ và thân thiện.
Trạng thái cảm xúc hiện tại: {emotion_tag}
Hãy phản hồi theo đúng cảm xúc này.

Quy tắc:
- Giữ phản hồi ngắn gọn (dưới 120 ký tự)
- Không sử dụng emoji
- Khi nhắc tên người dùng, viết [NAME] thay vì tên thật
- Không sử dụng danh sách (-,*,1.), bảng (|), hoặc code block (```)
- Tuyến tính ngữ nghĩa: không thay đổi cảm xúc đột ngột trong cùng câu
- Chèn dấu câu ngắn (8-12 từ mỗi dấu)"""
            
            response = self.model.generate_content(
                f"{system_prompt}\n\nYêu cầu: {prompt}",
                generation_config={
                    'max_output_tokens': 128,
                    'temperature': 0.7,
                }
            )
            
            return response.text.strip()
        
        except Exception as e:
            logger.error(f"Lỗi gọi Gemini API: {e}")
            return None
