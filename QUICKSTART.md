# 快速启动指南

## 方式一：直接运行（推荐，无需安装）

### 1. 测试运行

双击运行 `quick_test.bat` 或在命令行执行：

```bash
python run_direct.py
```

### 2. 在 Claude Desktop 中配置

编辑 Claude Desktop 配置文件，添加：

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "napcat-group-info": {
      "command": "python",
      "args": ["C:\\Users\\h3189\\server\\maibot\\maibot\\MaiBot-0.12.2\\napcat_group_info_mcp\\run_direct.py"],
      "env": {
        "NAPCAT_HOST": "http://localhost:3000",
        "NAPCAT_TOKEN": "your_token_here",
        "ALLOWED_GROUPS": "628101497"
      }
    }
  }
}
```

**注意：** 请将路径 `C:\\Users\\h3189\\server\\maibot\\maibot\\MaiBot-0.12.2\\napcat_group_info_mcp\\run_direct.py` 替换为你实际的完整路径。

### 3. 获取完整路径

在项目目录下执行：

```bash
cd /d C:\Users\h3189\server\maibot\maibot\MaiBot-0.12.2\napcat_group_info_mcp
python -c "import os; print(os.path.abspath('run_direct.py'))"
```

复制输出的路径到配置文件中。

## 方式二：安装后运行

### 1. 安装包

```bash
cd napcat_group_info_mcp
pip install -e .
```

### 2. 在 Claude Desktop 中配置

```json
{
  "mcpServers": {
    "napcat-group-info": {
      "command": "python",
      "args": ["-m", "napcat_group_info_mcp"],
      "env": {
        "NAPCAT_HOST": "http://localhost:3000",
        "NAPCAT_TOKEN": "your_token_here",
        "ALLOWED_GROUPS": "628101497"
      }
    }
  }
}
```

## 环境变量说明

- `NAPCAT_HOST`: NapCat 服务器地址（默认: http://localhost:3000）
- `NAPCAT_TOKEN`: NapCat 访问令牌（可选）
- `ALLOWED_GROUPS`: 允许访问的群号
  - 留空或设置为 `all`：允许所有群
  - 设置为 `628101497`：只允许这个群
  - 设置为 `628101497,123456789`：允许多个群

## 测试连接

运行测试脚本：

```bash
python test_client.py
```

如果成功，会显示群列表和各种信息。

## 故障排除

### 问题 1: 找不到模块

**解决方法：** 使用方式一（直接运行），不需要安装。

### 问题 2: 连接失败

**检查：**
1. NapCat 是否正在运行
2. `NAPCAT_HOST` 是否正确
3. 防火墙是否阻止连接

### 问题 3: 权限拒绝

**检查：**
1. `ALLOWED_GROUPS` 是否正确配置
2. 群号是否在允许列表中

## 启动日志

服务器启动时会显示：

```
============================================================
NapCat Group Info MCP Server
============================================================
✓ 权限配置: 只允许访问群 628101497
============================================================
```

这表示服务器已成功启动并配置了权限。