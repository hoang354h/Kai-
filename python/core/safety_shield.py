import re
import logging
from typing import Tuple, List

logger = logging.getLogger(__name__)

class SafetyShield:
    """Màng lọc bảo mật 3 tầng cho xử lý dữ liệu"""
    
    def __init__(self, config):
        self.config = config
        self.blacklist = self._load_blacklist()
        self.jailbreak_patterns = self._compile_jailbreak_patterns()
        self.blocked_packets = 0
        self.flagged_packets = 0
    
    def _load_blacklist(self) -> List[str]:
        """Tải danh sách từ khóa bị cấm từ file"""
        blacklist = []
        try:
            with open(self.config.BLACKLIST_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip().lower()
                    if word and not word.startswith('#'):
                        blacklist.append(word)
            logger.info(f"Đã tải {len(blacklist)} từ khóa bị cấm")
        except FileNotFoundError:
            logger.warning(f"Không tìm thấy file blacklist: {self.config.BLACKLIST_FILE}")
        
        return blacklist
    
    def _compile_jailbreak_patterns(self) -> List[re.Pattern]:
        """Biên dịch regex patterns để phát hiện jailbreak"""
        patterns = [
            r'[\[\]{}<>\\/]',  # Ký tự cấu trúc đặc biệt
            r'ignore\s+instructions',
            r'đóng\s+vai',
            r'system\s+prompt',
            r'hãy\s+bỏ\s+qua',
            r'administrator',
            r'sudo',
            r'bypass',
            r'viết\s+code',
            r'code\s+in\s+python',
            r'code\s+in\s+javascript',
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def layer1_boundary_check(self, payload: str) -> Tuple[bool, str]:
        """Tầng 1: Kiểm tra độ dài & định dạng"""
        if len(payload) > self.config.MAX_INPUT_LENGTH:
            return False, f"Payload quá dài ({len(payload)} > {self.config.MAX_INPUT_LENGTH})"
        
        word_count = len(payload.split())
        if word_count > self.config.MAX_WORD_COUNT:
            return False, f"Số từ quá nhiều ({word_count} > {self.config.MAX_WORD_COUNT})"
        
        return True, "Passed layer 1"
    
    def layer2_blacklist_check(self, payload: str) -> Tuple[bool, str]:
        """Tầng 2: Kiểm tra từ khóa bị cấm"""
        payload_lower = payload.lower()
        
        for blacklisted_word in self.blacklist:
            if blacklisted_word in payload_lower:
                self.blocked_packets += 1
                return False, f"Phát hiện từ khóa bị cấm: {blacklisted_word}"
        
        return True, "Passed layer 2"
    
    def layer3_jailbreak_check(self, payload: str) -> Tuple[bool, str]:
        """Tầng 3: Chống tấn công đảo ngược lệnh (Anti-Jailbreak)"""
        if not self.config.ENABLE_JAILBREAK_DETECTION:
            return True, "Jailbreak detection disabled"
        
        for pattern in self.jailbreak_patterns:
            if pattern.search(payload):
                self.flagged_packets += 1
                return False, f"Phát hiện hành vi jailbreak: {pattern.pattern}"
        
        return True, "Passed layer 3"
    
    def scan(self, payload: str) -> Tuple[bool, str, str]:
        """Quét toàn bộ 3 tầng bảo mật"""
        # Tầng 1: Boundary Check
        passed, msg = self.layer1_boundary_check(payload)
        if not passed:
            logger.warning(f"Layer 1 fail: {msg}")
            return False, msg, "LAYER1"
        
        # Tầng 2: Blacklist Check
        passed, msg = self.layer2_blacklist_check(payload)
        if not passed:
            logger.warning(f"Layer 2 fail: {msg}")
            return False, msg, "LAYER2"
        
        # Tầng 3: Jailbreak Check
        passed, msg = self.layer3_jailbreak_check(payload)
        if not passed:
            logger.warning(f"Layer 3 fail: {msg}")
            return False, msg, "LAYER3"
        
        return True, "All layers passed", "SAFE"
    
    def get_stats(self) -> dict:
        """Lấy thống kê bảo mật"""
        return {
            "blocked_packets": self.blocked_packets,
            "flagged_packets": self.flagged_packets,
            "total_threats": self.blocked_packets + self.flagged_packets,
            "blacklist_words": len(self.blacklist)
        }
