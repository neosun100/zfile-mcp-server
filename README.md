[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# ZFile MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

> A Model Context Protocol (MCP) server that enables AI assistants to interact with ZFile - upload files and generate shareable links seamlessly.

## ✨ Features

- 🔗 **SSE-based MCP Server** - No local dependencies required
- 📁 **File Listing** - Browse files in your ZFile storage
- 🔗 **Direct Link Generation** - Create permanent direct links
- ⏱️ **Short Link Generation** - Create time-limited short links
- 🐳 **Docker Ready** - Easy deployment with Docker Compose
- 🔒 **Secure** - Credentials stored on client side, passed via headers

## 🔐 Security Design

```
┌─────────────────────────┐         ┌─────────────────┐         ┌─────────┐
│  MCP Client (Kiro)      │  SSE    │  MCP Server     │  API    │  ZFile  │
│  ┌───────────────────┐  │ ──────► │  (Stateless)    │ ──────► │         │
│  │ Credentials here  │  │ Headers │  No credentials │         │         │
│  └───────────────────┘  │         │  stored here    │         │         │
└─────────────────────────┘         └─────────────────┘         └─────────┘
```

**Credentials are stored in your MCP client configuration, NOT on the server.** The server is stateless and only forwards authenticated requests.

## 🚀 Quick Start

### 1. Deploy the Server

```bash
# Clone the repository
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server

# Start the server
docker compose up -d
```

### 2. Configure MCP Client

Add to your MCP client configuration (e.g., `~/.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "zfile": {
      "type": "sse",
      "url": "https://your-mcp-server.com/sse",
      "headers": {
        "X-ZFile-URL": "https://your-zfile-server.com",
        "X-ZFile-User": "your_username",
        "X-ZFile-Pass": "your_password",
        "X-ZFile-Storage-Key": "1"
      },
      "autoApprove": ["*"]
    }
  }
}
```

## 📦 Installation

### Prerequisites

- Docker & Docker Compose (v2.0+)
- A running [ZFile](https://github.com/zfile-dev/zfile) instance
- (Optional) Nginx for reverse proxy with HTTPS

### Docker Deployment

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server
docker compose up -d

# Verify
curl http://localhost:8092/health
# {"status":"ok"}
```

### Direct Run (Development)

```bash
pip install fastapi uvicorn httpx
python server.py
```

## ⚙️ Configuration

### MCP Client Headers

| Header | Required | Description |
|--------|----------|-------------|
| `X-ZFile-URL` | ✅ | Your ZFile server URL |
| `X-ZFile-User` | ✅ | ZFile login username |
| `X-ZFile-Pass` | ✅ | ZFile login password |
| `X-ZFile-Storage-Key` | ❌ | Storage source key (default: `1`) |

### Nginx Reverse Proxy (Recommended for HTTPS)

```nginx
location /mcp/ {
    proxy_pass http://127.0.0.1:8092/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-ZFile-URL $http_x_zfile_url;
    proxy_set_header X-ZFile-User $http_x_zfile_user;
    proxy_set_header X-ZFile-Pass $http_x_zfile_pass;
    proxy_set_header X-ZFile-Storage-Key $http_x_zfile_storage_key;
    proxy_set_header Connection "";
    proxy_buffering off;
    proxy_cache off;
    chunked_transfer_encoding off;
}
```

## 📖 Usage

### Available Tools

| Tool | Description |
|------|-------------|
| `zfile_list` | List files in a directory |
| `zfile_direct_link` | Generate a permanent direct link |
| `zfile_short_link` | Generate a short link (31 days) |

### Examples

In your AI assistant:

```
"List files in ZFile root directory"
→ Calls zfile_list(path="/")

"Generate a direct link for /document.pdf"
→ Calls zfile_direct_link(file_path="/document.pdf")
→ Returns: https://your-zfile.com/directlink/1/document.pdf

"Create a short link for /image.png"
→ Calls zfile_short_link(file_path="/image.png")
→ Returns: https://your-zfile.com/s/AbCdEf
```

## 🏗️ Project Structure

```
zfile-mcp-server/
├── server.py           # Main MCP SSE server (stateless)
├── Dockerfile          # Docker build file
├── docker-compose.yml  # Docker Compose config
├── .gitignore
├── LICENSE
├── CHANGELOG.md
└── README.md
```

## 🛠️ Tech Stack

- **Python 3.11+**
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **httpx** - HTTP client
- **Docker** - Containerization

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [ZFile](https://github.com/zfile-dev/zfile) - The excellent file management system
- [Model Context Protocol](https://modelcontextprotocol.io/) - The MCP specification

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/zfile-mcp-server&type=Date)](https://star-history.com/#neosun100/zfile-mcp-server)

## 📱 Follow Me

![WeChat](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
