# Changelog

All notable changes to this project will be documented in this file.

## [1.3.2] - 2026-02-26

### Fixed
- Improved chunked upload merge reliability
- Fixed SSE POST mode response handling for Kiro rmcp client

## [1.3.0] - 2026-01-10

### Added
- **Chunked upload** for large files (Cloudflare-friendly, auto-merge)
  - `zfile_chunked_upload` - Initialize chunked upload, returns upload_id and curl instructions
  - `zfile_chunked_upload_status` - Check chunked upload progress
  - HTTP endpoint `POST /upload/chunk` for receiving individual chunks
  - HTTP endpoint `GET /upload/status` for querying upload status
  - Auto-cleanup of stale chunks (1 hour expiry, checked every 10 minutes)
- New environment variables: `CHUNK_SIZE_MB`, `MCP_SERVER_URL`

### Changed
- Health endpoint now reports supported protocols and features

## [1.2.0] - 2025-12-28

### Added
- **Streamable HTTP protocol** support (Google Gemini CLI compatible)
  - `POST /mcp` endpoint for streamable HTTP mode
  - `GET /mcp` returns server info and endpoint discovery
  - `GET /mcp/sse` and `POST /mcp/message` as SSE aliases
- SSE endpoint now also accepts POST for Kiro rmcp Streamable HTTP mode
- Root endpoint `/` returns full server info with protocol documentation

### Changed
- Version bumped to 1.2.0
- Server now supports dual protocol: SSE + Streamable HTTP

## [1.1.0] - 2025-12-22

### Changed
- Removed base64 upload tool (was consuming context tokens)
- Renamed `zfile_get_upload_url` to `zfile_upload` for simplicity
- Upload tool now returns direct link URL automatically

### Added
- `zfile_batch_upload` - Get upload URLs for multiple files at once
- `zfile_direct_links` - Generate direct links for multiple files at once

### Tools (v1.1.0)
| Tool | Description |
|------|-------------|
| `zfile_list` | List files in directory |
| `zfile_upload` | Get upload URL (returns URL + direct link) |
| `zfile_batch_upload` | Get upload URLs for multiple files |
| `zfile_direct_link` | Generate permanent direct link |
| `zfile_direct_links` | Generate direct links for multiple files |
| `zfile_short_link` | Generate 31-day short link |

## [1.0.0] - 2025-12-21

### Added
- Initial release
- SSE-based MCP server for ZFile integration
- Auto-generated ACCESS_TOKEN with persistence
- Docker Hub image: `neosun/zfile-mcp-server`
- Multi-language documentation (EN, CN, TW, JP)
- Nginx reverse proxy configuration
- Security architecture: credentials stored server-side only
