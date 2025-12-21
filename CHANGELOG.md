# Changelog

## [1.1.0] - 2024-12-22

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

## [1.0.0] - 2024-12-21

### Added
- Initial release
- SSE-based MCP server for ZFile integration
- Auto-generated ACCESS_TOKEN with persistence
- Docker Hub image: `neosun/zfile-mcp-server`
- Multi-language documentation (EN, CN, TW, JP)
