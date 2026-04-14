from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

from config import LLM_MODEL_NAME, LLM_TEMPERATURE
from brain.prompts import SYSTEM_PROMPT_STRATEGIC, SYSTEM_PROMPT_CODING, SYSTEM_PROMPT_QA
from mcp.file_ops import read_cpp_code, write_cpp_code
from mcp.builder import compile_and_run_cpp
from mcp.tester import run_mahjong_simulation

# 建立獨立的大腦實體
llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME, temperature=LLM_TEMPERATURE)

# ==============================================================
# 1. 總工程師 (Strategic Agent)
# 擁有工具: 只能讀文檔，寫失敗筆記 (lesson learned)
# ==============================================================
strategic_tools = [read_cpp_code, write_cpp_code] 
strategic_agent = create_react_agent(llm, tools=strategic_tools, state_modifier=SYSTEM_PROMPT_STRATEGIC)

# ==============================================================
# 2. 軟體工程師 (Coding Agent)
# 擁有工具: 負責動手改寫 tactics.cpp 與 score_weights.h
# ==============================================================
coding_tools = [read_cpp_code, write_cpp_code]
coding_agent = create_react_agent(llm, tools=coding_tools, state_modifier=SYSTEM_PROMPT_CODING)

# ==============================================================
# 3. 測試工程師 (QA Agent)
# 擁有工具: 完全摸不到檔案讀寫權限，只會編譯跟按壓測試按鈕
# ==============================================================
qa_tools = [compile_and_run_cpp, run_mahjong_simulation]
qa_agent = create_react_agent(llm, tools=qa_tools, state_modifier=SYSTEM_PROMPT_QA)

# ==============================================================
# Node Wrapper (將 Agent 與大迴圈 State 銜接的橋樑)
# ==============================================================
def agent_node(state, agent, name):
    result = agent.invoke(state)
    # 取出 Agent 在內部自主執行迴圈後，產出的最後一段話
    last_message = result["messages"][-1]
    
    # 強制塞入寄件者身分，供 Supervisor 辨識 (為了能呈現 "HumanMessage" 樣態以避免模型錯亂)
    # 對應 langgraph 標準的 name 屬性
    final_output = HumanMessage(content=last_message.content, name=name)
    
    return {
        "messages": [final_output], 
        "sender": name
    }

def strategic_node(state):
    return agent_node(state, strategic_agent, "Strategic")

def coding_node(state):
    return agent_node(state, coding_agent, "Coding")

def qa_node(state):
    return agent_node(state, qa_agent, "QA")
