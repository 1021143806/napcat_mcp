# NapCat MCP Server

封装 NapCat 所有 HTTP API 的 MCP 服务器，支持 HTTP 和 WebSocket 双模式。

> 基于 napcat-group-info-mcp 扩展，新增消息发送、群管理、好友管理、系统管理等全量 API。

## 功能特性

- 📋 群聊信息获取（只读）
- 👥 群成员信息获取（只读）
- 📁 群文件管理（读写）
- 💬 消息发送与管理
- 📢 群公告管理
- ⭐ 群精华消息管理
- 👤 好友/用户管理
- 🔧 群管理操作（踢人、禁言、管理员等）
- 🖥️ 系统管理（登录信息、状态等）
- 🎨 Napcat 扩展功能（OCR、图片、语音等）
- 🔒 支持群号访问限制
- 🔐 支持只读模式
- 🌐 支持 HTTP 和 WebSocket 双模式

## 安装

```bash
git clone https://github.com/1021143806/napcat_mcp.git
cd napcat_mcp
pip install -e .
```

## 配置

在 MCP 客户端配置文件中添加：

```json
{
  "mcpServers": {
    "napcat-mcp": {
      "command": "python",
      "args": ["path/to/run_direct.py"],
      "env": {
        "NAPCAT_HOST": "http://localhost:3000",
        "NAPCAT_TOKEN": "your_token_here",
        "ALLOWED_GROUPS": "",
        "READONLY_MODE": "false"
      }
    }
  }
}
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `NAPCAT_HOST` | NapCat 服务器地址 | `http://localhost:3000` |
| `NAPCAT_TOKEN` | NapCat 访问令牌 | 空 |
| `ALLOWED_GROUPS` | 允许访问的群号（逗号分隔），留空=全部 | 空 |
| `READONLY_MODE` | 只读模式（true/false） | `false` |

### 连接模式

根据 `NAPCAT_HOST` 前缀自动选择：
- `http://` 或 `https://` → HTTP 模式
- `ws://` 或 `wss://` → WebSocket 模式

## 安全特性

### 群号访问限制

```bash
ALLOWED_GROUPS=                    # 允许所有群
ALLOWED_GROUPS=628101497           # 只允许单个群
ALLOWED_GROUPS=628101497,123456789 # 允许多个群
```

### 只读模式

```bash
READONLY_MODE=true                 # 禁用所有写入操作
```

## 可用工具（55 个）

### 群聊信息（16 个）
`get_group_info` `get_group_info_ex` `get_group_list` `get_group_honor_info` `get_group_at_all_remain` `get_group_member_list` `get_group_member_info` `get_group_root_files` `get_group_files_by_folder` `get_group_file_system_info` `get_group_file_url` `get_group_msg_history` `get_group_announcement_list` `get_essence_msg_list` `get_group_system_msg` `get_group_ignore_add_request`

### 消息发送与管理（8 个）
`send_msg` `send_group_msg` `send_private_msg` `delete_msg` `get_msg` `get_forward_msg` `send_group_forward_msg` `mark_msg_as_read`

### 群管理（13 个）
`set_group_kick` `set_group_ban` `set_group_whole_ban` `set_group_admin` `set_group_card` `set_group_name` `set_group_leave` `set_group_special_title` `set_group_add_request` `upload_group_file` `delete_group_file` `send_group_notice` `set_essence_msg` `delete_essence_msg`

### 好友/用户（5 个）
`get_friend_list` `get_stranger_info` `get_friend_msg_history` `send_like` `set_friend_add_request`

### 系统管理（6 个）
`get_login_info` `get_status` `get_version_info` `get_cookies` `get_csrf_token` `get_credentials`

### Napcat 扩展（7 个）
`ocr_image` `get_image` `get_record` `can_send_image` `can_send_record` `get_online_client` `set_qq_profile`

## NapCat 配置

确保 NapCat 的 OneBot11 配置中启用了 HTTP 服务器：

```json
{
  "network": {
    "httpServers": [{
      "enable": true,
      "name": "napcat mcp",
      "host": "127.0.0.1",
      "port": 3000,
      "enableCors": true,
      "enableWebsocket": true,
      "messagePostFormat": "array",
      "token": "your_token_here",
      "debug": false
    }]
  }
}
```

## 技术细节

- 基于 OneBot11 标准
- 兼容 NapCat 4.9.91+
- HTTP 模式使用 `httpx` 异步客户端
- WebSocket 模式使用 `websockets` 库
- 使用 Pydantic 进行参数验证

## 许可证

AGPL-3.0
