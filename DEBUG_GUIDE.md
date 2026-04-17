# 🛠️ Akagi Autonomous Framework: DEBUG_GUIDE

本文件旨在提供開發者、面試官或 QA 人員，在不依賴前端介面的情況下，如何直接與系統各個組件進行交互與壓力測試。

---

## 1. C++ 核心與 MCP 自動化編譯
當你修改了 `core/engine/*.cpp` 或是 `core/include/*.h` 之後，必須重新編譯模組。

### 手動編譯指令
在專案根目錄下使用虛擬環境執行：
```bash
cd core
python setup.py build_ext --inplace
```
*   **預期結果**：產生 `tw_ukeire_cpp.pyd` (Windows) 或 `.so` (Linux)。
*   **測試載入**：執行 `python -c "import tw_ukeire_cpp; print('載入成功')"`。

### 手動叫 MCP 改寫 C++ 變數
如果你想測試 Agent 是否有權限改寫檔案，可以使用 `write_cpp_code` 工具（模擬 Agent 行為）：
```python
from mcp.file_ops import write_cpp_code
# 模擬改寫權重
write_cpp_code.invoke({"filename": "include/score_weights.h", "content": "// New Weights..."})
```

---

## 2. ChromaDB 向量記憶體測試
AI 的長期記憶存放在 `data/vector_db` 下。

### 手動執行語義查詢
如果你想知道資料庫裡存了哪些麻將理論，可以執行：
```python
from mcp.tools_memory import tool_retrieve_context
# 查詢關於防守的理論
res = tool_retrieve_context.invoke({"query_text": "什麼是壁 (Kabe) 理論？"})
print(res)
```

### 手動灌入新知識
執行 `scripts/ingest_docs.py` 會自動掃描 `docs/` 下的所有 Markdown 並轉為向量。

---

## 3. 直接觸發 Agent 工作流 (cURL / API)
在後端 `api.py` 啟動的情況下（Port 8000），你可以繞過前端直接對 Agent 下令。

### 使用 cURL 觸發 (SSE 串流輸出)
```bash
curl -G "http://localhost:8000/api/run" --data-urlencode "message=請優化防守邏輯"
```
*   **注意**：這會返回一個 SSE 串流 (text/event-stream)，你會在終端機看到 Agent 逐步思考的 JSON 數據。

---

## 4. 系統全健康檢查
我們提供了一個一鍵診斷腳本：
```bash
python scripts/test_components.py
```
它會依序測試：
1.  **ChromaDB** 是否能連線與讀取。
2.  **setuptools** 是否能成功呼叫編譯器。

---

## 🛑 常見錯誤排除 (Troubleshooting)
*   **ModuleNotFoundError: No module named 'tw_ukeire_cpp'**
    *   原因：尚未編譯或編譯路徑不對。
    *   解決：執行 `cd core && python setup.py build_ext --inplace`。
*   **UnicodeEncodeError**
    *   原因：Windows 終端機不支援 UTF-8。
    *   解決：已在 `test_components.py` 中加入強力修復邏輯。
*   **GOOGLE_API_KEY Missing**
    *   原因：`.env` 未設定。
    *   解決：在根目錄建立 `.env` 並填入 `GOOGLE_API_KEY=your_key`。
