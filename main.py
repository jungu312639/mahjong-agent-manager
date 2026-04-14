from brain import app
from langchain_core.messages import HumanMessage
import sys
import os

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

def main():
    display_welcome_banner()
    
    # 初始化一個空的訊息清單，作為持續對話的記憶體
    messages_history = []
    
    # 這是 Human-in-the-loop 的無限迴圈
    while True:
        try:
            user_input = input("User (你對演算法的想法或回饋): ")
            if user_input.lower() in ['exit', 'quit']:
                print("離開 AI Agent。")
                break
            if not user_input.strip():
                continue
            
            # 將使用者的訊息加入對話尾端
            messages_history.append(HumanMessage(content=user_input))
            
            print("\n[Agent 思考與執行中...]\n")
            
            # 將整串歷史訊息丟進去給 LangGraph 執行
            result = app.invoke({"messages": messages_history})
            
            # Graph 跑完（停在 end 節點）後，抓取最新的所有訊息
            updated_messages = result["messages"]
            messages_history = updated_messages
            
            # 找到最後一個 Agent 回應並印出，做為 Human-in-the-loop 讓你審核
            last_ai_message = updated_messages[-1]
            print("================ Agent 回報 ================")
            print(last_ai_message.content)
            print("==========================================\n")
            
        except KeyboardInterrupt:
            print("\n中斷程式執行。")
            break
        except Exception as e:
            print(f"\n發生錯誤: {e}")

if __name__ == "__main__":
    # 檢查是否設定了 API KEY，否則提醒使用者
    if not os.environ.get("GOOGLE_API_KEY"):
        print("警告：你尚未在 .env 檔案中設定 GOOGLE_API_KEY。")
        print("請建立 .env 檔案並加入 GOOGLE_API_KEY=<你的API金鑰>，否則會無法連線到 Gemini。")
        sys.exit(1)
        
    main()
