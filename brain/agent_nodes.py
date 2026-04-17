from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from config import LLM_MODEL_NAME, LLM_TEMPERATURE
from brain.prompts import SYSTEM_PROMPT_STRATEGIC, SYSTEM_PROMPT_CODING, SYSTEM_PROMPT_QA
from mcp.file_ops import read_cpp_code, write_cpp_code, edit_code_segment
from mcp.builder import compile_and_run_cpp, build_pyd_module
from mcp.tester import run_mahjong_simulation

# 建立獨立的大腦實體
llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME, temperature=LLM_TEMPERATURE)

from mcp import agent_tools

# 建立具備工具調用語義的大腦實體
llm_with_tools = llm.bind_tools(agent_tools)

# ==============================================================
# 1. 總工程師 (Strategic Agent)
# ==============================================================
# 現在這些 Agent 只是單純的思考者，不再負責內部的工具迴圈
async def strategic_agent(state):
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT_STRATEGIC),
        MessagesPlaceholder(variable_name="messages"),
    ])
    chain = prompt | llm_with_tools
    return await chain.ainvoke(state)

# ==============================================================
# 2. 軟體工程師 (Coding Agent)
# ==============================================================
async def coding_agent(state):
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT_CODING),
        MessagesPlaceholder(variable_name="messages"),
    ])
    chain = prompt | llm_with_tools
    return await chain.ainvoke(state)

# ==============================================================
# 3. 測試工程師 (QA Agent)
# ==============================================================
async def qa_agent(state):
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT_QA),
        MessagesPlaceholder(variable_name="messages"),
    ])
    chain = prompt | llm_with_tools
    return await chain.ainvoke(state)

# ==============================================================
import asyncio

async def agent_node(state, agent_fn, name):
    # 代理人執行前的小幅冷卻，確保在低 RPM 配額下不被門限阻斷
    await asyncio.sleep(5)
    
    # 執行思考流程
    result = await agent_fn(state)
    
    # 強制塞入寄件者身分 (為了讓 Supervisor 與 ToolNode 辨識是誰發出的 ToolCall)
    if isinstance(result, AIMessage):
        result.name = name
    
    return {
        "messages": [result], 
        "sender": name
    }

async def strategic_node(state):
    return await agent_node(state, strategic_agent, "Strategic")

async def coding_node(state):
    return await agent_node(state, coding_agent, "Coding")

async def qa_node(state):
    return await agent_node(state, qa_agent, "QA")
