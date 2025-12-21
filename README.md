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
- 🔒 **Secure** - Token-based authentication with ZFile API

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server

# Configure environment
cp .env.example .env
# Edit .env with your ZFile credentials

# Start the server
docker compose up -d
```

### Configure MCP Client

Add to your MCP client configuration (e.g., `~/.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "zfile": {
      "type": "sse",
      "url": "https://your-domain.com/mcp/sse",
      "autoApprove": ["*"]
    }
  }
}
```

## 📦 Installation

### Prerequisites

- Docker & Docker Compose (v2.0+)
- A running [ZFile](https://github.com/zfile-dev/zfile) instance
- (Optional) Nginx for reverse proxy

### Docker Deployment

1. **Clone and configure**

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server
cp .env.example .env
```

2. **Edit `.env` file**

```env
ZFILE_URL=https://your-zfile-domain.com
ZFILE_USER=your_username
ZFILE_PASS=your_password
ZFILE_STORAGE_KEY=1
```

3. **Start the service**

```bash
docker compose up -d
```

4. **Verify**

```bash
curl http://localhost:8092/health
# {"status":"ok"}
```

### Direct Run (Development)

```bash
# Install dependencies
pip install fastapi uvicorn httpx

# Set environment variables
export ZFILE_URL=https://your-zfile-domain.com
export ZFILE_USER=your_username
export ZFILE_PASS=your_password

# Run
python server.py
```

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ZFILE_URL` | ✅ | - | Your ZFile server URL |
| `ZFILE_USER` | ✅ | - | ZFile login username |
| `ZFILE_PASS` | ✅ | - | ZFile login password |
| `ZFILE_STORAGE_KEY` | ❌ | `1` | Storage source key in ZFile |

### Nginx Reverse Proxy (Optional)

```nginx
location /mcp/ {
    proxy_pass http://127.0.0.1:8092/;
    proxy_http_version 1.1;
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
→ Returns: https://your-domain.com/directlink/1/document.pdf

"Create a short link for /image.png"
→ Calls zfile_short_link(file_path="/image.png")
→ Returns: https://your-domain.com/s/AbCdEf
```

## 🏗️ Project Structure

```
zfile-mcp-server/
├── server.py           # Main MCP SSE server
├── Dockerfile          # Docker build file
├── docker-compose.yml  # Docker Compose config
├── .env.example        # Environment template
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

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

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
