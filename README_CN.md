[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# ZFile MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

> 一个基于 Model Context Protocol (MCP) 的服务器，让 AI 助手能够与 ZFile 交互 - 无缝上传文件并生成分享链接。

## ✨ 功能特性

- 🔗 **基于 SSE 的 MCP 服务器** - 无需本地依赖
- 📁 **文件列表** - 浏览 ZFile 存储中的文件
- 🔗 **直链生成** - 创建永久直链
- ⏱️ **短链生成** - 创建有时效的短链接
- 🐳 **Docker 就绪** - 使用 Docker Compose 轻松部署
- 🔒 **安全设计** - 凭据存储在客户端，通过 Header 传递

## 🔐 安全架构

```
┌─────────────────────────┐         ┌─────────────────┐         ┌─────────┐
│  MCP 客户端 (Kiro)       │  SSE    │  MCP 服务器      │  API    │  ZFile  │
│  ┌───────────────────┐  │ ──────► │  (无状态)        │ ──────► │         │
│  │ 凭据存储在这里     │  │ Headers │  不存储任何凭据   │         │         │
│  └───────────────────┘  │         │                 │         │         │
└─────────────────────────┘         └─────────────────┘         └─────────┘
```

**凭据存储在你的 MCP 客户端配置中，而不是服务器上。** 服务器是无状态的，只负责转发已认证的请求。

## 🚀 快速开始

### 1. 部署服务器

```bash
# 克隆仓库
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server

# 启动服务
docker compose up -d
```

### 2. 配置 MCP 客户端

在你的 MCP 客户端配置中添加（如 `~/.kiro/settings/mcp.json`）：

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

## 📦 安装部署

### 前置条件

- Docker & Docker Compose (v2.0+)
- 一个运行中的 [ZFile](https://github.com/zfile-dev/zfile) 实例
- （可选）Nginx 用于 HTTPS 反向代理

### Docker 部署

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server
docker compose up -d

# 验证
curl http://localhost:8092/health
# {"status":"ok"}
```

### 直接运行（开发环境）

```bash
pip install fastapi uvicorn httpx
python server.py
```

## ⚙️ 配置说明

### MCP 客户端 Headers

| Header | 必填 | 说明 |
|--------|------|------|
| `X-ZFile-URL` | ✅ | ZFile 服务器地址 |
| `X-ZFile-User` | ✅ | ZFile 登录用户名 |
| `X-ZFile-Pass` | ✅ | ZFile 登录密码 |
| `X-ZFile-Storage-Key` | ❌ | 存储源 Key（默认：`1`） |

### Nginx 反向代理（推荐用于 HTTPS）

⚠️ **重要提示**：必须转发 `X-ZFile-*` headers 到后端服务器。如果缺少这些 headers，认证将失败并返回 401 Unauthorized。

```nginx
location /mcp/ {
    proxy_pass http://127.0.0.1:8092/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # 关键：转发认证 headers
    proxy_set_header X-ZFile-URL $http_x_zfile_url;
    proxy_set_header X-ZFile-User $http_x_zfile_user;
    proxy_set_header X-ZFile-Pass $http_x_zfile_pass;
    proxy_set_header X-ZFile-Storage-Key $http_x_zfile_storage_key;
    
    # SSE 特定设置
    proxy_set_header Connection "";
    proxy_buffering off;
    proxy_cache off;
    chunked_transfer_encoding off;
}
```

**Header 转发说明：**
| Nginx 变量 | 来源 Header | 说明 |
|------------|-------------|------|
| `$http_x_zfile_url` | `X-ZFile-URL` | ZFile 服务器地址 |
| `$http_x_zfile_user` | `X-ZFile-User` | 登录用户名 |
| `$http_x_zfile_pass` | `X-ZFile-Pass` | 登录密码 |
| `$http_x_zfile_storage_key` | `X-ZFile-Storage-Key` | 存储源 Key |

## 📖 使用示例

### 可用工具

| 工具 | 说明 |
|------|------|
| `zfile_list` | 列出目录中的文件 |
| `zfile_direct_link` | 生成永久直链 |
| `zfile_short_link` | 生成短链（31天有效） |

### 示例

在 AI 助手中：

```
"列出 ZFile 根目录的文件"
→ 调用 zfile_list(path="/")

"给 /document.pdf 生成直链"
→ 调用 zfile_direct_link(file_path="/document.pdf")
→ 返回: https://your-zfile.com/directlink/1/document.pdf

"给 /image.png 创建短链"
→ 调用 zfile_short_link(file_path="/image.png")
→ 返回: https://your-zfile.com/s/AbCdEf
```

## 🏗️ 项目结构

```
zfile-mcp-server/
├── server.py           # MCP SSE 服务器（无状态）
├── Dockerfile          # Docker 构建文件
├── docker-compose.yml  # Docker Compose 配置
├── .gitignore
├── LICENSE
├── CHANGELOG.md
└── README.md
```

## 🛠️ 技术栈

- **Python 3.11+**
- **FastAPI** - Web 框架
- **Uvicorn** - ASGI 服务器
- **httpx** - HTTP 客户端
- **Docker** - 容器化

## 🤝 贡献指南

欢迎贡献！请随时提交 Pull Request。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [ZFile](https://github.com/zfile-dev/zfile) - 优秀的文件管理系统
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP 协议规范

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/zfile-mcp-server&type=Date)](https://star-history.com/#neosun100/zfile-mcp-server)

## 📱 关注公众号

![公众号](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
