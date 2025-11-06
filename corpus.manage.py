import random
from typing import List, Any, Set

class CorpusManager:
    """管理有效测试用例（带来新覆盖率的输入），去重并优先级排序"""
    def __init__(self):
        self.corpus: List[Any] = []  # 有效输入列表（按添加顺序排序）
        self.seen: Set[Any] = set()  # 去重集合

    def add(self, input_data: Any) -> bool:
        """添加输入到语料库（去重）"""
        if input_data not in self.seen:
            self.seen.add(input_data)
            self.corpus.append(input_data)
            return True
        return False

    def get_random_input(self) -> Any:
        """从语料库中随机选择一个输入（用于变异）"""
        return random.choice(self.corpus) if self.corpus else None

    def size(self) -> int:
        return len(self.corpus)

    # TODOLIST
    # - 基于覆盖率的种子优先级排序
    # - 能量调度机制  
    # - 种子质量评估
    # - 智能选择策略
