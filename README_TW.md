[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

<div align="center">
  <h1>🗂️ ZFile MCP Server</h1>
  <p>讓 AI 助手能夠與 ZFile 網盤系統互動的 MCP 伺服器</p>

  [![Docker Hub](https://img.shields.io/docker/v/neosun/zfile-mcp-server?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
  [![Docker Pulls](https://img.shields.io/docker/pulls/neosun/zfile-mcp-server?logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
  [![License](https://img.shields.io/github/license/neosun100/zfile-mcp-server)](LICENSE)
  [![GitHub Stars](https://img.shields.io/github/stars/neosun100/zfile-mcp-server?style=social)](https://github.com/neosun100/zfile-mcp-server)
</div>

---

## ✨ 功能特性

- 📁 **檔案列表** — 瀏覽 ZFile 目錄
- 📤 **上傳檔案** — 取得上傳 URL（無 base64，節省上下文 token）
- 📤 **批次上傳** — 一次取得多個上傳 URL
- 📦 **分塊上傳** — 大檔案分塊上傳（Cloudflare 友好，自動合併）
- 🔗 **直連生成** — 生成永久直連（單個或批次）
- 🔗 **短連生成** — 生成 31 天有效短連
- 🔐 **安全** — 自動生成存取權杖，憑據儲存在伺服端
- 🌐 **多協定** — SSE（Kiro、Claude Desktop）+ Streamable HTTP（Gemini CLI）

## 🏗️ 架構設計

```
┌─────────────────────────┐         ┌─────────────────────────┐         ┌─────────┐
│  MCP 用戶端 (Kiro/Claude) │  SSE    │  MCP 伺服器 (Docker)     │  API    │  ZFile  │
│  ┌───────────────────┐  │ ──────► │  ┌─────────────────┐    │ ──────► │         │
│  │ 僅存 ACCESS_TOKEN  │  │  Token  │  │ ZFile 憑據       │   │         │         │
│  └───────────────────┘  │         │  │ 儲存在這裡        │   │         │         │
└─────────────────────────┘         │  └─────────────────┘    │         └─────────┘
                                    └─────────────────────────┘
```

**安全模型：**
- 🔒 用戶端僅儲存 `ACCESS_TOKEN`（用於 MCP 認證）
- 🔒 伺服端透過環境變數儲存 ZFile 憑據
- 🔒 ZFile 憑據永不暴露給用戶端

## 🚀 快速開始

```bash
docker run -d --name zfile-mcp -p 8092:8092 \
  -e ZFILE_URL=https://your-zfile.com \
  -e ZFILE_USER=admin \
  -e ZFILE_PASS=password \
  -v ./data:/data \
  neosun/zfile-mcp-server:latest
```

取得 ACCESS_TOKEN：
```bash
docker logs zfile-mcp 2>&1 | grep ACCESS_TOKEN
```

## 📦 安裝部署

### 方式一：Docker Hub（推薦）

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

建立 `docker-compose.yml`：

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
      # - ACCESS_TOKEN=            # 不設定則自動生成
      # - CHUNK_SIZE_MB=10         # 分塊大小，預設 10MB
      # - MCP_SERVER_URL=          # 可選：分塊上傳命令中的外部 URL
    volumes:
      - ./data:/data
```

```bash
docker compose up -d
```

### 方式三：原始碼執行

**環境要求：** Python 3.11+

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server
pip install -r requirements.txt

export ZFILE_URL=https://your-zfile.com
export ZFILE_USER=admin
export ZFILE_PASS=password

python server.py
```

## ⚙️ 配置說明

### 環境變數

| 變數 | 必需 | 說明 | 預設值 |
|------|------|------|--------|
| `ZFILE_URL` | ✅ | ZFile 伺服器位址 | — |
| `ZFILE_USER` | ✅ | ZFile 管理員使用者名稱 | — |
| `ZFILE_PASS` | ✅ | ZFile 管理員密碼 | — |
| `ZFILE_STORAGE_KEY` | ❌ | 儲存源 Key | `1` |
| `ACCESS_TOKEN` | ❌ | 自訂存取權杖（不設定則自動生成） | 自動生成 |
| `CHUNK_SIZE_MB` | ❌ | 大檔案分塊大小 | `10` |
| `MCP_SERVER_URL` | ❌ | 分塊上傳命令中的外部 URL（反向代理場景下使用） | 自動偵測 |

> 💡 **提示：** 如果未設定 `MCP_SERVER_URL`，伺服器會從請求標頭（`X-Forwarded-Host`、`X-Forwarded-Proto`）自動偵測外部 URL。在複雜代理環境下建議顯式設定。

### MCP 用戶端配置

#### 🟢 Kiro CLI

新增至 `~/.kiro/settings/mcp.json`：

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

新增至 Claude Desktop 配置（macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`）：

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

Gemini CLI 使用 Streamable HTTP 協定。新增至 `~/.gemini/settings.json`：

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

新增至專案根目錄 `.cursor/mcp.json`：

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

新增至 `~/.codeium/windsurf/mcp_config.json`：

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

### 方案 A：Cloudflare Tunnel（推薦）

Cloudflare Tunnel 提供安全存取，無需暴露連接埠。在 Cloudflare Dashboard 配置：

| 公共主機名 | 服務 |
|-----------|------|
| `zfile.example.com` | `http://localhost:8090` (ZFile) |
| `zfile.example.com/mcp/*` | `http://localhost:8092` (MCP Server) |

> ⚠️ **Cloudflare 逾時：** Cloudflare 有 100s 代理讀取逾時。上傳大檔案時，請使用分塊上傳（`zfile_chunked_upload`），預設 `CHUNK_SIZE_MB=10` 可確保每個分塊在逾時內完成。

### 方案 B：Nginx 反向代理

```nginx
server {
    listen 443 ssl;
    server_name zfile.example.com;

    location /mcp/ {
        proxy_pass http://127.0.0.1:8092/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header Connection '';
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400s;
    }

    location / {
        proxy_pass http://127.0.0.1:8090/;
        proxy_set_header Host $host;
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

| 工具 | 說明 |
|------|------|
| 📁 `zfile_list` | 列出目錄檔案 |
| 📤 `zfile_upload` | 取得單個檔案上傳 URL（< 10MB） |
| 📤 `zfile_batch_upload` | 批次取得上傳 URL |
| 📦 `zfile_chunked_upload` | 初始化大檔案分塊上傳（> 10MB） |
| 📊 `zfile_chunked_upload_status` | 查詢分塊上傳進度 |
| 🔗 `zfile_direct_link` | 生成單個檔案永久直連 |
| 🔗 `zfile_direct_links` | 批次生成永久直連 |
| 🔗 `zfile_short_link` | 生成 31 天短連 |

### 💡 為什麼用 URL 上傳？

Base64 上傳會消耗上下文 token：
- 1MB 檔案 → ~35萬 tokens
- 5MB 檔案 → ~175萬 tokens（超出大多數上下文限制！）

URL 上傳：**0 tokens** — 用戶端直接上傳到 ZFile。

### 📦 分塊上傳流程

適用於 > 10MB 的檔案（尤其在 Cloudflare 代理後）：

```
1. AI 呼叫 zfile_chunked_upload → 取得 upload_id + curl 命令
2. 用戶端將檔案切分為 10MB 分塊
3. 用戶端逐個 POST 分塊到 /upload/chunk 端點
4. 伺服端收齊所有分塊後自動合併
5. 伺服端將合併檔案上傳到 ZFile
6. 回傳直連 ✅
```

> 💡 分塊上傳回傳的 `curl` 命令已包含真實的伺服器 URL 和 token，直接複製執行即可。

## 📁 專案結構

```
zfile-mcp-server/
├── server.py           # MCP 伺服器主程式
├── Dockerfile          # Docker 映像定義
├── docker-compose.yml  # Docker Compose 配置
├── requirements.txt    # Python 依賴
├── .env.example        # 環境變數範本
├── README.md           # English documentation
├── README_CN.md        # 简体中文文档
├── README_TW.md        # 繁體中文文檔
├── README_JP.md        # 日本語ドキュメント
├── CHANGELOG.md        # 版本更新記錄
├── LICENSE             # MIT 授權
└── .gitignore          # Git 忽略規則
```

## 🔧 技術棧

- **執行環境：** Python 3.11
- **框架：** FastAPI + Uvicorn
- **協定：** MCP (Model Context Protocol) — SSE + Streamable HTTP
- **HTTP 用戶端：** httpx
- **容器：** Docker

## 🤝 貢獻指南

歡迎貢獻！請隨時提交 Pull Request。

## 📋 更新日誌

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本歷史。

## 📄 授權

本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 檔案。

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/zfile-mcp-server&type=Date)](https://star-history.com/#neosun100/zfile-mcp-server)

## 📱 關注公眾號

![公眾號](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
