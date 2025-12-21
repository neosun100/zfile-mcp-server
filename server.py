#!/usr/bin/env python3
"""ZFile MCP SSE Server"""

import os
import json
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
import uuid

app = FastAPI()
sessions = {}

# 从环境变量或文件读取配置
DEFAULT_ZFILE_URL = os.getenv("ZFILE_URL", "")
DEFAULT_ZFILE_USER = os.getenv("ZFILE_USER", "")
DEFAULT_ZFILE_PASS = os.getenv("ZFILE_PASS", "")
DEFAULT_STORAGE_KEY = os.getenv("ZFILE_STORAGE_KEY", "1")

# ACCESS_TOKEN: 优先环境变量，否则从文件读取或自动生成
TOKEN_FILE = "/data/.access_token"
def get_access_token():
    if os.getenv("ACCESS_TOKEN"):
        return os.getenv("ACCESS_TOKEN")
    if os.path.exists(TOKEN_FILE):
        return open(TOKEN_FILE).read().strip()
    import secrets
    token = f"zfile-{secrets.token_hex(16)}"
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    open(TOKEN_FILE, "w").write(token)
    return token

ACCESS_TOKEN = get_access_token()

@app.on_event("startup")
async def startup_event():
    import sys
    if ACCESS_TOKEN:
        sys.stderr.write(f"\n{'='*50}\n")
        sys.stderr.write(f"ACCESS_TOKEN: {ACCESS_TOKEN}\n")
        sys.stderr.write(f"{'='*50}\n\n")
        sys.stderr.flush()


def get_zfile_token(zfile_url: str, username: str, password: str) -> str:
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


def zfile_upload(zfile_url: str, token: str, storage_key: str, path: str, filename: str, size: int) -> str:
    """Get upload URL and return with direct link generation info"""
    resp = httpx.post(f"{zfile_url}/api/file/operator/upload/file", json={
        "storageKey": storage_key, "path": path, "name": filename, "size": size
    }, headers={"zfile-token": token}, timeout=30)
    data = resp.json()
    if data.get("code") == "0":
        url = data.get('data')
        file_path = path.rstrip('/') + '/' + filename if path != '/' else '/' + filename
        direct_link_url = f"{zfile_url}/directlink/{storage_key}{file_path}"
        return f"""📤 Upload URL: {url}

📋 Upload command:
curl -X PUT '{url}' -F 'file=@{filename}'

✅ After upload, your direct link will be:
{direct_link_url}"""
    return f"Failed: {data.get('msg')}"


def zfile_batch_upload(zfile_url: str, token: str, storage_key: str, path: str, files: list) -> str:
    """Get upload URLs for multiple files"""
    results = []
    for f in files:
        filename = f.get("filename")
        size = f.get("size", 0)
        resp = httpx.post(f"{zfile_url}/api/file/operator/upload/file", json={
            "storageKey": storage_key, "path": path, "name": filename, "size": size
        }, headers={"zfile-token": token}, timeout=30)
        data = resp.json()
        if data.get("code") == "0":
            url = data.get('data')
            file_path = path.rstrip('/') + '/' + filename if path != '/' else '/' + filename
            results.append(f"📄 {filename}\n   URL: {url}\n   Direct: {zfile_url}/directlink/{storage_key}{file_path}")
        else:
            results.append(f"❌ {filename}: {data.get('msg')}")
    
    return "📤 Batch Upload URLs:\n\n" + "\n\n".join(results) + f"""

📋 Batch upload script:
for file in *.jpg; do
  curl -X PUT '{zfile_url}/file/upload/{storage_key}{path}' -F "file=@$file"
done"""


def zfile_direct_links(zfile_url: str, token: str, storage_key: str, file_paths: list) -> str:
    """Generate direct links for multiple files"""
    resp = httpx.post(f"{zfile_url}/api/path-link/batch/generate", json={
        "storageKey": storage_key, "paths": file_paths, "expireTime": 0
    }, headers={"zfile-token": token}, timeout=30)
    data = resp.json()
    if data.get("code") == "0" and data.get("data"):
        results = []
        for i, item in enumerate(data["data"]):
            results.append(f"📄 {file_paths[i]}\n   📎 {item.get('address', 'Failed')}")
        return "🔗 Direct Links:\n\n" + "\n\n".join(results)
    return f"Failed: {data.get('msg')}"


