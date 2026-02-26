[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

<div align="center">
  <img src="logo.png" alt="ZFile MCP Server" width="180" />
  <h1>ZFile MCP Server</h1>
  <p>AI アシスタントが ZFile と連携できる MCP サーバー</p>

  [![Docker Hub](https://img.shields.io/docker/v/neosun/zfile-mcp-server?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
  [![Docker Pulls](https://img.shields.io/docker/pulls/neosun/zfile-mcp-server?logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
  [![License](https://img.shields.io/github/license/neosun100/zfile-mcp-server)](LICENSE)
  [![GitHub Stars](https://img.shields.io/github/stars/neosun100/zfile-mcp-server?style=social)](https://github.com/neosun100/zfile-mcp-server)
</div>

---

## ✨ 機能

- 📁 **ファイル一覧** — ZFile ディレクトリを閲覧
- 📤 **ファイルアップロード** — アップロード URL を取得（base64 不要、トークン節約）
- 📤 **一括アップロード** — 複数のアップロード URL を一度に取得
- 📦 **チャンクアップロード** — 大容量ファイルのチャンク分割アップロード（Cloudflare 対応、自動マージ）
- 🔗 **直リンク生成** — 永久直リンクを生成（単一または一括）
- 🔗 **短縮リンク生成** — 31日間有効な短縮リンクを生成
- 🔐 **セキュア** — アクセストークン自動生成、認証情報はサーバー側に保存
- 🌐 **マルチプロトコル** — SSE（Kiro、Claude Desktop）+ Streamable HTTP（Gemini CLI）

## 🏗️ アーキテクチャ

```
┌─────────────────────────┐         ┌─────────────────────────┐         ┌─────────┐
│  MCP クライアント         │  SSE    │  MCP サーバー (Docker)   │  API    │  ZFile  │
│  ┌───────────────────┐  │ ──────► │  ┌─────────────────┐    │ ──────► │         │
│  │ ACCESS_TOKEN のみ  │  │  Token  │  │ ZFile 認証情報    │   │         │         │
│  └───────────────────┘  │         │  │ ここに保存        │   │         │         │
└─────────────────────────┘         │  └─────────────────┘    │         └─────────┘
                                    └─────────────────────────┘
```

**セキュリティモデル：**
- 🔒 クライアントは `ACCESS_TOKEN` のみ保存（MCP 認証用）
- 🔒 サーバーは環境変数で ZFile 認証情報を保存
- 🔒 ZFile 認証情報はクライアントに公開されない

## 🚀 クイックスタート

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
docker logs zfile-mcp 2>&1 | grep ACCESS_TOKEN
```

## 📦 インストール

### 方法1：Docker Hub（推奨）

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
      - ZFILE_URL=https://your-zfile-server.com
      - ZFILE_USER=your_username
      - ZFILE_PASS=your_password
      - ZFILE_STORAGE_KEY=1
      # - ACCESS_TOKEN=            # 未設定の場合は自動生成
      # - CHUNK_SIZE_MB=10         # チャンクサイズ（デフォルト: 10MB）
      # - MCP_SERVER_URL=          # オプション: チャンクアップロードコマンドの外部 URL
    volumes:
      - ./data:/data
```

```bash
docker compose up -d
```

### 方法3：ソースから実行

**要件：** Python 3.11+

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server
pip install -r requirements.txt

export ZFILE_URL=https://your-zfile.com
export ZFILE_USER=admin
export ZFILE_PASS=password

python server.py
```

## ⚙️ 設定

### 環境変数

| 変数 | 必須 | 説明 | デフォルト |
|------|------|------|-----------|
| `ZFILE_URL` | ✅ | ZFile サーバー URL | — |
| `ZFILE_USER` | ✅ | ZFile 管理者ユーザー名 | — |
| `ZFILE_PASS` | ✅ | ZFile 管理者パスワード | — |
| `ZFILE_STORAGE_KEY` | ❌ | ストレージソース Key | `1` |
| `ACCESS_TOKEN` | ❌ | カスタムアクセストークン（未設定の場合は自動生成） | 自動生成 |
| `CHUNK_SIZE_MB` | ❌ | 大容量ファイルのチャンクサイズ | `10` |
| `MCP_SERVER_URL` | ❌ | チャンクアップロードコマンドの外部 URL（リバースプロキシ環境で使用） | 自動検出 |

> 💡 **ヒント：** `MCP_SERVER_URL` が未設定の場合、サーバーはリクエストヘッダー（`X-Forwarded-Host`、`X-Forwarded-Proto`）から外部 URL を自動検出します。複雑なプロキシ環境では明示的に設定することを推奨します。

### MCP クライアント設定

#### 🟢 Kiro CLI

`~/.kiro/settings/mcp.json` に追加：

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

Claude Desktop 設定に追加（macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`）：

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

Gemini CLI は Streamable HTTP プロトコルを使用。`~/.gemini/settings.json` に追加：

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

プロジェクトルートの `.cursor/mcp.json` に追加：

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

`~/.codeium/windsurf/mcp_config.json` に追加：

```json
{
  "mcpServers": {
    "zfile": {
      "serverUrl": "https://your-server.com/mcp/sse?token=YOUR_ACCESS_TOKEN"
    }
  }
}
```

## 🌐 リバースプロキシ設定

### オプション A：Cloudflare Tunnel（推奨）

> ⚠️ **Cloudflare タイムアウト：** Cloudflare には 100s のプロキシ読み取りタイムアウトがあります。大容量ファイルのアップロードには、チャンクアップロード（`zfile_chunked_upload`）を使用してください。デフォルトの `CHUNK_SIZE_MB=10` で各チャンクがタイムアウト内に完了します。

### オプション B：Nginx

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

### オプション C：Caddy

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

## 🛠️ 利用可能なツール

| ツール | 説明 |
|--------|------|
| 📁 `zfile_list` | ディレクトリ内のファイルを一覧表示 |
| 📤 `zfile_upload` | 単一ファイルのアップロード URL を取得（< 10MB） |
| 📤 `zfile_batch_upload` | 複数ファイルのアップロード URL を一括取得 |
| 📦 `zfile_chunked_upload` | 大容量ファイルのチャンクアップロードを初期化（> 10MB） |
| 📊 `zfile_chunked_upload_status` | チャンクアップロードの進捗を確認 |
| 🔗 `zfile_direct_link` | 単一ファイルの永久直リンクを生成 |
| 🔗 `zfile_direct_links` | 複数ファイルの永久直リンクを一括生成 |
| 🔗 `zfile_short_link` | 31日間の短縮リンクを生成 |

### 💡 なぜ URL ベースのアップロード？

Base64 アップロードはコンテキストトークンを消費：
- 1MB ファイル → 約35万トークン
- 5MB ファイル → 約175万トークン（ほとんどのコンテキスト制限を超過！）

URL アップロード：**0 トークン** — クライアントが直接 ZFile にアップロード。

### 📦 チャンクアップロードフロー

10MB 以上のファイル向け（特に Cloudflare プロキシ経由の場合）：

```
1. AI が zfile_chunked_upload を呼び出し → upload_id + curl コマンドを取得
2. クライアントがファイルを 10MB チャンクに分割
3. クライアントが各チャンクを /upload/chunk エンドポイントに POST
4. サーバーが全チャンク受信後に自動マージ
5. サーバーがマージファイルを ZFile にアップロード
6. 直リンクを返却 ✅
```

> 💡 チャンクアップロードが返す `curl` コマンドには実際のサーバー URL とトークンが含まれています。そのままコピーして実行できます。

## 📁 プロジェクト構造

```
zfile-mcp-server/
├── server.py           # MCP サーバー本体
├── Dockerfile          # Docker イメージ定義
├── docker-compose.yml  # Docker Compose 設定
├── requirements.txt    # Python 依存関係
├── .env.example        # 環境変数テンプレート
├── README.md           # English documentation
├── README_CN.md        # 简体中文文档
├── README_TW.md        # 繁體中文文檔
├── README_JP.md        # 日本語ドキュメント
├── CHANGELOG.md        # バージョン履歴
├── LICENSE             # MIT ライセンス
└── .gitignore          # Git 無視ルール
```

## 🔧 技術スタック

- **ランタイム：** Python 3.11
- **フレームワーク：** FastAPI + Uvicorn
- **プロトコル：** MCP (Model Context Protocol) — SSE + Streamable HTTP
- **HTTP クライアント：** httpx
- **コンテナ：** Docker

## 🤝 コントリビューション

コントリビューション歓迎！Pull Request をお気軽にどうぞ。

## 📋 変更履歴

バージョン履歴は [CHANGELOG.md](CHANGELOG.md) を参照。

## 📄 ライセンス

MIT ライセンス - 詳細は [LICENSE](LICENSE) ファイルを参照。

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/zfile-mcp-server&type=Date)](https://star-history.com/#neosun100/zfile-mcp-server)

## 📱 フォロー

![WeChat](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
