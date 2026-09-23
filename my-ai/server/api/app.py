import json
import time
import logging
import asyncio
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class TaskRequest(BaseModel):
    request: str
    context: Optional[dict] = None


class ToolExecuteRequest(BaseModel):
    tool: str
    args: dict = {}


def create_app(agent_loop, auth_manager, tool_registry, knowledge_base, memory_system, config: dict):
    app = FastAPI(title="MyAI Server", version="1.0.0")

    connected_devices = {}
    connected_clients = set()

    async def verify_auth(authorization: str = Header(None)):
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization required")
        token = authorization.replace("Bearer ", "")
        if not auth_manager.validate_token(token):
            raise HTTPException(status_code=401, detail="Invalid token")
        return True

    @app.get("/", response_class=HTMLResponse)
    async def root():
        web_index = Path(__file__).resolve().parents[2] / "web" / "index.html"
        if web_index.exists():
            from fastapi.responses import HTMLResponse as HR
            content = web_index.read_text(encoding="utf-8")
            resp = HR(content)
            resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            resp.headers["Pragma"] = "no-cache"
            resp.headers["Expires"] = "0"
            return resp
        return HTMLResponse("<h1>NodeAI Server</h1><p>Web client not installed.</p>")

    @app.get("/api/status")
    async def get_status():
        llm_ok = await agent_loop.llm.health_check()
        mem_stats = await memory_system.get_stats()
        return {
            "status": "running",
            "llm_connected": llm_ok,
            "tools_count": len(tool_registry.list_tools()),
            "devices": len(connected_devices),
            "memory": mem_stats
        }

    @app.post("/api/chat")
    async def chat(request: ChatRequest, auth: bool = Depends(verify_auth)):
        try:
            response = await agent_loop.process_message(request.message)
            return {"response": response, "timestamp": time.time()}
        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/task")
    async def create_task(request: TaskRequest, auth: bool = Depends(verify_auth)):
        try:
            response = await agent_loop.process_message(request.request)
            task = agent_loop.conversation.current_task
            return {
                "task_id": task.id if task else None,
                "response": response,
                "state": task.state.value if task else "unknown"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/task/{task_id}")
    async def get_task(task_id: str, auth: bool = Depends(verify_auth)):
        task = agent_loop.conversation.current_task
        if task and task.id == task_id:
            return task.to_dict()
        raise HTTPException(status_code=404, detail="Task not found")

    @app.get("/api/tools")
    async def list_tools():
        return {"tools": tool_registry.get_schemas()}

    @app.post("/api/tool/execute")
    async def execute_tool(request: ToolExecuteRequest, auth: bool = Depends(verify_auth)):
        tool = tool_registry.get_tool(request.tool)
        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool not found: {request.tool}")
        try:
            result = await tool.execute(**request.args)
            return {"result": result, "success": not result.startswith("Error")}
        except Exception as e:
            return {"result": str(e), "success": False}

    @app.get("/api/memory")
    async def get_memory_stats(auth: bool = Depends(verify_auth)):
        return await memory_system.get_stats()

    @app.post("/api/memory/save")
    async def save_memory(key: str, content: str, category: str = "general", auth: bool = Depends(verify_auth)):
        await memory_system.save(key, content, category)
        return {"status": "saved"}

    @app.get("/api/memory/search")
    async def search_memory(query: str, limit: int = 10, auth: bool = Depends(verify_auth)):
        results = await memory_system.recall(query, limit)
        return {"results": results}

    @app.get("/api/knowledge")
    async def list_knowledge(category: str = None, auth: bool = Depends(verify_auth)):
        docs = await knowledge_base.list_documents(category)
        return {"documents": docs}

    @app.post("/api/knowledge/add")
    async def add_knowledge(title: str, content: str, source: str = "", category: str = "general", auth: bool = Depends(verify_auth)):
        doc_id = await knowledge_base.add_document(title, content, source, category)
        return {"id": doc_id, "status": "added"}

    @app.get("/api/knowledge/search")
    async def search_knowledge(query: str, limit: int = 5, auth: bool = Depends(verify_auth)):
        results = await knowledge_base.search(query, limit)
        return {"results": results}

    @app.get("/api/capabilities")
    async def get_capabilities():
        return {
            "tools": tool_registry.list_tools(),
            "devices": list(connected_devices.keys()),
            "platform": "windows"
        }

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        client_id = str(id(websocket))
        connected_clients.add(client_id)
        logger.info(f"WebSocket connected: {client_id}")

        try:
            await websocket.send_json({"type": "connected", "client_id": client_id})

            while True:
                data = await websocket.receive_text()
                msg = json.loads(data)

                if msg.get("type") == "chat":
                    response = await agent_loop.process_message(msg["content"])
                    await websocket.send_json({
                        "type": "response",
                        "content": response,
                        "timestamp": time.time()
                    })
                elif msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

        except WebSocketDisconnect:
            connected_clients.discard(client_id)
            logger.info(f"WebSocket disconnected: {client_id}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            connected_clients.discard(client_id)

    return app
