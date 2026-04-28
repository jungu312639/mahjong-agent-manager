# Akagi Mahjong Core - 專案啟動與測試指南

本專案是一個基於 LangGraph 多代理人架構的麻將 AI 研發系統。以下是啟動與測試的完整流程。

---

## 1. 環境準備 (Environment Setup)

1.  **Python 環境**：建議使用 Python 3.10 或以上版本。
2.  **安裝依賴**：
    ```bash
    pip install -r requirements.txt
    ```
3.  **環境變數**：在專案根目錄建立 `.env` 檔案，內容如下：
    ```env
    GOOGLE_API_KEY=你的_GEMINI_API_KEY
    ```

---

## 2. 啟動流程 (Startup Flow)

### 第一步：啟動後端 API (Backend)
這是系統的「大腦」，負責驅動多代理人工作流。
先啟動環境
```bash
.\.venv\Scripts\Activate.ps1 
```

```bash
python web/backend/api.py
```
*   **預設網址**：`http://localhost:8000`
*   **功能**：提供 `/api/run` 介面供前端調用，並處理所有工具執行。

### 第二步：啟動前端介面 (Frontend)
這是你的操作面板，用於查看 Agent 的對話與修改進度。
```bash
cd web/frontend
npm install   # 第一次啟動需要
npm run dev
```
*   **預設網址**：`http://localhost:5173`

---

## 3. 測試方式 (Testing)

為了確保系統各組件運作正常，你可以使用 `scripts` 資料夾中的工具：

### A. 快速 API 測試 (推薦)
不開啟前端，直接測試 Agent 的「執行力」。
```bash
# 測試 Agent 是否能真的修改程式碼
python scripts/test_api.py "請在 tactics.cpp 最後加入一行註解：// STARTUP_TEST_OK"
```

### B. 組件功能測試
測試文件讀寫、RAG 知識庫檢索與 C++ 編譯器。
```bash
python scripts/test_components.py
```

### C. 模型連通性測試
檢查 API Key 與 Google Gemini 模型的連線狀態。
```bash
python scripts/test_model.py
```

---

## 4. 專案結構說明
*   `brain/`：LangGraph 工作流、代理人節點、與指令 (Prompts)。
*   `mcp/`：Agent 擁有的工具箱（檔案讀寫、編譯、RAG 檢索）。
*   `core/`：麻將引擎核心與 Sandbox（Agent 修改的目標）。
*   `web/`：FastAPI 後端與 Vue/Vite 前端。

---

## 💡 常見問題
*   **429 錯誤 (Quota Exceeded)**：Gemini 免費版有 RPM (每分鐘請求數) 限制。本系統已內建 5 秒異步等待，請勿過快連續點擊。
*   **路徑問題**：Agent 修改代碼時會優先尋找 `core/sandbox/tactics.cpp`。
