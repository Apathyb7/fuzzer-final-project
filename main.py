import argparse
from config import FuzzerConfig
from fuzzer_engine import FuzzerEngine

def main():
    parser = argparse.ArgumentParser(description="Java Coverage-Based Fuzzer（对接ASM插桩）")
    # Java相关参数（可通过命令行指定）
    parser.add_argument("--java-class-path", default="bin:lib/asm.jar", help="Java类路径")
    parser.add_argument("--target-class", default="com.test.DivisionLoop", help="目标Java类名（含包名）")
    # Fuzz参数
    parser.add_argument("--max-iter", type=int, default=10000, help="最大迭代次数")
    parser.add_argument("--seed-count", type=int, default=100, help="初始种子数量")

    # 位图
    parser.add_argument("--coverage-map-size", type=int, default=65536, help="覆盖率位图的大小")
    args = parser.parse_args()

    # 初始化配置
    config = FuzzerConfig(
        java_class_path=args.java_class_path,
        target_class=args.target_class,
        max_iterations=args.max_iter,
        seed_count=args.seed_count,
        coverage_map_size=args.coverage_map_size
    )

    # 启动fuzzer
    fuzzer = FuzzerEngine(config)
    # fuzzer.run()
    fuzzer.run2()

if __name__ == "__main__":
    main()