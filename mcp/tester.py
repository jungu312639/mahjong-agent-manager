import os
import json
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
    simulator_script = os.path.join(TW_BOT_PATH, "simulator.py")
    
    cmd = ["python", simulator_script, str(games)]
    try:
        # 執行模擬器，捕獲標準輸出
        result = subprocess.run(cmd, cwd=TW_BOT_PATH, capture_output=True, text=True, timeout=600, encoding="utf-8")
        if result.returncode != 0:
            return f"SIMULATION EXACT ERROR:\n{result.stderr}"
            
        # 嘗試從 stdout 解析最後面的 JSON
        output_str = result.stdout
        # 簡單從 "{" 開始擷取
        if "{" in output_str and "}" in output_str:
            json_str = output_str[output_str.find("{") : output_str.rfind("}") + 1]
            try:
                # 驗證為合法 JSON
                parsed = json.loads(json_str)
                return json.dumps(parsed, indent=2)
            except:
                pass
        return f"SIMULATION RAW OUTPUT:\n{output_str}"
        
    except subprocess.TimeoutExpired:
        return f"SIMULATION TIMEOUT: 模擬 {games} 場耗時過長 (超過 600 秒)，請優化 C++ 效能。"
    except Exception as e:
        return f"Execution Error: {e}"
