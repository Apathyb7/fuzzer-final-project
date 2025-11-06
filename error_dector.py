# fuzzer/error_detector.py（修改后）
from typing import Optional, List, Dict
import hashlib

class ErrorDetector:
    def __init__(self):
        self.errors: List[Dict] = []
        self.seen_errors: Set[str] = set()  # 用哈希去重，避免重复记录同一错误

    def detect(self, input_data: int, error_msg: Optional[str]) -> bool:
        if not error_msg:
            return False

        # 生成错误唯一标识（基于错误信息的哈希，避免重复）
        error_hash = hashlib.md5(error_msg.encode("utf-8")).hexdigest()
        if error_hash in self.seen_errors:
            return False

        # 记录错误详情（包含Java输入和异常信息）
        self.seen_errors.add(error_hash)
        self.errors.append({
            "input": input_data,
            "error_message": error_msg,
            "error_type": self._extract_error_type(error_msg)  # 提取错误类型（如AssertionError）
        })
        return True

    def _extract_error_type(self, error_msg: str) -> str:
        """从Java异常信息中提取错误类型（如"java.lang.AssertionError"）"""
        if "Exception" in error_msg or "Error" in error_msg:
            # Java异常格式通常是"Exception in thread "main" 类名: 消息"
            for part in error_msg.split(":"):
                if part.strip().startswith(("java.lang.", "com.")):
                    return part.strip()
        return "UnknownError"

    def get_errors(self) -> List[Dict]:
        return self.errors

    def error_count(self) -> int:
        return len(self.errors)