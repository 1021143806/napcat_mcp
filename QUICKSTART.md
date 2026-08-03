# 快速開始

完整說明見 [README.md](README.md)；Windows + RikkaHub + DeepSeek 從零部署見 [docs/RIKKAHUB_WINDOWS.md](docs/RIKKAHUB_WINDOWS.md)。

## 安裝

```bash
git clone https://github.com/1021143806/napcat_mcp.git
cd napcat_mcp
python -m venv .venv
```

Windows：

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
Copy-Item .env.example .env
```

編輯 `.env` 後，RikkaHub 使用原生 Streamable HTTP：

```powershell
.\start-http.bat
```

端點預設為：

```text
http://127.0.0.1:18080/mcp
```

若供手機連線，將 `MCP_HTTP_HOST` 改為 Windows 的區域網路/Tailscale IP，並在 RikkaHub 加入：

```text
Authorization: Bearer <MCP_BEARER_TOKEN>
```

本機 stdio 客戶端則使用：

```powershell
.\start.bat
```

或：

```powershell
.\.venv\Scripts\python.exe -m napcat_mcp --transport stdio
```
