# Python Backend Configuration
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-key-here")
TIKTOK_API_KEY = os.getenv("TIKTOK_API_KEY", "your-tiktok-key-here")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "your-youtube-key-here")

# System Settings
MAX_INPUT_LENGTH = 120
MAX_WORD_COUNT = 25
COOLDOWN_PERIOD = 2.5  # giây
YOUTUBE_POLLING_FREQUENCY = 1  # giây

# LLM Settings
LOCAL_LLM_TIMEOUT = 2  # giây
CLOUD_LLM_TIMEOUT = 5  # giây
LOCAL_LLM_RESPONSE_TIME_THRESHOLD = 200  # ms

# TTS Settings
TTS_ENGINE = "local"  # "local" hoặc "google" hoặc "azure"
TTS_LANGUAGE = "vi-VN"
PUNCTUATION_DELAYS = {
    ",": 0.3,  # 300ms
    "...": 1.0,  # 1000ms
    "!": 0.2,  # 200ms
}

# Database Settings
DB_PATH = "bekai_history.db"
DB_SIZE_THRESHOLD = 30 * 1024 * 1024  # 30MB
DB_CLEANUP_LIMIT = 200  # số bản ghi xóa mỗi lần dọn dẹp

# Memory/Context Settings
CONTEXT_WINDOW_SIZE = 5  # lưu 5 lượt chat gần nhất

# Safety Shield Settings
ENABLE_JAILBREAK_DETECTION = True
BLACKLIST_FILE = "config/blacklist.txt"

# Emotion Tags
EMOTION_TAGS = {
    "CUTE": "Ngọt ngào, khen ngợi",
    "YANDERE": "Chiếm hữu, nói yêu",
    "TSUNDERE": "Kiêu kỳ, trêu ghẹo",
    "TROLL": "Cà khịa, hỏi xoáy",
    "GENKI": "Năng lượng cao, chơi game",
    "EXCITED": "Reo hò, nhận quà (ưu tiên 1)",
    "COMFORT": "Trầm ấm, an ủi",
    "SERIOUS": "Nghiêm túc, khoa học"
}

# Anti-Desync Settings
MIN_CLAUSE_BREAK_WORDS = 8
MAX_CLAUSE_BREAK_WORDS = 12
WORD_LEVEL_TIMESTAMPS = True

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "bekai.log"