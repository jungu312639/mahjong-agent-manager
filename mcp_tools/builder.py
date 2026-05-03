from langchain_core.tools import tool
import os
import sys
import subprocess
from config import TW_BOT_PATH
import pybind11

@tool
def compile_and_run_cpp(cpp_filename: str) -> str:
    """Compiles the specified C++ file using g++ and executes it.
       Returns the combined stdout/stderr output.
       Use this to test the C++ code you just modified.
    """
    cpp_path = os.path.join(TW_BOT_PATH, cpp_filename)
    exe_filename = cpp_filename.replace('.cpp', '.exe')
    exe_path = os.path.join(TW_BOT_PATH, exe_filename)
    
    # 修改 compile_cmd 加上 -I (Include) 參數
    py_include = pybind11.get_include()
    compile_cmd = ["g++", "-O3", "-shared", "-std=c++11", f"-I{py_include}", cpp_path, "-o", exe_path]
    try:
        compile_res = subprocess.run(
            compile_cmd, 
            cwd=TW_BOT_PATH, 
            capture_output=True, 
            text=True, 
            encoding="utf-8", 
            errors="replace",
            stdin=subprocess.DEVNULL,
            close_fds=True
        )
        if compile_res.returncode != 0:
            return f"COMPILATION ERROR:\n{compile_res.stderr}"
    except Exception as e:
        return f"Execution Error during compiling: {e}"

    # 2. 執行 (Run)
    run_cmd = [exe_path] 
    try:
        run_res = subprocess.run(
            run_cmd, 
            cwd=TW_BOT_PATH, 
            capture_output=True, 
            text=True, 
            timeout=10, 
            encoding="utf-8", 
            errors="replace",
            stdin=subprocess.DEVNULL,
            close_fds=True
        )
        return f"EXECUTION OUTPUT:\n{run_res.stdout}\nERRORS:\n{run_res.stderr}"
    except subprocess.TimeoutExpired:
        return "EXECUTION TIMEOUT: Program ran for more than 10 seconds and was terminated."
    except Exception as e:
        return f"Execution Error during running: {e}"

@tool
def build_pyd_module(module_name: str, reasoning: str) -> str:
    """
    使用 core/setup.py 將 C++ 核心編譯為 Python 模組。
    Args:
        module_name (str): 必須填寫，例如 'tw_ukeire_cpp'。
        reasoning (str): 為什麼現在需要編譯？(例如：代碼已修改完成)
    """
    # 這裡我們固定到專案根目錄下的 core 資料夾執行
    # 假設專案路徑是在當前目錄或透過 config 取得
    from config import AKAGI_BASE_PATH
    core_dir = os.path.join(AKAGI_BASE_PATH, "core")
    
    if not os.path.exists(core_dir):
        return f"ERROR: 找不到 core 目錄於 {core_dir}"

    # 執行標準的 setuptools 編譯指令
    # --inplace 會把編譯好的 .pyd 直接放在 core 裡面，方便 Python import
    cmd = [sys.executable, "setup.py", "build_ext", "--inplace"]
    
    try:
        result = subprocess.run(
            cmd, 
            cwd=core_dir, 
            capture_output=True, 
            text=True, 
            encoding="utf-8",
            errors="replace",
            stdin=subprocess.DEVNULL,
            close_fds=True
        )
        
        if result.returncode == 0:
            return f"SUCCESS: 模組編譯成功！\n日誌：\n{result.stdout}"
        else:
            return f"COMPILATION FAILED:\n[STDOUT]:\n{result.stdout}\n[STDERR]:\n{result.stderr}"
    except Exception as e:
        return f"Error executing setup.py: {str(e)}"