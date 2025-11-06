# fuzzer/fuzzer_engine.py（修改后）
from fuzzer.config import FuzzerConfig
from fuzzer.coverage_tracker import CoverageTracker
from fuzzer.input_generator import InputGenerator
from fuzzer.java_runner import JavaRunner
from fuzzer.corpus_manager import CorpusManager
from fuzzer.error_detector import ErrorDetector

class FuzzerEngine:
    def __init__(self, config: FuzzerConfig):
        self.config = config
        # 初始化Java程序调用器（对接插桩后的Java程序）
        self.java_runner = JavaRunner(
            java_class_path=config.java_class_path,
            target_class=config.target_class
        )
        # 初始化其他核心组件
        self.coverage_tracker = CoverageTracker()
        self.input_generator = InputGenerator(input_type=int)
        self.corpus_manager = CorpusManager()
        self.error_detector = ErrorDetector()

    def initialize(self):
        """初始化：生成初始种子并添加到语料库"""
        seeds = self.input_generator.generate_seeds(self.config.seed_count)
        for seed in seeds:
            self.corpus_manager.add(seed)
        print(f"初始化完成：生成 {len(seeds)} 个初始种子")
        print(f"Java目标类：{self.config.target_class}")
        print(f"Java类路径：{self.config.java_class_path}")

    def run(self):
        """启动模糊测试（核心调度逻辑）"""
        self.initialize()
        iteration = 0
        while iteration < self.config.max_iterations and self.corpus_manager.size() > 0:
            iteration += 1
            # 1. 从语料库随机选择一个有效输入
            original_input = self.corpus_manager.get_random_input()
            # 2. 对输入进行变异（生成多个变异体）
            for _ in range(self.config.mutate_count):
                new_input = self.input_generator.mutate(original_input)
                # 3. 执行Java程序，跟踪覆盖率和异常
                has_new_coverage, error_msg = self.coverage_tracker.track_execution(
                    self.java_runner, new_input
                )
                # 4. 检测并记录错误
                if error_msg:
                    self.error_detector.detect(new_input, error_msg)
                # 5. 若有新覆盖率，将输入加入语料库
                if has_new_coverage:
                    self.corpus_manager.add(new_input)
            # 打印进度（每1000次迭代）
            if iteration % 1000 == 0:
                coverage_stats = self.coverage_tracker.get_coverage_stats()
                print(
                    f"迭代 {iteration:5d} | "
                    f"语料库大小 {self.corpus_manager.size():4d} | "
                    f"覆盖分支数 {coverage_stats['total_covered_branches']:4d} | "
                    f"错误数 {self.error_detector.error_count()}"
                )
        # 输出测试总结
        self._print_summary()

    def _print_summary(self):
        coverage_stats = self.coverage_tracker.get_coverage_stats()
        print("\n" + "="*50)
        print("模糊测试结束")
        print("="*50)
        print(f"总迭代次数：{self.config.max_iterations}")
        print(f"有效测试用例数：{self.corpus_manager.size()}")
        print(f"覆盖分支总数：{coverage_stats['total_covered_branches']}")
        print(f"检测到错误数：{self.error_detector.error_count()}")
        if self.error_detector.get_errors():
            print("\n错误详情：")
            for i, error in enumerate(self.error_detector.get_errors(), 1):
                print(f"\n{i}. 输入：{error['input']}")
                print(f"   错误类型：{error['error_type']}")
                print(f"   错误信息：{error['error_message'][:100]}...")  # 截取前100字符