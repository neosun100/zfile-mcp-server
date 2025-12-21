[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# ZFile MCP Server

[![Docker Hub](https://img.shields.io/docker/v/neosun/zfile-mcp-server?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/zfile-mcp-server?logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
[![License](https://img.shields.io/github/license/neosun100/zfile-mcp-server)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/neosun100/zfile-mcp-server?style=social)](https://github.com/neosun100/zfile-mcp-server)

[ZFile](https://github.com/zfile-dev/zfile) オンラインファイル管理システムと AI アシスタントを連携させる Model Context Protocol (MCP) サーバーです。

## アーキテクチャ

```
┌─────────────────────────┐         ┌─────────────────────────┐         ┌─────────┐
│  MCP クライアント (Kiro) │  SSE    │  MCP サーバー (Docker)   │  API    │  ZFile  │
│  ┌───────────────────┐  │ ──────► │  ┌─────────────────┐    │ ──────► │         │
│  │ ACCESS_TOKEN のみ  │  │  Token  │  │ ZFile 認証情報   │    │         │         │
│  └───────────────────┘  │         │  │ ここに保存       │    │         │         │
└─────────────────────────┘         │  └─────────────────┘    │         └─────────┘
                                    └─────────────────────────┘
```

- **クライアント**: ACCESS_TOKEN のみ保存（MCP 認証用）
- **サーバー**: 環境変数で ZFile 認証情報を保存
- **セキュリティ**: ZFile 認証情報はクライアントに公開されません

## 機能

- 📁 **ファイル一覧** - ZFile ディレクトリを閲覧
- ⬆️ **ファイルアップロード** - アップロードと同時に直リンクを自動生成
- 🔗 **永久直リンク** - 永久ダウンロードリンクを生成
- 🔗 **短縮リンク** - 31日間有効な短縮リンクを生成
- 📤 **大容量ファイル対応** - アップロード URL を取得して直接アップロード
- 🔐 **セキュア** - アクセストークン自動生成、認証情報はサーバー側のみ保存

## クイックスタート

```bash
docker run -d --name zfile-mcp -p 8092:8092 \
  -e ZFILE_URL=https://your-zfile.com \
  -e ZFILE_USER=admin \
  -e ZFILE_PASS=password \
  -v ./data:/data \
  neosun/zfile-mcp-server:latest
```

ACCESS_TOKEN を取得：
```bash
docker logs zfile-mcp | grep ACCESS_TOKEN
```

## インストール

### 方法1：Docker Hub（推奨）

```bash
docker run -d \
  --name zfile-mcp \
  -p 8092:8092 \
  -e ZFILE_URL=https://あなたのZFileアドレス \
  -e ZFILE_USER=ユーザー名 \
  -e ZFILE_PASS=パスワード \
  -e ZFILE_STORAGE_KEY=1 \
  -v ./data:/data \
  neosun/zfile-mcp-server:latest
```

### 方法2：Docker Compose

`docker-compose.yml` を作成：

```yaml
services:
  zfile-mcp:
    image: neosun/zfile-mcp-server:latest
    container_name: zfile-mcp
    restart: always
    ports:
      - '8092:8092'
    environment:
      - ZFILE_URL=https://あなたのZFileアドレス
      - ZFILE_USER=ユーザー名
      - ZFILE_PASS=パスワード
      - ZFILE_STORAGE_KEY=1
    volumes:
      - ./data:/data
```

```bash
docker compose up -d
```

### 方法3：ソースからビルド

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

## 設定

### 環境変数

| 変数 | 必須 | 説明 | デフォルト |
|------|------|------|-----------|
| `ZFILE_URL` | ✅ | ZFile サーバー URL | - |
| `ZFILE_USER` | ✅ | ZFile ユーザー名 | - |
| `ZFILE_PASS` | ✅ | ZFile パスワード | - |
| `ZFILE_STORAGE_KEY` | ❌ | ストレージソース Key | `1` |
| `ACCESS_TOKEN` | ❌ | カスタムアクセストークン | 自動生成 |

### MCP クライアント設定

`~/.kiro/settings/mcp.json` に追加：

```json
{
  "mcpServers": {
    "zfile": {
      "type": "sse",
      "url": "https://あなたのサーバー/mcp/sse?token=あなたのACCESS_TOKEN",
      "headers": {},
      "autoApprove": ["*"],
      "disabled": false
    }
  }
}
```

### Nginx リバースプロキシ（オプション）

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

## 利用可能なツール

| ツール | 説明 | 用途 |
|--------|------|------|
| `zfile_list` | ディレクトリ内のファイルを一覧表示 | ファイル閲覧 |
| `zfile_upload` | ファイルをアップロード(base64)し直リンクを返す | 小さいファイル (<5MB) |
| `zfile_get_upload_url` | 直接アップロード URL を取得 | 大容量ファイル |
| `zfile_direct_link` | 永久直リンクを生成 | 永久共有 |
| `zfile_short_link` | 31日間の短縮リンクを生成 | 一時共有 |

### 使用例

**ファイル一覧：**
```
/documents ディレクトリのすべてのファイルを一覧表示
```

**アップロードしてリンク取得：**
```
このファイルを ZFile にアップロードして直リンクをください
```

**直リンク生成：**
```
/report.pdf の直リンクを生成
```

## 技術スタック

- **ランタイム**: Python 3.11
- **フレームワーク**: FastAPI + Uvicorn
- **プロトコル**: MCP (Model Context Protocol) over SSE
- **HTTP クライアント**: httpx
- **コンテナ**: Docker

## プロジェクト構成

```
zfile-mcp-server/
├── server.py           # MCP サーバーメイン
├── Dockerfile          # Docker イメージ定義
├── docker-compose.yml  # Docker Compose 設定
├── README.md           # 英語ドキュメント
├── README_CN.md        # 简体中文文档
├── README_TW.md        # 繁體中文文檔
├── README_JP.md        # 日本語ドキュメント
├── CHANGELOG.md        # バージョン履歴
├── LICENSE             # MIT ライセンス
└── .gitignore          # Git 無視ルール
```

## コントリビューション

コントリビューション歓迎！お気軽に Pull Request を送ってください。

1. リポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Request を開く

## 変更履歴

バージョン履歴は [CHANGELOG.md](CHANGELOG.md) をご覧ください。

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています - 詳細は [LICENSE](LICENSE) ファイルをご覧ください。

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/zfile-mcp-server&type=Date)](https://star-history.com/#neosun100/zfile-mcp-server)

## 📱 フォロー

![WeChat](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
