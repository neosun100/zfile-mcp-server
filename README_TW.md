# ZFile MCP Server

一個 Model Context Protocol (MCP) 伺服器，讓 AI 助手能夠與 [ZFile](https://github.com/zfile-dev/zfile) 線上檔案管理系統互動。

[![Docker Hub](https://img.shields.io/docker/v/neosun/zfile-mcp-server?label=Docker%20Hub)](https://hub.docker.com/r/neosun/zfile-mcp-server)
[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/zfile-mcp-server)](https://hub.docker.com/r/neosun/zfile-mcp-server)

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

## 快速開始

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

啟動：

```bash
docker compose up -d
```

### 方式三：從原始碼建構

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server
docker build -t zfile-mcp-server .
```

## 環境變數

| 變數 | 必填 | 說明 | 範例 |
|------|------|------|------|
| `ZFILE_URL` | ✅ | ZFile 伺服器地址 | `https://zfile.example.com` |
| `ZFILE_USER` | ✅ | ZFile 使用者名稱 | `admin` |
| `ZFILE_PASS` | ✅ | ZFile 密碼 | `your_password` |
| `ZFILE_STORAGE_KEY` | ❌ | 儲存源 Key（預設: 1） | `1` |
| `ACCESS_TOKEN` | ❌ | 自訂存取令牌（不設定則自動生成） | `zfile-xxx` |

## 獲取存取令牌

服務首次啟動時會自動生成安全令牌：

```bash
docker logs zfile-mcp
```

查找：
```
==================================================
ACCESS_TOKEN: zfile-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
==================================================
```

## 配置 MCP 客戶端

在 MCP 客戶端配置檔案中添加（如 `~/.kiro/settings/mcp.json`）：

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

## 可用工具

| 工具 | 描述 | 適用場景 |
|------|------|----------|
| `zfile_list` | 列出目錄檔案 | 瀏覽檔案 |
| `zfile_upload` | 上傳檔案(base64)並返回直連 | 小檔案 (<5MB) |
| `zfile_get_upload_url` | 獲取直傳 URL | 大檔案上傳 |
| `zfile_direct_link` | 生成永久直連 | 永久分享 |
| `zfile_short_link` | 生成 31 天短連 | 臨時分享 |

### 工具詳情

#### zfile_list
列出 ZFile 目錄中的檔案。

**參數：**
- `path` (字串, 可選): 目錄路徑，預設 "/"

#### zfile_upload
上傳小檔案，自動生成直連返回。

**參數：**
- `file_path` (字串, 必填): ZFile 中的目標路徑，如 "/uploads/test.txt"
- `file_content_base64` (字串, 必填): base64 編碼的檔案內容

**返回：**
```
✅ Upload success: /test.txt
📎 Direct link: https://你的ZFile地址/directlink/1/test.txt
```

#### zfile_get_upload_url
獲取大檔案直傳 URL，客戶端可直接 PUT 上傳。

**參數：**
- `path` (字串, 可選): 目標目錄，預設 "/"
- `filename` (字串, 必填): 檔案名稱
- `size` (整數, 必填): 檔案大小（位元組）

**返回：**
```
Upload URL: https://你的ZFile地址/file/upload/1/largefile.zip

Upload command:
curl -X PUT 'URL' -F 'file=@/path/to/yourfile'
```

#### zfile_direct_link
生成永久下載直連。

**參數：**
- `file_path` (字串, 必填): 檔案路徑，如 "/test.pdf"

#### zfile_short_link
生成 31 天有效期短連。

**參數：**
- `file_path` (字串, 必填): 檔案路徑，如 "/test.pdf"

## 安全性

- **存取令牌**: 首次啟動自動生成，儲存在 `./data/.access_token`
- **令牌持久化**: 容器重啟後令牌不變（儲存在 volume 中）
- **憑據安全**: ZFile 帳號密碼僅儲存在伺服器端，不暴露給客戶端
- **映像無敏感資訊**: Docker 映像不包含任何敏感資料

## Nginx 反向代理（可選）

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

## 授權條款

MIT License
