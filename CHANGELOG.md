# Changelog

All notable changes to this project will be documented in this file.

## [1.3.2] - 2026-02-26

### Fixed
- **Chunked upload curl commands now include real server URL and token** — Previously showed `<MCP_SERVER>` and `<TOKEN>` placeholders, making the commands unusable without manual editing. Now auto-detects the server URL from request headers or `MCP_SERVER_URL` env var.

### Added
- `MCP_SERVER_URL` env var — Optional override for the MCP server's external URL (useful behind reverse proxies)

## [1.3.1] - 2026-02-26

### Changed
- **CHUNK_SIZE_MB default: 50 → 10** — 50MB chunks exceeded Cloudflare's 100s timeout at ~300KB/s upload speed. 10MB chunks complete in ~36s, well within limits.
- Updated tool descriptions to reflect 10MB threshold

## [1.3.0] - 2026-02-26

### Added
- **Chunked upload** — Large file upload via chunks to bypass Cloudflare 120s timeout
  - `zfile_chunked_upload` tool: Initialize chunked upload, returns upload_id and instructions
  - `zfile_chunked_upload_status` tool: Check chunk upload progress
  - `POST /upload/chunk` endpoint: Receive individual chunks
  - `GET /upload/status` endpoint: Query upload status via HTTP
  - Auto-merge and upload to ZFile when all chunks arrive
  - Auto-cleanup of stale uploads after 1 hour
- `CHUNK_SIZE_MB` env var (default: 50MB per chunk)

### Changed
- SSE keepalive: comment format → `event: ping` for better proxy compatibility
- SSE keepalive interval: 30s → 25s (safety margin for Cloudflare 120s proxy read timeout)
- Added `X-Accel-Buffering: no` header for SSE responses
- Version constant extracted to `VERSION` variable

### Tools (v1.3.0)
| Tool | Description |
|------|-------------|
| `zfile_list` | List files in directory |
| `zfile_upload` | Get upload URL (small files < 50MB) |
| `zfile_chunked_upload` | **NEW** Initialize chunked upload (large files) |
| `zfile_chunked_upload_status` | **NEW** Check chunked upload progress |
| `zfile_batch_upload` | Get upload URLs for multiple files |
| `zfile_direct_link` | Generate permanent direct link |
| `zfile_direct_links` | Generate direct links for multiple files |
| `zfile_short_link` | Generate 31-day short link |

## [1.2.0] - 2026-01-07

### Added
- Streamable HTTP protocol support (Google Gemini CLI)
- Dual protocol: SSE + Streamable HTTP
- Access token authentication

## [1.1.0] - 2025-12-22

### Changed
- Removed base64 upload tool (was consuming context tokens)
- Renamed `zfile_get_upload_url` to `zfile_upload` for simplicity
- Upload tool now returns direct link URL automatically

### Added
- `zfile_batch_upload` - Get upload URLs for multiple files at once
- `zfile_direct_links` - Generate direct links for multiple files at once

## [1.0.0] - 2025-12-21

### Added
- Initial release
- SSE-based MCP server for ZFile integration
- Auto-generated ACCESS_TOKEN with persistence
- Docker Hub image: `neosun/zfile-mcp-server`
- Multi-language documentation (EN, CN, TW, JP)
