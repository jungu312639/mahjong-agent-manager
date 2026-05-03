import asyncio
import sys
import os
from brain import app # 確保從正確位置匯入 LangGraph App
from langchain_core.messages import HumanMessage
from brain.agent_nodes import initialize_tools # 從新節點檔案匯入連線邏輯[cite: 11]

def display_welcome_banner():
    print("================================================================")
    print("   Mahjong C++ AI Co-Design Agent (Powered by LangGraph)       ")
    print("================================================================")
    print("可用功能：")
    print(" - 分析與讀取現有 C++ 演算法")
    print(" - 快速改寫邏輯並自動除錯")
    print(" - 背景編譯並回報測試結果")
    print("\n輸入 'exit' 或 'quit' 即可離開程式。")
    print("================================================================\n")

async def run_main():
    display_welcome_banner()
    
    # 1. 初始化持久化 MCP 連線池 (面試亮點：確保 Session 在整個迴圈存活)[cite: 11, 13]
    print("[*] 正在連線至 MCP 工具服務器...", flush=True)
    try:
        tools = await initialize_tools() 
        print(f"[*] MCP 初始化成功，已獲取 {len(tools)} 個工具", flush=True)
    except Exception as e:
        print(f"[!] MCP 初始化失敗: {e}", flush=True)
        return

    # 初始化對話歷史[cite: 12]
    messages_history = []
    
    # Human-in-the-loop 迴圈[cite: 12]
    while True:
        try:
            # 由於 input 是阻塞的，在 async 中建議用 to_thread[cite: 12]
            user_input = await asyncio.to_thread(input, "User (你對演算法的想法或回饋): ")
            
            if user_input.lower() in ['exit', 'quit']:
                print("離開 AI Agent。")
                break
            if not user_input.strip():
                continue
            
            # 加入使用者訊息[cite: 12]
            messages_history.append(HumanMessage(content=user_input))
            
            print("\n[Agent 團隊正在思考與執行工具中...]\n")
            
            # 2. 改用 ainvoke 以支援非同步的 MCP 工具呼叫[cite: 12]
            result = await app.ainvoke({"messages": messages_history})
            
            # 更新對話紀錄[cite: 12]
            messages_history = result["messages"]
            
            # 顯示最後一個 Agent 回應[cite: 12]
            last_ai_message = messages_history[-1]
            print("================ Agent 回報 ================")
            print(last_ai_message.content)
            print("==========================================\n")
            
        except KeyboardInterrupt:
            print("\n中斷程式執行。")
            break
        except Exception as e:
            print(f"\n發生錯誤: {e}")

if __name__ == "__main__":
    # 環境檢查[cite: 12]
    if not os.environ.get("GOOGLE_API_KEY"):
        print("警告：你尚未在 .env 檔案中設定 GOOGLE_API_KEY。")
        sys.exit(1)
    
    # 使用 asyncio 啟動[cite: 14]
    asyncio.run(run_main())