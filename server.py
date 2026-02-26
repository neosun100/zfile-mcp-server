#!/usr/bin/env python3
"""
ZFile MCP Server v1.3.0
- SSE 协议 (Kiro, Claude Desktop)
- Streamable HTTP 协议 (Google Gemini CLI)
- 分片上传 (Cloudflare 友好, 自动合并)
"""

import os
import json
import time
import shutil
import hashlib
import httpx
from fastapi import FastAPI, Request, HTTPException, Response, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
import asyncio
import uuid

VERSION = "1.3.0"
app = FastAPI()
sessions = {}

# 分片上传状态: {upload_id: {filename, path, total_chunks, received: set(), chunk_dir, created_at, config}}
chunked_uploads = {}

# 配置
DEFAULT_ZFILE_URL = os.getenv("ZFILE_URL", "")
DEFAULT_ZFILE_USER = os.getenv("ZFILE_USER", "")
DEFAULT_ZFILE_PASS = os.getenv("ZFILE_PASS", "")
DEFAULT_STORAGE_KEY = os.getenv("ZFILE_STORAGE_KEY", "1")
CHUNK_DIR = os.getenv("CHUNK_DIR", "/tmp/zfile-chunks")
CHUNK_SIZE_MB = int(os.getenv("CHUNK_SIZE_MB", "50"))

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
    os.makedirs(CHUNK_DIR, exist_ok=True)
    if ACCESS_TOKEN:
        sys.stderr.write(f"\n{'='*50}\n")
        sys.stderr.write(f"ACCESS_TOKEN: {ACCESS_TOKEN}\n")
        sys.stderr.write(f"{'='*50}\n\n")
        sys.stderr.flush()
    # 清理残留分片
    asyncio.create_task(cleanup_stale_uploads())

async def cleanup_stale_uploads():
    """每 10 分钟清理超过 1 小时的残留分片"""
    while True:
        await asyncio.sleep(600)
        now = time.time()
        stale = [uid for uid, u in chunked_uploads.items() if now - u["created_at"] > 3600]
        for uid in stale:
            info = chunked_uploads.pop(uid, None)
            if info:
                shutil.rmtree(info["chunk_dir"], ignore_errors=True)


# ============================================================
# ZFile API helpers
# ============================================================

def get_zfile_token(zfile_url: str, username: str, password: str) -> str:
    resp = httpx.post(f"{zfile_url}/user/login", json={
        "username": username, "password": password
    }, timeout=30)
    data = resp.json()
    if data.get("code") == "0":
        return data["data"]["token"]
    raise Exception(f"ZFile login failed: {data.get('msg')}")


def zfile_list(zfile_url, token, storage_key, path="/"):
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


def zfile_direct_link(zfile_url, token, storage_key, file_path):
    resp = httpx.post(f"{zfile_url}/api/path-link/batch/generate", json={
        "storageKey": storage_key, "paths": [file_path], "expireTime": 0
    }, headers={"zfile-token": token}, timeout=30)
    data = resp.json()
    if data.get("code") == "0" and data.get("data"):
        return data["data"][0].get("address", "Generation failed")
    return f"Failed: {data.get('msg')}"


def zfile_short_link(zfile_url, token, storage_key, file_path):
    resp = httpx.post(f"{zfile_url}/api/short-link/batch/generate", json={
        "storageKey": storage_key, "paths": [file_path], "expireTime": 2678400
    }, headers={"zfile-token": token}, timeout=30)
    data = resp.json()
    if data.get("code") == "0" and data.get("data"):
        return data["data"][0].get("url", data["data"][0].get("address", "Generation failed"))
    return f"Failed: {data.get('msg')}"


def zfile_upload(zfile_url, token, storage_key, path, filename, size):
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


def zfile_batch_upload(zfile_url, token, storage_key, path, files):
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
            fp = path.rstrip('/') + '/' + filename if path != '/' else '/' + filename
            results.append(f"📄 {filename}\n   URL: {url}\n   Direct: {zfile_url}/directlink/{storage_key}{fp}")
        else:
            results.append(f"❌ {filename}: {data.get('msg')}")
    return "📤 Batch Upload URLs:\n\n" + "\n\n".join(results)


def zfile_direct_links(zfile_url, token, storage_key, file_paths):
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


