import argparse
import sys
import json
import time
from config import FuzzerConfig
from fuzzer_engine import FuzzerEngine
from java_runner import JavaRunner
from common.exchange_format import ExecutionRecord 

def main():
    parser = argparse.ArgumentParser(description="Java Coverage-Based Fuzzer（对接ASM插桩）")
    parser.add_argument("--java-class-path", default="bin:lib/asm.jar", help="Java类路径")
    parser.add_argument("--target-class", default="com.test.DivisionLoop", help="目标Java类名（含包名）")
    parser.add_argument("--coverage-output", default="coverage_temp.json", help="覆盖率输出JSON路径或文件名")
    parser.add_argument("--max-iter", type=int, default=10, help="最大迭代次数")
    parser.add_argument("--target-method", default="jpamb.cases.Simple.divideByN:(I)I", help="目标测试Java方法（带包名，类名，出入参类型）")
    parser.add_argument("--agent-path", default="./bytescribe-agent-1.0-SNAPSHOT.jar", help="插桩Agent jar包路径")

    # Fuzz参数
    parser.add_argument("--max-iter", type=int, default=10000, help="最大迭代次数")
    parser.add_argument("--seed-count", type=int, default=100, help="初始种子数量")

    # 位图
    parser.add_argument("--coverage-map-size", type=int, default=65536, help="覆盖率位图的大小")
    parser.add_argument("--driver", action="store_true", help="启用单次驱动模式")
    parser.add_argument("--driver-input", default=None, help="驱动模式输入JSON路径；为'-'时从stdin读取")
    parser.add_argument("--driver-output", default=None, help="驱动模式输出JSON路径；缺省时stdout")
    args = parser.parse_args()

    # --- (Driver Mode) ---
    if args.driver:
        config = FuzzerConfig(
            java_class_path=args.java_class_path,
            target_class=args.target_class,
            max_iterations=args.max_iter,
            seed_count=args.seed_count
        )
        jr = JavaRunner(
            java_class_path=config.java_class_path,
            target_class=config.target_class,
            config=config,
            coverage_output_path=config.coverage_output_path,
        )
        if args.driver_input is None or args.driver_input == "-":
            req_text = sys.stdin.read()
        else:
            with open(args.driver_input, "r", encoding="utf-8") as rf:
                req_text = rf.read()
        try:
            req = json.loads(req_text)
        except json.JSONDecodeError:
            resp = {
                "status": "error",
                "error": {"message": "无效的输入JSON格式"}
            }
            print(json.dumps(resp, ensure_ascii=False))
            return
 
        run_id = req.get("run_id", "")
        method = req.get("method", None)
        inputs = req.get("inputs", [])   # 从输入中获取参数列表

         # 确保 inputs 是一个列表
        if not isinstance(inputs, list):
            inputs = [inputs]

        t0 = time.perf_counter()
        trace, err = jr.run_java_program2(input_data=inputs, method=method)
        t_ms = int((time.perf_counter() - t0) * 1000)
 
        status = "ok" if err is None else "error"

        # 构建 ExecutionRecord 对象
        record = ExecutionRecord(
            method=method or f"{config.target_class}.main",
            inputs=inputs,
            trace=trace or [] # 如果 trace 为 None（发生错误），则用空列表
        )

        resp = {
            "run_id": run_id,
            "status": status,
            "error": {"message": err} if err else None,
            "data": record.__dict__, # 将 ExecutionRecord 对象转为字典
            "time_ms": t_ms,
        }
        out_text = json.dumps(resp, ensure_ascii=False)
        if args.driver_output:
            with open(args.driver_output, "w", encoding="utf-8") as wf:
                wf.write(out_text)
        else:
            print(out_text)
        return

    config = FuzzerConfig(
        java_class_path=args.java_class_path,
        # coverage_output_path=args.coverage_output,
        target_method=args.target_method,
        agent_path=args.agent_path,
        max_iterations=args.max_iter,
        seed_count=args.seed_count,
        coverage_map_size=args.coverage_map_size
    )

    fuzzer = FuzzerEngine(config)
    # fuzzer.run()
    fuzzer.run2()

if __name__ == "__main__":
    main()
