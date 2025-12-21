[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# ZFile MCP Server

[![Docker Hub](https://img.shields.io/docker/v/neosun/zfile-mcp-server?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/zfile-mcp-server?logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
[![License](https://img.shields.io/github/license/neosun100/zfile-mcp-server)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/neosun100/zfile-mcp-server?style=social)](https://github.com/neosun100/zfile-mcp-server)

一個 Model Context Protocol (MCP) 伺服器，讓 AI 助手能夠與 [ZFile](https://github.com/zfile-dev/zfile) 線上檔案管理系統互動。

## 架構

```
┌─────────────────────────┐         ┌─────────────────────────┐         ┌─────────┐
│  MCP 客戶端 (Kiro)       │  SSE    │  MCP 伺服器 (Docker)     │  API    │  ZFile  │
│  ┌───────────────────┐  │ ──────► │  ┌─────────────────┐    │ ──────► │         │
│  │ 僅存儲 ACCESS_TOKEN│  │  Token  │  │ ZFile 帳號密碼   │    │         │         │
│  └───────────────────┘  │         │  │ 存儲在這裡       │    │         │         │
└─────────────────────────┘         │  └─────────────────┘    │         └─────────┘
                                    └─────────────────────────┘
```

- **客戶端**: 僅存儲 ACCESS_TOKEN（用於 MCP 認證）
- **伺服器端**: 通過環境變數存儲 ZFile 帳號密碼
- **安全性**: ZFile 憑據永遠不會暴露給客戶端

## 功能特性

- 📁 **檔案列表** - 瀏覽 ZFile 目錄
- ⬆️ **檔案上傳** - 上傳檔案並自動生成直連
- 🔗 **永久直連** - 生成永久下載直連
- 🔗 **臨時短連** - 生成 31 天有效期短連
- 📤 **大檔案支援** - 獲取上傳 URL 直接上傳大檔案
- 🔐 **安全可靠** - 自動生成存取令牌，憑據僅存儲在伺服器端

## 快速開始

```bash
docker run -d --name zfile-mcp -p 8092:8092 \
  -e ZFILE_URL=https://your-zfile.com \
  -e ZFILE_USER=admin \
  -e ZFILE_PASS=password \
  -v ./data:/data \
  neosun/zfile-mcp-server:latest
```

獲取 ACCESS_TOKEN：
```bash
docker logs zfile-mcp | grep ACCESS_TOKEN
```

## 安裝部署

### 方式一：Docker Hub（推薦）

```bash
docker run -d \
  --name zfile-mcp \
  -p 8092:8092 \
  -e ZFILE_URL=https://你的ZFile地址 \
  -e ZFILE_USER=使用者名稱 \
  -e ZFILE_PASS=密碼 \
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
      - ZFILE_URL=https://你的ZFile地址
      - ZFILE_USER=使用者名稱
      - ZFILE_PASS=密碼
      - ZFILE_STORAGE_KEY=1
    volumes:
      - ./data:/data
```

```bash
docker compose up -d
```

### 方式三：從原始碼建構

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

## 配置說明

### 環境變數

| 變數 | 必填 | 說明 | 預設值 |
|------|------|------|--------|
| `ZFILE_URL` | ✅ | ZFile 伺服器地址 | - |
| `ZFILE_USER` | ✅ | ZFile 使用者名稱 | - |
| `ZFILE_PASS` | ✅ | ZFile 密碼 | - |
| `ZFILE_STORAGE_KEY` | ❌ | 儲存源 Key | `1` |
| `ACCESS_TOKEN` | ❌ | 自訂存取令牌 | 自動生成 |

### MCP 客戶端配置

在 `~/.kiro/settings/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "zfile": {
      "type": "sse",
      "url": "https://你的伺服器/mcp/sse?token=你的ACCESS_TOKEN",
      "headers": {},
      "autoApprove": ["*"],
      "disabled": false
    }
  }
}
```

### Nginx 反向代理（可選）

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

| 工具 | 描述 | 適用場景 |
|------|------|----------|
| `zfile_list` | 列出目錄檔案 | 瀏覽檔案 |
| `zfile_upload` | 上傳檔案(base64)並返回直連 | 小檔案 (<5MB) |
| `zfile_get_upload_url` | 獲取直傳 URL | 大檔案上傳 |
| `zfile_direct_link` | 生成永久直連 | 永久分享 |
| `zfile_short_link` | 生成 31 天短連 | 臨時分享 |

### 使用範例

**列出檔案：**
```
列出 /documents 目錄的所有檔案
```

**上傳並獲取連結：**
```
把這個檔案上傳到 ZFile 並給我直連
```

**生成直連：**
```
給 /report.pdf 生成一個直連
```

## 技術棧

- **執行環境**: Python 3.11
- **框架**: FastAPI + Uvicorn
- **協議**: MCP (Model Context Protocol) over SSE
- **HTTP 客戶端**: httpx
- **容器**: Docker

## 專案結構

```
zfile-mcp-server/
├── server.py           # MCP 伺服器主程式
├── Dockerfile          # Docker 映像定義
├── docker-compose.yml  # Docker Compose 配置
├── README.md           # 英文文檔
├── README_CN.md        # 简体中文文档
├── README_TW.md        # 繁體中文文檔
├── README_JP.md        # 日本語ドキュメント
├── CHANGELOG.md        # 版本歷史
├── LICENSE             # MIT 授權條款
└── .gitignore          # Git 忽略規則
```

## 貢獻指南

歡迎貢獻！請隨時提交 Pull Request。

1. Fork 本倉庫
2. 建立特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 更新日誌

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本歷史。

## 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案。

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/zfile-mcp-server&type=Date)](https://star-history.com/#neosun100/zfile-mcp-server)

## 📱 關注公眾號

![公眾號](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
