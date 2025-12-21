[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# ZFile MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

> 一个基于 Model Context Protocol (MCP) 的服务器，让 AI 助手能够与 ZFile 交互 - 无缝上传文件并生成分享链接。

## ✨ 功能特性

- 🔗 **基于 SSE 的 MCP 服务器** - 无需本地依赖
- 📁 **文件列表** - 浏览 ZFile 存储中的文件
- 🔗 **直链生成** - 创建永久直链
- ⏱️ **短链生成** - 创建有时效的短链接
- 🐳 **Docker 就绪** - 使用 Docker Compose 轻松部署
- 🔒 **安全可靠** - 基于 Token 的 ZFile API 认证

## 🚀 快速开始

### 使用 Docker（推荐）

```bash
# 克隆仓库
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 ZFile 凭据

# 启动服务
docker compose up -d
```

### 配置 MCP 客户端

在你的 MCP 客户端配置中添加（如 `~/.kiro/settings/mcp.json`）：

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

## 📦 安装部署

### 前置条件

- Docker & Docker Compose (v2.0+)
- 一个运行中的 [ZFile](https://github.com/zfile-dev/zfile) 实例
- （可选）Nginx 用于反向代理

### Docker 部署

1. **克隆并配置**

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server
cp .env.example .env
```

2. **编辑 `.env` 文件**

```env
ZFILE_URL=https://your-zfile-domain.com
ZFILE_USER=your_username
ZFILE_PASS=your_password
ZFILE_STORAGE_KEY=1
```

3. **启动服务**

```bash
docker compose up -d
```

4. **验证**

```bash
curl http://localhost:8092/health
# {"status":"ok"}
```

### 直接运行（开发环境）

```bash
# 安装依赖
pip install fastapi uvicorn httpx

# 设置环境变量
export ZFILE_URL=https://your-zfile-domain.com
export ZFILE_USER=your_username
export ZFILE_PASS=your_password

# 运行
python server.py
```

## ⚙️ 配置说明

### 环境变量

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `ZFILE_URL` | ✅ | - | ZFile 服务器地址 |
| `ZFILE_USER` | ✅ | - | ZFile 登录用户名 |
| `ZFILE_PASS` | ✅ | - | ZFile 登录密码 |
| `ZFILE_STORAGE_KEY` | ❌ | `1` | ZFile 中的存储源 Key |

### Nginx 反向代理（可选）

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

| 工具 | 说明 |
|------|------|
| `zfile_list` | 列出目录中的文件 |
| `zfile_direct_link` | 生成永久直链 |
| `zfile_short_link` | 生成短链（31天有效） |

### 示例

在 AI 助手中：

```
"列出 ZFile 根目录的文件"
→ 调用 zfile_list(path="/")

"给 /document.pdf 生成直链"
→ 调用 zfile_direct_link(file_path="/document.pdf")
→ 返回: https://your-domain.com/directlink/1/document.pdf

"给 /image.png 创建短链"
→ 调用 zfile_short_link(file_path="/image.png")
→ 返回: https://your-domain.com/s/AbCdEf
```

## 🏗️ 项目结构

```
zfile-mcp-server/
├── server.py           # MCP SSE 服务器主文件
├── Dockerfile          # Docker 构建文件
├── docker-compose.yml  # Docker Compose 配置
├── .env.example        # 环境变量模板
├── .gitignore
├── LICENSE
├── CHANGELOG.md
└── README.md
```

## 🛠️ 技术栈

- **Python 3.11+**
- **FastAPI** - Web 框架
- **Uvicorn** - ASGI 服务器
- **httpx** - HTTP 客户端
- **Docker** - 容器化

## 🤝 贡献指南

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [ZFile](https://github.com/zfile-dev/zfile) - 优秀的文件管理系统
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP 协议规范

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/zfile-mcp-server&type=Date)](https://star-history.com/#neosun100/zfile-mcp-server)

## 📱 关注公众号

![公众号](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
