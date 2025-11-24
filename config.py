# fuzzer/config.py（正确版本）
class FuzzerConfig:
    def __init__(
        self,
        # Java相关配置
        java_class_path: str = "bin:lib/asm.jar",
        target_class: str = "com.test.DivisionLoop",
        # 原有fuzz配置
        timeout: float = 5.0,
        seed_count: int = 100,
        mutate_count: int = 5,
        max_iterations: int = 10000
    ):
        # 目标java项目编译后的jar包路径
        self.java_class_path = java_class_path

        # 目标测试Java类（带包名）
        self.target_class = target_class
        
        # 【已删除】错误的行：self.coverage_output_path = coverage_output_path
        
        self.timeout = timeout
        self.seed_count = seed_count
        self.mutate_count = mutate_count
        self.max_iterations = max_iterations

        # --- 新增：插桩相关配置 ---
        # 建议使用绝对路径或相对于项目根目录的路径
        # Agent jar包
        self.agent_path = "./bytescribe-agent-1.0-SNAPSHOT.jar"
        self.coverage_output_path = "./bytescribe.cov" # 正确的赋值
        self.map_output_path = "./bytescribe-map.csv"
        self.edge_coverage_path = "./per-edge.csv"