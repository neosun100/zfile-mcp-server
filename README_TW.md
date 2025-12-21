[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# ZFile MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

> 一個基於 Model Context Protocol (MCP) 的伺服器，讓 AI 助手能夠與 ZFile 互動 - 無縫上傳檔案並生成分享連結。

## ✨ 功能特性

- 🔗 **基於 SSE 的 MCP 伺服器** - 無需本地依賴
- 📁 **檔案列表** - 瀏覽 ZFile 儲存中的檔案
- 🔗 **直連生成** - 建立永久直連
- ⏱️ **短連生成** - 建立有時效的短連結
- 🐳 **Docker 就緒** - 使用 Docker Compose 輕鬆部署
- 🔒 **安全設計** - 憑據儲存在客戶端，通過 Header 傳遞

## 🔐 安全架構

```
┌─────────────────────────┐         ┌─────────────────┐         ┌─────────┐
│  MCP 客戶端 (Kiro)       │  SSE    │  MCP 伺服器      │  API    │  ZFile  │
│  ┌───────────────────┐  │ ──────► │  (無狀態)        │ ──────► │         │
│  │ 憑據儲存在這裡     │  │ Headers │  不儲存任何憑據   │         │         │
│  └───────────────────┘  │         │                 │         │         │
└─────────────────────────┘         └─────────────────┘         └─────────┘
```

**憑據儲存在你的 MCP 客戶端配置中，而不是伺服器上。** 伺服器是無狀態的，只負責轉發已認證的請求。

## 🚀 快速開始

### 1. 部署伺服器

```bash
# 克隆倉庫
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server

# 啟動服務
docker compose up -d
```

### 2. 配置 MCP 客戶端

在你的 MCP 客戶端配置中添加（如 `~/.kiro/settings/mcp.json`）：

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

## 📦 安裝部署

### 前置條件

- Docker & Docker Compose (v2.0+)
- 一個運行中的 [ZFile](https://github.com/zfile-dev/zfile) 實例
- （可選）Nginx 用於 HTTPS 反向代理

### Docker 部署

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server
docker compose up -d

# 驗證
curl http://localhost:8092/health
# {"status":"ok"}
```

### 直接運行（開發環境）

```bash
pip install fastapi uvicorn httpx
python server.py
```

## ⚙️ 配置說明

### MCP 客戶端 Headers

| Header | 必填 | 說明 |
|--------|------|------|
| `X-ZFile-URL` | ✅ | ZFile 伺服器地址 |
| `X-ZFile-User` | ✅ | ZFile 登入用戶名 |
| `X-ZFile-Pass` | ✅ | ZFile 登入密碼 |
| `X-ZFile-Storage-Key` | ❌ | 儲存源 Key（預設：`1`） |

### Nginx 反向代理（推薦用於 HTTPS）

⚠️ **重要提示**：必須轉發 `X-ZFile-*` headers 到後端伺服器。如果缺少這些 headers，認證將失敗並返回 401 Unauthorized。

```nginx
location /mcp/ {
    proxy_pass http://127.0.0.1:8092/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # 關鍵：轉發認證 headers
    proxy_set_header X-ZFile-URL $http_x_zfile_url;
    proxy_set_header X-ZFile-User $http_x_zfile_user;
    proxy_set_header X-ZFile-Pass $http_x_zfile_pass;
    proxy_set_header X-ZFile-Storage-Key $http_x_zfile_storage_key;
    
    # SSE 特定設置
    proxy_set_header Connection "";
    proxy_buffering off;
    proxy_cache off;
    chunked_transfer_encoding off;
}
```

**Header 轉發說明：**
| Nginx 變數 | 來源 Header | 說明 |
|------------|-------------|------|
| `$http_x_zfile_url` | `X-ZFile-URL` | ZFile 伺服器地址 |
| `$http_x_zfile_user` | `X-ZFile-User` | 登入用戶名 |
| `$http_x_zfile_pass` | `X-ZFile-Pass` | 登入密碼 |
| `$http_x_zfile_storage_key` | `X-ZFile-Storage-Key` | 儲存源 Key |

## 📖 使用示例

### 可用工具

| 工具 | 說明 |
|------|------|
| `zfile_list` | 列出目錄中的檔案 |
| `zfile_direct_link` | 生成永久直連 |
| `zfile_short_link` | 生成短連（31天有效） |

### 示例

在 AI 助手中：

```
"列出 ZFile 根目錄的檔案"
→ 調用 zfile_list(path="/")

"給 /document.pdf 生成直連"
→ 調用 zfile_direct_link(file_path="/document.pdf")
→ 返回: https://your-zfile.com/directlink/1/document.pdf

"給 /image.png 建立短連"
→ 調用 zfile_short_link(file_path="/image.png")
→ 返回: https://your-zfile.com/s/AbCdEf
```

## 🏗️ 專案結構

```
zfile-mcp-server/
├── server.py           # MCP SSE 伺服器（無狀態）
├── Dockerfile          # Docker 構建檔案
├── docker-compose.yml  # Docker Compose 配置
├── .gitignore
├── LICENSE
├── CHANGELOG.md
└── README.md
```

## 🛠️ 技術棧

- **Python 3.11+**
- **FastAPI** - Web 框架
- **Uvicorn** - ASGI 伺服器
- **httpx** - HTTP 客戶端
- **Docker** - 容器化

## 🤝 貢獻指南

歡迎貢獻！請隨時提交 Pull Request。

## 📄 許可證

本專案採用 MIT 許可證 - 詳見 [LICENSE](LICENSE) 檔案。

## 🙏 致謝

- [ZFile](https://github.com/zfile-dev/zfile) - 優秀的檔案管理系統
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP 協議規範

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/zfile-mcp-server&type=Date)](https://star-history.com/#neosun100/zfile-mcp-server)

## 📱 關注公眾號

![公眾號](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
