from typing import Literal
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI

from brain.state import GraphState
from brain.agent_nodes import strategic_node, coding_node, qa_node
from brain.prompts import SYSTEM_PROMPT_SUPERVISOR
from config import LLM_MODEL_NAME, LLM_TEMPERATURE

# ==========================================
# 1. 架構定義與 Supervisor 路由器設定
# ==========================================
members = ["Strategic", "Coding", "QA"]
options = ["FINISH"] + members

class RouteResponse(BaseModel):
    # 強制 LLM 丟出的 JSON 的 next 欄位只能出現這四種字串之一
    next: Literal["FINISH", "Strategic", "Coding", "QA"]

llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME, temperature=LLM_TEMPERATURE)

# 設計主管專屬的 Prompt，把對話跟清單交給它做選擇
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT_SUPERVISOR),
        MessagesPlaceholder(variable_name="messages"),
        (
            "system",
            "分析上述所有團隊成員的回報。\n"
            "現在控制權正在你手上，請決定下一棒應該呼叫誰？\n"
            "選擇清單: {options}"
        ),
    ]
).partial(options=str(options))

# 綁定 Pydantic 結構強制輸出
supervisor_chain = prompt | llm.with_structured_output(RouteResponse)

def supervisor_node(state: GraphState):
    routing_decision = supervisor_chain.invoke(state)
    print(f"\n[🔄 路由器] Supervisor 統籌決策: 將控制權轉交給 -> {routing_decision.next}")
    return {"next": routing_decision.next}

# ==========================================
# 2. 畫圖 (建構 Multi-Agent StateGraph)
# ==========================================
workflow = StateGraph(GraphState)

# 註冊所有部門 (Nodes)
workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("Strategic", strategic_node)
workflow.add_node("Coding", coding_node)
workflow.add_node("QA", qa_node)

# 每當任何一個工程師完成他的任務 (例如 QA 測完，或是 Coding 寫完程式)
# 控制權「強制」拉回給 Supervisor 讓主管裁決下一步
for member in members:
    workflow.add_edge(member, "Supervisor")

# 主管(Supervisor)節點的分支邏輯 (Conditional Edges)
# 根據 Supervisor JSON 的 next 屬性進行物理分發
conditional_map = {k: k for k in members}
conditional_map["FINISH"] = END

workflow.add_conditional_edges("Supervisor", lambda state: state["next"], conditional_map)

# 設定起點
workflow.add_edge(START, "Supervisor")

# 編譯整張地圖成為實體
app = workflow.compile()