def zfile_chunked_upload_init(zfile_url, token, storage_key, path, filename, total_size, config):
    """初始化分片上传，返回 upload_id 和分片信息"""
    chunk_size = CHUNK_SIZE_MB * 1024 * 1024
    total_chunks = (total_size + chunk_size - 1) // chunk_size
    if total_chunks < 1:
        total_chunks = 1

    upload_id = str(uuid.uuid4())
    chunk_dir = os.path.join(CHUNK_DIR, upload_id)
    os.makedirs(chunk_dir, exist_ok=True)

    chunked_uploads[upload_id] = {
        "filename": filename,
        "path": path,
        "total_size": total_size,
        "total_chunks": total_chunks,
        "chunk_size": chunk_size,
        "received": set(),
        "chunk_dir": chunk_dir,
        "created_at": time.time(),
        "config": config,
    }

    return f"""📤 Chunked upload initialized!

📋 Upload ID: {upload_id}
📄 File: {filename}
📦 Total size: {total_size} bytes
🧩 Chunks: {total_chunks} × {CHUNK_SIZE_MB}MB

📋 Upload each chunk with:
  curl -X POST '<MCP_SERVER>/upload/chunk?token=<TOKEN>' \\
    -F 'upload_id={upload_id}' \\
    -F 'chunk_index=<0-{total_chunks - 1}>' \\
    -F 'file=@chunk_file'

Or use this script to split and upload automatically:
  split -b {CHUNK_SIZE_MB}m -d '{filename}' /tmp/chunk_
  for i in $(seq 0 {total_chunks - 1}); do
    idx=$(printf "%02d" $i)
    curl -X POST '<MCP_SERVER>/upload/chunk?token=<TOKEN>' \\
      -F "upload_id={upload_id}" -F "chunk_index=$i" -F "file=@/tmp/chunk_$idx"
  done

⏳ Chunks expire after 1 hour. Upload will auto-complete when all chunks arrive."""


def zfile_chunked_upload_status(upload_id):
    """查询分片上传状态"""
    if upload_id not in chunked_uploads:
        return "❌ Upload ID not found or expired"
    info = chunked_uploads[upload_id]
    received = sorted(info["received"])
    missing = sorted(set(range(info["total_chunks"])) - info["received"])
    return f"""📋 Upload: {upload_id}
📄 File: {info['filename']}
✅ Received: {len(received)}/{info['total_chunks']} chunks
{'🧩 Missing: ' + str(missing) if missing else '🎉 All chunks received! Merging...'}"""


# ============================================================
# MCP Tools definition
# ============================================================