TOOLS = [
    {"name": "zfile_list", "description": "List files in ZFile directory", 
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string", "description": "Directory path, default /", "default": "/"}}}},
    
    {"name": "zfile_upload", "description": "Get upload URL for a file. Returns URL for direct PUT upload and the resulting direct link.",
     "inputSchema": {"type": "object", "properties": {
         "path": {"type": "string", "description": "Target directory, e.g. /uploads/", "default": "/"},
         "filename": {"type": "string", "description": "File name, e.g. app.apk"},
         "size": {"type": "integer", "description": "File size in bytes", "default": 0}
     }, "required": ["filename"]}},
    
    {"name": "zfile_batch_upload", "description": "Get upload URLs for multiple files at once",
     "inputSchema": {"type": "object", "properties": {
         "path": {"type": "string", "description": "Target directory", "default": "/"},
         "files": {"type": "array", "description": "Array of {filename, size} objects", "items": {
             "type": "object", "properties": {
                 "filename": {"type": "string"},
                 "size": {"type": "integer", "default": 0}
             }, "required": ["filename"]
         }}
     }, "required": ["files"]}},
    
    {"name": "zfile_direct_link", "description": "Generate permanent direct link for a file",
     "inputSchema": {"type": "object", "properties": {"file_path": {"type": "string", "description": "File path, e.g. /test.pdf"}}, "required": ["file_path"]}},
    
    {"name": "zfile_direct_links", "description": "Generate permanent direct links for multiple files",
     "inputSchema": {"type": "object", "properties": {
         "file_paths": {"type": "array", "description": "Array of file paths", "items": {"type": "string"}}
     }, "required": ["file_paths"]}},
    
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
            "serverInfo": {"name": "zfile-mcp", "version": "1.1.0"}
        }}
    elif method == "tools/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        zfile_url = config.get("zfile_url")
        token = config.get("token")
        storage_key = config.get("storage_key", "1")
        
        if not token:
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -1, "message": "Not authenticated"}}
        
        try:
            if name == "zfile_list":
                result = zfile_list(zfile_url, token, storage_key, args.get("path", "/"))
            elif name == "zfile_upload":
                result = zfile_upload(zfile_url, token, storage_key, args.get("path", "/"), args["filename"], args.get("size", 0))
            elif name == "zfile_batch_upload":
                result = zfile_batch_upload(zfile_url, token, storage_key, args.get("path", "/"), args["files"])
            elif name == "zfile_direct_link":
                result = zfile_direct_link(zfile_url, token, storage_key, args["file_path"])
            elif name == "zfile_direct_links":
                result = zfile_direct_links(zfile_url, token, storage_key, args["file_paths"])
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


@app.api_route("/sse", methods=["GET", "POST", "HEAD"])
async def sse_endpoint(request: Request, token: str = None):
    if ACCESS_TOKEN and token != ACCESS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    if request.method == "HEAD":
        return {"status": "ok"}
    
    zfile_url = DEFAULT_ZFILE_URL
    zfile_user = DEFAULT_ZFILE_USER
    zfile_pass = DEFAULT_ZFILE_PASS
    storage_key = DEFAULT_STORAGE_KEY
    
    if not all([zfile_url, zfile_user, zfile_pass]):
        raise HTTPException(status_code=500, detail="Server not configured")
    
    try:
        zfile_token = get_zfile_token(zfile_url, zfile_user, zfile_pass)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    session_id = str(uuid.uuid4())
    queue = asyncio.Queue()
    sessions[session_id] = {
        "queue": queue,
        "config": {"zfile_url": zfile_url, "token": zfile_token, "storage_key": storage_key}
    }
    
    async def event_generator():
        scheme = request.headers.get("x-forwarded-proto", "https")
        host = request.headers.get("x-forwarded-host", request.headers.get("host", ""))
        yield f"event: endpoint\ndata: {scheme}://{host}/mcp/message?session_id={session_id}\n\n"
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
