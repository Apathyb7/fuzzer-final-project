# fuzzer/input_generator.py
import random
from typing import List, Any

class InputGenerator:
    def __init__(self, input_type: type = int):
        """
        初始化输入生成器
        :param input_type: 目标输入类型（默认int，适配Proposal中的division_loop(int n)）
        """
        self.input_type = input_type
        self.random = random.Random()
        self.random.seed(42)  # 固定种子，保证可复现性  

    def generate_seeds(self, count: int = 100) -> List[Any]:
        """
        生成初始种子输入（覆盖常见值和边界值）
        :param count: 种子数量
        :return: 种子列表
        """
        seeds = []
        if self.input_type == int:
            # 包含边界值（0、最大值、最小值、2的幂次，适配Proposal中1024=2^10的场景）
            boundary_values = [0, 1, -1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048,
                               int(1e5), int(-1e5), int(2**31-1), int(-2**31)]
            seeds.extend(boundary_values)
            # 补充随机int值，确保种子多样性
            while len(seeds) < count:
                seeds.append(self.random.randint(-10**6, 10**6))
        # 后续可扩展其他类型（如str：生成随机字符串、常见关键词）
        return list(set(seeds))  # 去重

    def mutate(self, original_input: Any) -> Any:
        """
        变异输入（核心：基于有效输入生成新输入，触发新路径）
        变异策略：针对int类型，采用“随机修改位、加减偏移、乘除2”等算术变异（适配循环/算术密集型代码）
        :param original_input: 原始有效输入
        :return: 变异后的新输入
        """
        if self.input_type == int:
            mutation_choice = self.random.choice([
                self._bit_flip,    # 随机翻转1位二进制
                self._add_offset,  # 加减随机偏移
                self._multiply_divide,  # 乘/除2（适配Proposal中n /=2的循环）
                self._negate       # 取反
            ])
            return mutation_choice(original_input)
        return original_input

    # 以下是具体变异策略
    def _bit_flip(self, x: int) -> int:
        """随机翻转x的1位二进制位"""
        bit_pos = self.random.randint(0, 30)  # 针对32位int，避免符号位溢出
        return x ^ (1 << bit_pos)

    def _add_offset(self, x: int) -> int:
        """加减随机偏移（-10~10）"""
        offset = self.random.randint(-10, 10)
        return x + offset

    def _multiply_divide(self, x: int) -> int:
        """乘2或除2（避免除零）"""
        if x == 0:
            return x * 2
        return x * 2 if self.random.choice([True, False]) else x // 2

    def _negate(self, x: int) -> int:
        """取反"""
        return -x