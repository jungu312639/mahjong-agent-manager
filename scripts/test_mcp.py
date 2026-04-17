import os
import sys

# 確保可以讀取到專案根目錄的 mcp 模組
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp.file_ops import write_cpp_code
# 模擬改寫權重
print("正在測試 MCP 寫入功能...")
res = write_cpp_code.invoke({"filename": "include/score_weights.h", "content": "// Final Weight Test"})
print(res)