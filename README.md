[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# ZFile MCP Server

[![Docker Hub](https://img.shields.io/docker/v/neosun/zfile-mcp-server?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/zfile-mcp-server?logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
[![License](https://img.shields.io/github/license/neosun100/zfile-mcp-server)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/neosun100/zfile-mcp-server?style=social)](https://github.com/neosun100/zfile-mcp-server)

A Model Context Protocol (MCP) server that enables AI assistants to interact with [ZFile](https://github.com/zfile-dev/zfile) - a powerful online file management system.

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
- **Server**: Stores ZFile credentials via environment variables
- **Security**: ZFile credentials never exposed to clients

## Features

- 📁 **List Files** - Browse directories in ZFile
- ⬆️ **Upload Files** - Upload files with automatic direct link generation
- 🔗 **Direct Links** - Generate permanent direct download links
- 🔗 **Short Links** - Generate temporary short links (31 days)
- 📤 **Large File Support** - Get upload URLs for direct large file uploads
- 🔐 **Secure** - Auto-generated access token, credentials stored server-side

## Quick Start

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
docker logs zfile-mcp | grep ACCESS_TOKEN
```

## Installation

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

```bash
docker compose up -d
```

### Option 3: Build from Source

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server
docker build -t zfile-mcp-server .
docker run -d --name zfile-mcp -p 8092:8092 \
  -e ZFILE_URL=https://your-zfile.com \
  -e ZFILE_USER=admin \
  -e ZFILE_PASS=password \
  -v ./data:/data \
  zfile-mcp-server
```

## Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `ZFILE_URL` | ✅ | ZFile server URL | - |
| `ZFILE_USER` | ✅ | ZFile username | - |
| `ZFILE_PASS` | ✅ | ZFile password | - |
| `ZFILE_STORAGE_KEY` | ❌ | Storage source key | `1` |
| `ACCESS_TOKEN` | ❌ | Custom access token | Auto-generated |

### MCP Client Configuration

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

### Nginx Reverse Proxy (Optional)

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

## Available Tools

| Tool | Description | Use Case |
|------|-------------|----------|
| `zfile_list` | List files in a directory | Browse files |
| `zfile_upload` | Upload file (base64) with auto direct link | Small files (<5MB) |
| `zfile_get_upload_url` | Get direct upload URL | Large files |
| `zfile_direct_link` | Generate permanent direct link | Permanent sharing |
| `zfile_short_link` | Generate 31-day short link | Temporary sharing |

### Usage Examples

**List files:**
```
List all files in /documents
```

**Upload and get link:**
```
Upload this file to ZFile and give me the direct link
```

**Generate direct link:**
```
Generate a direct link for /report.pdf
```

## Tech Stack

- **Runtime**: Python 3.11
- **Framework**: FastAPI + Uvicorn
- **Protocol**: MCP (Model Context Protocol) over SSE
- **HTTP Client**: httpx
- **Container**: Docker

## Project Structure

```
zfile-mcp-server/
├── server.py           # Main MCP server
├── Dockerfile          # Docker image definition
├── docker-compose.yml  # Docker Compose config
├── README.md           # English documentation
├── README_CN.md        # 简体中文文档
├── README_TW.md        # 繁體中文文檔
├── README_JP.md        # 日本語ドキュメント
├── CHANGELOG.md        # Version history
├── LICENSE             # MIT License
└── .gitignore          # Git ignore rules
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/zfile-mcp-server&type=Date)](https://star-history.com/#neosun100/zfile-mcp-server)

## 📱 Follow

![WeChat](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
