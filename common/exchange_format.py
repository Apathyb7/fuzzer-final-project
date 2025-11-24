import json
from dataclasses import dataclass, asdict
from typing import List

@dataclass
class ExecutionRecord:
    """
    一个标准化的数据类，用于封装单次程序执行的关键信息。
    它作为模糊器、Java运行器和符号执行引擎之间的数据交换格式。
    """
    method: str
    inputs: List[int]
    trace: List[int]

    def to_json(self) -> str:
        """将 ExecutionRecord 对象序列化为 JSON 字符串"""
        return json.dumps(asdict(self), indent=2)

    @staticmethod
    def from_json(json_str: str) -> "ExecutionRecord":
        """从 JSON 字符串反序列化为 ExecutionRecord 对象"""
        data = json.loads(json_str)
        return ExecutionRecord(
            method=data["method"],
            inputs=data["inputs"],
            trace=data["trace"]
        )