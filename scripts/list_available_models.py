import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("[*] 正在獲取當前 API Key 可使用的完整模型清單...")
try:
    models = genai.list_models()
    for m in models:
        # 只顯示支援 generateContent 的模型，並印出 RPD/RPM 資訊 (如果有的話)
        if "generateContent" in m.supported_generation_methods:
            print(f"- {m.name} (DisplayName: {m.display_name})")
except Exception as e:
    print(f"[❌] 獲取失敗: {str(e)}")
