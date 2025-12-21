[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

# ZFile MCP Server

[![Docker Hub](https://img.shields.io/docker/v/neosun/zfile-mcp-server?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
[![Docker Pulls](https://img.shields.io/docker/pulls/neosun/zfile-mcp-server?logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
[![License](https://img.shields.io/github/license/neosun100/zfile-mcp-server)](LICENSE)

AI アシスタントが [ZFile](https://github.com/zfile-dev/zfile) と連携できる MCP サーバー。

## アーキテクチャ

```
┌─────────────────────────┐         ┌─────────────────────────┐         ┌─────────┐
│  MCP クライアント (Kiro)  │  SSE    │  MCP サーバー (Docker)   │  API    │  ZFile  │
│  ┌───────────────────┐  │ ──────► │  ┌─────────────────┐    │ ──────► │         │
│  │ ACCESS_TOKEN のみ  │  │  Token  │  │ ZFile 認証情報    │   │         │         │
│  └───────────────────┘  │         │  │ ここに保存        │   │         │         │
└─────────────────────────┘         │  └─────────────────┘    │         └─────────┘
                                    └─────────────────────────┘
```

## 機能

- 📁 **ファイル一覧** - ZFile ディレクトリを閲覧
- 📤 **ファイルアップロード** - アップロード URL を取得（base64 不要、トークン節約）
- 📤 **一括アップロード** - 複数のアップロード URL を一度に取得
- 🔗 **直リンク生成** - 永久直リンクを生成（単一または一括）
- 🔗 **短縮リンク生成** - 31日間有効な短縮リンクを生成
- 🔐 **セキュア** - アクセストークン自動生成、認証情報はサーバー側に保存

## クイックスタート

```bash
docker run -d --name zfile-mcp -p 8092:8092 \
  -e ZFILE_URL=https://your-zfile.com \
  -e ZFILE_USER=admin \
  -e ZFILE_PASS=password \
  -v ./data:/data \
  neosun/zfile-mcp-server:latest
```

ACCESS_TOKEN を取得:
```bash
docker logs zfile-mcp | grep ACCESS_TOKEN
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

`~/.kiro/settings/mcp.json` に追加:

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

## 利用可能なツール

| ツール | 説明 |
|--------|------|
| `zfile_list` | ディレクトリ内のファイルを一覧表示 |
| `zfile_upload` | 単一ファイルのアップロード URL を取得 |
| `zfile_batch_upload` | 複数ファイルのアップロード URL を一括取得 |
| `zfile_direct_link` | 単一ファイルの永久直リンクを生成 |
| `zfile_direct_links` | 複数ファイルの永久直リンクを一括生成 |
| `zfile_short_link` | 31日間の短縮リンクを生成 |

### なぜ URL ベースのアップロード？

Base64 アップロードはコンテキストトークンを消費:
- 1MB ファイル → 約35万トークン
- 5MB ファイル → 約175万トークン（ほとんどのコンテキスト制限を超過！）

URL アップロード：**0 トークン** - クライアントが直接 ZFile にアップロード。

## ライセンス

MIT License - [LICENSE](LICENSE) を参照
