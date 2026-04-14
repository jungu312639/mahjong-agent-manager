from typing import Annotated, TypedDict, Sequence
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

# =========================================================================
# Multi-Agent 專用的 Graph State (狀態機資料結構)
# 確保 Supervisor 能夠追蹤是「誰」做完了事，以及該交給「誰」
# =========================================================================
class GraphState(TypedDict):
    # 對話歷史，LangGraph 會自動把所有 Agent 處理的步驟 append 在這裡
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # 路由決策：決定下一棒 (Strategic, Coding, QA, 或 FINISH)
    next: str
    
    # 紀錄最後發話的部門與身分，預防訊息發送者錯亂
    sender: str
