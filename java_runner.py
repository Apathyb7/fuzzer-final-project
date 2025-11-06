import subprocess
import json
import tempfile
import os
from typing import Tuple, Optional, Dict

class JavaRunner:
    def __init__(self, java_class_path: str, target_class: str, coverage_output_path: str = "coverage_temp.json"):
        """
        :param java_class_path: Java类路径（如"bin:lib/asm.jar"，包含插桩后的类文件）
        :param target_class: 目标类名（如"com.test.DivisionLoop"）
        :param coverage_output_path: 插桩Java程序输出覆盖率数据的文件路径（之前约定的）
        """
        self.java_class_path = java_class_path
        self.target_class = target_class
        self.coverage_output_path = coverage_output_path
        # 确保覆盖率输出文件不存在残留
        if os.path.exists(coverage_output_path):
            os.remove(coverage_output_path)

    def run_java_program(self, input_data: int) -> Tuple[Optional[Dict], Optional[str]]:
        """
        运行插桩后的Java程序，返回覆盖率数据和异常信息
        :param input_data: 测试用例输入（适配Java程序的int参数）
        :return: (coverage_data: 覆盖率分支列表字典, error_msg: 异常信息（无则None）)
        """
        # 1. 构造Java执行命令（如：java -cp bin:lib/asm.jar com.test.DivisionLoop 1024）
        cmd = [
            "java",
            "-cp", self.java_class_path,
            self.target_class,
            str(input_data)  # 传递输入参数（Java程序需读取命令行参数）
        ]

        try:
            # 2. 执行Java程序，捕获stdout（正常输出）和stderr（异常输出）
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5  # 超时控制（避免死循环）
            )

            # 3. 读取异常信息（Java程序抛出的异常会打印到stderr）
            error_msg = None
            if result.returncode != 0:  # 返回码非0表示执行异常
                error_msg = f"Java执行异常（返回码{result.returncode}）：{result.stderr.strip()}"

            # 4. 读取覆盖率数据（插桩程序执行后写入的文件）
            coverage_data = None
            if os.path.exists(self.coverage_output_path):
                with open(self.coverage_output_path, "r", encoding="utf-8") as f:
                    coverage_data = json.load(f)  # 预期格式：{"covered_branches": ["类:方法:行:分支ID", ...]}
                # 读取后删除临时文件，避免残留
                os.remove(self.coverage_output_path)

            return coverage_data, error_msg

        except subprocess.TimeoutExpired:
            return None, f"Java程序执行超时（超过5秒）"
        except Exception as e:
            return None, f"Python调用Java失败：{str(e)}"