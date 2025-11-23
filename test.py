import re

def cgi_decode_manual(s: str, encoding: str = 'utf-8', errors: str = 'strict') -> str:
    """
    手动实现的 CGI 解码（不依赖 urllib，用于理解底层原理）
    功能与 cgi_decode 一致，但性能略低于内置实现
    """
    if not isinstance(s, str):
        raise TypeError(f"输入必须是字符串，当前类型: {type(s).__name__}")

    # 替换 + 为空格
    s = s.replace('+', ' ')

    # 匹配 %XX 格式的十六进制编码（XX 为 0-9, a-f, A-F）
    hex_pattern = re.compile(r'%([0-9a-fA-F]{2})')

    # 替换函数：将 %XX 转换为对应的字节
    def replace_hex(match: re.Match) -> str:
        hex_str = match.group(1)
        return chr(int(hex_str, 16))

    # 先解码 %XX 为字节对应的字符，再按指定编码解码
    try:
        # 生成字节串（处理多字节字符）
        byte_str = ''.join([
            chr(int(match.group(1), 16)) if hex_pattern.match(c) else c
            for c in hex_pattern.split(s)
        ]).encode('latin-1')  # latin-1 可无损映射 0x00-0xFF
        return byte_str.decode(encoding=encoding, errors=errors)
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            encoding,
            e.bytes,
            e.start,
            e.end,
            f"在手动 CGI 解码过程中遇到无效 {encoding} 编码: {e.reason}"
        ) from None

def traceit(frame,event,arg):
    if event == 'call':
        print(f"调用函数: {frame.f_code.co_name}")
        line = frame.f_lineno
        function_name = frame.f_code.co_name
        print(f"{function_name} 第 {line} 行调用 event: {event}")
    return traceit

import sys

def trace_cgi_decode_manual(s):
    sys.settrace(traceit)
    result = cgi_decode_manual(s)
    sys.settrace(None)
    return result

trace_cgi_decode_manual('Hello%20World')
