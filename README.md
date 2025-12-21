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
- 📤 **Upload Files** - Get upload URLs (no base64, saves context tokens)
- 📤 **Batch Upload** - Get multiple upload URLs at once
- 🔗 **Direct Links** - Generate permanent direct download links (single or batch)
- 🔗 **Short Links** - Generate temporary short links (31 days)
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

## Available Tools

| Tool | Description |
|------|-------------|
| `zfile_list` | List files in a directory |
| `zfile_upload` | Get upload URL for a file (returns URL + direct link) |
| `zfile_batch_upload` | Get upload URLs for multiple files |
| `zfile_direct_link` | Generate permanent direct link for a file |
| `zfile_direct_links` | Generate direct links for multiple files |
| `zfile_short_link` | Generate 31-day short link |

### Why URL-based Upload?

Base64 upload consumes context tokens:
- 1MB file → ~350K tokens
- 5MB file → ~1.75M tokens (exceeds most context limits!)

URL-based upload: **0 tokens** - client uploads directly to ZFile.

## Nginx Reverse Proxy

```nginx
location /mcp/ {
    proxy_pass http://127.0.0.1:8092/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
    proxy_buffering off;
    proxy_cache off;
}
```

## License

MIT License - see [LICENSE](LICENSE)

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/zfile-mcp-server&type=Date)](https://star-history.com/#neosun100/zfile-mcp-server)
