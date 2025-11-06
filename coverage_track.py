# fuzzer/coverage_tracker.py（修改后，对接Java插桩）
from typing import Set, Optional, Dict
import json

class CoverageTracker:
    def __init__(self):
        self.covered_branches: Set[str] = set()  # 存储已覆盖的分支（Java插桩输出的分支ID）

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

    def get_coverage_stats(self) -> Dict:
        """返回覆盖率统计信息"""
        return {
            "total_covered_branches": len(self.covered_branches),
            "coverage_detail": list(self.covered_branches)
        }

    def reset(self):
        """重置覆盖率（如需重新执行时使用）"""
        self.covered_branches.clear()