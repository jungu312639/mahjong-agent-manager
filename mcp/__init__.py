from .file_ops import read_cpp_code, write_cpp_code
from .builder import compile_and_run_cpp
from .tester import run_tester

# 將所有定義好的 tool 收集成清單，供後續幫 LLM 綁定時使用
agent_tools = [
    read_cpp_code,
    write_cpp_code,
    compile_and_run_cpp,
    run_tester
]
