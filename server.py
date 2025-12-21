#!/usr/bin/env python3
"""ZFile MCP SSE Server - Credentials passed from client via headers"""

import os
import json
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
import uuid
from urllib.parse import parse_qs

app = FastAPI()

sessions = {}


def get_zfile_token(zfile_url: str, username: str, password: str) -> str:
    """Login to ZFile and get token"""
    resp = httpx.post(f"{zfile_url}/user/login", json={
        "username": username, "password": password
    }, timeout=30)
    data = resp.json()
    if data.get("code") == "0":
        return data["data"]["token"]
    raise Exception(f"ZFile login failed: {data.get('msg')}")


def zfile_list(zfile_url: str, token: str, storage_key: str, path: str = "/") -> str:
    resp = httpx.post(f"{zfile_url}/api/storage/files", json={
        "storageKey": storage_key, "path": path
    }, headers={"zfile-token": token}, timeout=30)
    data = resp.json()
    if data.get("code") != "0":
        return f"Failed: {data.get('msg')}"
    files = data.get("data", {}).get("files", [])
    if not files:
        return "Directory is empty"
    return "\n".join([f"{'📁' if f.get('type')=='FOLDER' else '📄'} {f.get('name')} ({f.get('size','')})" for f in files])


def zfile_direct_link(zfile_url: str, token: str, storage_key: str, file_path: str) -> str:
    resp = httpx.post(f"{zfile_url}/api/path-link/batch/generate", json={
        "storageKey": storage_key, "paths": [file_path], "expireTime": 0
    }, headers={"zfile-token": token}, timeout=30)
    data = resp.json()
    if data.get("code") == "0" and data.get("data"):
        return data["data"][0].get("address", "Generation failed")
    return f"Failed: {data.get('msg')}"


def zfile_short_link(zfile_url: str, token: str, storage_key: str, file_path: str) -> str:
    resp = httpx.post(f"{zfile_url}/api/short-link/batch/generate", json={
        "storageKey": storage_key, "paths": [file_path], "expireTime": 2678400
    }, headers={"zfile-token": token}, timeout=30)
    data = resp.json()
    if data.get("code") == "0" and data.get("data"):
        return data["data"][0].get("url", data["data"][0].get("address", "Generation failed"))
    return f"Failed: {data.get('msg')}"


TOOLS = [
    {"name": "zfile_list", "description": "List files in ZFile directory", 
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string", "description": "Directory path, default /", "default": "/"}}}},
    {"name": "zfile_direct_link", "description": "Generate permanent direct link for a file",
     "inputSchema": {"type": "object", "properties": {"file_path": {"type": "string", "description": "File path, e.g. /test.pdf"}}, "required": ["file_path"]}},
    {"name": "zfile_short_link", "description": "Generate short link (31 days) for a file",
     "inputSchema": {"type": "object", "properties": {"file_path": {"type": "string", "description": "File path, e.g. /test.pdf"}}, "required": ["file_path"]}},
]


def handle_message(msg: dict, config: dict) -> dict:
    method = msg.get("method")
    params = msg.get("params", {})
    msg_id = msg.get("id")
    
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "zfile-mcp", "version": "1.0.0"}
        }}
    elif method == "tools/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        
        # Get credentials from session config
        zfile_url = config.get("zfile_url")
        token = config.get("token")
        storage_key = config.get("storage_key", "1")
        
        if not token:
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -1, "message": "Not authenticated. Check your credentials."}}
        
        try:
            if name == "zfile_list":
                result = zfile_list(zfile_url, token, storage_key, args.get("path", "/"))
            elif name == "zfile_direct_link":
                result = zfile_direct_link(zfile_url, token, storage_key, args["file_path"])
            elif name == "zfile_short_link":
                result = zfile_short_link(zfile_url, token, storage_key, args["file_path"])
            else:
                result = f"Unknown tool: {name}"
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": result}]}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -1, "message": str(e)}}
    elif method == "notifications/initialized":
        return None
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Method not found"}}


@app.get("/sse")
async def sse_endpoint(request: Request):
    # Get credentials from headers (passed by MCP client)
    zfile_url = request.headers.get("X-ZFile-URL", "")
    zfile_user = request.headers.get("X-ZFile-User", "")
    zfile_pass = request.headers.get("X-ZFile-Pass", "")
    storage_key = request.headers.get("X-ZFile-Storage-Key", "1")
    
    if not all([zfile_url, zfile_user, zfile_pass]):
        raise HTTPException(status_code=401, detail="Missing credentials in headers")
    
    # Authenticate with ZFile
    try:
        token = get_zfile_token(zfile_url, zfile_user, zfile_pass)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    session_id = str(uuid.uuid4())
    queue = asyncio.Queue()
    sessions[session_id] = {
        "queue": queue,
        "config": {
            "zfile_url": zfile_url,
            "token": token,
            "storage_key": storage_key
        }
    }
    
    async def event_generator():
        yield f"event: endpoint\ndata: /message?session_id={session_id}\n\n"
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=30)
                    yield f"event: message\ndata: {json.dumps(msg)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            sessions.pop(session_id, None)
    
    return StreamingResponse(event_generator(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"})


@app.post("/message")
async def message_endpoint(request: Request, session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    body = await request.json()
    response = handle_message(body, session["config"])
    
    if response:
        await session["queue"].put(response)
    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8092)
