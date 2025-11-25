import subprocess
import json
import tempfile
import os
from typing import Tuple, Optional, Dict

class JavaRunner:
    def __init__(self, java_class_path: str, target_method: str, config, coverage_output_path: str = "coverage_temp.json"):
        """
        :param java_class_path: Java类路径（如"bin:lib/asm.jar"，包含插桩后的类文件）
        :param target_method: 目标测试Java方法（带包名，类名，出入参类型）
        :param coverage_output_path: 插桩Java程序输出覆盖率数据的文件路径（之前约定的）
        """
        self.java_class_path = java_class_path
        self.target_method = target_method
        self.config = config # 传入 FuzzerConfig对象
        self.runtime_class = "jpamb.Runtime"    # 固定的运行时类，用于执行目标方法

        self.coverage_output_path = coverage_output_path
        # 确保覆盖率输出文件不存在残留
        if os.path.exists(coverage_output_path):
            os.remove(coverage_output_path)

    # # def run_java_program(self, input_data: int, method: Optional[str] = None) -> Tuple[Optional[Dict], Optional[str]]:
    # #     """
    # #     运行插桩后的Java程序，返回覆盖率数据和异常信息
    # #     :param input_data: 测试用例输入（适配Java程序的int参数）
    # #     :return: (coverage_data: 覆盖率分支列表字典, error_msg: 异常信息（无则None）)
    # #     """
    # #     # 1. 构造Java执行命令（如：java -cp bin:lib/asm.jar com.test.DivisionLoop 1024）
    # #     cmd = [
    # #         "java",
    # #         "-cp", self.java_class_path,
    # #         self.target_class,
    # #     ]
    #     if method is not None:
    #         cmd.append(method)
    # #     cmd.append(str(input_data))
    #
    # #     try:
    # #         # 2. 执行Java程序，捕获stdout（正常输出）和stderr（异常输出）
    # #         result = subprocess.run(
    # #             cmd,
    # #             stdout=subprocess.PIPE,
    # #             stderr=subprocess.PIPE,
    # #             text=True,
    # #             timeout=5  # 超时控制（避免死循环）
    # #         )
    #
    # #         # 3. 读取异常信息（Java程序抛出的异常会打印到stderr）
    # #         error_msg = None
    # #         if result.returncode != 0:  # 返回码非0表示执行异常
    # #             error_msg = f"Java执行异常（返回码{result.returncode}）：{result.stderr.strip()}"
    #
    # #         # 4. 读取覆盖率数据（插桩程序执行后写入的文件）
    # #         coverage_data = None
    # #         if os.path.exists(self.coverage_output_path):
    # #             with open(self.coverage_output_path, "r", encoding="utf-8") as f:
    # #                 coverage_data = json.load(f)  # 预期格式：{"covered_branches": ["类:方法:行:分支ID", ...]}
    # #             # 读取后删除临时文件，避免残留
    # #             os.remove(self.coverage_output_path)
    #
    # #         return coverage_data, error_msg
    #
    # #     except subprocess.TimeoutExpired:
    # #         return None, f"Java程序执行超时（超过5秒）"
    # #     except Exception as e:
    # #         return None, f"Python调用Java失败：{str(e)}"

    def run_java_program2(self, input_data: str, method: Optional[str] = None):
        """
        使用插桩代理执行Java程序，并返回执行结果。
        """
        # 1. 定义插桩代理和输出文件的路径 (从配置中读取)
        agent_path = self.config.agent_path
        shm_path = self.config.coverage_output_path
        map_path = self.config.map_output_path
        edge_coverage_path = self.config.edge_coverage_path

        # 2. 构建 -javaagent 参数字符串
        agent_args = (
            f"-javaagent:{agent_path}="
            f"size=65536,"
            f"shm={os.path.abspath(shm_path)},"
            f"map={os.path.abspath(map_path)},"
            f"map.append=false,"
            f"perEdge=true,"
            f"perEdgePath={os.path.abspath(edge_coverage_path)}"
        )

        # 3. 输入数据格式化
        formatted_input = f"({input_data})"

        # 4. 构建完整的Java执行命令列表
        command = [
            "java",
            agent_args,
            "-ea", # 开启断言
            "-cp",
            self.java_class_path,
            self.runtime_class,
            self.target_method, # 第一个参数: 方法签名
            formatted_input     # 第二个参数： 格式化目标待执行方法所需参数
        ] 
                
        if method:  
            command.append(method)
        if not isinstance(input_data, list):
            input_data = [input_data]
        command.extend(map(str, input_data))

        os.makedirs(os.path.dirname(edge_coverage_path), exist_ok=True)

        if os.path.exists(edge_coverage_path):
            os.remove(edge_coverage_path)

        # 4.1 log
        print(f"========executed java command is: {command}========")

        # 5. 执行命令
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.config.timeout  # 设置一个超时，防止程序卡死
            )

            error_msg = None
            if result.returncode != 0:
                error_msg = f"Java执行异常 (返回码: {result.returncode}): {result.stderr.strip()}"

            # 读取并解析覆盖率文件，提取执行轨迹（trace）
            trace = []
            if os.path.exists(edge_coverage_path):
                with open(edge_coverage_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            # 假设 per-edge.csv 的格式是 "source_offset,target_offset"
                            # 我们可以提取 source_offset 作为轨迹的一部分
                            parts = line.split(",")
                            if len(parts) >= 1:
                                try:
                                    trace.append(int(parts[0]))
                                except ValueError:
                                    # 如果格式不正确，忽略这条记录
                                    pass
            
            # 返回执行轨迹和错误信息
            return trace, error_msg

        except subprocess.TimeoutExpired:
            return None, f"Java程序执行超时 (超过 {self.config.timeout} 秒)"
        except Exception as e:
            return None, f"调用Java程序失败: {str(e)}"