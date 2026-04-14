from .file_ops import read_cpp_code, write_cpp_code
from .builder import compile_and_run_cpp
from .tester import run_mahjong_simulation
from .tools_memory import tool_retrieve_context, tool_commit_experience

agent_tools = [
    read_cpp_code,
    write_cpp_code,
    compile_and_run_cpp,
    run_mahjong_simulation,
    tool_retrieve_context,
    tool_commit_experience
]
