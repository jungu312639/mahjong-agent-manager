from langchain_core.tools import tool
import os
import subprocess
from config import TW_BOT_PATH

@tool
def compile_and_run_cpp(cpp_filename: str) -> str:
    """Compiles the specified C++ file using g++ and executes it.
       Returns the combined stdout/stderr output.
       Use this to test the C++ code you just modified.
    """
    cpp_path = os.path.join(TW_BOT_PATH, cpp_filename)
    exe_filename = cpp_filename.replace('.cpp', '.exe')
    exe_path = os.path.join(TW_BOT_PATH, exe_filename)
    
    # 1. 編譯 (Compile)
    compile_cmd = ["g++", cpp_path, "-o", exe_path]
    try:
        compile_res = subprocess.run(compile_cmd, cwd=TW_BOT_PATH, capture_output=True, text=True, encoding="utf-8")
        if compile_res.returncode != 0:
            return f"COMPILATION ERROR:\n{compile_res.stderr}"
    except Exception as e:
        return f"Execution Error during compiling: {e}"

    # 2. 執行 (Run)
    run_cmd = [exe_path] 
    try:
        run_res = subprocess.run(run_cmd, cwd=TW_BOT_PATH, capture_output=True, text=True, timeout=10, encoding="utf-8")
        return f"EXECUTION OUTPUT:\n{run_res.stdout}\nERRORS:\n{run_res.stderr}"
    except subprocess.TimeoutExpired:
        return "EXECUTION TIMEOUT: Program ran for more than 10 seconds and was terminated."
    except Exception as e:
        return f"Execution Error during running: {e}"
