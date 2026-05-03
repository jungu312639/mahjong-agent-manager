import asyncio
import sys
import os

# 確保可以 import 專案根目錄
sys.path.append(os.getcwd())

from langchain_core.messages import HumanMessage
from brain import agent_nodes
from brain.workflow import get_app

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))

async def run_integration_test():
    safe_print("=== Agentic Workflow 整合測試開始 ===")
    
    # 1. 啟動 MCP 底層通訊管線
    safe_print("[*] 正在啟動 MCP Server 並掛載工具...")
    try:
        tools = await agent_nodes.initialize_tools()
        safe_print(f"[+] 成功掛載 {len(tools)} 個工具，準備接收指令。")
        app = get_app()
    except Exception as e:
        safe_print(f"[-] 初始化工具失敗: {e}")
        return

    # 2. 定義真實使用者的考題
    prompt = (
        "幫我把防禦巡目改為 12 巡，然後跑 50 場模擬告訴我勝率，"
        "並將勝率結果寫回data/lesson_learned並且要存入向量資料庫，"
        "最後輸出存入data/lesson_learned的紀錄檔案"
    )
    
    safe_print(f"\n[USER_PROMPT] {prompt}\n")
    safe_print("-" * 50)
    
    # 3. 觸發 LangGraph 工作流
    inputs = {
        "messages": [HumanMessage(content=prompt)]
    }
    
    # 這裡我們使用 astream 捕捉每個節點的輸出，方便在終端機追蹤
    try:
        async for output in app.astream(inputs, {"recursion_limit": 50}):
            for node_name, state in output.items():
                safe_print(f"\n[Node Execution: {node_name}]")
                # 如果有回傳新的 messages，印出最後一則
                if "messages" in state and len(state["messages"]) > 0:
                    last_msg = state["messages"][-1]
                    # 判斷是否為 AI 回覆
                    if hasattr(last_msg, "content") and last_msg.content:
                        safe_print(f"-> 思考/回報內容:\n{str(last_msg.content)[:500]}...")
                    
                    # 判斷是否準備呼叫工具
                    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                        for tool in last_msg.tool_calls:
                            safe_print(f"-> [TOOL CALL]: {tool['name']} \n   參數: {tool['args']}")

    except Exception as e:
        safe_print(f"\n[CRITICAL ERROR] 工作流執行時崩潰: {e}")
    finally:
        # 4. 正確關閉 MCP 管線
        safe_print("\n[*] 正在關閉 MCP 連線與釋放資源...")
        if agent_nodes._mcp_session:
            await agent_nodes._mcp_session.__aexit__(None, None, None)
        if agent_nodes._mcp_transport:
            await agent_nodes._mcp_transport.__aexit__(None, None, None)
        safe_print("=== 整合測試結束 ===")

if __name__ == "__main__":
    asyncio.run(run_integration_test())
