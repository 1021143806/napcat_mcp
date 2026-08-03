# NapCat MCP

把 NapCat / OneBot 11 API 暴露為 MCP 工具，供 RikkaHub、Claude Desktop、Cline 等客戶端使用。

- **原生 Streamable HTTP**：RikkaHub 可直接連接，不再需要 Supergateway/MCPHub
- **stdio**：保留相容 Claude Desktop、Cline 等本機 MCP 客戶端
- **57 個工具**：群聊、訊息、好友、群管理、檔案及 NapCat 擴充 API
- **安全限制**：群號白名單、唯讀模式、單工具停用、HTTP Bearer Token、DNS rebinding 防護
- **LLM 友善輸出**：大型 OneBot 回應自動精簡，並提供輕量讀群訊息工具

> Windows + RikkaHub + DeepSeek 從零部署請直接閱讀：
> **[docs/RIKKAHUB_WINDOWS.md](docs/RIKKAHUB_WINDOWS.md)**

---

## 架構

### RikkaHub（推薦）

```text
RikkaHub ── Streamable HTTP ──> napcat_mcp ── OneBot HTTP ──> NapCat/QQ
              :18080/mcp                         127.0.0.1:3000
```

### 本機 stdio 客戶端

```text
Claude Desktop/Cline ── stdio ──> napcat_mcp ── OneBot HTTP/WS ──> NapCat
```

這裡有兩種不同的 HTTP：

1. `NAPCAT_HOST` 是 **napcat_mcp → NapCat** 的 OneBot API。
2. `MCP_HTTP_*` 是 **RikkaHub → napcat_mcp** 的 MCP Streamable HTTP。

---

## 要求

- Python 3.10+
- NapCat 4.9.91+
- NapCat 已登入 QQ
- NapCat OneBot 11 已啟用 HTTP 服務端

建議 NapCat 與 napcat_mcp 在同一台電腦運行，並讓 OneBot 僅監聽：

```text
127.0.0.1:3000
```

不要把 NapCat 的 3000 端口暴露到網路。

---

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

Linux/macOS：

```bash
.venv/bin/python -m pip install -e .
cp .env.example .env
```

然後編輯 `.env`。

---

## RikkaHub：原生 Streamable HTTP

### 最小安全配置

```env
# napcat_mcp 連 NapCat
NAPCAT_HOST=http://127.0.0.1:3000
NAPCAT_TOKEN=你的_NapCat_OneBot_Token
ALLOWED_GROUPS=628101497
READONLY_MODE=true
NAPCAT_RESPONSE_MODE=compact

# RikkaHub 連 napcat_mcp
MCP_TRANSPORT=streamable-http
MCP_HTTP_HOST=192.168.1.20
MCP_HTTP_PORT=18080
MCP_HTTP_PATH=/mcp
MCP_BEARER_TOKEN=另一串獨立的長隨機密碼
```

`MCP_HTTP_HOST` 填 Windows 的區域網路或 Tailscale IP。若填 `0.0.0.0`，還必須明確設定：

```env
MCP_ALLOWED_HOSTS=192.168.1.20:18080
```

### 啟動

Windows 雙擊或執行：

```powershell
.\start-http.bat
```

Linux/macOS：

```bash
./start-http.sh
```

也可直接執行：

```powershell
.\.venv\Scripts\python.exe -m napcat_mcp --transport streamable-http
```

健康檢查：

```text
http://192.168.1.20:18080/healthz
```

MCP 端點：

```text
http://192.168.1.20:18080/mcp
```

### RikkaHub 配置

在 **設定 → MCP → `+` → Streamable HTTP** 填寫：

- 名稱：`NapCat`
- URL：`http://192.168.1.20:18080/mcp`
- Header 名稱：`Authorization`
- Header 值：`Bearer 你的_MCP_BEARER_TOKEN`

保存後應顯示 `Connected`，並讀取到 57 個工具。接著在助手設定中啟用這個 MCP；僅添加到全域 MCP 列表並不會自動附加給助手。

> HTTP Bearer Token 在純 HTTP 上不具傳輸加密。只應在可信任的區域網路或 Tailscale 中使用；若跨公網，請在前方加 HTTPS 反向代理，且不要直接公開 18080。

---

## stdio 模式

stdio 仍是預設值，因此舊配置不需要改：

```json
{
  "mcpServers": {
    "napcat-mcp": {
      "command": "C:\\path\\to\\napcat_mcp\\.venv\\Scripts\\python.exe",
      "args": ["-m", "napcat_mcp"],
      "env": {
        "NAPCAT_HOST": "http://127.0.0.1:3000",
        "NAPCAT_TOKEN": "your_napcat_token",
        "ALLOWED_GROUPS": "628101497",
        "READONLY_MODE": "true"
      }
    }
  }
}
```

