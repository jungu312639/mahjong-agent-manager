import os
import sys
import asyncio
import json

# 確保可以 import 專案根目錄的模組 (如 brain, mcp, config)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

# 引入我們之前寫好的大腦核心
from brain import app
from langchain_core.messages import HumanMessage

server = FastAPI(title="Akagi AI Agent API")

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
        # 初始化對話背景
        inputs = {"messages": [HumanMessage(content=message)]}
        
        # 使用 astream 獲取流式更新
        # Note: 這邊假設你的 LangGraph app 支援 astream 
        try:
            async for event in app.astream(inputs, stream_mode="values"):
                # 提取最新的訊息內容
                if "messages" in event:
                    last_msg = event["messages"][-1]
                    sender = getattr(last_msg, "name", "AI")
                    
                    data = {
                        "sender": sender,
                        "content": last_msg.content,
                        "type": "message"
                    }
                    yield json.dumps(data)
                
                # 你可以在這裡加入其他的事件類型，例如勝率更新、代碼變更等
                await asyncio.sleep(0.1)
                
            yield json.dumps({"type": "finish", "content": "流程點結束"})
        except Exception as e:
            yield json.dumps({"type": "error", "content": str(e)})

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server, host="0.0.0.0", port=8000)
