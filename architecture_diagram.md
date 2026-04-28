# Akagi Mahjong Core - 系統架構圖

這張圖展示了專案的 4 大核心分層與資料流向。您可以直接將此圖截圖放入您的簡報中，或是將下方的 Mermaid 程式碼貼到 [Mermaid Live Editor](https://mermaid.live/) 或 [Draw.io](https://app.diagrams.net/) 進行二次修改。

```mermaid
graph TD
    %% 設定整體樣式
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef layerBox fill:#eef2f5,stroke:#4a5568,stroke-width:2px,stroke-dasharray: 5 5;
    classDef highlight fill:#ebf8ff,stroke:#3182ce,stroke-width:2px;
    classDef db fill:#f0fff4,stroke:#38a169,stroke-width:2px;
    classDef cpp fill:#fff5f5,stroke:#e53e3e,stroke-width:2px;
    classDef web fill:#fffff0,stroke:#d69e2e,stroke-width:2px;

    %% Web Layer
    subgraph Web_Layer ["Web Layer (人機協作介面)"]
        UI["Vue3 Dashboard"]:::web
        API["FastAPI (SSE 串流)"]:::web
    end

    %% Brain Layer
    subgraph Brain_Layer ["Brain Layer (多代理大腦) - LangGraph"]
        Supervisor{"Supervisor (路由中心)"}:::highlight
        Strategic["Strategic Agent<br>(制定戰略)"]:::highlight
        Coding["Coding Agent<br>(編寫程式)"]:::highlight
        QA["QA Agent<br>(測試驗證)"]:::highlight
    end

    %% MCP Layer
    subgraph MCP_Layer ["MCP Layer (工具調用層)"]
        Tool_Mem["tools_memory<br>(RAG 檢索與寫入)"]
        Tool_Ops["file_ops<br>(讀寫檔案)"]
        Tool_Build["builder & tester<br>(編譯與跑分)"]
    end

    %% Data & Core Layer
    subgraph Data_Layer ["Data Layer (動態記憶體)"]
        Chroma[(ChromaDB<br>向量資料庫)]:::db
    end

    subgraph Core_Layer ["Core Layer (物理執行層)"]
        Sandbox["tactics.cpp<br>(C++ 沙盒)"]:::cpp
        Sim["simulator.py<br>(驗證引擎)"]:::cpp
    end

    %% 連線與資料流
    UI -- "Human-in-the-loop<br>即時監控" --> API
    API -- "觸發與推播" --> Supervisor

    Supervisor -->|分配任務| Strategic
    Supervisor -->|分配任務| Coding
    Supervisor -->|分配任務| QA

    Strategic -. "1. Tool Call" .-> Tool_Mem
    Tool_Mem <-->|語義檢索| Chroma

    Coding -. "2. Tool Call" .-> Tool_Ops
    Tool_Ops -->|修改| Sandbox

    QA -. "3. Tool Call" .-> Tool_Build
    Tool_Build -->|執行測試| Sim
    Sim -->|回傳勝率| Tool_Build
    QA -. "4. 寫入教訓" .-> Tool_Mem

    %% 替子圖套用樣式
    class Web_Layer,Brain_Layer,MCP_Layer,Data_Layer,Core_Layer layerBox;
```

## 報告時的解說重點 (搭配此圖)：

1. **由上而下 (Web -> Brain)**：提到這是一個有前端 UI 監控的系統，人類下達指令給 FastAPI 後，交給大腦層的 Supervisor 進行任務路由。
2. **中間協作 (Brain -> MCP)**：強調 LangGraph 確保了流程的可控性，三個 Agent 職責分明，不會越權。他們必須透過 MCP Layer (Model Context Protocol) 提供的工具才能對外操作。
3. **左側循環 (Strategic <-> Data)**：展示您的 **RAG 記憶庫能力**。戰略 Agent 修改前會先去 ChromaDB 檢索歷史失敗紀錄。
4. **右側循環 (QA <-> Core <-> Data)**：展示 **Tool-use 能力與閉環**。Agent 去修改 C++ Sandbox 代碼，QA 編譯跑分後，將成功/失敗的經驗寫回 ChromaDB，完成「自我進化」。
