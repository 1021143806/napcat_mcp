# Windows + RikkaHub + DeepSeek：從零部署 NapCat MCP

本教程給完全不熟悉命令列的使用者。最終結構：

```text
手機 RikkaHub
  ├─ 工作區 Shell ── SSH ──> Windows（讓模型部署/維護）
  └─ Streamable HTTP ───────> NapCat MCP :18080/mcp
                                      │
                                      └─ OneBot HTTP ──> NapCat :3000 ──> QQ
```

SSH 是部署通道，Streamable HTTP 是日常 MCP 工具通道。兩者不是同一回事。

---

## 1. 安裝 NapCat

### Windows AMD64 一鍵版

1. 打開 <https://github.com/NapNeko/NapCatQQ/releases>。
2. 下載 `NapCat.Shell.Windows.OneKey.zip`。
3. 解壓到例如 `C:\NapCat`。
4. 執行 `NapCatInstaller.exe`。
5. 進入生成的 `NapCat.XXXX.Shell` 目錄，執行 `napcat.bat`。
6. 啟動日誌會顯示類似：

   ```text
   http://127.0.0.1:6099/webui?token=xxxxx
   ```

7. 在 Windows 瀏覽器打開該網址，按提示登入 WebUI，並用手機 QQ 掃碼登入機器人帳號。

### 配置 OneBot HTTP

在 NapCat WebUI → **網路配置 → 新建 → HTTP 服務端**：

```text
名稱：napcat-mcp
啟用：是
Host：127.0.0.1
Port：3000
訊息格式：array
Token：自己生成一串長隨機密碼
Debug：否
```

保存並確認已啟用。

> WebUI 登入 Token 和 OneBot Token 是兩個不同的密碼。napcat_mcp 使用的是 OneBot Token。

在 PowerShell 測試：

```powershell
$Token = '你的 OneBot Token'
Invoke-RestMethod `
  -Uri 'http://127.0.0.1:3000/get_status' `
  -Headers @{ Authorization = "Bearer $Token" }
```

能返回 JSON 即成功。不要開放 NapCat 3000 防火牆。

---

## 2. 在 Windows 安裝 OpenSSH Server

這一步讓 RikkaHub 工作區中的模型可以登入 Windows 執行部署。

以**管理員身份**打開 PowerShell：

```powershell
$ErrorActionPreference = 'Stop'
$cap = Get-WindowsCapability -Online |
  Where-Object Name -Like 'OpenSSH.Server*' |
  Select-Object -First 1

if ($cap.State -ne 'Installed') {
  Add-WindowsCapability -Online -Name $cap.Name
}

Set-Service sshd -StartupType Automatic
Start-Service sshd
Get-Service sshd
Get-NetTCPConnection -LocalPort 22 -State Listen
```

若手機與 Windows 在同一 Wi-Fi，可以使用區域網路 IP；需要跨網路時，推薦兩邊安裝 Tailscale，不要直接做公網端口映射。

查 Windows IPv4：

```powershell
Get-NetIPAddress -AddressFamily IPv4 |
  Where-Object { $_.IPAddress -notlike '127.*' } |
  Select-Object InterfaceAlias,IPAddress
```

記下可從手機訪問的 IP，例如 `<WINDOWS-LAN-IP>`。

---

## 3. 在 RikkaHub 建工作區並接入 SSH

1. RikkaHub → **設定 → 擴充管理 → Workspace**。
2. 點 `+`，名稱填英文，例如 `napcat-deploy`。
3. 點進工作區 → **Install Rootfs**。
4. 打開右上角終端，執行：

   ```bash
   apt update && apt install -y openssh-client git
   mkdir -p ~/.ssh && chmod 700 ~/.ssh
   ssh-keygen -t ed25519 -f ~/.ssh/napcat_windows -N '' -C 'rikkahub-napcat-deploy'
   cat ~/.ssh/napcat_windows.pub
   ```

5. 複製最後輸出的整行 `.pub` 公鑰；不要複製或分享沒有 `.pub` 的私鑰。

