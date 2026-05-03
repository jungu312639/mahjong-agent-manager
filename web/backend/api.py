import os
import sys
import asyncio
import json
import io

# 強制 Windows 終端機使用 UTF-8 編碼輸出，防止 Agent 日誌 Emoji 導致報錯
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 確保可以 import 專案根目錄的模組 (如 brain, mcp, config)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

# 引入我們之前寫好的大腦核心
from brain import get_app
from brain.agent_nodes import initialize_tools, shutdown_tools
from langchain_core.messages import HumanMessage

app = None

async def lifespan_context(server: FastAPI):
    global app
    print("Initializing MCP tools...")
    await initialize_tools()
    app = get_app()
    yield
    print("Shutting down MCP tools...")
    await shutdown_tools()

server = FastAPI(title="Akagi AI Agent API", lifespan=lifespan_context)

# 允許跨域請求 (因為前端 Vite 預設在 5173 埠)
server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    mode: str = "manual"  # manual or autonomous

@server.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

@server.get("/api/run")
async def run_workflow(message: str = "開始優化", mode: str = "manual"):
    """
    啟動 LangGraph 模型流式輸出。
    使用 SSE (Server-Sent Events) 將 Agent 的每一步發送給前端。
    """
    async def event_generator():
        global app
        if app is None:
            yield json.dumps({"type": "error", "content": "App not initialized"})
            return

        # 初始化對話背景
        inputs = {"messages": [HumanMessage(content=message)]}
        
        # 使用 astream 獲取流式更新
        # Note: 這邊假設你的 LangGraph app 支援 astream 
        try:
            # 增加防呆設定，最多執行 20 個 Node 轉換，防止陷入無限錯誤修復迴圈
            config = {"recursion_limit": 50}
            # 改用 updates 模式，這樣只會抓取「該節點產生的變更」，避免重複與 values 帶來的舊資料
            async for event in app.astream(inputs, config, stream_mode="updates"):
                # 在 updates 模式下，event 的結構是 { "NodeName": { "messages": [...], "sender": "..." } }
                for node_name, node_output in event.items():
                    if "messages" in node_output:
                        # 處理該節點產生的所有新訊息
                        for msg in node_output["messages"]:
                            sender = getattr(msg, "name", node_name)
                            msg_type = getattr(msg, "type", "")
                            
                            # 情況 1：Agent 呼叫了工具 (存在 tool_calls)
                            if hasattr(msg, "tool_calls") and msg.tool_calls:
                                for tc in msg.tool_calls:
                                    tool_name = tc.get("name", "unknown")
                                    args = tc.get("args", {})
                                    
                                    # 1-A: 發送工具呼叫日誌
                                    yield json.dumps({
                                        "type": "tool_call",
                                        "sender": sender,
                                        "content": f"調用 {tool_name} 工具進行處理",
                                        "tool_name": tool_name
                                    })
                                    
                                    # 1-B: 如果是修改程式碼，攔截參數並發送 code_diff 事件
                                    if tool_name == "edit_code_segment":
                                        yield json.dumps({
                                            "type": "code_diff",
                                            "old_code": args.get("target_content", "// 無法取得舊代碼"),
                                            "new_code": args.get("replacement_content", "// 無法取得新代碼")
                                        })
                                    await asyncio.sleep(0.1)
                                    
                            # 情況 2：一般文字訊息 (過濾掉純粹的 ToolMessage 與空內容)
                            if msg.content and msg_type != "tool":
                                # 處理 Google 模型回傳的複雜 content 格式
                                final_content = msg.content
                                if isinstance(final_content, list):
                                    final_content = "\n".join([item.get("text", str(item)) for item in final_content if isinstance(item, dict)])
                                elif isinstance(final_content, dict):
                                    final_content = final_content.get("text", str(final_content))
                                elif isinstance(final_content, str):
                                    # 如果是字串，但包含了 {'type': 'text', 'text': '...', 'extras': ...} 這樣的結構
                                    import re
                                    matches = re.findall(r"'text':\s*'(.*?)',\s*'extras'", final_content, re.DOTALL)
                                    if matches:
                                        # 單純替換換行符號與跳脫字元，不要用 unicode_escape 以免破壞中文編碼
                                        final_content = "\n\n".join([m.replace("\\n", "\n").replace('\\"', '"').replace("\\'", "'") for m in matches])

                                if final_content:
                                    yield json.dumps({
                                        "type": "message",
                                        "sender": sender,
                                        "content": final_content
                                    })
                                    await asyncio.sleep(0.1)
                                
                            # 情況 3：工具執行完畢的回傳結果 (ToolMessage)
                            if msg_type == "tool":
                                tool_name = getattr(msg, "name", "unknown")
                                
                                # 正確提取 tool content，因為 Gemini 可能將其包裝為 [{'type': 'text', 'text': '...'}]
                                tool_content_raw = msg.content
                                if isinstance(tool_content_raw, list) and len(tool_content_raw) > 0:
                                    if isinstance(tool_content_raw[0], dict) and "text" in tool_content_raw[0]:
                                        tool_content = tool_content_raw[0]["text"]
                                    else:
                                        tool_content = str(tool_content_raw)
                                else:
                                    tool_content = str(tool_content_raw)
                                
                                # 發送系統層級的日誌
                                # 取前 150 字避免日誌太長洗版
                                preview_content = tool_content[:150].replace("\n", " ") + "..." if len(tool_content) > 150 else tool_content
                                yield json.dumps({
                                    "type": "message",
                                    "sender": "System",
                                    "content": f"[{tool_name}] 執行完畢：{preview_content}"
                                })
                                
                                # 3-A: 如果是跑分模擬器，擷取勝率並發送 metrics 事件
                                if tool_name == "run_mahjong_simulation":
                                    try:
                                        import json as std_json
                                        res_data = std_json.loads(tool_content)
                                        win_rate = res_data.get("win_rate_percentage") or res_data.get("win_rate")
                                        if win_rate is not None:
                                            yield json.dumps({
                                                "type": "metric",
                                                "win_rate": float(win_rate)
                                            })
                                    except Exception as e:
                                        print(f"解析勝率失敗: {e}")
                                await asyncio.sleep(0.1)
                                
            yield json.dumps({"type": "finish", "content": "流程點結束"})
        except Exception as e:
            yield json.dumps({"type": "error", "content": str(e)})

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server, host="0.0.0.0", port=8000)
