# ZFile MCP Server

一个 Model Context Protocol (MCP) 服务器，让 AI 助手能够与 [ZFile](https://github.com/zfile-dev/zfile) 在线文件管理系统交互。

[![Docker Hub](https://img.shields.io/docker/v/neosun/zfile-mcp-server?label=Docker%20Hub)](https://hub.docker.com/r/neosun/zfile-mcp-server)
[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/zfile-mcp-server)](https://hub.docker.com/r/neosun/zfile-mcp-server)

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

## 快速开始

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

启动：

```bash
docker compose up -d
```

### 方式三：从源码构建

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server
docker build -t zfile-mcp-server .
```

## 环境变量

| 变量 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `ZFILE_URL` | ✅ | ZFile 服务器地址 | `https://zfile.example.com` |
| `ZFILE_USER` | ✅ | ZFile 用户名 | `admin` |
| `ZFILE_PASS` | ✅ | ZFile 密码 | `your_password` |
| `ZFILE_STORAGE_KEY` | ❌ | 存储源 Key（默认: 1） | `1` |
| `ACCESS_TOKEN` | ❌ | 自定义访问令牌（不设置则自动生成） | `zfile-xxx` |

## 获取访问令牌

服务首次启动时会自动生成安全令牌：

```bash
docker logs zfile-mcp
```

查找：
```
==================================================
ACCESS_TOKEN: zfile-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
==================================================
```

## 配置 MCP 客户端

在 MCP 客户端配置文件中添加（如 `~/.kiro/settings/mcp.json`）：

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

## 可用工具

| 工具 | 描述 | 适用场景 |
|------|------|----------|
| `zfile_list` | 列出目录文件 | 浏览文件 |
| `zfile_upload` | 上传文件(base64)并返回直链 | 小文件 (<5MB) |
| `zfile_get_upload_url` | 获取直传 URL | 大文件上传 |
| `zfile_direct_link` | 生成永久直链 | 永久分享 |
| `zfile_short_link` | 生成 31 天短链 | 临时分享 |

### 工具详情

#### zfile_list
列出 ZFile 目录中的文件。

**参数：**
- `path` (字符串, 可选): 目录路径，默认 "/"

#### zfile_upload
上传小文件，自动生成直链返回。

**参数：**
- `file_path` (字符串, 必填): ZFile 中的目标路径，如 "/uploads/test.txt"
- `file_content_base64` (字符串, 必填): base64 编码的文件内容

**返回：**
```
✅ Upload success: /test.txt
📎 Direct link: https://你的ZFile地址/directlink/1/test.txt
```

#### zfile_get_upload_url
获取大文件直传 URL，客户端可直接 PUT 上传。

**参数：**
- `path` (字符串, 可选): 目标目录，默认 "/"
- `filename` (字符串, 必填): 文件名
- `size` (整数, 必填): 文件大小（字节）

**返回：**
```
Upload URL: https://你的ZFile地址/file/upload/1/largefile.zip

Upload command:
curl -X PUT 'URL' -F 'file=@/path/to/yourfile'
```

#### zfile_direct_link
生成永久下载直链。

**参数：**
- `file_path` (字符串, 必填): 文件路径，如 "/test.pdf"

#### zfile_short_link
生成 31 天有效期短链。

**参数：**
- `file_path` (字符串, 必填): 文件路径，如 "/test.pdf"

## 安全性

- **访问令牌**: 首次启动自动生成，存储在 `./data/.access_token`
- **令牌持久化**: 容器重启后令牌不变（存储在 volume 中）
- **凭据安全**: ZFile 账号密码仅存储在服务端，不暴露给客户端
- **镜像无敏感信息**: Docker 镜像不包含任何敏感数据

## Nginx 反向代理（可选）

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

## 许可证

MIT License
