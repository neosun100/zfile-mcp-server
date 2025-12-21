[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# ZFile MCP Server

[![Docker Hub](https://img.shields.io/docker/v/neosun/zfile-mcp-server?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/zfile-mcp-server?logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
[![License](https://img.shields.io/github/license/neosun100/zfile-mcp-server)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/neosun100/zfile-mcp-server?style=social)](https://github.com/neosun100/zfile-mcp-server)

一个 Model Context Protocol (MCP) 服务器，让 AI 助手能够与 [ZFile](https://github.com/zfile-dev/zfile) 在线文件管理系统交互。

## 架构

```
┌─────────────────────────┐         ┌─────────────────────────┐         ┌─────────┐
│  MCP 客户端 (Kiro)       │  SSE    │  MCP 服务器 (Docker)     │  API    │  ZFile  │
│  ┌───────────────────┐  │ ──────► │  ┌─────────────────┐    │ ──────► │         │
│  │ 仅存储 ACCESS_TOKEN│  │  Token  │  │ ZFile 账号密码   │    │         │         │
│  └───────────────────┘  │         │  │ 存储在这里       │    │         │         │
└─────────────────────────┘         │  └─────────────────┘    │         └─────────┘
                                    └─────────────────────────┘
```

- **客户端**: 仅存储 ACCESS_TOKEN（用于 MCP 认证）
- **服务端**: 通过环境变量存储 ZFile 账号密码
- **安全性**: ZFile 凭据永远不会暴露给客户端

## 功能特性

- 📁 **文件列表** - 浏览 ZFile 目录
- ⬆️ **文件上传** - 上传文件并自动生成直链
- 🔗 **永久直链** - 生成永久下载直链
- 🔗 **临时短链** - 生成 31 天有效期短链
- 📤 **大文件支持** - 获取上传 URL 直接上传大文件
- 🔐 **安全可靠** - 自动生成访问令牌，凭据仅存储在服务端

## 快速开始

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
docker logs zfile-mcp | grep ACCESS_TOKEN
```

## 安装部署

### 方式一：Docker Hub（推荐）

```bash
docker run -d \
  --name zfile-mcp \
  -p 8092:8092 \
  -e ZFILE_URL=https://你的ZFile地址 \
  -e ZFILE_USER=用户名 \
  -e ZFILE_PASS=密码 \
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
      - ZFILE_URL=https://你的ZFile地址
      - ZFILE_USER=用户名
      - ZFILE_PASS=密码
      - ZFILE_STORAGE_KEY=1
    volumes:
      - ./data:/data
```

```bash
docker compose up -d
```

### 方式三：从源码构建

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

## 配置说明

### 环境变量

| 变量 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| `ZFILE_URL` | ✅ | ZFile 服务器地址 | - |
| `ZFILE_USER` | ✅ | ZFile 用户名 | - |
| `ZFILE_PASS` | ✅ | ZFile 密码 | - |
| `ZFILE_STORAGE_KEY` | ❌ | 存储源 Key | `1` |
| `ACCESS_TOKEN` | ❌ | 自定义访问令牌 | 自动生成 |

### MCP 客户端配置

在 `~/.kiro/settings/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "zfile": {
      "type": "sse",
      "url": "https://你的服务器/mcp/sse?token=你的ACCESS_TOKEN",
      "headers": {},
      "autoApprove": ["*"],
      "disabled": false
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

## 可用工具

| 工具 | 描述 | 适用场景 |
|------|------|----------|
| `zfile_list` | 列出目录文件 | 浏览文件 |
| `zfile_upload` | 上传文件(base64)并返回直链 | 小文件 (<5MB) |
| `zfile_get_upload_url` | 获取直传 URL | 大文件上传 |
| `zfile_direct_link` | 生成永久直链 | 永久分享 |
| `zfile_short_link` | 生成 31 天短链 | 临时分享 |

### 使用示例

**列出文件：**
```
列出 /documents 目录的所有文件
```

**上传并获取链接：**
```
把这个文件上传到 ZFile 并给我直链
```

**生成直链：**
```
给 /report.pdf 生成一个直链
```

## 技术栈

- **运行时**: Python 3.11
- **框架**: FastAPI + Uvicorn
- **协议**: MCP (Model Context Protocol) over SSE
- **HTTP 客户端**: httpx
- **容器**: Docker

## 项目结构

```
zfile-mcp-server/
├── server.py           # MCP 服务器主程序
├── Dockerfile          # Docker 镜像定义
├── docker-compose.yml  # Docker Compose 配置
├── README.md           # 英文文档
├── README_CN.md        # 简体中文文档
├── README_TW.md        # 繁體中文文檔
├── README_JP.md        # 日本語ドキュメント
├── CHANGELOG.md        # 版本历史
├── LICENSE             # MIT 许可证
└── .gitignore          # Git 忽略规则
```

## 贡献指南

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

## 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本历史。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/zfile-mcp-server&type=Date)](https://star-history.com/#neosun100/zfile-mcp-server)

## 📱 关注公众号

![公众号](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
