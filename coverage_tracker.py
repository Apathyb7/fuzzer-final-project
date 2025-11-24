# fuzzer/coverage_tracker.py（修改后，对接Java插桩）
from typing import Set, Optional, Dict, Tuple
import json
import os
import csv

class CoverageTracker:
    def __init__(self, config):
        self.covered_branches: Set[str] = set()  # 存储已覆盖的分支（Java插桩输出的分支ID）
        self.config = config

        # 使用一个集合(set)来存储所有已经覆盖过的边的ID，查询效率高
        self.covered_edges = set()
        self.total_covered_count = 0  # 可以用来统计累计覆盖的边数量

        # 初始化一个全局覆盖率位图，用 bytearray 效率更高
        # 所有位置的初始值都为 0
        self.global_coverage_map = bytearray(self.config.coverage_map_size)

        # AFL-style 的命中次数分类表。将原始计数值映射到代表性的“桶”里。
        # 0 -> 0, 1 -> 1, 2 -> 2, 3 -> 3, 4-7 -> 4, 8-15 -> 5, 16-31 -> 6, 32-127 -> 7, 128+ -> 8
        self.hit_count_buckets = self._initialize_buckets()

    def _initialize_buckets(self):
        """预先计算好0-255每个计数值对应的桶，避免重复计算"""
        buckets = bytearray(256)
        for i in range(256):
            if i == 0:
                buckets[i] = 0
            elif i == 1:
                buckets[i] = 1
            elif i == 2:
                buckets[i] = 2
            elif i == 3:
                buckets[i] = 3
            elif i < 8:
                buckets[i] = 4
            elif i < 16:
                buckets[i] = 5
            elif i < 32:
                buckets[i] = 6
            elif i < 128:
                buckets[i] = 7
            else:
                buckets[i] = 8
        return buckets

    def track_execution(self, java_runner, input_data: int) -> Tuple[bool, Optional[str]]:
        """
        调用Java程序，跟踪覆盖率并捕获异常
        :param java_runner: JavaRunner实例（负责调用Java程序）
        :param input_data: 测试用例输入
        :return: (has_new_coverage: 是否有新分支覆盖, error_msg: 异常信息（无则None）)
        """
        # 1. 调用Java程序，获取本次执行的覆盖率和异常
        coverage_data, error_msg = java_runner.run_java_program(input_data)
        if not coverage_data or "covered_branches" not in coverage_data:
            return False, error_msg  # 无覆盖率数据，视为无新覆盖

        # 2. 提取本次执行的新分支
        current_branches = set(coverage_data["covered_branches"])
        # 3. 判断是否有新分支被覆盖
        has_new_coverage = not current_branches.issubset(self.covered_branches)
        if has_new_coverage:
            self.covered_branches.update(current_branches)  # 更新全局覆盖分支

        return has_new_coverage, error_msg

    def track_execution2(self, java_runner, new_input):
        """
        执行、读取覆盖率位图并判断是否有新覆盖。
        """
        # 1. 执行Java程序
        error_msg = java_runner.run_java_program2(new_input)

        # 2. 读取本次运行生成的覆盖率位图 (bytescribe.cov)
        bitmap_file = self.config.coverage_output_path
        try:
            with open(bitmap_file, 'rb') as f:
                current_run_map = bytearray(f.read())
        except FileNotFoundError:
            # 如果位图文件不存在，说明执行失败，没有新覆盖
            return False, error_msg

        # 3. 比较位图，判断是否有新行为 (核心逻辑)
        has_new_coverage = False
        for i in range(self.config.coverage_map_size):
            # 如果当前运行的命中次数不为0
            if current_run_map[i] != 0:
                # 将当前命中次数和全局命中次数都归入“桶”中
                current_bucket = self.hit_count_buckets[current_run_map[i]]
                global_bucket = self.hit_count_buckets[self.global_coverage_map[i]]

                # 如果当前“桶”比全局“桶”更大，说明发现了新的行为
                # 例如，之前只命中1次(桶1)，现在命中了5次(桶4)，这是一个有价值的发现
                if current_bucket > global_bucket:
                    has_new_coverage = True
                    # 更新全局位图，记录下这个更有价值的命中次数
                    self.global_coverage_map[i] = current_run_map[i]

        # 4. 返回结果
        is_error = bool(error_msg and "Exception" in error_msg)
        return has_new_coverage, error_msg if is_error else None

    def get_coverage_stats(self) -> Dict:
        """返回覆盖率统计信息"""
        return {
            "total_covered_branches": len(self.covered_branches),
            "coverage_detail": list(self.covered_branches)
        }

    def get_coverage_stats2(self):
        """计算已覆盖的边的总数"""
        # 统计全局位图中非零项的数量，即为覆盖到的总边数
        total_covered_edges = sum(1 for byte in self.global_coverage_map if byte > 0)
        return {
            "total_covered_branches": total_covered_edges
        }

    def reset(self):
        """重置覆盖率（如需重新执行时使用）"""
        self.covered_branches.clear()