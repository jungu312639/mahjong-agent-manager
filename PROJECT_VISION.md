# 🚀 Akagi Project: Autonomous Algorithm Evolution Framework

## 專案開發需求文檔 (Project Requirements Document)

> **版本狀態:** v4.0 (全端視覺化與向量記憶體大滿貫)
> **設計對標:** 模仿真實半導體廠 (如 Phison 群聯電子) 之韌體驗證、自動化測試 (Testbench)、持續整合 (CI/CD) 開發流程與多代理協同平台。

### 1. 核心願景 (Vision)
本專案的終極目標是打造一個 **Multi-Agent R&D 工作流**。
我們利用多個大型語言模型 (LLM) 扮演不同職位的工程師，透過 **MCP (Model Context Protocol)** 賦予其操作底層 **C++ 演算法引擎** 的雙手；並透過 **動態 RAG (長期記憶知識庫 - ChromaDB)** 達成自我反思與學習進化。

讓團隊能夠自主進行 **「討論方向 -> 改寫沙盒代碼 -> 自動跑分 -> 針對失敗撰寫 RAG 記憶 -> 視覺化呈現演化過程」** 的閉環開發。這不僅僅是一個打牌機器人，而是一個具備工業級水準的 AI 賦能韌體研發自動化生態系。

---

### 2. 系統架構 (System Architecture - Multi-Agent Monorepo)

為了展現最高水準的軟體工程架構 (Software Architecture)，本專案採用單體化倉庫 (Monorepo) 並嚴格劃分四大層級。

```text
akagi-autonomous-framework/ (Root)
│
├── core/                   # 【執行層】 (DUT - 韌體驗證標的物)
│   ├── engine/             # [不可變區] 底層數學引擎
│   ├── include/            # [參數區] LLM 可微調的 score_weights.h
│   ├── sandbox/            # [實驗區] 供 Agent 實作戰術的 tactics.cpp
│   └── testbench/          # [驗證區] 壓力測試 simulator.py
│
├── mcp/                    # 【工具層】 (The Arms & Eyes)
│   ├── builder.py          # 自動化編譯器
│   ├── tester.py           # 自動化跑分器
│   └── tools_memory.py     # [RAG] ChromaDB 向量讀寫工具
│
├── brain/                  # 【大腦層】 (Multi-Agent 協同中樞)
│   ├── workflow.py         # 總控台 (LangGraph Supervisor)
│   ├── agent_nodes.py      # Agent 實體封裝
│   └── prompts.py          # 系統指令 (System Prompts) 定義
│
├── web/                    # 【介面層】 (Full-stack Dashboard)
│   ├── backend/            # FastAPI (SSE Streaming API)
│   └── frontend/           # Vue 3 (Vite + Tailwind IDE Dashboard)
│
├── data/                   # 【記憶層】 (Vector DB)
│   └── vector_db/          # ChromaDB 持久化檔案
│
└── docs/                   # 【知識層】 (Markdown Knowledge Base)
```

---

### 3. CI/CD 與 動態學習審核機制 (HITL + Dynamic Memory)

1. **沙盒隔離 (Sandbox Isolation)**：將可能的損壞侷限於 `tactics.cpp`。
2. **多代理協同驗證 (Multi-Agent TDD)**：由 QA Agent 執行過萬巡對局驗證代碼。
3. **動態學習 (RAG Memory)**：Strategic Agent 透過 ChromaDB 記錄失敗痛點，下次決策會自動執行「語義檢索」。
4. **視覺化監控 (Dashboard)**：透過 Vue 3 儀表板，即時監看 Agent 之間的對話、勝率趨勢與代碼變動。

---

### 4. 專案里程碑回顧 (Milestones - COMPLETED)

- [x] **Phase 1: 架構大遷徙與去耦合 (Decoupling)**
  - [x] 整體專案重構為 Monorepo 結構。
  - [x] 提取 C++ 參數至 `score_weights.h` 並建立沙盒攔截器。
- [x] **Phase 2: Multi-Agent 協作網建立**
  - [x] 使用 LangGraph 實作 Supervisor 路由器模式。
  - [x] 成功建立 Strategic, Coding, QA 三大專家節點。
- [x] **Phase 3: RAG 動態長期記憶整合**
  - [x] 導入 ChromaDB 持久化向量資料庫。
  - [x] 實作自動化 Chunking 灌注腳本與向量檢索工具。
- [x] **Phase 4: Dashboard 視覺化監控系統**
  - [x] 建立 IDE 風格的 Vue 3 儀表板，支援即時日誌流 (SSE)。
  - [x] 實作「手動/自動」雙模式切換與 Agent 討論功能。

---

> **致面試官 (Note to Phison Reviewer):**
> 本框架的核心亮點在於「權限隔離」與「自我進化」。它不只是一個 AI 應用程式，它展示了如何利用現代 AI 技術來加速傳統韌體開發中極其枯燥的「參數調優」與「回歸測試」流程，是一個完整的 AI-Enabled R&D 解決方案。
