[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# ZFile MCP Server

[![Docker Hub](https://img.shields.io/docker/v/neosun/zfile-mcp-server?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/zfile-mcp-server?logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
[![License](https://img.shields.io/github/license/neosun100/zfile-mcp-server)](LICENSE)

MCP 服务器，让 AI 助手能够与 [ZFile](https://github.com/zfile-dev/zfile) 网盘系统交互。

## 架构

```
┌─────────────────────────┐         ┌─────────────────────────┐         ┌─────────┐
│  MCP 客户端 (Kiro)       │  SSE    │  MCP 服务器 (Docker)     │  API    │  ZFile  │
│  ┌───────────────────┐  │ ──────► │  ┌─────────────────┐    │ ──────► │         │
│  │ 仅存 ACCESS_TOKEN  │  │  Token  │  │ ZFile 凭据       │   │         │         │
│  └───────────────────┘  │         │  │ 存储在这里        │   │         │         │
└─────────────────────────┘         │  └─────────────────┘    │         └─────────┘
                                    └─────────────────────────┘
```

- **客户端**: 仅存储 ACCESS_TOKEN（用于 MCP 认证）
- **服务端**: 通过环境变量存储 ZFile 凭据
- **安全性**: ZFile 凭据永不暴露给客户端

## 功能

- 📁 **文件列表** - 浏览 ZFile 目录
- 📤 **上传文件** - 获取上传 URL（无 base64，节省上下文 token）
- 📤 **批量上传** - 一次获取多个上传 URL
- 🔗 **直链生成** - 生成永久直链（单个或批量）
- 🔗 **短链生成** - 生成 31 天有效短链
- 🔐 **安全** - 自动生成访问令牌，凭据存储在服务端

## 快速开始

```bash
docker run -d --name zfile-mcp -p 8092:8092 \
  -e ZFILE_URL=https://your-zfile.com \
  -e ZFILE_USER=admin \
  -e ZFILE_PASS=password \
  -v ./data:/data \
  neosun/zfile-mcp-server:latest
```

获取 ACCESS_TOKEN:
```bash
docker logs zfile-mcp | grep ACCESS_TOKEN
```

## 配置

### 环境变量

| 变量 | 必需 | 说明 | 默认值 |
|------|------|------|--------|
| `ZFILE_URL` | ✅ | ZFile 服务器地址 | - |
| `ZFILE_USER` | ✅ | ZFile 用户名 | - |
| `ZFILE_PASS` | ✅ | ZFile 密码 | - |
| `ZFILE_STORAGE_KEY` | ❌ | 存储源 Key | `1` |
| `ACCESS_TOKEN` | ❌ | 自定义访问令牌 | 自动生成 |

### MCP 客户端配置

添加到 `~/.kiro/settings/mcp.json`:

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

## 可用工具

| 工具 | 说明 |
|------|------|
| `zfile_list` | 列出目录文件 |
| `zfile_upload` | 获取单个文件上传 URL（返回 URL + 直链） |
| `zfile_batch_upload` | 批量获取上传 URL |
| `zfile_direct_link` | 生成单个文件永久直链 |
| `zfile_direct_links` | 批量生成永久直链 |
| `zfile_short_link` | 生成 31 天短链 |

### 为什么用 URL 上传？

Base64 上传会消耗上下文 token：
- 1MB 文件 → ~35万 tokens
- 5MB 文件 → ~175万 tokens（超出大多数上下文限制！）

URL 上传：**0 tokens** - 客户端直接上传到 ZFile。

## 许可证

MIT License - 见 [LICENSE](LICENSE)
