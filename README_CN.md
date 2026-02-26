[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

<div align="center">
  <img src="logo.png" alt="ZFile MCP Server" width="180" />
  <h1>ZFile MCP Server</h1>
  <p>让 AI 助手能够与 ZFile 网盘系统交互的 MCP 服务器</p>

  [![Docker Hub](https://img.shields.io/docker/v/neosun/zfile-mcp-server?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
  [![Docker Pulls](https://img.shields.io/docker/pulls/neosun/zfile-mcp-server?logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
  [![License](https://img.shields.io/github/license/neosun100/zfile-mcp-server)](LICENSE)
  [![GitHub Stars](https://img.shields.io/github/stars/neosun100/zfile-mcp-server?style=social)](https://github.com/neosun100/zfile-mcp-server)
</div>

---

## ✨ 功能特性

- 📁 **文件列表** — 浏览 ZFile 目录
- 📤 **上传文件** — 获取上传 URL（无 base64，节省上下文 token）
- 📤 **批量上传** — 一次获取多个上传 URL
- 📦 **分块上传** — 大文件分块上传（Cloudflare 友好，自动合并）
- 🔗 **直链生成** — 生成永久直链（单个或批量）
- 🔗 **短链生成** — 生成 31 天有效短链
- 🔐 **安全** — 自动生成访问令牌，凭据存储在服务端
- 🌐 **多协议** — SSE（Kiro、Claude Desktop）+ Streamable HTTP（Gemini CLI）

## 🏗️ 架构设计

```
┌─────────────────────────┐         ┌─────────────────────────┐         ┌─────────┐
│  MCP 客户端 (Kiro/Claude) │  SSE    │  MCP 服务器 (Docker)     │  API    │  ZFile  │
│  ┌───────────────────┐  │ ──────► │  ┌─────────────────┐    │ ──────► │         │
│  │ 仅存 ACCESS_TOKEN  │  │  Token  │  │ ZFile 凭据       │   │         │         │
│  └───────────────────┘  │         │  │ 存储在这里        │   │         │         │
└─────────────────────────┘         │  └─────────────────┘    │         └─────────┘
                                    └─────────────────────────┘
```

**安全模型：**
- 🔒 客户端仅存储 `ACCESS_TOKEN`（用于 MCP 认证）
- 🔒 服务端通过环境变量存储 ZFile 凭据
- 🔒 ZFile 凭据永不暴露给客户端

## 🚀 快速开始

```bash
docker run -d --name zfile-mcp -p 8092:8092 \
  -e ZFILE_URL=https://your-zfile.com \
  -e ZFILE_USER=admin \
  -e ZFILE_PASS=password \
  -v ./data:/data \
  neosun/zfile-mcp-server:latest
```

获取 ACCESS_TOKEN：
```bash
docker logs zfile-mcp 2>&1 | grep ACCESS_TOKEN
```

## 📦 安装部署

### 方式一：Docker Hub（推荐）

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

### 方式二：Docker Compose

创建 `docker-compose.yml`：

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
      # - ACCESS_TOKEN=            # 不设置则自动生成
      # - CHUNK_SIZE_MB=10         # 分块大小，默认 10MB
      # - MCP_SERVER_URL=          # 可选：分块上传命令中的外部 URL
    volumes:
      - ./data:/data
```

```bash
docker compose up -d
```

### 方式三：源码运行

**环境要求：** Python 3.11+

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server
pip install -r requirements.txt

export ZFILE_URL=https://your-zfile.com
export ZFILE_USER=admin
export ZFILE_PASS=password

python server.py
```

## ⚙️ 配置说明

### 环境变量

| 变量 | 必需 | 说明 | 默认值 |
|------|------|------|--------|
| `ZFILE_URL` | ✅ | ZFile 服务器地址 | — |
| `ZFILE_USER` | ✅ | ZFile 管理员用户名 | — |
| `ZFILE_PASS` | ✅ | ZFile 管理员密码 | — |
| `ZFILE_STORAGE_KEY` | ❌ | 存储源 Key | `1` |
| `ACCESS_TOKEN` | ❌ | 自定义访问令牌（不设置则自动生成） | 自动生成 |
| `CHUNK_SIZE_MB` | ❌ | 大文件分块大小 | `10` |
| `MCP_SERVER_URL` | ❌ | 分块上传命令中的外部 URL（反向代理场景下使用） | 自动检测 |

> 💡 **提示：** 如果未设置 `MCP_SERVER_URL`，服务器会从请求头（`X-Forwarded-Host`、`X-Forwarded-Proto`）自动检测外部 URL。在复杂代理环境下建议显式设置。

### MCP 客户端配置

#### 🟢 Kiro CLI

添加到 `~/.kiro/settings/mcp.json`：

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

添加到 Claude Desktop 配置（macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`）：

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

Gemini CLI 使用 Streamable HTTP 协议。添加到 `~/.gemini/settings.json`：

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

添加到项目根目录 `.cursor/mcp.json`：

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

添加到 `~/.codeium/windsurf/mcp_config.json`：

```json
{
  "mcpServers": {
    "zfile": {
      "serverUrl": "https://your-server.com/mcp/sse?token=YOUR_ACCESS_TOKEN"
    }
  }
}
```

## 🌐 反向代理配置

### 方案 A：Cloudflare Tunnel（推荐）

Cloudflare Tunnel 提供安全访问，无需暴露端口。在 Cloudflare Dashboard 配置：

| 公共主机名 | 服务 |
|-----------|------|
| `zfile.example.com` | `http://localhost:8090` (ZFile) |
| `zfile.example.com/mcp/*` | `http://localhost:8092` (MCP Server) |

**在 Cloudflare Zero Trust 中配置路径路由：**
1. 进入 **Zero Trust** → **Networks** → **Tunnels**
2. 选择你的隧道 → **Public Hostname**
3. 添加两条记录：
   - Path: `/mcp/*` → Service: `http://localhost:8092`
   - Path: (空) → Service: `http://localhost:8090`

> ⚠️ **Cloudflare 超时：** Cloudflare 有 100s 代理读取超时。上传大文件时，请使用分块上传（`zfile_chunked_upload`），默认 `CHUNK_SIZE_MB=10` 可确保每个分块在超时内完成。

### 方案 B：Nginx 反向代理

```nginx
server {
    listen 443 ssl;
    server_name zfile.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # MCP Server（SSE 需要特殊处理）
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

    # ZFile 主应用
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

### 方案 C：Caddy

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

## 🛠️ 可用工具

| 工具 | 说明 |
|------|------|
| 📁 `zfile_list` | 列出目录文件 |
| 📤 `zfile_upload` | 获取单个文件上传 URL（< 10MB） |
| 📤 `zfile_batch_upload` | 批量获取上传 URL |
| 📦 `zfile_chunked_upload` | 初始化大文件分块上传（> 10MB） |
| 📊 `zfile_chunked_upload_status` | 查询分块上传进度 |
| 🔗 `zfile_direct_link` | 生成单个文件永久直链 |
| 🔗 `zfile_direct_links` | 批量生成永久直链 |
| 🔗 `zfile_short_link` | 生成 31 天短链 |

### 使用示例

**列出文件：**
```
列出 /documents 目录下的所有文件
```

**上传小文件：**
```
我需要上传 app.apk 到 /releases 文件夹
```

**上传大文件（分块）：**
```
上传一个 200MB 的视频文件到 /videos
```

**生成直链：**
```
为 /report.pdf 生成直链
```

### 💡 为什么用 URL 上传（而不是 Base64）？

有些 MCP 服务器会把文件编码成 base64 塞进大模型上下文 — 这会浪费大量 token 和费用：
- 1MB 文件 → 浪费 ~35万 tokens
- 5MB 文件 → 浪费 ~175万 tokens（超出大多数上下文限制！）

**ZFile MCP Server 完全避免了这个问题。** 服务器只返回一个上传 URL 给 AI 客户端，文件通过 `curl` 直接上传到 ZFile，完全不经过大模型。结果：文件上传 **消耗 0 tokens**。

### 📦 分块上传流程

适用于 > 10MB 的文件（尤其在 Cloudflare 代理后）：

```
1. AI 调用 zfile_chunked_upload → 获取 upload_id + curl 命令
2. 客户端将文件切分为 10MB 分块
3. 客户端逐个 POST 分块到 /upload/chunk 端点
4. 服务端收齐所有分块后自动合并
5. 服务端将合并文件上传到 ZFile
6. 返回直链 ✅
```

> 💡 分块上传返回的 `curl` 命令已包含真实的服务器 URL 和 token，直接复制运行即可。

## 📁 项目结构

```
zfile-mcp-server/
├── server.py           # MCP 服务器主程序
├── Dockerfile          # Docker 镜像定义
├── docker-compose.yml  # Docker Compose 配置
├── requirements.txt    # Python 依赖
├── .env.example        # 环境变量模板
├── README.md           # English documentation
├── README_CN.md        # 简体中文文档
├── README_TW.md        # 繁體中文文檔
├── README_JP.md        # 日本語ドキュメント
├── CHANGELOG.md        # 版本更新记录
├── LICENSE             # MIT 许可证
└── .gitignore          # Git 忽略规则
```

## 🔧 技术栈

- **运行时：** Python 3.11
- **框架：** FastAPI + Uvicorn
- **协议：** MCP (Model Context Protocol) — SSE + Streamable HTTP
- **HTTP 客户端：** httpx
- **容器：** Docker

## 🤝 贡献指南

欢迎贡献！请随时提交 Pull Request。

## 📋 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本历史。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/zfile-mcp-server&type=Date)](https://star-history.com/#neosun100/zfile-mcp-server)

## 📱 关注公众号

![公众号](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