### Windows 安裝公鑰

以管理員 PowerShell 執行，先替換公鑰內容：

```powershell
$PublicKey = 'ssh-ed25519 AAAA... rikkahub-napcat-deploy'
$File = "$env:ProgramData\ssh\administrators_authorized_keys"
New-Item -ItemType File -Path $File -Force | Out-Null
if ((Get-Content $File -ErrorAction SilentlyContinue) -notcontains $PublicKey) {
  Add-Content -Path $File -Value $PublicKey
}
icacls $File /inheritance:r
icacls $File /grant '*S-1-5-18:F' /grant '*S-1-5-32-544:F'
Restart-Service sshd
```

### 工作區測試 SSH

```bash
ssh -i ~/.ssh/napcat_windows \
  -o StrictHostKeyChecking=accept-new \
  Windows用戶名@<WINDOWS-LAN-IP> \
  'whoami'
```

成功後建立別名：

```bash
cat > ~/.ssh/config <<'EOF'
Host napcat-pc
    HostName <WINDOWS-LAN-IP>
    User Windows用戶名
    IdentityFile ~/.ssh/napcat_windows
    IdentitiesOnly yes
    ServerAliveInterval 30
EOF
chmod 600 ~/.ssh/config
ssh napcat-pc 'whoami'
```

返回聊天頁，把 `napcat-deploy` 工作區綁定給 DeepSeek 助手。沒有綁定工作區，模型不會獲得 Shell 工具。

---

## 4. 把下面整段發給 DeepSeek

先替換尖括號內的內容：

```text
你要使用 RikkaHub 工作區 Shell，透過 `ssh napcat-pc` 直接在 Windows 部署 NapCat MCP。

項目：https://github.com/1021143806/napcat_mcp
Windows SSH 別名：napcat-pc
NapCat 地址：http://127.0.0.1:3000
NapCat OneBot Token：<填 OneBot Token>
允許群號：<填群號，多個用英文逗號>
Windows 區域網路/Tailscale IP：<例如 <WINDOWS-LAN-IP>>

必須遵守：
1. 直接執行，不要只寫教程。
2. 開始先執行 `ssh napcat-pc 'whoami'`。
3. 複雜 PowerShell 先在工作區寫成 .ps1，再用 stdin 執行：
   `cat script.ps1 | ssh napcat-pc 'powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command -'`
4. 不得關閉防火牆、殺毒軟體或系統安全功能。
5. 不得開放 NapCat 的 3000 端口；NAPCAT_HOST 固定為 http://127.0.0.1:3000。
6. 首次部署 READONLY_MODE=true，ALLOWED_GROUPS 必須是我給的群號。
7. 不得回顯 Token、密碼、Cookie 或 SSH 私鑰。
8. 本項目已原生支援 Streamable HTTP，不要安裝 Supergateway、MCPHub 或其他代理。
9. 不要使用舊包名 napcat_group_info_mcp。
10. 遇到需要 UAC 的操作就停止，告訴我需要人工執行的那一條管理員命令。

依序完成：

A. 檢查 Windows 上的 git 與 Python；Python 必須 >=3.10。缺少時優先用 winget 安裝 Git.Git 和 Python.Python.3.12。

B. clone 到 C:\NapCatMCP；已存在且無本地修改時 git pull --ff-only；不得覆蓋本地修改。

C. 建立 C:\NapCatMCP\.venv，使用虛擬環境 Python 執行：
   `-m pip install --upgrade pip`
   `-m pip install -e .`

D. 複製 `.env.example` 為 `.env`，填入：
   NAPCAT_HOST=http://127.0.0.1:3000
   NAPCAT_TOKEN=<上方 OneBot Token>
   ALLOWED_GROUPS=<上方群號>
   READONLY_MODE=true
   NAPCAT_RESPONSE_MODE=compact
   MCP_TRANSPORT=streamable-http
   MCP_HTTP_HOST=<Windows IP>
   MCP_HTTP_PORT=18080
   MCP_HTTP_PATH=/mcp
   MCP_BEARER_TOKEN=<生成另一串至少 32 bytes 的密碼，不得與 OneBot Token 相同>

E. 限制 `.env` ACL，只允許目前使用者、SYSTEM 和 Administrators 讀取。

F. 啟動 `start-http.bat`，並建立登入時自啟的計畫任務。確認：
   - http://127.0.0.1:3000/get_status 可帶 OneBot Token 訪問
   - http://<Windows IP>:18080/healthz 返回 ok
   - 未帶 MCP Bearer Token 訪問 /mcp 返回 401
   - 帶 Token 完成 MCP initialize 與 tools/list，應有 57 個工具

G. 新建防火牆規則 `NapCat MCP for RikkaHub`，只允許 Private 網路的 TCP 18080；如果能取得手機的固定 Tailscale IP，再把 RemoteAddress 限制為該 IP。不要開放 3000。

最後只回報：
- SSH：成功/失敗
- 安裝目錄：
- NapCat HTTP：成功/失敗
- Streamable HTTP：成功/失敗
- 工具數：
- 只讀：true
- RikkaHub URL：
- RikkaHub Header 名稱：Authorization
- RikkaHub Header 值格式：Bearer <Token，不要顯示實際值>
- 仍需人工操作：
```

