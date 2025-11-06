# fuzzer/config.py（修改后）
class FuzzerConfig:
    def __init__(
        self,
        # Java相关配置（与同学约定后填写）
        java_class_path: str = "bin:lib/asm.jar",  # Java类路径（包含插桩后的类和ASM依赖）
        target_class: str = "com.test.DivisionLoop",  # 目标Java类名（含包名）
        # 原有fuzz配置
        timeout: float = 5.0,
        seed_count: int = 100,
        mutate_count: int = 5,
        max_iterations: int = 10000
    ):
        self.java_class_path = java_class_path
        self.target_class = target_class
        self.timeout = timeout
        self.seed_count = seed_count
        self.mutate_count = mutate_count
        self.max_iterations = max_iterations