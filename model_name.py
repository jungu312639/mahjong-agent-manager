import google as genai

genai.configure(api_key="AIzaSyABiUyJkRlS39huI3I0zaP75XYNbuwuPUY")

# 1. 抓取該模型物件的詳細資訊
try:
    m = genai.get_model("models/gemini-3.1-flash-live-preview")
    print(f"成功找到模型！支援的方法有: {m.supported_generation_methods}")
except Exception as e:
    print(f"確認失敗: {e}")

# 2. 測試最簡單的呼叫
model = genai.GenerativeModel('gemini-3.1-flash-live-preview')
try:
    response = model.generate_content("Hi")
    print("呼叫成功！")
except Exception as e:
    print(f"呼叫依然失敗: {e}")