也可執行：

```bash
python -m napcat_mcp --transport stdio
```

所有啟動日誌均寫入 `stderr`，不會污染 stdio MCP 協議的 `stdout`。

---

## 環境變數

### NapCat / 權限

| 變數 | 說明 | 預設值 |
|---|---|---|
| `NAPCAT_HOST` | NapCat OneBot HTTP/WS 地址 | `http://localhost:3000` |
| `NAPCAT_TOKEN` | NapCat OneBot Token | 空 |
| `ALLOWED_GROUPS` | 允許操作的群號，逗號分隔；空值表示全部 | 空 |
| `READONLY_MODE` | 禁用所有寫入工具 | `false` |
| `DISABLED_TOOLS` | 額外禁用的工具名，逗號分隔 | 空 |
| `NAPCAT_RESPONSE_MODE` | `compact` 或 `full` | `compact` |

### MCP Streamable HTTP

| 變數 | 說明 | 預設值 |
|---|---|---|
| `MCP_TRANSPORT` | `stdio` / `streamable-http` | `stdio` |
| `MCP_HTTP_HOST` | HTTP 監聽地址 | `127.0.0.1` |
| `MCP_HTTP_PORT` | HTTP 監聽端口 | `18080` |
| `MCP_HTTP_PATH` | MCP 路徑 | `/mcp` |
| `MCP_BEARER_TOKEN` | MCP 靜態 Bearer Token | 空 |
| `MCP_ALLOWED_HOSTS` | DNS rebinding Host 白名單 | 自動依監聽 IP 產生 |
| `MCP_ALLOWED_ORIGINS` | Origin 白名單 | localhost |
| `MCP_HTTP_STATELESS` | 每個請求使用獨立 session | `false` |
| `MCP_HTTP_JSON_RESPONSE` | 使用 JSON 而非 SSE 回應 | `false` |
| `MCP_HTTP_LOG_LEVEL` | Uvicorn 日誌級別 | `info` |

安全保護：

- 只要監聽地址不是 loopback，就強制要求 `MCP_BEARER_TOKEN`。
- 監聽 `0.0.0.0` / `::` 時強制要求 `MCP_ALLOWED_HOSTS`。
- Bearer 驗證使用 constant-time 比較。
- 狀態型 session 綁定建立它的認證主體。

---

## 安全模式

### 群號白名單

```env
ALLOWED_GROUPS=628101497
ALLOWED_GROUPS=628101497,123456789
```

正式部署不建議留空、`all` 或 `*`。

### 唯讀模式

```env
READONLY_MODE=true
```

首次連接 RikkaHub 時建議保持 `true`。確認查詢功能正常後，再決定是否開放寫入工具；RikkaHub 中所有發訊息、撤回、踢人、禁言、群設定和檔案操作工具都應開啟 **Needs Approval**。

---

## 工具

共 57 個工具，包括：

- 群資訊、群成員、群檔案、歷史訊息
- 發送/撤回訊息、合併轉發
- 群管理、公告、精華訊息
- 好友與使用者
- 登入狀態、版本、憑證
- OCR、圖片、語音及 NapCat 擴充功能

一般閱讀群聊時優先使用：

```text
read_group_messages(group_id, count)
```

它只返回人類可讀時間線，不攜帶訊息 ID、圖片 URL 等大型欄位。只有需要分頁、引用、撤回或原始 OneBot segment 時，才使用 `get_group_msg_history`。

---

## NapCat OneBot 配置示例

```json
{
  "network": {
    "httpServers": [
      {
        "enable": true,
        "name": "napcat mcp",
        "host": "127.0.0.1",
        "port": 3000,
        "enableCors": true,
        "enableWebsocket": true,
        "messagePostFormat": "array",
        "token": "your_napcat_token",
        "debug": false
      }
    ]
  }
}
```

NapCat WebUI 中應建立的是 **HTTP 服務端**，不是 HTTP 客戶端。

---

## 測試

```bash
python -m pip install -e ".[dev]"
pytest -q tests
ruff check src tests run_direct.py
```

測試包含：

- Streamable HTTP MCP 完整 initialize / tools/list
- Bearer Token 拒絕未授權請求
- 非本機監聽未設 Token 時拒絕啟動
- 57 個工具完整性
- 回應精簡與 19 位合併轉發 ID 精度

---

## 授權

AGPL-3.0
