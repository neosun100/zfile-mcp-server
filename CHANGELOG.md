# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-12-21

### Added
- Initial release with Docker Hub image: `neosun/zfile-mcp-server:latest`
- SSE-based MCP server for ZFile integration
- Auto-generated ACCESS_TOKEN with persistence
- Architecture diagram in all READMEs

### Tools
- `zfile_list` - List files in ZFile directory
- `zfile_upload` - Upload file (base64) with automatic direct link generation
- `zfile_get_upload_url` - Get direct upload URL for large files
- `zfile_direct_link` - Generate permanent direct link
- `zfile_short_link` - Generate 31-day short link

### Security
- ZFile credentials stored server-side only (via environment variables)
- ACCESS_TOKEN for MCP client authentication
- Token persistence in Docker volume

### Documentation
- README in 4 languages: English, 简体中文, 繁體中文, 日本語
- Docker Hub deployment guide
- Docker Compose deployment guide
- Nginx reverse proxy configuration
- Environment variables documentation
