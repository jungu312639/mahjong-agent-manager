import asyncio
import sys
import os
import logging
import io

# =========================================================
# 1. Stdio 底層隔離與無緩衝配置 (防護 C++ 擴充套件污染 stdout)
# =========================================================
# 強制 Python logging 走 stderr
logging.basicConfig(level=logging.ERROR, stream=sys.stderr)

# 備份原始的 stdout file descriptor (fd 1)
original_stdout_fd = os.dup(1)

# 核心修復：在作業系統層級，將 fd 1 (stdout) 導向 fd 2 (stderr)
# 這樣一來，任何 C/C++/Rust 擴充套件 (如 PyTorch, hnswlib) 寫入 stdout 的日誌，都會被導向 stderr
os.dup2(2, 1)

# 把 Python 的 sys.stdout 也強制導向 sys.stderr
sys.stdout = sys.stderr

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server.stdio import stdio_server

from mcp_tools.file_ops import read_cpp_code, write_cpp_code, edit_code_segment
from mcp_tools.builder import build_pyd_module, compile_and_run_cpp
from mcp_tools.tester import run_mahjong_simulation
from mcp_tools.tools_memory import tool_retrieve_context, tool_commit_experience

server = Server("Mahjong-Agent-Manager")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(name="read_cpp_code", description="讀取 C++ 檔案內容", inputSchema={"type": "object", "properties": {"filename": {"type": "string"}}, "required": ["filename"]}),
        types.Tool(name="write_cpp_code", description="覆寫整個 C++ 檔案", inputSchema={"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}),
        types.Tool(name="edit_code_segment", description="精準替換程式碼片段", inputSchema={"type": "object", "properties": {"filename": {"type": "string"}, "target_content": {"type": "string"}, "replacement_content": {"type": "string"}}, "required": ["filename", "target_content", "replacement_content"]}),
        types.Tool(name="compile_and_run_cpp", description="編譯並執行 C++ 檔案進行獨立測試", inputSchema={"type": "object", "properties": {"cpp_filename": {"type": "string"}}, "required": ["cpp_filename"]}),
        types.Tool(name="run_mahjong_simulation", description="執行麻將模擬器測試", inputSchema={"type": "object", "properties": {"games": {"type": "integer"}}, "required": ["games"]}),
        types.Tool(name="build_pyd_module", description="將 C++ 編譯為 Python 模組", inputSchema={"type": "object", "properties": {"module_name": {"type": "string"}, "reasoning": {"type": "string"}}, "required": ["module_name", "reasoning"]}),
        types.Tool(name="tool_retrieve_context", description="搜尋記憶庫知識", inputSchema={"type": "object", "properties": {"query_text": {"type": "string"}}, "required": ["query_text"]}),
        types.Tool(name="tool_commit_experience", description="儲存優化經驗到記憶庫", inputSchema={"type": "object", "properties": {"summary": {"type": "string"}, "win_rate": {"type": "number"}, "compiler_status": {"type": "string"}}, "required": ["summary", "win_rate", "compiler_status"]}),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    tools_map = {
        "read_cpp_code": read_cpp_code.func,
        "write_cpp_code": write_cpp_code.func,
        "edit_code_segment": edit_code_segment.func,
        "compile_and_run_cpp": compile_and_run_cpp.func,
        "run_mahjong_simulation": run_mahjong_simulation.func,
        "build_pyd_module": build_pyd_module.func,
        "tool_retrieve_context": tool_retrieve_context.func,
        "tool_commit_experience": tool_commit_experience.func
    }
    args = arguments or {}

    if name not in tools_map:
        return [types.TextContent(type="text", text=f"Error: Tool {name} not found")]

    func = tools_map[name]
    try:
        res = await func(**args) if asyncio.iscoroutinefunction(func) else await asyncio.to_thread(func, **args)
        return [types.TextContent(type="text", text=str(res))]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Tool Execution Error: {str(e)}")]

async def main():
    import anyio
    from mcp.server import NotificationOptions
    
    # 建構一個獨立、無緩衝的寫入管道專門給 MCP JSON-RPC 使用 (write_through=True 保證即時發送)
    # 這裡我們使用剛才透過 os.dup(1) 備份出來的底層 fd
    mcp_stdout_file = os.fdopen(original_stdout_fd, "wb", buffering=0)
    mcp_stdout_wrapper = io.TextIOWrapper(mcp_stdout_file, encoding="utf-8", write_through=True)
    mcp_stdout_async = anyio.wrap_file(mcp_stdout_wrapper)
    
    # 針對 stdin 也獨立包裹
    mcp_stdin_async = anyio.wrap_file(io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace"))

    # =========================================================
    # 2. 核心：capabilities 必須顯式傳入且避免 keyword argument 報錯
    # =========================================================
    # 為了避開某些版本的 kwargs 解析問題，我們直接使用 Positional Arguments
    capabilities = server.get_capabilities(NotificationOptions(), {})

    init_options = InitializationOptions(
        server_name="Mahjong-Agent-Manager",
        server_version="1.0.0",
        capabilities=capabilities
    )

    async with stdio_server(stdin=mcp_stdin_async, stdout=mcp_stdout_async) as (read_stream, write_stream):
        await server.run(read_stream, write_stream, init_options)

if __name__ == "__main__":
    asyncio.run(main())