import sys
import os
import io

# 強制 UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append(os.getcwd())

from brain.workflow import supervisor_chain
from brain.state import GraphState
from langchain_core.messages import HumanMessage

print("[*] 正在測試 Supervisor 決策鏈路...")

state = {
    "messages": [HumanMessage(content="請協助修改代碼")],
    "next": "",
    "sender": ""
}

try:
    result = supervisor_chain.invoke(state)
    print(f"[✅] 決策成功: {result.next}")
except Exception as e:
    print(f"[❌] 決策失敗: {str(e)}")
