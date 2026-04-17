from typing import Literal
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from brain.state import GraphState
from brain.agent_nodes import strategic_node, coding_node, qa_node
from brain.prompts import SYSTEM_PROMPT_SUPERVISOR
from config import LLM_MODEL_NAME, LLM_TEMPERATURE
from mcp import agent_tools

# ==========================================
# 1. 架構定義與 Supervisor 路由器設定
# ==========================================
members = ["Strategic", "Coding", "QA"]
options = ["FINISH"] + members

class RouteResponse(BaseModel):
    next: Literal["FINISH", "Strategic", "Coding", "QA"]

llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME, temperature=LLM_TEMPERATURE)

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

supervisor_chain = prompt | llm.with_structured_output(RouteResponse)

import asyncio

async def supervisor_node(state: GraphState):
    # RPM 15 限制下，每分鐘 15 次，約每 4 秒一次。使用非阻塞延遲確保百分之百穩定。
    await asyncio.sleep(5)
    routing_decision = await supervisor_chain.ainvoke(state)
    print(f"\n[Routing] Supervisor 統籌決策: 將控制權轉交給 -> {routing_decision.next}")
    return {"next": routing_decision.next}

# 工具執行節點
tool_node = ToolNode(agent_tools)

# ------------------------------------------
# 路由邏輯：判斷 Agent 是否需要執行工具
# ------------------------------------------
def router(state):
    """
    根據最後一則訊息是否有 tool_calls 來決定去向。
    """
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "call_tool"
    return "continue"

# ==========================================
# 2. 畫圖 (建構 Multi-Agent StateGraph)
# ==========================================
workflow = StateGraph(GraphState)

# 註冊所有節點
workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("Strategic", strategic_node)
workflow.add_node("Coding", coding_node)
workflow.add_node("QA", qa_node)
workflow.add_node("tools", tool_node)

# ------------------------------------------
# 設定邊 (Edges)
# ------------------------------------------

# 1. 每個 Agent 做完後，檢查是否需要呼叫工具
for member in members:
    workflow.add_conditional_edges(
        member,
        router,
        {
            "call_tool": "tools",     # 有工具需求 -> 去執行工具
            "continue": "Supervisor" # 沒工具需求 -> 回報給主管
        }
    )

# 2. 工具執行完後，必須「回到原本的 Agent」繼續思考/回報
workflow.add_conditional_edges(
    "tools",
    lambda state: state["sender"],
    {
        "Strategic": "Strategic",
        "Coding": "Coding",
        "QA": "QA"
    }
)

# 3. 主管決定下一棒
conditional_map = {k: k for k in members}
conditional_map["FINISH"] = END
workflow.add_conditional_edges("Supervisor", lambda state: state["next"], conditional_map)

# 設定進入點
workflow.add_edge(START, "Supervisor")

# 編譯
app = workflow.compile()
