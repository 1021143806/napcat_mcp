# 專案摘要

NapCat MCP 將 NapCat / OneBot 11 API 暴露為 57 個 MCP 工具。

## 0.3.0 架構

- `src/napcat_mcp/server.py`：工具 schema、權限與工具執行、stdio/HTTP CLI
- `src/napcat_mcp/napcat_client.py`：NapCat OneBot HTTP/WebSocket 客戶端
- `src/napcat_mcp/http_transport.py`：原生 Streamable HTTP、Bearer 驗證與 DNS rebinding 防護
- `tests/`：回應精簡、ID 精度、stdio 與 Streamable HTTP 整合測試
- `docs/RIKKAHUB_WINDOWS.md`：Windows/RikkaHub/DeepSeek 完整部署

支援：

- stdio：本機 Claude Desktop/Cline
- Streamable HTTP：RikkaHub 等遠端 MCP 客戶端
- 群號白名單、唯讀模式、單工具禁用
- HTTP 靜態 Bearer Token
- LLM 導向 compact 回應與 `read_group_messages`

詳細安裝與配置見 [README.md](README.md)。
