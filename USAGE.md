# NapCat Group Info MCP Server - 使用说明

## 快速开始

### 1. 安装依赖

```bash
cd napcat_group_info_mcp
pip install -e .
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
NAPCAT_HOST=http://localhost:3000
NAPCAT_TOKEN=your_token_here
```

### 3. 在 Claude Desktop 中配置

编辑 Claude Desktop 配置文件：

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

添加以下配置：

```json
{
  "mcpServers": {
    "napcat-group-info": {
      "command": "python",
      "args": ["-m", "napcat_group_info_mcp"],
      "env": {
        "NAPCAT_HOST": "http://localhost:3000",
        "NAPCAT_TOKEN": "your_token_here"
      }
    }
  }
}
```

### 4. 重启 Claude Desktop

重启 Claude Desktop 后，即可在对话中使用 NapCat 群聊信息获取功能。

## 可用工具列表

### 群聊信息

#### get_group_info
获取群详细信息

**参数:**
- `group_id` (int): 群号

**示例:**
```
获取群 628101497 的详细信息
```

#### get_group_list
获取当前账号加入的所有群列表

**参数:** 无

**示例:**
```
获取我加入的所有群列表
```

#### get_group_honor_info
获取群荣誉信息

**参数:**
- `group_id` (int): 群号
- `type` (string, 可选): 荣誉类型
  - `talkative` - 龙王
  - `performer` - 群聊炽焰
  - `legend` - 传奇新人
  - `strong_newbie` - 聊得火热
  - `emotion` - 快乐源泉
  - `all` - 所有荣誉（默认）

**示例:**
```
获取群 628101497 的龙王荣誉
```

#### get_group_at_all_remain
获取群@全体成员剩余次数

**参数:**
- `group_id` (int): 群号

**示例:**
```
获取群 628101497 的@全体成员剩余次数
```

### 群成员信息

#### get_group_member_list
获取群成员列表

**参数:**
- `group_id` (int): 群号

**示例:**
```
获取群 628101497 的成员列表
```

#### get_group_member_info
获取指定群成员的详细信息

**参数:**
- `group_id` (int): 群号
- `user_id` (int): 用户 QQ 号

**示例:**
```
获取群 628101497 中用户 123456789 的详细信息
```

### 群文件

#### get_group_root_files
获取群根目录文件列表

**参数:**
- `group_id` (int): 群号

**示例:**
```
获取群 628101497 根目录的文件列表
```

#### get_group_files_by_folder
获取群指定文件夹内的文件列表

**参数:**
- `group_id` (int): 群号
- `folder_id` (string, 可选): 文件夹 ID，空字符串表示根目录

**示例:**
```
获取群 628101497 中文件夹 abc123 的文件列表
```

#### get_group_file_system_info
获取群文件系统信息

**参数:**
- `group_id` (int): 群号

**示例:**
```
获取群 628101497 的文件系统信息
```

#### get_group_file_url
获取群文件的下载链接

**参数:**
- `group_id` (int): 群号
- `file_id` (string): 文件 ID
- `busid` (int, 可选): 文件类型，默认 0

**示例:**
```
获取群 628101497 中文件 file123 的下载链接
```

### 历史消息

#### get_group_msg_history
获取群历史消息

**参数:**
- `group_id` (int): 群号
- `message_seq` (int, 可选): 起始消息序号，0 表示最新消息
- `count` (int, 可选): 获取数量，默认 20

**示例:**
```
获取群 628101497 的最近 50 条消息
```

## 使用示例

### 示例 1: 查看群基本信息

```
帮我查看群 628101497 的基本信息，包括群名称、成员数量等
```

### 示例 2: 获取群成员列表

```
获取群 628101497 的所有成员列表
```

### 示例 3: 查看群文件

```
查看群 628101497 根目录下有哪些文件
```

### 示例 4: 获取历史消息

```
获取群 628101497 最近的 30 条消息
```

### 示例 5: 组合查询

```
帮我查看群 628101497 的详细信息，然后获取该群的成员列表，最后看看群文件
```

## 故障排除

### 连接失败

如果遇到连接失败，请检查：

1. NapCat 服务器是否正在运行
2. `NAPCAT_HOST` 配置是否正确
3. 防火墙是否阻止了连接
4. NapCat 是否配置了正确的 OneBot 接口

### 权限问题

如果遇到权限错误，请检查：

1. `NAPCAT_TOKEN` 是否正确配置
2. NapCat 是否启用了鉴权
3. 当前账号是否有足够的权限访问群信息

### 工具调用失败

如果工具调用失败，请检查：

1. 群号是否正确
2. 当前账号是否在该群中
3. 群是否仍然存在

## 注意事项

1. **只读操作**: 本 MCP 服务器仅提供只读功能，不会修改任何数据
2. **权限限制**: 某些操作可能需要管理员权限
3. **频率限制**: 避免频繁调用，以免被 NapCat 限流
4. **数据隐私**: 请确保遵守相关隐私法规和群规

## 技术支持

如有问题，请查看：
- [NapCat API 文档](https://napcat.apifox.cn/5430207m0)
- [MCP 协议文档](https://modelcontextprotocol.io/)