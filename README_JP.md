[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# ZFile MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

> Model Context Protocol (MCP) に基づくサーバーで、AI アシスタントが ZFile と連携し、ファイルのアップロードと共有リンクの生成をシームレスに行えます。

## ✨ 機能

- 🔗 **SSE ベースの MCP サーバー** - ローカル依存不要
- 📁 **ファイル一覧** - ZFile ストレージ内のファイルを閲覧
- 🔗 **直接リンク生成** - 永続的な直接リンクを作成
- ⏱️ **短縮リンク生成** - 期限付き短縮リンクを作成
- 🐳 **Docker 対応** - Docker Compose で簡単デプロイ
- 🔒 **セキュア設計** - 認証情報はクライアント側に保存、Header で送信

## 🔐 セキュリティアーキテクチャ

```
┌─────────────────────────┐         ┌─────────────────┐         ┌─────────┐
│  MCP クライアント (Kiro) │  SSE    │  MCP サーバー    │  API    │  ZFile  │
│  ┌───────────────────┐  │ ──────► │  (ステートレス)  │ ──────► │         │
│  │ 認証情報はここに   │  │ Headers │  認証情報なし    │         │         │
│  └───────────────────┘  │         │                 │         │         │
└─────────────────────────┘         └─────────────────┘         └─────────┘
```

**認証情報は MCP クライアント設定に保存され、サーバーには保存されません。** サーバーはステートレスで、認証済みリクエストを転送するだけです。

## 🚀 クイックスタート

### 1. サーバーをデプロイ

```bash
# リポジトリをクローン
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server

# サービスを起動
docker compose up -d
```

### 2. MCP クライアントを設定

MCP クライアント設定に追加（例：`~/.kiro/settings/mcp.json`）：

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

## 📦 インストール

### 前提条件

- Docker & Docker Compose (v2.0+)
- 稼働中の [ZFile](https://github.com/zfile-dev/zfile) インスタンス
- （オプション）HTTPS 用の Nginx リバースプロキシ

### Docker デプロイ

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server
docker compose up -d

# 確認
curl http://localhost:8092/health
# {"status":"ok"}
```

### 直接実行（開発環境）

```bash
pip install fastapi uvicorn httpx
python server.py
```

## ⚙️ 設定

### MCP クライアント Headers

| Header | 必須 | 説明 |
|--------|------|------|
| `X-ZFile-URL` | ✅ | ZFile サーバー URL |
| `X-ZFile-User` | ✅ | ZFile ログインユーザー名 |
| `X-ZFile-Pass` | ✅ | ZFile ログインパスワード |
| `X-ZFile-Storage-Key` | ❌ | ストレージソースキー（デフォルト：`1`） |

### Nginx リバースプロキシ（HTTPS 推奨）

```nginx
location /mcp/ {
    proxy_pass http://127.0.0.1:8092/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-ZFile-URL $http_x_zfile_url;
    proxy_set_header X-ZFile-User $http_x_zfile_user;
    proxy_set_header X-ZFile-Pass $http_x_zfile_pass;
    proxy_set_header X-ZFile-Storage-Key $http_x_zfile_storage_key;
    proxy_set_header Connection "";
    proxy_buffering off;
    proxy_cache off;
    chunked_transfer_encoding off;
}
```

## 📖 使用方法

### 利用可能なツール

| ツール | 説明 |
|--------|------|
| `zfile_list` | ディレクトリ内のファイルを一覧表示 |
| `zfile_direct_link` | 永続的な直接リンクを生成 |
| `zfile_short_link` | 短縮リンクを生成（31日間有効） |

### 例

AI アシスタントで：

```
「ZFile のルートディレクトリのファイルを一覧表示」
→ zfile_list(path="/") を呼び出し

「/document.pdf の直接リンクを生成」
→ zfile_direct_link(file_path="/document.pdf") を呼び出し
→ 戻り値: https://your-zfile.com/directlink/1/document.pdf

「/image.png の短縮リンクを作成」
→ zfile_short_link(file_path="/image.png") を呼び出し
→ 戻り値: https://your-zfile.com/s/AbCdEf
```

## 🏗️ プロジェクト構成

```
zfile-mcp-server/
├── server.py           # MCP SSE サーバー（ステートレス）
├── Dockerfile          # Docker ビルドファイル
├── docker-compose.yml  # Docker Compose 設定
├── .gitignore
├── LICENSE
├── CHANGELOG.md
└── README.md
```

## 🛠️ 技術スタック

- **Python 3.11+**
- **FastAPI** - Web フレームワーク
- **Uvicorn** - ASGI サーバー
- **httpx** - HTTP クライアント
- **Docker** - コンテナ化

## 🤝 コントリビューション

コントリビューション歓迎！お気軽に Pull Request を送ってください。

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています - 詳細は [LICENSE](LICENSE) ファイルをご覧ください。

## 🙏 謝辞

- [ZFile](https://github.com/zfile-dev/zfile) - 優れたファイル管理システム
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP プロトコル仕様

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/zfile-mcp-server&type=Date)](https://star-history.com/#neosun100/zfile-mcp-server)

## 📱 公式アカウント

![WeChat](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
