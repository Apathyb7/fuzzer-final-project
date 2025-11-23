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
        执行、读取覆盖率文件并判断是否有新覆盖。
        """
        # 1. 执行Java程序
        error_msg = java_runner.run_java_program2(new_input)

        # 2. 读取并解析边覆盖率文件 (per-edge.csv)
        has_new_coverage = False
        edge_file = self.config.edge_coverage_path

        if not os.path.exists(edge_file):
            # 如果文件不存在，说明执行可能失败或没有产生覆盖率信息
            return False, error_msg

        with open(edge_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row: continue
                try:
                    edge_id, hit_count_str = row[0].split(':')
                    hit_count = int(hit_count_str)
                except ValueError:
                    # 如果无法解析或转换，很可能是表头，直接跳过
                    continue

                # 只要边被命中(hit_count > 0)，并且是第一次见到这个边
                if hit_count > 0 and edge_id not in self.covered_edges:
                    has_new_coverage = True
                    self.covered_edges.add(edge_id)

        self.total_covered_count = len(self.covered_edges)

        # 3. 返回结果
        # 如果有错误信息，说明可能触发了bug
        is_error = bool(error_msg and "Exception" in error_msg)
        return has_new_coverage, error_msg if is_error else None

    def get_coverage_stats(self) -> Dict:
        """返回覆盖率统计信息"""
        return {
            "total_covered_branches": len(self.covered_branches),
            "coverage_detail": list(self.covered_branches)
        }

    def get_coverage_stats2(self):
        return {
            "total_covered_branches": self.total_covered_count # 分支现在等同于边
        }

    def reset(self):
        """重置覆盖率（如需重新执行时使用）"""
        self.covered_branches.clear()