# MCP 客戶端配置

## RikkaHub（Streamable HTTP）

完整 Windows 部署見 [docs/RIKKAHUB_WINDOWS.md](docs/RIKKAHUB_WINDOWS.md)。

1. 啟動 `start-http.bat`。
2. RikkaHub → 設定 → MCP → 新增 → Streamable HTTP。
3. URL 填 `http://<Windows IP>:18080/mcp`。
4. Header 填：

   ```text
   Authorization: Bearer <MCP_BEARER_TOKEN>
   ```

5. Connected 後，在助手設定中勾選該 MCP。

## Claude Desktop / Cline（stdio）

```json
{
  "mcpServers": {
    "napcat-mcp": {
      "command": "C:\\NapCatMCP\\.venv\\Scripts\\python.exe",
      "args": ["-m", "napcat_mcp"],
      "env": {
        "NAPCAT_HOST": "http://127.0.0.1:3000",
        "NAPCAT_TOKEN": "your_napcat_onebot_token",
        "ALLOWED_GROUPS": "628101497",
        "READONLY_MODE": "true"
      }
    }
  }
}
```

`command` 必須改為虛擬環境 Python 的實際絕對路徑。stdio 啟動日誌寫入 stderr，不會污染 MCP stdout。
