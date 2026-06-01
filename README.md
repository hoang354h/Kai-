# Bé Kai AI Streamer - Omni-Engine V4.0

Hệ thống AI Streamer toàn năng với Text-to-Voice Anti-Desync Protocol, Multi-Layer Safety Shield, và Hybrid LLM Routing Engine.

## Tính năng chính

✨ **Xử lý luồng dữ liệu đa nền tảng** (TikTok, YouTube)
🛡️ **Màng lọc bảo mật 3 tầng** (Input Boundary, Blacklist, Anti-Jailbreak)
🧠 **Bộ điều phối LLM lai** (Local + Cloud API)
🎭 **Ma trận thẻ cảm xúc động** (CUTE, YANDERE, TSUNDERE, TROLL, v.v.)
🔊 **Tối ưu hóa TTS và Lip-sync** (Anti-Desync Protocol)
💾 **Quản lý ký ức SQLite tự dọn dẹp**
⚡ **Streaming âm thanh theo từng câu** (Sub-second latency)

## Cấu trúc dự án

```
Kai-/
├── python/
│   ├── config/
│   │   ├── config.py
│   │   └── blacklist.txt
│   ├── core/
│   │   ├── input_handler.py
│   │   ├── safety_shield.py
│   │   ├── llm_router.py
│   │   ├─�� emotion_tagger.py
│   │   ├── text_normalizer.py
│   │   ├── anti_desync.py
│   │   └── memory_manager.py
│   ├── models/
│   │   ├── local_llm_handler.py
│   │   └── tts_handler.py
│   ├── api/
│   │   ├── tiktok_api.py
│   │   ├── youtube_api.py
│   │   └── gemini_api.py
│   ├── main.py
│   └── requirements.txt
├── nodejs/
│   ├── config/
│   │   └── config.js
│   ├── controllers/
│   │   ├── streamController.js
│   │   ├── emotionController.js
│   │   └── desyncController.js
│   ├── services/
│   │   ├── queueService.js
│   │   ├── ttsService.js
│   │   └── lipSyncService.js
│   ├── routes/
│   │   └── api.js
│   ├── server.js
│   └── package.json
├── docs/
│   └── SPECIFICATION.md
└── .gitignore
```

## Bắt đầu nhanh

### Python Backend
```bash
cd python
pip install -r requirements.txt
python main.py
```

### Node.js Frontend/Orchestrator
```bash
cd nodejs
npm install
npm start
```

## Tài liệu

Xem chi tiết tại [SPECIFICATION.md](docs/SPECIFICATION.md)

---

**Version:** 4.0  
**Author:** hoang354h  
**License:** MIT