---

## 5. 在 RikkaHub 添加 MCP

DeepSeek 完成後：

1. **設定 → MCP → `+` → Streamable HTTP**。
2. 名稱：`NapCat`。
3. URL：

   ```text
   http://<WINDOWS-LAN-IP>:18080/mcp
   ```

4. 自訂 Header：

   ```text
   Authorization: Bearer 你的_MCP_BEARER_TOKEN
   ```

5. 保存並等待 `Connected`，應顯示 57 個工具。
6. 在助手設定中把 `NapCat` MCP 勾選給 DeepSeek。
7. 第一次只啟用 `get_status`、`get_login_info`、`get_group_list`、`read_group_messages` 等只讀工具。
8. 所有發訊息、撤回、踢人、禁言、群設定、公告、好友請求及檔案工具都開啟 **Needs Approval**。

測試：

```text
只調用 NapCat 的 get_status，禁止任何寫入操作。
```

---

## 常見問題

### RikkaHub 連不上 18080

Windows 檢查：

```powershell
Get-NetTCPConnection -LocalPort 18080 -State Listen
Get-NetFirewallRule -DisplayName 'NapCat MCP for RikkaHub'
```

手機和 Windows 必須在同一區域網路，或同時連上 Tailscale。

### `/mcp` 返回 401

這代表網路已通，但 RikkaHub Header 缺失或錯誤。填：

```text
Authorization
Bearer <MCP_BEARER_TOKEN>
```

不要填 OneBot Token。

### NapCat API 返回 401

`.env` 的 `NAPCAT_TOKEN` 必須等於 NapCat WebUI 中 HTTP 服務端的 OneBot Token。

### `Invalid Host header` / HTTP 421

若 `MCP_HTTP_HOST=0.0.0.0`，必須配置：

```env
MCP_ALLOWED_HOSTS=<WINDOWS-LAN-IP>:18080
```

更推薦直接讓 `MCP_HTTP_HOST` 綁定實際 IP。

### 找不到 `napcat_mcp`

確保使用：

```powershell
C:\NapCatMCP\.venv\Scripts\python.exe -m pip install -e C:\NapCatMCP
```

不要用舊文件中的 `napcat_group_info_mcp`。

### 關於安全

- `MCP_BEARER_TOKEN` 與 `NAPCAT_TOKEN` 必須不同。
- Bearer Token 在純 HTTP 中不加密；僅限可信 Wi-Fi/Tailscale。
- 跨公網請使用 HTTPS 反向代理，不要直接映射 18080。
- 不使用 SSH 後，可以停用 `sshd` 並刪除專用公鑰。
