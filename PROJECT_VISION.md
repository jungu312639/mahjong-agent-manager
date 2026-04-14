# 🚀 Akagi Project: Autonomous Algorithm Evolution Framework

## 專案開發需求文檔 (Project Requirements Document)

> **版本狀態:** v3.0 (整合 Multi-Agent 協同機制與動態長期記憶庫)
> **設計對標:** 模仿真實半導體廠 (如 Phison 群聯電子) 之韌體驗證、自動化測試 (Testbench)、持續整合 (CI/CD) 開發流程與多代理協同平台。

### 1. 核心願景 (Vision)
本專案的終極目標是打造一個 **Multi-Agent R&D 工作流**。
我們利用多個大型語言模型 (LLM) 扮演不同職位的工程師，透過 **MCP (Model Context Protocol)** 賦予其操作底層 **C++ 演算法引擎** 的雙手；並透過 **動態 RAG (長期記憶知識庫)** 達成自我反思與學習進化。

讓團隊能夠自主進行 **「討論方向 -> 改寫沙盒代碼 -> 自動跑分 -> 針對失敗撰寫 RAG 記憶 -> 將成功修改提交 Pull Request (PR)」** 的閉環開發。這不僅僅是一個打牌機器人，而是一個具備工業級水準的 AI 賦能韌體研發自動化生態系。

---

### 2. 系統架構 (System Architecture - Multi-Agent Monorepo)

為了展現最高水準的軟體工程架構 (Software Architecture)，本專案破除散落的程式腳本，採用單體化倉庫 (Monorepo) 並嚴格劃分四大層級。AI 僅能透過工具層與執行層互動，絕不可隨意破壞核心數理邏輯。

```text
akagi-autonomous-framework/ (Root)
│
├── core/                   # 【執行層】 (DUT - 韌體驗證標的物)
│   ├── engine/             # [不可變區] 底層數學、向聽數 O(1) 演算法主幹
│   ├── include/            # [參數區] 存放 LLM 可安全微調的設定檔 (score_weights.h)
│   ├── sandbox/            # [實驗區] 專供 Agent 撰寫高階防守或攻擊策略的 C++ 邏輯沙盒 (tactics.cpp)
│   ├── testbench/          # [驗證區] 負責啟動大量壓力測試並倒出勝率日誌 (simulator.py / replay.py)
│   └── setup.py            # 編譯封裝系統
│
├── mcp/                    # 【工具層】 (The Arms & Eyes)
│   ├── builder.py          # 自動化編譯器 (呼叫 setup.py)
│   ├── tester.py           # 自動化跑分器 (擷取 Testbench JSON 報告)
│   └── reviewer.py         # [核心] CI/CD 發起工具：將測試結果打包成 PR 供人類審核
│
├── brain/                  # 【大腦層】 (Multi-Agent 協同中樞)
│   ├── workflow.py         # 總控台：定義 Agent 之間的溝通圖 (LangGraph)
│   ├── agent_strategic.py  # 🧠 Strategic Agent (總工程師)：負責查閱 RAG 理論，制定優化大方向
│   ├── agent_coding.py     # 💻 Coding Agent (軟體工程師)：負責根據方向撰寫 sandbox/tactics.cpp
│   └── agent_qa.py         # 🧪 QA Agent (測試工程師)：負責操作 Testbench，驗證勝率並給出 Report
│
├── docs/                   # 【知識層】 (Dynamic RAG Database)
│   ├── mahjong_theory/     # [靜態知識] 存放基礎防守理論、數學機率 Markdown
│   └── lesson_learned/     # [動態記憶] 失敗筆記庫。當策略失敗時，Strategic Agent 會自動將其寫入，保證下次不重蹈覆轍，達成「動態長期記憶系統」
│
└── dashboard/              # 【介面層】 (Human-in-the-Loop)
    └── (保留區)            # 未來的 Vue3/FastAPI 儀表板，提供人類總監點擊 "Approve" 進行整合
```

---

### 3. CI/CD 與 動態學習審核機制 (HITL + Dynamic Memory)

為了防止 AI 的「幻覺」破壞高穩定性架構，專案實作了嚴格的防呆與自我進化機制：
1. **沙盒隔離 (Sandbox Isolation)**：Coding Agent 只允許改動 `sandbox/tactics.cpp` 或 `score_weights.h`，將可能的記憶體崩潰災害侷限於此。
2. **多代理協同驗證 (Multi-Agent TDD)**：修訂後由 QA Agent 執行過萬巡對局，若發現勝率無提升，QA Agent 會將錯誤報表打回給 Strategic Agent。
3. **動態學習 (Lesson Learned)**：Strategic Agent 收到失敗報告後，會分析痛點並生成 `lesson_learned/failure_00X.md`，寫入 RAG 記憶體。未來的改動將首先檢索此資料夾，這是系統真正具備「自主進化」的核心關鍵。
4. **人類把關 (Human-in-the-Loop)**：當 QA Agent 確認勝率提升，將生成 PR 呈交 Dashboard。必須經過人類工程師 (你) 的確認 (Approve) 後，才正式被納入演算法核心。

---

### 4. 當前實作里程碑與進度追蹤 (Milestones)

- [x] **Phase 1: 架構大遷徙與去耦合 (Decoupling)**
  - [x] 將舊散落的檔案整合成上述 `core`, `mcp`, `brain` 目錄。
  - [x] 開發 `core/include/score_weights.h`。
  - [x] 開發 `core/sandbox/tactics.cpp`。
- [x] **Phase 2: Multi-Agent 協作網建立**
  - [x] 使用 LangGraph 實作 Strategic, Coding, QA Agent 三方會議迴圈。
  - [x] 讓各 Agent 能夠自主呼叫專屬 MCP 工具 (如 QA 負責呼叫 `tester.py`)。
- [ ] **Phase 3: RAG 動態長期記憶整合**
  - [ ] 建立 `docs/lesson_learned/` 動態寫入機制。
  - [ ] 讓 Strategic Agent 在每次優化前檢索歷史教訓，展現動態適應能力。
- [ ] **Phase 4: Dashboard 與 HITL 整合**
  - [ ] 實裝 Vue3 儀表板，將整個 Multi-Agent 協作與測試流程視覺化。

---

> **給 Agent 的守則 (Instructions for Antigravity):**
> *   **模組化優先**：C++ (算力) 與 Python (測試與思維) 必須嚴格分離。
> *   **多代理權責**：請明確區分不同角色的任務（誰負責想、誰負責寫、誰負責測）。
> *   **寫入歷史教訓**：如果改寫的演算法失敗，不只要重試，更要將錯誤的原因與解決方案寫入 RAG。
