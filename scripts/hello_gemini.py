import os
import sys
import io
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# 確保可以 import 專案根目錄的 config 模組 (雖然這個腳本直接寫死模型名稱測試)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 強制 Windows 終端機使用 UTF-8 編碼輸出，避免 Emoji 導致報測
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

# 使用列表中的確切名稱 (根據剛才 scan 的結果)
model_name = "gemini-flash-latest"

print(f"[*] 正在發動「極簡直連測試」... (模型: {model_name})")

try:
    # 直接初始化模型，不經過任何 Agent 邏輯
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.7)
    
    # 提問
    response = llm.invoke([HumanMessage(content="你好！這是一條極簡連通性測試。如果你收到了這則訊息，請簡短回覆我目前是什麼時間，並說一句鼓勵我的話。")])
    
    print("\n[✅ 測試成功] 模型回覆內容：")
    print("-" * 30)
    print(response.content)
    print("-" * 30)
    
except Exception as e:
    print(f"\n[❌ 測試失敗] 發生錯誤：{str(e)}")
    print("\n提示：請檢查 .env 中的 GOOGLE_API_KEY 是否有效。")
