import logging
from typing import Dict, Any, Optional, List
import numpy as np

logger = logging.getLogger(__name__)

class TTSHandler:
    """Xử lý Text-to-Speech"""
    
    def __init__(self, config):
        self.config = config
        self.tts_engine = config.TTS_ENGINE
        self.language = config.TTS_LANGUAGE
        
        if self.tts_engine == "local":
            self._init_local_tts()
        elif self.tts_engine == "google":
            self._init_google_tts()
    
    def _init_local_tts(self):
        """Khởi tạo TTS local (pyttsx3)"""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)  # Tốc độ đọc
            self.engine.setProperty('volume', 0.9)
            logger.info("Local TTS (pyttsx3) khởi tạo thành công")
        except Exception as e:
            logger.error(f"Lỗi khởi tạo pyttsx3: {e}")
            self.engine = None
    
    def _init_google_tts(self):
        """Khởi tạo Google TTS"""
        try:
            from google.cloud import texttospeech
            self.client = texttospeech.TextToSpeechClient()
            logger.info("Google TTS khởi tạo thành công")
        except Exception as e:
            logger.error(f"Lỗi khởi tạo Google TTS: {e}")
            self.client = None
    
    def synthesize(self, text: str, emotion_tag: str = "GENKI", output_file: str = None) -> Optional[bytes]:
        """Chuyển text thành âm thanh"""
        if self.tts_engine == "local":
            return self._synthesize_local(text, emotion_tag, output_file)
        elif self.tts_engine == "google":
            return self._synthesize_google(text, emotion_tag, output_file)
        
        return None
    
    def _synthesize_local(self, text: str, emotion_tag: str, output_file: str = None) -> Optional[bytes]:
        """Synthesize với pyttsx3"""
        try:
            if not self.engine:
                return None
            
            # Điều chỉnh tốc độ theo cảm xúc
            if emotion_tag == "GENKI":
                self.engine.setProperty('rate', 180)  # Nhanh hơn
            elif emotion_tag == "COMFORT":
                self.engine.setProperty('rate', 120)  # Chậm hơn
            else:
                self.engine.setProperty('rate', 150)
            
            if output_file:
                self.engine.save_to_file(text, output_file)
                self.engine.runAndWait()
                
                with open(output_file, 'rb') as f:
                    return f.read()
            else:
                self.engine.say(text)
                self.engine.runAndWait()
                return b"local_tts"  # Placeholder
        
        except Exception as e:
            logger.error(f"Lỗi Local TTS synthesis: {e}")
            return None
    
    def _synthesize_google(self, text: str, emotion_tag: str, output_file: str = None) -> Optional[bytes]:
        """Synthesize với Google TTS"""
        try:
            if not self.client:
                return None
            
            from google.cloud import texttospeech
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code="vi-VN",
                name="vi-VN-Standard-A"
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            if output_file:
                with open(output_file, 'wb') as out:
                    out.write(response.audio_content)
            
            return response.audio_content
        
        except Exception as e:
            logger.error(f"Lỗi Google TTS synthesis: {e}")
            return None
    
    def get_word_level_timestamps(self, text: str) -> List[Dict[str, Any]]:
        """Lấy word-level timestamps cho Lip-sync"""
        words = text.split()
        timestamps = []
        current_time = 0
        
        for word in words:
            # Ước tính: ~300ms mỗi từ
            duration = len(word) * 0.05 + 0.2
            
            timestamps.append({
                'word': word,
                'start_time': current_time,
                'end_time': current_time + duration,
                'amplitude': np.random.rand()  # Giả lập biên độ
            })
            
            current_time += duration
        
        return timestamps
