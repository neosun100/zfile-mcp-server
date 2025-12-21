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

- 📁 **檔案列表** - 瀏覽 ZFile 目錄
- 📤 **上傳檔案** - 取得上傳 URL（無 base64，節省上下文 token）
- 📤 **批次上傳** - 一次取得多個上傳 URL
- 🔗 **直連生成** - 生成永久直連（單個或批次）
- 🔗 **短連生成** - 生成 31 天有效短連
- 🔐 **安全** - 自動生成存取權杖，憑據儲存在伺服端

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
- 用戶端僅儲存 `ACCESS_TOKEN`（用於 MCP 認證）
- 伺服端透過環境變數儲存 ZFile 憑據
- ZFile 憑據永不暴露給用戶端

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
    volumes:
      - ./data:/data
```

```bash
docker compose up -d
```

### 方式三：原始碼執行

**環境要求：**
- Python 3.11+
- pip

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server

# 安裝依賴
pip install fastapi uvicorn httpx

# 設定環境變數
export ZFILE_URL=https://your-zfile.com
export ZFILE_USER=admin
export ZFILE_PASS=password

# 執行
python server.py
```

## ⚙️ 配置說明

### 環境變數

| 變數 | 必需 | 說明 | 預設值 |
|------|------|------|--------|
| `ZFILE_URL` | ✅ | ZFile 伺服器位址 | - |
| `ZFILE_USER` | ✅ | ZFile 管理員使用者名稱 | - |
| `ZFILE_PASS` | ✅ | ZFile 管理員密碼 | - |
| `ZFILE_STORAGE_KEY` | ❌ | 儲存源 Key | `1` |
| `ACCESS_TOKEN` | ❌ | 自訂存取權杖 | 自動生成 |

### MCP 用戶端配置

#### Kiro CLI

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

## 🛠️ 可用工具

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

## 📁 專案結構

```
zfile-mcp-server/
├── server.py           # MCP 伺服器主程式
├── Dockerfile          # Docker 映像定義
├── docker-compose.yml  # Docker Compose 配置
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
- **協定：** MCP (Model Context Protocol) over SSE
- **HTTP 用戶端：** httpx
- **容器：** Docker

## 🤝 貢獻指南

歡迎貢獻！請隨時提交 Pull Request。

1. Fork 本倉庫
2. 建立特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 📋 更新日誌

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本歷史。

## 📄 授權

本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 檔案。

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/zfile-mcp-server&type=Date)](https://star-history.com/#neosun100/zfile-mcp-server)

## 📱 關注公眾號

![公眾號](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
