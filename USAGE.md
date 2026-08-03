# 使用說明

目前維護中的使用方式統一放在：

- [README.md](README.md)：安裝、stdio、Streamable HTTP、環境變數與安全設定
- [docs/RIKKAHUB_WINDOWS.md](docs/RIKKAHUB_WINDOWS.md)：Windows + NapCat + OpenSSH + RikkaHub + DeepSeek 從零部署
- [RESPONSE_COMPACTION.md](RESPONSE_COMPACTION.md)：大型 OneBot 回應精簡規則

## RikkaHub

```powershell
Copy-Item .env.example .env
# 編輯 .env
.\start-http.bat
```

RikkaHub 使用：

```text
URL: http://<Windows IP>:18080/mcp
Authorization: Bearer <MCP_BEARER_TOKEN>
```

## 本機 stdio 客戶端

```powershell
.\start.bat
```

正確 Python 模組名稱是 `napcat_mcp`；不要使用早期文件中的 `napcat_group_info_mcp`。
