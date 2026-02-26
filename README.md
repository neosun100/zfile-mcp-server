[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

<div align="center">
  <h1>🗂️ ZFile MCP Server</h1>
  <p>A Model Context Protocol server that enables AI assistants to interact with ZFile</p>

  [![Docker Hub](https://img.shields.io/docker/v/neosun/zfile-mcp-server?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
  [![Docker Pulls](https://img.shields.io/docker/pulls/neosun/zfile-mcp-server?logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
  [![License](https://img.shields.io/github/license/neosun100/zfile-mcp-server)](LICENSE)
  [![GitHub Stars](https://img.shields.io/github/stars/neosun100/zfile-mcp-server?style=social)](https://github.com/neosun100/zfile-mcp-server)
</div>

---

## ✨ Features

- 📁 **List Files** — Browse directories in ZFile
- 📤 **Upload Files** — Get upload URLs (no base64, saves context tokens)
- 📤 **Batch Upload** — Get multiple upload URLs at once
- 📦 **Chunked Upload** — Large file upload via chunks (Cloudflare-friendly, auto-merge)
- 🔗 **Direct Links** — Generate permanent direct download links (single or batch)
- 🔗 **Short Links** — Generate temporary short links (31 days)
- 🔐 **Secure** — Auto-generated access token, credentials stored server-side
- 🌐 **Multi-Protocol** — SSE (Kiro, Claude Desktop) + Streamable HTTP (Gemini CLI)

## 🏗️ Architecture

```
┌─────────────────────────┐         ┌─────────────────────────┐         ┌─────────┐
│  MCP Client (Kiro/Claude)│  SSE    │  MCP Server (Docker)    │  API    │  ZFile  │
│  ┌───────────────────┐  │ ──────► │  ┌─────────────────┐    │ ──────► │         │
│  │ Only ACCESS_TOKEN │  │  Token  │  │ ZFile credentials│   │         │         │
│  └───────────────────┘  │         │  │ stored here      │   │         │         │
└─────────────────────────┘         │  └─────────────────┘    │         └─────────┘
                                    └─────────────────────────┘
```

**Security Model:**
- 🔒 Client only stores `ACCESS_TOKEN` (for MCP authentication)
- 🔒 Server stores ZFile credentials via environment variables
- 🔒 ZFile credentials are never exposed to clients

## 🚀 Quick Start

```bash
docker run -d --name zfile-mcp -p 8092:8092 \
  -e ZFILE_URL=https://your-zfile.com \
  -e ZFILE_USER=admin \
  -e ZFILE_PASS=password \
  -v ./data:/data \
  neosun/zfile-mcp-server:latest
```

Get your ACCESS_TOKEN:
```bash
docker logs zfile-mcp 2>&1 | grep ACCESS_TOKEN
```

## 📦 Installation

### Option 1: Docker Hub (Recommended)

```bash
docker run -d \
  --name zfile-mcp \
  -p 8092:8092 \
  -e ZFILE_URL=https://your-zfile-server.com \
  -e ZFILE_USER=your_username \
  -e ZFILE_PASS=your_password \
  -e ZFILE_STORAGE_KEY=1 \
  -v ./data:/data \
  neosun/zfile-mcp-server:latest
```

### Option 2: Docker Compose

Create `docker-compose.yml`:

```yaml
services:
  zfile-mcp:
    image: neosun/zfile-mcp-server:latest
    container_name: zfile-mcp
    restart: always
    ports:
      - '8092:8092'
    environment:
      - ZFILE_URL=https://your-zfile-server.com
      - ZFILE_USER=your_username
      - ZFILE_PASS=your_password
      - ZFILE_STORAGE_KEY=1
      # - ACCESS_TOKEN=            # auto-generated if not set
      # - CHUNK_SIZE_MB=10         # chunk size for large file upload (default: 10)
      # - MCP_SERVER_URL=          # optional: external URL for chunked upload commands
    volumes:
      - ./data:/data
```

```bash
docker compose up -d
```

### Option 3: Run from Source

**Requirements:** Python 3.11+

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server
pip install -r requirements.txt

export ZFILE_URL=https://your-zfile.com
export ZFILE_USER=admin
export ZFILE_PASS=password

python server.py
```

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `ZFILE_URL` | ✅ | ZFile server URL (e.g., `https://zfile.example.com`) | — |
| `ZFILE_USER` | ✅ | ZFile admin username | — |
| `ZFILE_PASS` | ✅ | ZFile admin password | — |
| `ZFILE_STORAGE_KEY` | ❌ | Storage source key | `1` |
| `ACCESS_TOKEN` | ❌ | Custom access token (auto-generated if not set) | Auto |
| `CHUNK_SIZE_MB` | ❌ | Chunk size for large file upload | `10` |
| `MCP_SERVER_URL` | ❌ | External URL override for chunked upload commands (useful behind reverse proxies) | Auto-detect |

> 💡 **Tip:** If `MCP_SERVER_URL` is not set, the server auto-detects its URL from request headers (`X-Forwarded-Host`, `X-Forwarded-Proto`). Set it explicitly when behind complex proxy setups.

### MCP Client Configuration

#### 🟢 Kiro CLI

Add to `~/.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "zfile": {
      "type": "sse",
      "url": "https://your-server.com/mcp/sse?token=YOUR_ACCESS_TOKEN",
      "headers": {},
      "autoApprove": ["*"],
      "disabled": false
    }
  }
}
```

#### 🟣 Claude Desktop

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "zfile": {
      "type": "sse",
      "url": "https://your-server.com/mcp/sse?token=YOUR_ACCESS_TOKEN"
    }
  }
}
```

#### 🔵 Google Gemini CLI

Gemini CLI uses Streamable HTTP protocol. Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "zfile": {
      "uri": "https://your-server.com/mcp?token=YOUR_ACCESS_TOKEN"
    }
  }
}
```

#### 🟡 Cursor

Add to `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "zfile": {
      "url": "https://your-server.com/mcp/sse?token=YOUR_ACCESS_TOKEN"
    }
  }
}
```

#### 🔴 Windsurf

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "zfile": {
      "serverUrl": "https://your-server.com/mcp/sse?token=YOUR_ACCESS_TOKEN"
    }
  }
}
```

## 🌐 Reverse Proxy Configuration

### Option A: Cloudflare Tunnel (Recommended)

Cloudflare Tunnel provides secure access without exposing ports. Configure in Cloudflare Dashboard:

| Public hostname | Service |
|-----------------|---------|
| `zfile.example.com` | `http://localhost:8090` (ZFile) |
| `zfile.example.com/mcp/*` | `http://localhost:8092` (MCP Server) |

**Path-based routing in Cloudflare Zero Trust:**
1. Go to **Zero Trust** → **Networks** → **Tunnels**
2. Select your tunnel → **Public Hostname**
3. Add two entries:
   - Path: `/mcp/*` → Service: `http://localhost:8092`
   - Path: (empty) → Service: `http://localhost:8090`

> ⚠️ **Cloudflare Timeout:** Cloudflare has a 100s proxy read timeout. For large file uploads, use chunked upload (`zfile_chunked_upload`) with `CHUNK_SIZE_MB=10` (default) to keep each chunk within the timeout.

### Option B: Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl;
    server_name zfile.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # MCP Server (SSE requires special handling)
    location /mcp/ {
        proxy_pass http://127.0.0.1:8092/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header Connection '';
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding off;
        proxy_read_timeout 86400s;
    }

    # ZFile main application
    location / {
        proxy_pass http://127.0.0.1:8090/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 10G;
    }
}
```

### Option C: Caddy

```caddyfile
zfile.example.com {
    handle_path /mcp/* {
        reverse_proxy localhost:8092
    }
    
    handle {
        reverse_proxy localhost:8090
    }
}
```

## 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| 📁 `zfile_list` | List files in a directory |
| 📤 `zfile_upload` | Get upload URL for a single file (< 10MB) |
| 📤 `zfile_batch_upload` | Get upload URLs for multiple files at once |
| 📦 `zfile_chunked_upload` | Initialize chunked upload for large files (> 10MB) |
| 📊 `zfile_chunked_upload_status` | Check chunked upload progress |
| 🔗 `zfile_direct_link` | Generate permanent direct link for a file |
| 🔗 `zfile_direct_links` | Generate direct links for multiple files |
| 🔗 `zfile_short_link` | Generate 31-day short link |

### Usage Examples

**List files:**
```
List all files in /documents
```

**Upload a small file:**
```
I need to upload app.apk to /releases folder
```

**Upload a large file (chunked):**
```
Upload a 200MB video file to /videos
```

**Generate direct link:**
```
Generate a direct link for /report.pdf
```

**Batch operations:**
```
Generate direct links for all PDF files in /documents
```

### 💡 Why URL-based Upload?

Base64 upload consumes context tokens:
- 1MB file → ~350K tokens
- 5MB file → ~1.75M tokens (exceeds most context limits!)

URL-based upload: **0 tokens** — client uploads directly to ZFile.

### 📦 Chunked Upload Flow

For files > 10MB (especially behind Cloudflare):

```
1. AI calls zfile_chunked_upload → gets upload_id + curl commands
2. Client splits file into 10MB chunks
3. Client POSTs each chunk to /upload/chunk endpoint
4. Server auto-merges all chunks when complete
5. Server uploads merged file to ZFile
6. Returns direct link ✅
```

> 💡 Chunked upload returns ready-to-use `curl` commands with the real server URL and token — just copy and run.

## 📁 Project Structure

```
zfile-mcp-server/
├── server.py           # Main MCP server implementation
├── Dockerfile          # Docker image definition
├── docker-compose.yml  # Docker Compose configuration
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── README.md           # English documentation
├── README_CN.md        # 简体中文文档
├── README_TW.md        # 繁體中文文檔
├── README_JP.md        # 日本語ドキュメント
├── CHANGELOG.md        # Version history
├── LICENSE             # MIT License
└── .gitignore          # Git ignore rules
```

## 🔧 Tech Stack

- **Runtime:** Python 3.11
- **Framework:** FastAPI + Uvicorn
- **Protocol:** MCP (Model Context Protocol) — SSE + Streamable HTTP
- **HTTP Client:** httpx
- **Container:** Docker

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/zfile-mcp-server&type=Date)](https://star-history.com/#neosun100/zfile-mcp-server)

## 📱 Follow

![WeChat](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
