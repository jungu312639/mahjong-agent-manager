import os
import json
import sys
import subprocess
from langchain_core.tools import tool
from config import TW_BOT_PATH

@tool
def run_mahjong_simulation(games: int = 1000) -> str:
    """Run a headless Mahjong simulation for the specified number of games.
       This will autonomously compile and bind the latest C++ models from tw_ukeire_cpp,
       pit the P0 (C++ AI) against 3 Greedy Baselines, and return a JSON performance report.
       Use this carefully when determining if an algorithm modification is effective.
    """
    # 定義路徑
    simulator_script = os.path.join(TW_BOT_PATH, "testbench", "simulator.py")
    # 使用 PID 建立唯一檔名，避免多個進程同時執行時發生檔案鎖死
    result_file = os.path.join(TW_BOT_PATH, "testbench", f"sim_res_{os.getpid()}.json")
    
    # 確保路徑存在
    os.makedirs(os.path.dirname(result_file), exist_ok=True)
    
    cmd = [sys.executable, "-u", simulator_script, str(games)]
    
    try:
        # 使用 Python 原生檔案重定向，並徹底隔離 stdin (DEVNULL) 與檔案描述符 (close_fds=True)
        with open(result_file, "w", encoding="utf-8") as f:
            subprocess.run(
                cmd, 
                cwd=TW_BOT_PATH, 
                stdin=subprocess.DEVNULL, 
                stdout=f, 
                stderr=subprocess.STDOUT, 
                timeout=120,
                close_fds=True
            )
        
        if not os.path.exists(result_file):
            return f"SIMULATION ERROR: 找不到結果檔案 {result_file}"
            
        with open(result_file, "r", encoding="utf-8", errors="replace") as f:
            output_str = f.read()
            
        # 嘗試刪除暫存檔 (Cleanup)
        try:
            os.remove(result_file)
        except:
            pass
            
        # 嘗試從檔案內容解析 JSON
        if "{" in output_str and "}" in output_str:
            json_str = output_str[output_str.find("{") : output_str.rfind("}") + 1]
            try:
                parsed = json.loads(json_str)
                return json.dumps(parsed, indent=2)
            except:
                pass
        return f"SIMULATION OUTPUT:\n{output_str}"
        
    except subprocess.TimeoutExpired:
        return f"SIMULATION TIMEOUT: 模擬耗時過長，請檢查 C++ 效能。"
    except Exception as e:
        return f"Execution Error: {e}"
