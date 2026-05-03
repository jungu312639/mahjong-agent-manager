import asyncio
import os
import sys

# 確保可以 import 專案根目錄
sys.path.append(os.getcwd())

from brain import agent_nodes

async def test_mcp_flow():
    print("=== MCP 連線與工具調用驗證 ===")
    
    try:
        # 1. 初始化連線
        print("[*] 正在啟動 MCP Server 並建立 Client 連線...")
        tools = await agent_nodes.initialize_tools()
        print(f"[+] 成功獲取 {len(tools)} 個工具")
        
        for i, tool in enumerate(tools):
            print(f"    {i+1}. {tool.name}: {tool.description}")

        # 修正：直接從模組讀取更新後的 session
        session = agent_nodes._mcp_session
        if not session:
            print("[-] 錯誤: MCP Session 未建立")
            return

        # 2. 測試各個工具
        print("\n" + "="*30)
        print("  開始全工具冒煙測試")
        print("="*30)

        # (1) read_cpp_code
        print("\n[Test 1/6] read_cpp_code")
        res_read = await session.call_tool("read_cpp_code", arguments={"filename": "include/score_weights.h"})
        print(f"  回傳成功: {str(res_read.content[0].text)[:50]}...")

        # (2) edit_code_segment (對註解做微調測試)
        print("\n[Test 2/6] edit_code_segment")
        res_edit = await session.call_tool("edit_code_segment", arguments={
            "filename": "include/score_weights.h",
            "target_content": "// 台灣麻將總牌數",
            "replacement_content": "// 台灣麻將總牌數 (Verified by MCP)"
        })
        print(f"  回傳結果: {res_edit.content[0].text}")

        # (3) run_mahjong_simulation (跑 1 場測試)
        print("\n[Test 3/6] run_mahjong_simulation")
        res_sim = await session.call_tool("run_mahjong_simulation", arguments={"games": 1})
        print(f"  回傳結果: {res_sim.content[0].text}")

        # (4) tool_retrieve_context (RAG 搜尋)
        print("\n[Test 4/6] tool_retrieve_context")
        res_rag = await session.call_tool("tool_retrieve_context", arguments={"query_text": "如何提高勝率?"})
        print(f"  回傳結果: {str(res_rag.content[0].text)[:100]}...")

        # (5) tool_commit_experience (紀錄經驗)
        print("\n[Test 5/6] tool_commit_experience")
        res_memo = await session.call_tool("tool_commit_experience", arguments={
            "summary": "Everything looks good",
            "win_rate": 0.5,
            "compiler_status": "SUCCESS"
        })
        print(f"  回傳結果: {res_memo.content[0].text}")

        # (6) build_pyd_module (編譯測試 - 可能較慢)
        print("\n[Test 6/6] build_pyd_module")
        res_build = await session.call_tool("build_pyd_module", arguments={
            "module_name": "tw_ukeire_cpp", 
            "reasoning": "Verification build"
        })
        print(f"  回傳結果: {res_build.content[0].text}")

    except Exception as e:
        print(f"[CRITICAL] MCP 測試過程發生錯誤: {e}")
    finally:
        # 3. 正確關閉連線以避免 RuntimeError
        print("\n[*] 正在關閉 MCP 連線...")
        if agent_nodes._mcp_session:
            await agent_nodes._mcp_session.__aexit__(None, None, None)
        if agent_nodes._mcp_transport:
            await agent_nodes._mcp_transport.__aexit__(None, None, None)
        print("=== 測試結束 ===")

if __name__ == "__main__":
    asyncio.run(test_mcp_flow())
