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
- 🔒 **セキュア** - ZFile API のトークンベース認証

## 🚀 クイックスタート

### Docker を使用（推奨）

```bash
# リポジトリをクローン
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server

# 環境変数を設定
cp .env.example .env
# .env を編集して ZFile の認証情報を入力

# サービスを起動
docker compose up -d
```

### MCP クライアントの設定

MCP クライアント設定に追加（例：`~/.kiro/settings/mcp.json`）：

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

## 📦 インストール

### 前提条件

- Docker & Docker Compose (v2.0+)
- 稼働中の [ZFile](https://github.com/zfile-dev/zfile) インスタンス
- （オプション）リバースプロキシ用の Nginx

### Docker デプロイ

1. **クローンと設定**

```bash
git clone https://github.com/neosun100/zfile-mcp-server.git
cd zfile-mcp-server
cp .env.example .env
```

2. **`.env` ファイルを編集**

```env
ZFILE_URL=https://your-zfile-domain.com
ZFILE_USER=your_username
ZFILE_PASS=your_password
ZFILE_STORAGE_KEY=1
```

3. **サービスを起動**

```bash
docker compose up -d
```

4. **確認**

```bash
curl http://localhost:8092/health
# {"status":"ok"}
```

### 直接実行（開発環境）

```bash
# 依存関係をインストール
pip install fastapi uvicorn httpx

# 環境変数を設定
export ZFILE_URL=https://your-zfile-domain.com
export ZFILE_USER=your_username
export ZFILE_PASS=your_password

# 実行
python server.py
```

## ⚙️ 設定

### 環境変数

| 変数 | 必須 | デフォルト | 説明 |
|------|------|------------|------|
| `ZFILE_URL` | ✅ | - | ZFile サーバー URL |
| `ZFILE_USER` | ✅ | - | ZFile ログインユーザー名 |
| `ZFILE_PASS` | ✅ | - | ZFile ログインパスワード |
| `ZFILE_STORAGE_KEY` | ❌ | `1` | ZFile のストレージソースキー |

### Nginx リバースプロキシ（オプション）

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
→ 戻り値: https://your-domain.com/directlink/1/document.pdf

「/image.png の短縮リンクを作成」
→ zfile_short_link(file_path="/image.png") を呼び出し
→ 戻り値: https://your-domain.com/s/AbCdEf
```

## 🏗️ プロジェクト構成

```
zfile-mcp-server/
├── server.py           # MCP SSE サーバーメインファイル
├── Dockerfile          # Docker ビルドファイル
├── docker-compose.yml  # Docker Compose 設定
├── .env.example        # 環境変数テンプレート
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

1. リポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Request を開く

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
