[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

<div align="center">
  <h1>🗂️ ZFile MCP Server</h1>
  <p>让 AI 助手能够与 ZFile 网盘系统交互的 MCP 服务器</p>

  [![Docker Hub](https://img.shields.io/docker/v/neosun/zfile-mcp-server?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
  [![Docker Pulls](https://img.shields.io/docker/pulls/neosun/zfile-mcp-server?logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
  [![License](https://img.shields.io/github/license/neosun100/zfile-mcp-server)](LICENSE)
  [![GitHub Stars](https://img.shields.io/github/stars/neosun100/zfile-mcp-server?style=social)](https://github.com/neosun100/zfile-mcp-server)
</div>

---

## ✨ 功能特性

- 📁 **文件列表** - 浏览 ZFile 目录
- 📤 **上传文件** - 获取上传 URL（无 base64，节省上下文 token）
- 📤 **批量上传** - 一次获取多个上传 URL
- 🔗 **直链生成** - 生成永久直链（单个或批量）
- 🔗 **短链生成** - 生成 31 天有效短链
- 🔐 **安全** - 自动生成访问令牌，凭据存储在服务端

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
- 客户端仅存储 `ACCESS_TOKEN`（用于 MCP 认证）
- 服务端通过环境变量存储 ZFile 凭据
- ZFile 凭据永不暴露给客户端

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
    volumes:
      - ./data:/data
```

```bash
docker compose up -d
```

### 方式三：源码运行

**环境要求：**
- Python 3.11+
- pip

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server

# 安装依赖
pip install fastapi uvicorn httpx

# 设置环境变量
export ZFILE_URL=https://your-zfile.com
export ZFILE_USER=admin
export ZFILE_PASS=password

# 运行
python server.py
```

### 方式四：构建 Docker 镜像

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

## ⚙️ 配置说明

### 环境变量

| 变量 | 必需 | 说明 | 默认值 |
|------|------|------|--------|
| `ZFILE_URL` | ✅ | ZFile 服务器地址（如 `https://zfile.example.com`） | - |
| `ZFILE_USER` | ✅ | ZFile 管理员用户名 | - |
| `ZFILE_PASS` | ✅ | ZFile 管理员密码 | - |
| `ZFILE_STORAGE_KEY` | ❌ | 存储源 Key | `1` |
| `ACCESS_TOKEN` | ❌ | 自定义访问令牌（不设置则自动生成） | 自动 |

### MCP 客户端配置

#### Kiro CLI

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

#### Claude Desktop

添加到 Claude Desktop 配置：

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

### Nginx 反向代理（可选）

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

## 🛠️ 可用工具

| 工具 | 说明 |
|------|------|
| `zfile_list` | 列出目录文件 |
| `zfile_upload` | 获取单个文件上传 URL（返回 URL + 直链） |
| `zfile_batch_upload` | 批量获取上传 URL |
| `zfile_direct_link` | 生成单个文件永久直链 |
| `zfile_direct_links` | 批量生成永久直链 |
| `zfile_short_link` | 生成 31 天短链 |

### 使用示例

**列出文件：**
```
列出 /documents 目录下的所有文件
```

**上传文件：**
```
我需要上传 app.apk 到 /releases 文件夹
```

**生成直链：**
```
为 /report.pdf 生成直链
```

**批量操作：**
```
为 /documents 目录下所有 PDF 文件生成直链
```

### 为什么用 URL 上传？

Base64 上传会消耗上下文 token：
- 1MB 文件 → ~35万 tokens
- 5MB 文件 → ~175万 tokens（超出大多数上下文限制！）

URL 上传：**0 tokens** - 客户端直接上传到 ZFile。

## 📁 项目结构

```
zfile-mcp-server/
├── server.py           # MCP 服务器主程序
├── Dockerfile          # Docker 镜像定义
├── docker-compose.yml  # Docker Compose 配置
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
- **协议：** MCP (Model Context Protocol) over SSE
- **HTTP 客户端：** httpx
- **容器：** Docker

## 🤝 贡献指南

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

## 📋 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本历史。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/zfile-mcp-server&type=Date)](https://star-history.com/#neosun100/zfile-mcp-server)

## 📱 关注公众号

![公众号](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
