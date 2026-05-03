import asyncio
import os
import sys

# 確保可以 import 專案根目錄
sys.path.append(os.getcwd())

from brain.agent_nodes import initialize_tools
from brain import app
from langchain_core.messages import HumanMessage

async def main():
    print("--- Testing Workflow ---")
    try:
        # 1. 初始化工具
        print("[*] Initializing MCP tools...")
        await initialize_tools()
        print("[+] MCP tools initialized.")

        # 2. 呼叫 Agent
        print("[*] Sending message to Agent...")
        messages = [HumanMessage(content="Hello! Please use the 'read_cpp_code' tool to read 'include/score_weights.h' and summarize it.")]
        
        async for chunk in app.astream({"messages": messages}, stream_mode="values"):
            if "messages" in chunk:
                last_msg = chunk["messages"][-1]
                print(f"[{getattr(last_msg, 'name', 'AI')}] {str(last_msg.content)[:100]}...")
                if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                    print(f"  (Tool Calls: {[tc['name'] for tc in last_msg.tool_calls]})")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        from brain import agent_nodes
        if agent_nodes._mcp_session:
            await agent_nodes._mcp_session.__aexit__(None, None, None)
        if agent_nodes._mcp_transport:
            await agent_nodes._mcp_transport.__aexit__(None, None, None)
        print("--- End Test ---")

if __name__ == "__main__":
    asyncio.run(main())
