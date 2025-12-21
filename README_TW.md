[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# ZFile MCP Server

[![Docker Hub](https://img.shields.io/docker/v/neosun/zfile-mcp-server?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/zfile-mcp-server?logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
[![License](https://img.shields.io/github/license/neosun100/zfile-mcp-server)](LICENSE)

MCP 伺服器，讓 AI 助手能夠與 [ZFile](https://github.com/zfile-dev/zfile) 網盤系統互動。

## 架構

```
┌─────────────────────────┐         ┌─────────────────────────┐         ┌─────────┐
│  MCP 用戶端 (Kiro)       │  SSE    │  MCP 伺服器 (Docker)     │  API    │  ZFile  │
│  ┌───────────────────┐  │ ──────► │  ┌─────────────────┐    │ ──────► │         │
│  │ 僅存 ACCESS_TOKEN  │  │  Token  │  │ ZFile 憑據       │   │         │         │
│  └───────────────────┘  │         │  │ 儲存在這裡        │   │         │         │
└─────────────────────────┘         │  └─────────────────┘    │         └─────────┘
                                    └─────────────────────────┘
```

## 功能

- 📁 **檔案列表** - 瀏覽 ZFile 目錄
- 📤 **上傳檔案** - 取得上傳 URL（無 base64，節省上下文 token）
- 📤 **批次上傳** - 一次取得多個上傳 URL
- 🔗 **直連生成** - 生成永久直連（單個或批次）
- 🔗 **短連生成** - 生成 31 天有效短連
- 🔐 **安全** - 自動生成存取權杖，憑據儲存在伺服端

## 快速開始

```bash
docker run -d --name zfile-mcp -p 8092:8092 \
  -e ZFILE_URL=https://your-zfile.com \
  -e ZFILE_USER=admin \
  -e ZFILE_PASS=password \
  -v ./data:/data \
  neosun/zfile-mcp-server:latest
```

取得 ACCESS_TOKEN:
```bash
docker logs zfile-mcp | grep ACCESS_TOKEN
```

## 配置

### 環境變數

| 變數 | 必需 | 說明 | 預設值 |
|------|------|------|--------|
| `ZFILE_URL` | ✅ | ZFile 伺服器位址 | - |
| `ZFILE_USER` | ✅ | ZFile 使用者名稱 | - |
| `ZFILE_PASS` | ✅ | ZFile 密碼 | - |
| `ZFILE_STORAGE_KEY` | ❌ | 儲存源 Key | `1` |
| `ACCESS_TOKEN` | ❌ | 自訂存取權杖 | 自動生成 |

### MCP 用戶端配置

新增至 `~/.kiro/settings/mcp.json`:

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

| 工具 | 說明 |
|------|------|
| `zfile_list` | 列出目錄檔案 |
| `zfile_upload` | 取得單個檔案上傳 URL |
| `zfile_batch_upload` | 批次取得上傳 URL |
| `zfile_direct_link` | 生成單個檔案永久直連 |
| `zfile_direct_links` | 批次生成永久直連 |
| `zfile_short_link` | 生成 31 天短連 |

### 為什麼用 URL 上傳？

Base64 上傳會消耗上下文 token：
- 1MB 檔案 → ~35萬 tokens
- 5MB 檔案 → ~175萬 tokens（超出大多數上下文限制！）

URL 上傳：**0 tokens** - 用戶端直接上傳到 ZFile。

## 授權

MIT License - 見 [LICENSE](LICENSE)
