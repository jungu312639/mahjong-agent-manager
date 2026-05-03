import os
import sys
import asyncio
from typing import Annotated
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, trim_messages
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from config import LLM_MODEL_NAME_PRO, LLM_TEMPERATURE
from brain.prompts import SYSTEM_PROMPT_STRATEGIC, SYSTEM_PROMPT_CODING, SYSTEM_PROMPT_QA

# ==============================================================
# 1. 配置與初始化環境
# ==============================================================

# 定義裁切器 (暫時保留邏輯，但可在 node 中選擇性開啟)
trimmer = trim_messages(
    strategy="last",
    max_tokens=15, 
    token_counter=len,
    include_system=True,
    allow_partial=False,
    start_on="human"
)

# 定義 MCP Server 連線參數
MCP_SERVER_CONFIG = {
    "command": sys.executable,
    "args": ["-u", os.path.join(os.getcwd(), "mcp_tools", "server.py")], # 加上 -u
    "env": {**os.environ, "PYTHONPATH": os.getcwd()}
}

# 全域連線池，確保 Session 在 main.py 執行期間持續存活
_mcp_transport = None
_mcp_session = None
agent_tools = []

# LLM 實體初始化[cite: 11]
llm = ChatGoogleGenerativeAI(
    model=LLM_MODEL_NAME_PRO, 
    temperature=LLM_TEMPERATURE, 
    max_retries=10, 
    timeout=60
)

# ==============================================================
# 2. MCP 連線管理 (面試亮點：Persistent Connection)
# ==============================================================

async def initialize_tools():
    """初始化 MCP 連線並獲取工具清單，此函數由 main.py 在啟動時呼叫一次[cite: 11, 13]"""
    global _mcp_transport, _mcp_session, agent_tools
    
    server_params = StdioServerParameters(
        command=MCP_SERVER_CONFIG["command"],
        args=MCP_SERVER_CONFIG["args"],
        env=MCP_SERVER_CONFIG["env"]
    )
    
    # 建立持久化 Transport 與 Session[cite: 11]
    print(f"[*] 正在啟動 MCP Transport: {server_params.command} {' '.join(server_params.args)}")
    _mcp_transport = stdio_client(server_params)
    print("[*] 正在進入 Transport Context...")
    read, write = await _mcp_transport.__aenter__()
    print("[*] 正在建立 Client Session...")
    _mcp_session = ClientSession(read, write)
    print("[*] 正在進入 Session Context...")
    await _mcp_session.__aenter__() # 核心修正：必須進入 Context 以啟動背景任務
    
    sys.stdout.flush()
    print("[*] 正在執行 Session Initialize (等待 Server 回應)...")
    await _mcp_session.initialize()
    print("[*] MCP 初始化完成！")
    
    # 加載 MCP 工具並存入全域變數[cite: 11]
    agent_tools = await load_mcp_tools(_mcp_session)
    
    # 重新綁定工具給各個 Agent[cite: 11]
    _bind_agent_tools()
    
    return agent_tools

async def shutdown_tools():
    """清理 MCP 連線資源"""
    global _mcp_transport, _mcp_session
    try:
        if _mcp_session:
            await _mcp_session.__aexit__(None, None, None)
    except Exception:
        pass
    try:
        if _mcp_transport:
            await _mcp_transport.__aexit__(None, None, None)
    except Exception:
        pass

def _bind_agent_tools():
    """根據角色分配工具權限 (Tool Isolation)[cite: 11]"""
    global llm_strategic, llm_coding, llm_qa
    
    def get_tools(names):
        return [t for t in agent_tools if t.name in names]

    # 與 prompts_2.py 的工具需求嚴格對齊
    llm_strategic = llm.bind_tools(get_tools(["tool_retrieve_context", "tool_commit_experience"]))
    llm_coding = llm.bind_tools(get_tools(["read_cpp_code", "edit_code_segment"]))
    llm_qa = llm.bind_tools(get_tools(["build_pyd_module", "run_mahjong_simulation", "tool_commit_experience"]))

# 初始空綁定，待 initialize_tools 執行後會更新
llm_strategic = llm
llm_coding = llm
llm_qa = llm

# ==============================================================
# 3. Agent 思考邏輯定義[cite: 11]
# ==============================================================

async def strategic_agent(state):
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT_STRATEGIC),
        MessagesPlaceholder(variable_name="messages"),
    ])
    return await (prompt | llm_strategic).ainvoke(state)

async def coding_agent(state):
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT_CODING),
        MessagesPlaceholder(variable_name="messages"),
    ])
    return await (prompt | llm_coding).ainvoke(state)

async def qa_agent(state):
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT_QA),
        MessagesPlaceholder(variable_name="messages"),
    ])
    return await (prompt | llm_qa).ainvoke(state)

# ==============================================================
# 4. 核心節點包裝器 (Node Wrapper)[cite: 11]
# ==============================================================

async def agent_node(state, agent_fn, name):
    # 此處可依據需求決定是否啟用 trimmer (目前暫時跳過以確保 context 完整)
    # trimmed_messages = trimmer.invoke(state["messages"])
    # temp_state = state.copy()
    # temp_state["messages"] = trimmed_messages
    
    # 執行 Agent 思考流程
    result = await agent_fn(state)
    
    # ---------------------------------------------------------
    # 強化型保險絲：防止 'list' object has no attribute 'strip' 與空回應[cite: 11]
    # ---------------------------------------------------------
    content = result.content
    has_tool_calls = hasattr(result, 'tool_calls') and len(result.tool_calls) > 0
    is_content_empty = False

    # 型別安全檢查 (Type Guarding)[cite: 11]
    if content is None:
        is_content_empty = True
    elif isinstance(content, str):
        is_content_empty = (len(content.strip()) == 0)
    elif isinstance(content, list):
        # 解決 list 沒有 strip() 的問題，並合併內容
        result.content = " ".join([str(item) for item in content]) # 解決 list no strip 報錯
        is_content_empty = (len(result.content.strip()) == 0)
    
    # 【防止 contents are required 錯誤】：若無內容且無工具呼叫，強制填充[cite: 11]
    if is_content_empty and not has_tool_calls:
        if name == "Strategic":
            result.content = "Strategic analysis complete. I am assessing the next move based on current performance data."
        elif name == "QA":
            result.content = "QA evaluation finished. Preparing the verification report for the latest build."
        else:
            result.content = f"Action processed by {name}. Handing over control to the Supervisor."

    # 確保 sender 身分正確被記錄，供 Supervisor 路由使用[cite: 11]
    if isinstance(result, AIMessage):
        result.name = name
    
    return {
        "messages": [result], 
        "sender": name
    }

# 匯出給 workflow.py 使用的節點函數
async def strategic_node(state): return await agent_node(state, strategic_agent, "Strategic")
async def coding_node(state): return await agent_node(state, coding_agent, "Coding")
async def qa_node(state): return await agent_node(state, qa_agent, "QA")