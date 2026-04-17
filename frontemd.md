# Create the markdown file for the frontend specification
content = """# Akagi 前端實作規範手冊 (Frontend Implementation Specification)

## 1. 系統佈局設計 (System Layout)
本系統旨在提供高度的「系統觀測性 (Observability)」，確保開發者能即時監控 AI 對 C++ 核心模組的優化行為。

### 1.1 佈局分配 (Bento Box 佈局)
- **側邊控制欄 (Sidebar, 20%)**：負責指令輸入、常用工具按鈕、系統狀態燈號（API 配額與連線狀態）。
- **中央任務流 (Action Log, 45%)**：即時顯示 Agent 的思考 (Thought) 與動作 (Tool Call) 過程。
- **右側效能看板 (Performance Dashboard, 35%)**：
    - **上半部 (Code Diff)**：顯示 AI 對代碼的具體修改差異。
    - **下半部 (Metrics)**：顯示模擬器勝率曲線、編譯狀態指標與向量庫狀態。

---

## 2. 核心組件細節 (Core Component Requirements)

### 2.1 中央任務流：Agent 動作實錄 (The Brain Log)
* **視覺設計**：IDE 終端機風格，黑色背景，綠色/白色文字。
* **功能需求**：
    - **角色標籤**：明確標註 `[SUPERVISOR]`、`[STRATEGIC]`、`[CODING]`、`[QA]`。
    - **時間戳記**：每條紀錄需包含 `HH:mm:ss`。
    - **動作監控**：需呈現工具呼叫狀態（例如：`Calling tool: build_pyd_module... SUCCESS`）。
    - **自動滾動**：新訊息產生時視窗需自動鎖定於底部。

### 2.2 右側看板：Code Diff 視窗
* **視覺設計**：側邊對比 (Side-by-side) 或 行內對比 (Unified Diff)。
* **功能需求**：
    - **亮點標註**：特別標註位元運算 (Bitwise)、權重常數、演算法邏輯的變更。
    - **推理摘要**：在 Diff 下方顯示 AI 修改該段代碼的技術理由（Reasoning）。
    - **全屏切換**：右上角提供展開按鈕，可將代碼視窗最大化以利審閱。

### 2.3 右側看板：效能指標卡片 (KPI Cards)
* **功能需求**：
    - **勝率追蹤**：使用折線圖顯示優化過程中的勝率起伏。
    - **編譯狀態燈**：綠色 (Success)、紅色 (Fail)、黃色 (Building)。
    - **數據摘要**：顯示「目前勝率」、「相比初始提升百分比」、「總優化輪次」。

---

## 3. 互動與通訊邏輯 (Interaction Logic)

### 3.1 單一指令入口
* 用戶僅透過側邊欄對「總工程師 (Supervisor)」下令。
* 指令輸入時，輸入框應進入 Disabled 狀態直到 Agent 階段性任務完成。
* 提供「常用指令快捷鍵」：🚀 啟動全自動優化、🔍 系統狀態掃描、🧪 僅執行模擬測試。

### 3.2 數據流處理 (SSE)
* 前端需透過 SSE 接收來自 `/api/run` 的數據。
* **數據分流類型**：
    - `type: "thought"` -> 丟入中央日誌。
    - `type: "tool_call"` -> 丟入中央日誌並更新編譯燈號。
    - `type: "diff"` -> 更新右側 Code Diff 組件。
    - `type: "metric"` -> 更新勝率折線圖。

---

## 4. 實作路徑 (Implementation Roadmap)

1.  **Step 1: 數據格式定義**：對齊後端 `api.py` 的 SSE 輸出格式，確保 `type` 欄位完整。
2.  **Step 2: 佈局搭建**：使用 Vue 3 + Tailwind CSS 完成三欄式架構。
3.  **Step 3: 組件開發**：優先完成自動滾動 Log 與 Code Diff 顯示功能。
4.  **Step 4: 狀態聯調**：測試當編譯失敗時，Log 區變紅且能自動觸發「自我修復 (Self-healing)」視覺回饋。

---

## 5. 核心價值主張 (For Interviewer)
* **閉環驗證**：展示「修改 -> 編譯 -> 測試 -> 數據回饋」的完整自動化流程。
* **高觀測性**：強調代碼變動與效能指標的即時連動，展現嚴謹的韌體研發思維。
"""

import os

file_path = "akagi-frontend-spec.md"
with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"File created: {file_path}")