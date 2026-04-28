# Akagi 前端實作藍圖 V2：Demo 衝刺與後端整合規範

## 1. 開發策略：雙模切換架構 (Dual-Mode Architecture)
本系統需具備「Mock 數據演示」與「真實後端接入」兩套數據流路徑。

### 1.1 核心開關設定
在專案全域配置中定義控制變數：
- **`IS_MOCK_MODE`**: `true` (用於明天 Demo) / `false` (用於後續開發) [cite: 1.1]。
- **`API_BASE_URL`**: 指向 `http://localhost:8000/api/run` [cite: 1.1]。

---

## 2. 後端與 Agent 接入點 (Integration Guide)
當系統切換為真實模式時，請確保以下函數與 API 成功對接。

### 2.1 API 通訊服務 (ApiService.js)
- **實作 SSE 連線**：使用 `EventSource` 訂閱後端串流 [cite: 1.1, 1.3]。
- **連線函數**：`startAgentSession(userMessage)`。
- **異常處理**：需捕捉 `429 Resource Exhausted` 等 Rate Limit 錯誤並在 UI 顯示警告 [cite: 1.1]。

### 2.2 數據映射邏輯 (Data Mapping)
接收到的 SSE JSON 數據應按以下 `type` 欄位分發給組件：
| 數據類型 (Type) | 內容用途 | 前端更新對象 |
| :--- | :--- | :--- |
| `thought` | Agent 的思考文字 | 中央任務日誌 (Action Log) [cite: 1.3] |
| `tool_call` | 工具呼叫紀錄 | 中央日誌 & 側邊狀態燈號 [cite: 1.1] |
| `diff` | C++ 代碼變更數據 | 右側 Code Diff 視窗 [cite: 1.1] |
| `metric` | 模擬勝率數值 | 右側勝率進化折線圖 [cite: 1.3] |

---

## 3. 明日 Demo 專用：Mock 演示模式
為了確保 Demo 萬無一失，請在 `useAgent` Hook 中實作模擬數據噴發邏輯。

### 3.1 演示腳本流程 (Demo Script)
1. **[0s]** 使用者點擊「啟動優化」 -> 顯示 API 連線成功燈號。
2. **[2s]** 發送 `thought`：「Supervisor 收到指令，分配任務給 Coding Agent...」 [cite: 1.2, 1.4]。
3. **[5s]** 更新 `diff`：展示 `tactics.cpp` 中「壁理論」權重的數值變化 [cite: 1.1]。
4. **[8s]** 發送 `metric`：勝率曲線從 50% 跳動至 65% [cite: 1.3]。

---

## 4. UI 佈局細節 (Tailwind CSS 實作)
- **左側 (20%)**：側邊控制欄。包含指令 Input、API 狀態燈、Demo 觸發按鈕 [cite: 1.1]。
- **中央 (45%)**：任務日誌。黑底 Terminal 風格，需具備 `overflow-y-auto` 與自動滾底功能 [cite: 1.3]。
- **右側 (35%)**：效能看板。上方為代碼對比區，下方為 ECharts 折線圖區 [cite: 1.1]。

---

## 5. 給 Antigravity 的重要備註
- **保留接頭**：請在所有 Mock 數據賦值處加上註解 `// TODO: Connect to Real API` [cite: 1.1]。
- **穩定性**：Demo 模式下，請確保所有動畫與數據更新節奏平穩，以利於邊演示邊解說。
