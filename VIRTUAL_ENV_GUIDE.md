# 虛擬環境

## Windows

```powershell
cd C:\NapCatMCP
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .
```

啟動 stdio：

```powershell
.\.venv\Scripts\python.exe -m napcat_mcp --transport stdio
```

啟動 Streamable HTTP：

```powershell
Copy-Item .env.example .env
# 編輯 .env 後：
.\.venv\Scripts\python.exe -m napcat_mcp --transport streamable-http
```

## Linux/macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .
.venv/bin/python -m napcat_mcp --transport stdio
```

完整說明見 [README.md](README.md)。
