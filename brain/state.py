from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

# 定義狀態結構 (Graph State)
# 使用 messages 陣列來存放對話紀錄
class GraphState(TypedDict):
    messages: Annotated[list, add_messages]
