import os
import sys

# 確保可以讀取到專案根目錄的 mcp 模組
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp.file_ops import edit_code_segment

print("=== Akagi 精密代碼修改工具測試 (Partial Update) ===")

# 定義要測試的目標
filename = "include/score_weights.h"
target = "constexpr double WEIGHT_BASE_DRAW = 1.0;"
replacement = "constexpr double WEIGHT_BASE_DRAW = 1.2; // Optimized by MCP"

print(f"[*] 嘗試在 {filename} 中搜尋並替換特定變數...")

try:
    res = edit_code_segment.invoke({
        "filename": filename,
        "target_content": target,
        "replacement_content": replacement
    })
    print(f"\n[MCP 工具回報]: {res}")
    
    if "Successfully" in res:
        print("[+] 測試成功！請手動檢查檔案內容。")
    else:
        print("[-] 測試失敗，請檢查錯誤訊息。")

except Exception as e:
    print(f"[FAIL] 執行過程發生異常: {str(e)}")

print("\n=== 測試結束 ===")
