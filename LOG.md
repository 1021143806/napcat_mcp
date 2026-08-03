# napcat mcp 更改日誌

> 本日誌從 AGENT.md 拆分而來（2026-07-21），記錄本項目的詳細更改歷史。
> AGENT.md 僅保留簡略索引，完整細節見此文件。
---

【napcat_mcp MCP 回應精簡（2026-07-20）】
- 專案本地：`/workspace/napcat_mcp/`；VPS：`/main/app/github/mcphub/napcat_mcp/`；實測對象 `napcat_8_claude`
- 根因：原最新版僅把 JSON 改成無縮排，OneBot 歷史每筆仍重複 self_id/post_type/group_id/group_name/sender/raw_message 等；合併轉發內又遞迴重複；群成員列表每行重複全部 key
- 新增 `NAPCAT_RESPONSE_MODE`：預設 `compact` 面向 LLM；`full`/`raw`/`lossless` 可保留完整原始回應
- compact：歷史/get_msg/轉發統一保留 seq,id,time,user_id,name,message，合併轉發節點遞迴精簡；群成員/群列表/好友列表改 `columns + rows + count` 表格格式
- 真實資料 benchmark（內容未輸出/未帶離 VPS）：群列表 1112→480 B(-56.8%)；333群成員 108657→26491 B(-75.6%)；184條歷史 146520→54602 B(-62.7%)
- 測試：`tests/` 8 passed；部署後 Claude 20條歷史實際輸出 5736 B，keys 為 seq/id/time/user_id/name/message，raw_message/sender 已去重
- VPS 已部署；共享同一源碼的其他 NapCat 實例均顯式設 `full` 避免改變既有行為，只有 `napcat_8_claude.env` 設 `compact` 作實做案例；`supervisorctl restart mcphub` 後 pid 950429 RUNNING，56 tools 列出成功
- 備份：VPS `src/napcat_mcp/server.py.bak.response-compact.20260720-234643`、`/main/app/github/mcphub/mcp_settings.json.bak.response-compact.20260720-234643`
- 詳細設計/數據：`/workspace/napcat_mcp/RESPONSE_COMPACTION.md`


【獨立輕量讀群消息工具（2026-07-23）】
- 新增 `read_group_messages(group_id,count)`，專供 LLM 閱讀群聊；原 `get_group_msg_history` 保留給分頁、引用、撤回及原始 segment 等操作場景
- 返回純文字時間線：日期標題 + `HH:MM 顯示名: 正文`；不返回 seq/id、事件 metadata、群號；有顯示名時不返回 QQ 號
- 純文字直接輸出；圖片/回覆/語音/影片/檔案/轉發等變短標記，丟棄附件 URL、file 等大欄位；多行正文轉義為單行，防止格式混淆
- count 限制 1-100；沿用 ALLOWED_GROUPS 權限檢查
- 真實 Claude 群 17 條抽樣：原始 12887 B、既有 compact JSON 4765 B、新 light 1065 B（比原始少91.7%，比 compact 少77.6%）；未輸出聊天正文
- 測試：10 passed；工具列表 57 entries / 57 unique；詳細說明見 `RESPONSE_COMPACTION.md`
- commit `fd3003c`；已部署 VPS 並重啟 MCPHub（pid 349873），`napcat_8_claude` 成功連線/列出 57 tools；live call 20條輸出1065 B/22行、純文字、無 seq/id key
- VPS 備份：`src/napcat_mcp/server.py.bak.light-reader.20260723-080002`



---

【NapCat MCP 原生 Streamable HTTP 與 RikkaHub 部署（2026-08-03）】
- 版本升至 0.3.0；新增原生 MCP Streamable HTTP，不再需要 Supergateway/MCPHub 轉發；stdio 保持預設以相容既有客戶端。
- 新增 `src/napcat_mcp/http_transport.py`：Starlette/Uvicorn + 官方 `StreamableHTTPSessionManager`，提供 `/mcp` 與 `/healthz`。
- HTTP 安全：遠端監聽強制 `MCP_BEARER_TOKEN`；靜態 Bearer 使用 constant-time 比較；stateful session 綁定認證主體；啟用 DNS rebinding Host/Origin 驗證；監聽通配地址時強制填 `MCP_ALLOWED_HOSTS`。
- 修正原本所有啟動 `print()` 寫 stdout、可能污染 stdio MCP 協議的問題，統一改寫 stderr。
- 修正 `__main__.py`、`run_direct.py` 與 `start.bat/start.sh` 的舊 async 入口/舊包名；新增 `start-http.bat/start-http.sh`。
- 加入 `.env` 自動讀取與完整 HTTP 設定範例；MCP SDK 鎖定 `>=1.28,<2`（需要 session owner/idle timeout 能力）。
- README 重寫，新增 `docs/RIKKAHUB_WINDOWS.md`：NapCat 安裝、Windows OpenSSH、RikkaHub Workspace SSH、公鑰、DeepSeek 可直接執行的部署提示、RikkaHub Header 配置與排障。
- 測試：12 passed；ruff 全過；原生 HTTP initialize/tools/list 57 tools；無 Token 401；遠端無 Token 拒絕啟動；stdio initialize/tools/list 57 tools。
