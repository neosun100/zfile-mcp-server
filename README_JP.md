# ZFile MCP Server

[ZFile](https://github.com/zfile-dev/zfile) オンラインファイル管理システムと AI アシスタントを連携させる Model Context Protocol (MCP) サーバーです。

[![Docker Hub](https://img.shields.io/docker/v/neosun/zfile-mcp-server?label=Docker%20Hub)](https://hub.docker.com/r/neosun/zfile-mcp-server)
[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/zfile-mcp-server)](https://hub.docker.com/r/neosun/zfile-mcp-server)

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

## クイックスタート

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

起動：

```bash
docker compose up -d
```

### 方法3：ソースからビルド

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server
docker build -t zfile-mcp-server .
```

## 環境変数

| 変数 | 必須 | 説明 | 例 |
|------|------|------|------|
| `ZFILE_URL` | ✅ | ZFile サーバー URL | `https://zfile.example.com` |
| `ZFILE_USER` | ✅ | ZFile ユーザー名 | `admin` |
| `ZFILE_PASS` | ✅ | ZFile パスワード | `your_password` |
| `ZFILE_STORAGE_KEY` | ❌ | ストレージソース Key（デフォルト: 1） | `1` |
| `ACCESS_TOKEN` | ❌ | カスタムアクセストークン（未設定時は自動生成） | `zfile-xxx` |

## アクセストークンを取得

初回起動時にセキュアなトークンが自動生成されます：

```bash
docker logs zfile-mcp
```

以下を探してください：
```
==================================================
ACCESS_TOKEN: zfile-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
==================================================
```

## MCP クライアントを設定

MCP クライアント設定ファイルに追加（例：`~/.kiro/settings/mcp.json`）：

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

## 利用可能なツール

| ツール | 説明 | 用途 |
|--------|------|------|
| `zfile_list` | ディレクトリ内のファイルを一覧表示 | ファイル閲覧 |
| `zfile_upload` | ファイルをアップロード(base64)し直リンクを返す | 小さいファイル (<5MB) |
| `zfile_get_upload_url` | 直接アップロード URL を取得 | 大容量ファイル |
| `zfile_direct_link` | 永久直リンクを生成 | 永久共有 |
| `zfile_short_link` | 31日間の短縮リンクを生成 | 一時共有 |

### ツール詳細

#### zfile_list
ZFile ディレクトリ内のファイルを一覧表示します。

**パラメータ：**
- `path` (文字列, 任意): ディレクトリパス、デフォルト "/"

#### zfile_upload
小さいファイルをアップロードし、直リンクを自動生成して返します。

**パラメータ：**
- `file_path` (文字列, 必須): ZFile 内の保存先パス、例 "/uploads/test.txt"
- `file_content_base64` (文字列, 必須): base64 エンコードされたファイル内容

**戻り値：**
```
✅ Upload success: /test.txt
📎 Direct link: https://あなたのZFileアドレス/directlink/1/test.txt
```

#### zfile_get_upload_url
大容量ファイル用の直接アップロード URL を取得します。

**パラメータ：**
- `path` (文字列, 任意): 保存先ディレクトリ、デフォルト "/"
- `filename` (文字列, 必須): ファイル名
- `size` (整数, 必須): ファイルサイズ（バイト）

**戻り値：**
```
Upload URL: https://あなたのZFileアドレス/file/upload/1/largefile.zip

Upload command:
curl -X PUT 'URL' -F 'file=@/path/to/yourfile'
```

#### zfile_direct_link
永久ダウンロードリンクを生成します。

**パラメータ：**
- `file_path` (文字列, 必須): ファイルパス、例 "/test.pdf"

#### zfile_short_link
31日間有効な短縮リンクを生成します。

**パラメータ：**
- `file_path` (文字列, 必須): ファイルパス、例 "/test.pdf"

## セキュリティ

- **アクセストークン**: 初回起動時に自動生成、`./data/.access_token` に保存
- **トークン永続化**: コンテナ再起動後もトークンは変わりません（volume に保存）
- **認証情報の安全性**: ZFile のアカウント情報はサーバー側のみに保存、クライアントには公開されません
- **イメージに機密情報なし**: Docker イメージには機密データは含まれません

## Nginx リバースプロキシ（オプション）

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

## ライセンス

MIT License
