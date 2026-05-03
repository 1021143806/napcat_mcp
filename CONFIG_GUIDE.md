# Claude Desktop 配置指南

## 步骤 1: 找到配置文件

**Windows:** 打开文件资源管理器，输入 `%APPDATA%\Claude\`，找到 `claude_desktop_config.json`

**macOS:** 打开终端，输入 `open ~/Library/Application\ Support/Claude/`

**Linux:** 打开终端，输入 `xdg-open ~/.config/Claude/`

## 步骤 2: 编辑配置文件

用文本编辑器（如记事本、VS Code）打开 `claude_desktop_config.json`

## 步骤 3: 添加 MCP 服务器配置

将以下内容添加到配置文件中（注意修改路径）：

```json
{
  "mcpServers": {
    "napcat-group-info": {
      "command": "python",
      "args": ["C:\\Users\\h3189\\server\\maibot\\maibot\\MaiBot-0.12.2\\napcat_group_info_mcp\\run_direct.py"],
      "env": {
        "NAPCAT_HOST": "http://localhost:3000",
        "NAPCAT_TOKEN": "",
        "ALLOWED_GROUPS": "628101497"
      }
    }
  }
}
```

**重要：** 如果配置文件中已经有其他 MCP 服务器，只需要添加 `"napcat-group-info"` 部分，注意逗号的位置。

## 步骤 4: 修改路径

将 `C:\\Users\\h3189\\server\\maibot\\maibot\\MaiBot-0.12.2\\napcat_group_info_mcp\\run_direct.py` 替换为你的实际路径。

**获取实际路径的方法：**

在项目目录下打开命令行，执行：

```bash
cd /d C:\Users\h3189\server\maibot\maibot\MaiBot-0.12.2\napcat_group_info_mcp
python -c "import os; print(os.path.abspath('run_direct.py'))"
```

复制输出的路径，注意将 `\` 替换为 `\\`（双反斜杠）。

## 步骤 5: 配置环境变量

根据需要修改以下环境变量：

- `NAPCAT_HOST`: NapCat 服务器地址
- `NAPCAT_TOKEN`: NapCat 访问令牌（如果没有设置鉴权，留空）
- `ALLOWED_GROUPS`: 允许访问的群号
  - 留空或 `all`: 允许所有群
  - `628101497`: 只允许群 628101497
  - `628101497,123456789`: 允许多个群

## 步骤 6: 保存并重启

1. 保存配置文件
2. 完全退出 Claude Desktop
3. 重新启动 Claude Desktop

## 步骤 7: 验证

在 Claude Desktop 中输入：

```
获取群 628101497 的详细信息
```

如果成功返回群信息，说明配置成功！

## 完整配置示例

如果你的配置文件是空的，完整内容如下：

```json
{
  "mcpServers": {
    "napcat-group-info": {
      "command": "python",
      "args": ["C:\\Users\\h3189\\server\\maibot\\maibot\\MaiBot-0.12.2\\napcat_group_info_mcp\\run_direct.py"],
      "env": {
        "NAPCAT_HOST": "http://localhost:3000",
        "NAPCAT_TOKEN": "",
        "ALLOWED_GROUPS": "628101497"
      }
    }
  }
}
```

如果已经有其他 MCP 服务器，例如：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"]
    },
    "napcat-group-info": {
      "command": "python",
      "args": ["C:\\Users\\h3189\\server\\maibot\\maibot\\MaiBot-0.12.2\\napcat_group_info_mcp\\run_direct.py"],
      "env": {
        "NAPCAT_HOST": "http://localhost:3000",
        "NAPCAT_TOKEN": "",
        "ALLOWED_GROUPS": "628101497"
      }
    }
  }
}
```

注意 `"filesystem"` 后面的逗号。

## 常见问题

### Q: 启动后 Claude Desktop 没有反应

A: 检查配置文件格式是否正确，特别是 JSON 的逗号和引号。

### Q: 提示找不到文件

A: 检查路径是否正确，注意使用双反斜杠 `\\`。

### Q: 提示权限拒绝

A: 检查 `ALLOWED_GROUPS` 是否包含你要访问的群号。

### Q: 连接失败

A: 检查 NapCat 是否正在运行，`NAPCAT_HOST` 是否正确。