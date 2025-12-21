#!/usr/bin/env python3
"""ZFile MCP SSE Server"""

import os
import json
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
import uuid

app = FastAPI()

ZFILE_URL = os.getenv("ZFILE_URL", "https://zfile.aws.xin")
ZFILE_USER = os.getenv("ZFILE_USER", "")
ZFILE_PASS = os.getenv("ZFILE_PASS", "")
STORAGE_KEY = os.getenv("ZFILE_STORAGE_KEY", "1")

_token_cache = {"token": None}


def get_token() -> str:
    if _token_cache["token"]:
        return _token_cache["token"]
    resp = httpx.post(f"{ZFILE_URL}/user/login", json={
        "username": ZFILE_USER, "password": ZFILE_PASS
    }, timeout=30)
    data = resp.json()
    if data.get("code") == "0":
        _token_cache["token"] = data["data"]["token"]
        return _token_cache["token"]
    raise Exception(f"登录失败: {data.get('msg')}")


def auth_headers() -> dict:
    return {"zfile-token": get_token()}


# MCP 工具实现
def zfile_list(path: str = "/") -> str:
    resp = httpx.post(f"{ZFILE_URL}/api/storage/files", json={
        "storageKey": STORAGE_KEY, "path": path
    }, headers=auth_headers(), timeout=30)
    data = resp.json()
    if data.get("code") != "0":
        return f"获取失败: {data.get('msg')}"
    files = data.get("data", {}).get("files", [])
    if not files:
        return "目录为空"
    return "\n".join([f"{'📁' if f.get('type')=='FOLDER' else '📄'} {f.get('name')} ({f.get('size','')})" for f in files])


def zfile_upload(file_path: str, remote_path: str = "/") -> str:
    if not os.path.exists(file_path):
        return f"错误: 文件不存在 {file_path}"
    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        resp = httpx.put(f"{ZFILE_URL}/file/upload/{STORAGE_KEY}{remote_path}",
            files={"file": (filename, f)}, params={"filename": filename},
            headers=auth_headers(), timeout=300)
    data = resp.json()
    return f"上传成功: {remote_path.rstrip('/')}/{filename}" if data.get("code") == "0" else f"上传失败: {data.get('msg')}"


def zfile_direct_link(file_path: str) -> str:
    resp = httpx.post(f"{ZFILE_URL}/api/path-link/batch/generate", json={
        "storageKey": STORAGE_KEY, "paths": [file_path], "expireTime": 0
    }, headers=auth_headers(), timeout=30)
    data = resp.json()
    if data.get("code") == "0" and data.get("data"):
        return data["data"][0].get("address", "生成失败")
    return f"生成失败: {data.get('msg')}"


def zfile_short_link(file_path: str) -> str:
    resp = httpx.post(f"{ZFILE_URL}/api/short-link/batch/generate", json={
        "storageKey": STORAGE_KEY, "paths": [file_path], "expireTime": 2678400
    }, headers=auth_headers(), timeout=30)
    data = resp.json()
    if data.get("code") == "0" and data.get("data"):
        return data["data"][0].get("url", data["data"][0].get("address", "生成失败"))
    return f"生成失败: {data.get('msg')}"


# MCP 协议定义
TOOLS = [
    {"name": "zfile_list", "description": "列出 ZFile 目录下的文件", 
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string", "description": "目录路径，默认 /", "default": "/"}}}},
    {"name": "zfile_direct_link", "description": "生成文件的永久直链",
     "inputSchema": {"type": "object", "properties": {"file_path": {"type": "string", "description": "文件路径，如 /test.pdf"}}, "required": ["file_path"]}},
    {"name": "zfile_short_link", "description": "生成文件的短链（31天有效）",
     "inputSchema": {"type": "object", "properties": {"file_path": {"type": "string", "description": "文件路径，如 /test.pdf"}}, "required": ["file_path"]}},
]

sessions = {}


def handle_message(msg: dict) -> dict:
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
        try:
            if name == "zfile_list":
                result = zfile_list(args.get("path", "/"))
            elif name == "zfile_direct_link":
                result = zfile_direct_link(args["file_path"])
            elif name == "zfile_short_link":
                result = zfile_short_link(args["file_path"])
            else:
                result = f"未知工具: {name}"
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": result}]}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -1, "message": str(e)}}
    elif method == "notifications/initialized":
        return None
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Method not found"}}


@app.get("/sse")
async def sse_endpoint(request: Request):
    session_id = str(uuid.uuid4())
    queue = asyncio.Queue()
    sessions[session_id] = queue
    
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
    body = await request.json()
    response = handle_message(body)
    if response and session_id in sessions:
        await sessions[session_id].put(response)
    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8092)
