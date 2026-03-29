[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

<div align="center">
  <h1>🗂️ ZFile MCP Server</h1>
  <p>AI アシスタントが ZFile と連携できる MCP サーバー</p>

  [![Docker Hub](https://img.shields.io/docker/v/neosun/zfile-mcp-server?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
  [![Docker Pulls](https://img.shields.io/docker/pulls/neosun/zfile-mcp-server?logo=docker)](https://hub.docker.com/r/neosun/zfile-mcp-server)
  [![License](https://img.shields.io/github/license/neosun100/zfile-mcp-server)](LICENSE)
  [![GitHub Stars](https://img.shields.io/github/stars/neosun100/zfile-mcp-server?style=social)](https://github.com/neosun100/zfile-mcp-server)
</div>

---

## ✨ 機能

- 📁 **ファイル一覧** - ZFile ディレクトリを閲覧
- 📤 **ファイルアップロード** - アップロード URL を取得（base64 不要、トークン節約）
- 📤 **一括アップロード** - 複数のアップロード URL を一度に取得
- 🔗 **直リンク生成** - 永久直リンクを生成（単一または一括）
- 🔗 **短縮リンク生成** - 31日間有効な短縮リンクを生成
- 🔐 **セキュア** - アクセストークン自動生成、認証情報はサーバー側に保存

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
- クライアントは `ACCESS_TOKEN` のみ保存（MCP 認証用）
- サーバーは環境変数で ZFile 認証情報を保存
- ZFile 認証情報はクライアントに公開されない

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
    volumes:
      - ./data:/data
```

```bash
docker compose up -d
```

### 方法3：ソースから実行

**要件：**
- Python 3.11+
- pip

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server

# 依存関係をインストール
pip install fastapi uvicorn httpx

# 環境変数を設定
export ZFILE_URL=https://your-zfile.com
export ZFILE_USER=admin
export ZFILE_PASS=password

# 実行
python server.py
```

## ⚙️ 設定

### 環境変数

| 変数 | 必須 | 説明 | デフォルト |
|------|------|------|-----------|
| `ZFILE_URL` | ✅ | ZFile サーバー URL | - |
| `ZFILE_USER` | ✅ | ZFile 管理者ユーザー名 | - |
| `ZFILE_PASS` | ✅ | ZFile 管理者パスワード | - |
| `ZFILE_STORAGE_KEY` | ❌ | ストレージソース Key | `1` |
| `ACCESS_TOKEN` | ❌ | カスタムアクセストークン | 自動生成 |

### MCP クライアント設定

#### Kiro CLI

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

## 🛠️ 利用可能なツール

| ツール | 説明 |
|--------|------|
| `zfile_list` | ディレクトリ内のファイルを一覧表示 |
| `zfile_upload` | 単一ファイルのアップロード URL を取得 |
| `zfile_batch_upload` | 複数ファイルのアップロード URL を一括取得 |
| `zfile_direct_link` | 単一ファイルの永久直リンクを生成 |
| `zfile_direct_links` | 複数ファイルの永久直リンクを一括生成 |
| `zfile_short_link` | 31日間の短縮リンクを生成 |

### なぜ URL ベースのアップロード？

Base64 アップロードはコンテキストトークンを消費：
- 1MB ファイル → 約35万トークン
- 5MB ファイル → 約175万トークン（ほとんどのコンテキスト制限を超過！）

URL アップロード：**0 トークン** - クライアントが直接 ZFile にアップロード。

## 📁 プロジェクト構造

```
zfile-mcp-server/
├── server.py           # MCP サーバー本体
├── Dockerfile          # Docker イメージ定義
├── docker-compose.yml  # Docker Compose 設定
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
- **プロトコル：** MCP (Model Context Protocol) over SSE
- **HTTP クライアント：** httpx
- **コンテナ：** Docker

## 🤝 コントリビューション

コントリビューション歓迎！Pull Request をお気軽にどうぞ。

1. リポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Request を開く

## 📋 変更履歴

バージョン履歴は [CHANGELOG.md](CHANGELOG.md) を参照。

## 📄 ライセンス

MIT ライセンス - 詳細は [LICENSE](LICENSE) ファイルを参照。

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/zfile-mcp-server&type=Date)](https://star-history.com/#neosun100/zfile-mcp-server)

## 📱 フォロー

![WeChat](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)
