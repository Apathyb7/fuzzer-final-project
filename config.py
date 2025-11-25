# fuzzer/config.py（修改后）
class FuzzerConfig:
    def __init__(
        self,
        # Java相关配置（与同学约定后填写）
        java_class_path: str = "bin:lib/asm.jar",  # Java类路径（包含插桩后的类和ASM依赖）
        target_method: str = "jpamb.cases.Simple.divideByN:(I)I",  # 目标测试Java方法（带包名，类名，出入参类型）
        agent_path: str = "./bytescribe-agent-1.0-SNAPSHOT.jar", # 插桩Agent jar包路径
        # 原有fuzz配置
        timeout: float = 5.0,
        seed_count: int = 100,
        mutate_count: int = 5,
        max_iterations: int = 10000,
        coverage_map_size: int = 65536
    ):
        # 目标java项目编译后的jar包路径
        self.java_class_path = java_class_path

        # 目标测试Java方法（带包名，类名，出入参类型）
        self.target_method = target_method
        self.timeout = timeout
        self.seed_count = seed_count
        self.mutate_count = mutate_count
        self.max_iterations = max_iterations

        # --- 新增：插桩相关配置 ---
        # 位图大小
        self.coverage_map_size = coverage_map_size

        # 建议使用绝对路径或相对于项目根目录的路径
        # Agent jar包
        self.agent_path = agent_path
        self.coverage_output_path = "./bytescribe.cov"
        self.map_output_path = "./bytescribe-map.csv"
        self.edge_coverage_path = "./per-edge.csv"  # 这是最重要的文件