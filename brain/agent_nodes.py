from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from config import LLM_MODEL_NAME_PRO, LLM_TEMPERATURE
from brain.prompts import SYSTEM_PROMPT_STRATEGIC, SYSTEM_PROMPT_CODING, SYSTEM_PROMPT_QA
from mcp.file_ops import read_cpp_code, write_cpp_code, edit_code_segment
from mcp.builder import compile_and_run_cpp, build_pyd_module
from mcp.tester import run_mahjong_simulation

from langchain_core.messages import trim_messages

# 1. 定義裁切器 (Trimmer) - 避免對話歷史過長導致 503 錯誤
# 保留最後 15 則訊息，且強制包含 System Message (Prompt)
trimmer = trim_messages(
    strategy="last",
    max_tokens=15, 
    token_counter=len, # 以訊息則數計算，若要更精確可用 llm.get_num_tokens
    include_system=True,
    allow_partial=False,
    start_on="human"
)

# 建立獨立的大腦實體
# 建立獨立的大腦實體 (處理代碼修改與報告分析，使用 Pro 等級模型)
llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME_PRO, temperature=LLM_TEMPERATURE, max_retries=10, timeout=60)
from mcp.tools_memory import tool_retrieve_context, tool_commit_experience

# 建立專屬的工具清單 (Tool Isolation)
# 修正：將 tool_commit_experience 也分給 Strategic，因為他需要寫 Lesson Learned
strategic_tools = [tool_retrieve_context, tool_commit_experience]
coding_tools = [read_cpp_code, write_cpp_code, edit_code_segment]
qa_tools = [build_pyd_module, compile_and_run_cpp, run_mahjong_simulation, tool_commit_experience]

# 分別綁定給不同的大腦實體
llm_strategic = llm.bind_tools(strategic_tools)
llm_coding = llm.bind_tools(coding_tools)
llm_qa = llm.bind_tools(qa_tools)

# ==============================================================
# 1. 總工程師 (Strategic Agent)
# ==============================================================
# 現在這些 Agent 只是單純的思考者，不再負責內部的工具迴圈
async def strategic_agent(state):
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT_STRATEGIC),
        MessagesPlaceholder(variable_name="messages"),
    ])
    chain = prompt | llm_strategic
    return await chain.ainvoke(state)

# ==============================================================
# 2. 軟體工程師 (Coding Agent)
# ==============================================================
async def coding_agent(state):
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT_CODING),
        MessagesPlaceholder(variable_name="messages"),
    ])
    chain = prompt | llm_coding
    return await chain.ainvoke(state)

# ==============================================================
# 3. 測試工程師 (QA Agent)
# ==============================================================
async def qa_agent(state):
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT_QA),
        MessagesPlaceholder(variable_name="messages"),
    ])
    chain = prompt | llm_qa
    return await chain.ainvoke(state)

# ==============================================================
import asyncio

async def agent_node(state, agent_fn, name):
    # ---------------------------------------------------------
    # 1. 偵錯期：暫時跳過裁切，確認是否為 trimmer 導致內容被刪光
    # ---------------------------------------------------------
    # trimmed_messages = trimmer.invoke(state["messages"])
    # temp_state = state.copy()
    # temp_state["messages"] = trimmed_messages
    
    # 目前直接使用完整的 state 進行呼叫
    result = await agent_fn(state)
    
    # ---------------------------------------------------------
    # 2. 強化型保險絲：只在真的「完全沒反應」時才介入
    # ---------------------------------------------------------
    content = result.content
    has_tool_calls = hasattr(result, 'tool_calls') and len(result.tool_calls) > 0
    is_content_empty = False

    if content is None:
        is_content_empty = True
    elif isinstance(content, str):
        is_content_empty = (len(content.strip()) == 0)
    elif isinstance(content, list):
        is_content_empty = (len(content) == 0)
    
    # 【關鍵修正】：如果內容為空 且 沒有呼叫任何工具，才填充預設文字
    if is_content_empty and not has_tool_calls:
        if name == "Strategic":
            result.content = "I have received the latest information and am analyzing the next strategic move."
        elif name == "QA":
            result.content = "I am processing the simulation request and will provide the report shortly."
        else:
            result.content = f"Processing complete by {name}. Handing over to next stage."

    # 確保 sender 身分正確被記錄
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
