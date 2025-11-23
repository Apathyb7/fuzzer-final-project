# fuzzer/config.py（修改后）
class FuzzerConfig:
    def __init__(
        self,
        java_class_path: str = "bin:lib/asm.jar",
        target_class: str = "com.test.DivisionLoop",
        coverage_output_path: str = "coverage_temp.json",
        timeout: float = 5.0,
        seed_count: int = 100,
        mutate_count: int = 5,
        max_iterations: int = 10000
    ):
        self.java_class_path = java_class_path
        self.target_class = target_class
        self.coverage_output_path = coverage_output_path
        self.timeout = timeout
        self.seed_count = seed_count
        self.mutate_count = mutate_count
        self.max_iterations = max_iterations