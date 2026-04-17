import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

model_name = "gemini-3.1-flash-lite-preview"
print(f"[*] 正在測試模型: {model_name} ...")

try:
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
    res = llm.invoke([HumanMessage(content="你好，測試一下")])
    print(f"\n[SUCCESS]:\n{res.content}")
except Exception as e:
    print(f"\n[FAIL]: {str(e)}")
