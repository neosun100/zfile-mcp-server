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
- 🔒 **安全可靠** - 基於 Token 的 ZFile API 認證

## 🚀 快速開始

### 使用 Docker（推薦）

```bash
# 克隆倉庫
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server

# 配置環境變數
cp .env.example .env
# 編輯 .env 填入你的 ZFile 憑據

# 啟動服務
docker compose up -d
```

### 配置 MCP 客戶端

在你的 MCP 客戶端配置中添加（如 `~/.kiro/settings/mcp.json`）：

```json
{
  "mcpServers": {
    "zfile": {
      "type": "sse",
      "url": "https://your-domain.com/mcp/sse",
      "autoApprove": ["*"]
    }
  }
}
```

## 📦 安裝部署

### 前置條件

- Docker & Docker Compose (v2.0+)
- 一個運行中的 [ZFile](https://github.com/zfile-dev/zfile) 實例
- （可選）Nginx 用於反向代理

### Docker 部署

1. **克隆並配置**

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server
cp .env.example .env
```

2. **編輯 `.env` 檔案**

```env
ZFILE_URL=https://your-zfile-domain.com
ZFILE_USER=your_username
ZFILE_PASS=your_password
ZFILE_STORAGE_KEY=1
```

3. **啟動服務**

```bash
docker compose up -d
```

4. **驗證**

```bash
curl http://localhost:8092/health
# {"status":"ok"}
```

### 直接運行（開發環境）

```bash
# 安裝依賴
pip install fastapi uvicorn httpx

# 設置環境變數
export ZFILE_URL=https://your-zfile-domain.com
export ZFILE_USER=your_username
export ZFILE_PASS=your_password

# 運行
python server.py
```

## ⚙️ 配置說明

### 環境變數

| 變數 | 必填 | 預設值 | 說明 |
|------|------|--------|------|
| `ZFILE_URL` | ✅ | - | ZFile 伺服器地址 |
| `ZFILE_USER` | ✅ | - | ZFile 登入用戶名 |
| `ZFILE_PASS` | ✅ | - | ZFile 登入密碼 |
| `ZFILE_STORAGE_KEY` | ❌ | `1` | ZFile 中的儲存源 Key |

### Nginx 反向代理（可選）

```nginx
location /mcp/ {
    proxy_pass http://127.0.0.1:8092/;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_buffering off;
    proxy_cache off;
    chunked_transfer_encoding off;
}
```

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
→ 返回: https://your-domain.com/directlink/1/document.pdf

"給 /image.png 建立短連"
→ 調用 zfile_short_link(file_path="/image.png")
→ 返回: https://your-domain.com/s/AbCdEf
```

## 🏗️ 專案結構

```
zfile-mcp-server/
├── server.py           # MCP SSE 伺服器主檔案
├── Dockerfile          # Docker 構建檔案
├── docker-compose.yml  # Docker Compose 配置
├── .env.example        # 環境變數模板
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

1. Fork 本倉庫
2. 建立特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

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
