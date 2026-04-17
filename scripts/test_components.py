import os
import sys
import io

# 強制 Windows 終端機使用 UTF-8 編碼輸出，避免 Emoji 導致報錯
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 確保可以讀取到專案根目錄的 mcp 模組
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp.builder import build_pyd_module, compile_and_run_cpp
from mcp.tools_memory import tool_retrieve_context

print("=== Akagi 系統整合診斷 (Comprehensive Check) ===")

# 1. 測試向量資料庫 (ChromaDB)
print("\n[測試 1] ChromaDB 連線與檢索測試...")
try:
    # 測試檢索「防守」相關內容
    result = tool_retrieve_context.invoke({"query_text": "防守理論"})
    if "對象錯誤" in result or "失敗" in result:
        print(f"[-] 檢索回傳異常: {result}")
    else:
        print(f"[+] 檢索成功！取得內容長度: {len(result)}")
except Exception as e:
    print(f"[FAIL] ChromaDB 測試失敗: {str(e)}")

# 2. 測試 C++ 編譯引擎 (Pybind11 專項)
print("\n[測試 2] C++ 核心模組編譯測試 (setup.py)...")
source_folder = "core/engine" 
test_cpp = "tw_ukeire.cpp"
full_path = os.path.join(source_folder, test_cpp)

if os.path.exists(full_path):
    print(f"[*] 找到核心檔案: {full_path}，準備啟動自動編譯工具...")
    try:
        res = build_pyd_module.invoke({})
        print(f"\n[編譯工具回報]:\n{res}")
    except Exception as e:
        print(f"\n[FAIL] 工具執行失敗: {str(e)}")
else:
    print(f"[FAIL] 找不到路徑 {full_path}")

print("\n=== 診斷結束 ===")