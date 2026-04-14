from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode

from .state import GraphState
from tools import agent_tools
from config import LLM_MODEL_NAME, LLM_TEMPERATURE

# 1. 初始化模型並綁定工具
llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME, temperature=LLM_TEMPERATURE)
llm_with_tools = llm.bind_tools(agent_tools)

# 2. 定義節點 (Node)
def chatbot_node(state: GraphState):
    """大腦節點，負責推理並決定要呼叫什麼工具，或者回覆人類"""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# 工具節點：當大腦要求執行讀寫檔案、編譯時，由這個節點執行
tool_node = ToolNode(agent_tools)

# 3. 定義條件流向 (Conditional Edge)
def should_continue(state: GraphState):
    """判斷剛剛模型是否回傳了工具呼叫 (Tool Calls)。如果有，就走向工具節點，否則就結束迴圈等待人類輸入。"""
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

# 4. 建構有向圖 (Graph)
def build_graph():
    workflow = StateGraph(GraphState)
    
    # 新增節點
    workflow.add_node("agent", chatbot_node)
    workflow.add_node("tools", tool_node)
    
    # 設定起點與連接
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")
    
    # 返回編譯後的應用程式
    return workflow.compile()

# 將對外開放的編譯實體直接儲存供 main.py 匯入
app = build_graph()