TOOLS = [
    {"name": "zfile_list", "description": "List files in ZFile directory",
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string", "description": "Directory path, default /", "default": "/"}}}},

    {"name": "zfile_upload", "description": "Get upload URL for a file (small files < 50MB). Returns URL for direct PUT upload.",
     "inputSchema": {"type": "object", "properties": {
         "path": {"type": "string", "description": "Target directory, e.g. /uploads/", "default": "/"},
         "filename": {"type": "string", "description": "File name"},
         "size": {"type": "integer", "description": "File size in bytes", "default": 0}
     }, "required": ["filename"]}},

    {"name": "zfile_chunked_upload", "description": "Initialize chunked upload for large files (>50MB). Splits file into chunks to avoid Cloudflare timeout. Returns upload_id and instructions.",
     "inputSchema": {"type": "object", "properties": {
         "path": {"type": "string", "description": "Target directory", "default": "/"},
         "filename": {"type": "string", "description": "File name"},
         "total_size": {"type": "integer", "description": "Total file size in bytes"}
     }, "required": ["filename", "total_size"]}},

    {"name": "zfile_chunked_upload_status", "description": "Check status of a chunked upload",
     "inputSchema": {"type": "object", "properties": {
         "upload_id": {"type": "string", "description": "Upload ID from zfile_chunked_upload"}
     }, "required": ["upload_id"]}},

    {"name": "zfile_batch_upload", "description": "Get upload URLs for multiple files at once",
     "inputSchema": {"type": "object", "properties": {
         "path": {"type": "string", "description": "Target directory", "default": "/"},
         "files": {"type": "array", "description": "Array of {filename, size} objects", "items": {
             "type": "object", "properties": {"filename": {"type": "string"}, "size": {"type": "integer", "default": 0}}, "required": ["filename"]
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
            "serverInfo": {"name": "zfile-mcp", "version": VERSION}
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
            elif name == "zfile_chunked_upload":
                result = zfile_chunked_upload_init(zfile_url, token, storage_key, args.get("path", "/"), args["filename"], args["total_size"], config)
            elif name == "zfile_chunked_upload_status":
                result = zfile_chunked_upload_status(args["upload_id"])
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


def get_config_and_token(access_token: str = None):
    if ACCESS_TOKEN and access_token != ACCESS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid access token")
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
    return {"zfile_url": zfile_url, "token": zfile_token, "storage_key": storage_key}


# ============================================================
# 分片上传 HTTP 端点
# ============================================================

@app.post("/upload/chunk")
async def upload_chunk(
    request: Request,
    token: str = None,
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    file: UploadFile = File(...)
):
    """接收单个分片，全部到齐后自动合并并上传到 ZFile"""
    if ACCESS_TOKEN and token != ACCESS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid access token")

    if upload_id not in chunked_uploads:
        raise HTTPException(status_code=404, detail="Upload ID not found or expired")

    info = chunked_uploads[upload_id]
    if chunk_index < 0 or chunk_index >= info["total_chunks"]:
        raise HTTPException(status_code=400, detail=f"Invalid chunk_index, must be 0-{info['total_chunks']-1}")

    # 保存分片
    chunk_path = os.path.join(info["chunk_dir"], f"{chunk_index:06d}")
    content = await file.read()
    with open(chunk_path, "wb") as f:
        f.write(content)
    info["received"].add(chunk_index)

    # 检查是否全部到齐
    if len(info["received"]) == info["total_chunks"]:
        # 合并并上传
        try:
            result = await merge_and_upload(upload_id)
            return JSONResponse({"status": "completed", "message": result})
        except Exception as e:
            return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

    return JSONResponse({
        "status": "ok",
        "received": len(info["received"]),
        "total": info["total_chunks"],
        "missing": sorted(set(range(info["total_chunks"])) - info["received"])
    })


async def merge_and_upload(upload_id: str) -> str:
    """合并分片并上传到 ZFile"""
    info = chunked_uploads[upload_id]
    config = info["config"]
    merged_path = os.path.join(info["chunk_dir"], info["filename"])

    # 合并
    with open(merged_path, "wb") as out:
        for i in range(info["total_chunks"]):
            chunk_path = os.path.join(info["chunk_dir"], f"{i:06d}")
            with open(chunk_path, "rb") as chunk:
                shutil.copyfileobj(chunk, out)

    merged_size = os.path.getsize(merged_path)

    # 获取上传 URL
    zfile_url = config["zfile_url"]
    zfile_token = config["token"]
    storage_key = config.get("storage_key", "1")
    path = info["path"]
    filename = info["filename"]

    resp = httpx.post(f"{zfile_url}/api/file/operator/upload/file", json={
        "storageKey": storage_key, "path": path, "name": filename, "size": merged_size
    }, headers={"zfile-token": zfile_token}, timeout=30)
    data = resp.json()
    if data.get("code") != "0":
        raise Exception(f"Failed to get upload URL: {data.get('msg')}")

    upload_url = data["data"]

    # 上传合并后的文件到 ZFile (服务端到服务端，不经过 Cloudflare)
    with open(merged_path, "rb") as f:
        upload_resp = httpx.put(upload_url, files={"file": (filename, f)}, timeout=600)

    # 清理
    shutil.rmtree(info["chunk_dir"], ignore_errors=True)
    chunked_uploads.pop(upload_id, None)

    file_path = path.rstrip('/') + '/' + filename if path != '/' else '/' + filename
    direct_link = f"{zfile_url}/directlink/{storage_key}{file_path}"

    if upload_resp.status_code < 400:
        return f"✅ Upload complete! {filename} ({merged_size} bytes)\n📎 Direct link: {direct_link}"
    else:
        raise Exception(f"Upload failed: HTTP {upload_resp.status_code}")


@app.get("/upload/status")
async def upload_status(token: str = None, upload_id: str = None):
    """查询分片上传状态"""
    if ACCESS_TOKEN and token != ACCESS_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid access token")
    if upload_id and upload_id in chunked_uploads:
        info = chunked_uploads[upload_id]
        return {
            "upload_id": upload_id,
            "filename": info["filename"],
            "received": len(info["received"]),
            "total": info["total_chunks"],
            "missing": sorted(set(range(info["total_chunks"])) - info["received"])
        }
    # 列出所有活跃上传
    return {"active_uploads": [
        {"upload_id": uid, "filename": u["filename"],
         "received": len(u["received"]), "total": u["total_chunks"]}
        for uid, u in chunked_uploads.items()
    ]}


# ============================================================
# SSE 协议端点 (Kiro, Claude Desktop)
# ============================================================

@app.api_route("/sse", methods=["GET", "POST", "HEAD"])
async def sse_endpoint(request: Request, token: str = None):
    if request.method == "HEAD":
        return {"status": "ok"}
    config = get_config_and_token(token)
    session_id = str(uuid.uuid4())
    queue = asyncio.Queue()
    sessions[session_id] = {"queue": queue, "config": config}

    async def event_generator():
        scheme = request.headers.get("x-forwarded-proto", "https")
        host = request.headers.get("x-forwarded-host", request.headers.get("host", ""))
        yield f"event: endpoint\ndata: {scheme}://{host}/mcp/message?session_id={session_id}\n\n"
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=25)
                    yield f"event: message\ndata: {json.dumps(msg)}\n\n"
                except asyncio.TimeoutError:
                    yield "event: ping\ndata: {}\n\n"
        finally:
            sessions.pop(session_id, None)

    return StreamingResponse(event_generator(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"})


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


# ============================================================
# Streamable HTTP 协议端点 (Google Gemini CLI)
# ============================================================

@app.api_route("/mcp", methods=["GET", "POST", "OPTIONS"])
@app.api_route("/mcp/", methods=["GET", "POST", "OPTIONS"], include_in_schema=False)
async def streamable_http_endpoint(request: Request, token: str = None):
    if request.method == "OPTIONS":
        return Response(status_code=200, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Accept, Authorization",
        })
    if request.method == "GET":
        accept = request.headers.get("accept", "")
        if "text/event-stream" in accept:
            return await sse_endpoint(request, token)
        return JSONResponse({
            "name": "zfile-mcp", "version": VERSION,
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "endpoints": {"streamable_http": "/mcp", "sse": "/mcp/sse"}
        })
    if request.method == "POST":
        accept = request.headers.get("accept", "")
        if "application/json" not in accept and "text/event-stream" not in accept:
            return JSONResponse(
                {"jsonrpc": "2.0", "error": {"code": -32000, "message": "Not Acceptable"}, "id": None}, status_code=406)
        config = get_config_and_token(token)
        try:
            body = await request.json()
        except Exception as e:
            return JSONResponse(
                {"jsonrpc": "2.0", "error": {"code": -32700, "message": f"Parse error: {e}"}, "id": None}, status_code=400)
        response = handle_message(body, config)
        if response is None:
            return Response(status_code=204)
        return JSONResponse(response, headers={"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"})


@app.api_route("/mcp/sse", methods=["GET", "POST", "HEAD"])
async def mcp_sse_endpoint(request: Request, token: str = None):
    return await sse_endpoint(request, token)

@app.post("/mcp/message")
async def mcp_message_endpoint(request: Request, session_id: str):
    return await message_endpoint(request, session_id)


# ============================================================
# 健康检查
# ============================================================

@app.get("/health")
async def health():
    return {"status": "ok", "version": VERSION, "protocols": ["sse", "streamable-http"],
            "features": ["chunked-upload"]}

@app.get("/")
async def root():
    return {
        "name": "ZFile MCP Server", "version": VERSION,
        "description": "MCP server for ZFile file management with chunked upload support",
        "protocols": {
            "streamable_http": {"endpoint": "/mcp"},
            "sse": {"endpoint": "/mcp/sse or /sse"}
        },
        "tools": [t["name"] for t in TOOLS],
        "chunked_upload": {
            "endpoint": "/upload/chunk",
            "status": "/upload/status",
            "chunk_size_mb": CHUNK_SIZE_MB
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8092)
