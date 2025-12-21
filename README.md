# ZFile MCP Server

A Model Context Protocol (MCP) server that enables AI assistants to interact with [ZFile](https://github.com/zfile-dev/zfile) - a powerful online file management system.

[![Docker Hub](https://img.shields.io/docker/v/neosun/zfile-mcp-server?label=Docker%20Hub)](https://hub.docker.com/r/neosun/zfile-mcp-server)
[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/zfile-mcp-server)](https://hub.docker.com/r/neosun/zfile-mcp-server)

## Architecture

```
┌─────────────────────────┐         ┌─────────────────────────┐         ┌─────────┐
│  MCP Client (Kiro)      │  SSE    │  MCP Server (Docker)    │  API    │  ZFile  │
│  ┌───────────────────┐  │ ──────► │  ┌─────────────────┐    │ ──────► │         │
│  │ Only ACCESS_TOKEN │  │  Token  │  │ ZFile credentials│   │         │         │
│  └───────────────────┘  │         │  │ stored here      │   │         │         │
└─────────────────────────┘         │  └─────────────────┘    │         └─────────┘
                                    └─────────────────────────┘
```

- **Client**: Only stores ACCESS_TOKEN (for MCP authentication)
- **Server**: Stores ZFile credentials (username/password) via environment variables
- **Security**: ZFile credentials never exposed to clients

## Features

- 📁 **List Files** - Browse directories in ZFile
- ⬆️ **Upload Files** - Upload files with automatic direct link generation
- 🔗 **Direct Links** - Generate permanent direct download links
- 🔗 **Short Links** - Generate temporary short links (31 days)
- 📤 **Large File Support** - Get upload URLs for direct large file uploads

## Quick Start

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
    volumes:
      - ./data:/data
```

Start:

```bash
docker compose up -d
```

### Option 3: Build from Source

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server
docker build -t zfile-mcp-server .
```

## Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `ZFILE_URL` | ✅ | ZFile server URL | `https://zfile.example.com` |
| `ZFILE_USER` | ✅ | ZFile username | `admin` |
| `ZFILE_PASS` | ✅ | ZFile password | `your_password` |
| `ZFILE_STORAGE_KEY` | ❌ | Storage source key (default: 1) | `1` |
| `ACCESS_TOKEN` | ❌ | Custom access token (auto-generated if not set) | `zfile-xxx` |

## Get Access Token

The server automatically generates a secure access token on first startup:

```bash
docker logs zfile-mcp
```

Look for:
```
==================================================
ACCESS_TOKEN: zfile-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
==================================================
```

## Configure MCP Client

Add to your MCP client configuration (e.g., `~/.kiro/settings/mcp.json`):

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

## Available Tools

| Tool | Description | Use Case |
|------|-------------|----------|
| `zfile_list` | List files in a directory | Browse files |
| `zfile_upload` | Upload file (base64) with auto direct link | Small files (<5MB) |
| `zfile_get_upload_url` | Get direct upload URL | Large files |
| `zfile_direct_link` | Generate permanent direct link | Share files permanently |
| `zfile_short_link` | Generate 31-day short link | Temporary sharing |

### Tool Details

#### zfile_list
List files in a ZFile directory.

**Parameters:**
- `path` (string, optional): Directory path, default "/"

#### zfile_upload
Upload a small file with automatic direct link generation.

**Parameters:**
- `file_path` (string, required): Target path in ZFile, e.g., "/uploads/test.txt"
- `file_content_base64` (string, required): File content encoded in base64

**Returns:**
```
✅ Upload success: /test.txt
📎 Direct link: https://your-zfile-server.com/directlink/1/test.txt
```

#### zfile_get_upload_url
Get a direct upload URL for large files.

**Parameters:**
- `path` (string, optional): Target directory, default "/"
- `filename` (string, required): File name
- `size` (integer, required): File size in bytes

**Returns:**
```
Upload URL: https://your-zfile-server.com/file/upload/1/largefile.zip

Upload command:
curl -X PUT 'URL' -F 'file=@/path/to/yourfile'
```

#### zfile_direct_link
Generate a permanent direct download link.

**Parameters:**
- `file_path` (string, required): File path, e.g., "/test.pdf"

#### zfile_short_link
Generate a short link valid for 31 days.

**Parameters:**
- `file_path` (string, required): File path, e.g., "/test.pdf"

## Security

- **Access Token**: Auto-generated on first startup, stored in `./data/.access_token`
- **Token Persistence**: Token survives container restarts (stored in volume)
- **Credentials**: ZFile credentials stored server-side only, never exposed to clients
- **No Secrets in Image**: Docker image contains no sensitive data

## Nginx Reverse Proxy (Optional)

```nginx
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
}
```

## License

MIT License
