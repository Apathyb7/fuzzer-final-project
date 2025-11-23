import argparse
import sys
import json
import time
from config import FuzzerConfig
from fuzzer_engine import FuzzerEngine
from java_runner import JavaRunner

def main():
    parser = argparse.ArgumentParser(description="Java Coverage-Based Fuzzer（对接ASM插桩）")
    parser.add_argument("--java-class-path", default="bin:lib/asm.jar", help="Java类路径")
    parser.add_argument("--target-class", default="com.test.DivisionLoop", help="目标Java类名（含包名）")
    parser.add_argument("--coverage-output", default="coverage_temp.json", help="覆盖率输出JSON路径或文件名")
    parser.add_argument("--max-iter", type=int, default=10000, help="最大迭代次数")
    parser.add_argument("--seed-count", type=int, default=100, help="初始种子数量")
    parser.add_argument("--driver", action="store_true", help="启用单次驱动模式")
    parser.add_argument("--driver-input", default=None, help="驱动模式输入JSON路径；为'-'时从stdin读取")
    parser.add_argument("--driver-output", default=None, help="驱动模式输出JSON路径；缺省时stdout")
    args = parser.parse_args()

    if args.driver:
        config = FuzzerConfig(
            java_class_path=args.java_class_path,
            target_class=args.target_class,
            coverage_output_path=args.coverage_output,
        )
        jr = JavaRunner(
            java_class_path=config.java_class_path,
            target_class=config.target_class,
            coverage_output_path=config.coverage_output_path,
        )
        if args.driver_input is None or args.driver_input == "-":
            req_text = sys.stdin.read()
        else:
            with open(args.driver_input, "r", encoding="utf-8") as rf:
                req_text = rf.read()
        try:
            req = json.loads(req_text)
        except Exception:
            resp = {
                "run_id": "",
                "status": "error",
                "error": {"message": "invalid input json"},
                "coverage": {"covered_branches": [], "total": 0},
                "trace": [],
                "time_ms": 0,
            }
            out_text = json.dumps(resp, ensure_ascii=False)
            if args.driver_output:
                with open(args.driver_output, "w", encoding="utf-8") as wf:
                    wf.write(out_text)
            else:
                print(out_text)
            return
        run_id = req.get("run_id", "")
        input_value = int(req.get("input", 0))
        t0 = time.perf_counter()
        data, err = jr.run_java_program(input_value)
        t_ms = int((time.perf_counter() - t0) * 1000)
        covered = []
        trace = []
        if isinstance(data, dict):
            covered = data.get("covered_branches", []) or []
            trace = data.get("trace", []) or []
        status = "ok" if err is None else "error"
        resp = {
            "run_id": run_id,
            "status": status,
            "error": None if err is None else {"message": err},
            "coverage": {"covered_branches": covered, "total": len(covered)},
            "trace": trace,
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
        target_class=args.target_class,
        coverage_output_path=args.coverage_output,
        max_iterations=args.max_iter,
        seed_count=args.seed_count
    )

    fuzzer = FuzzerEngine(config)
    # fuzzer.run()
    fuzzer.run2()

if __name__ == "__main__":
    main()