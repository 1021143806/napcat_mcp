# NapCat Group Info MCP Server - 项目总结

## 项目概述

这是一个专门用于获取 NapCat 群聊信息的**只读型** MCP (Model Context Protocol) 服务器。该工具提供了 11 个只读工具，可以安全地获取群聊信息、成员信息、群文件和历史消息，而不会对群聊进行任何修改操作。

## 项目结构

```
napcat_group_info_mcp/
├── src/
│   ├── __init__.py                    # 包初始化文件
│   ├── napcat_client.py               # NapCat API 客户端
│   ├── server.py                      # MCP 服务器主文件
│   └── napcat_group_info_mcp/
│       └── __main__.py                # 包入口点
├── .env.example                       # 环境变量配置示例
├── mcp_config_example.json            # MCP 客户端配置示例
├── pyproject.toml                     # Python 项目配置
├── README.md                          # 项目说明
├── USAGE.md                           # 详细使用说明
├── test_client.py                     # 测试脚本
├── start.bat                          # Windows 启动脚本
├── start.sh                           # Linux/Mac 启动脚本
└── PROJECT_SUMMARY.md                 # 本文件
```

## 核心功能

### 1. 群聊信息获取（4 个工具）
- **get_group_info**: 获取群详细信息
- **get_group_list**: 获取群列表
- **get_group_honor_info**: 获取群荣誉信息
- **get_group_at_all_remain**: 获取@全体成员剩余次数

### 2. 群成员信息获取（2 个工具）
- **get_group_member_list**: 获取群成员列表
- **get_group_member_info**: 获取群成员详细信息

### 3. 群文件获取（4 个工具）
- **get_group_root_files**: 获取群根目录文件列表
- **get_group_files_by_folder**: 获取群子目录文件列表
- **get_group_file_system_info**: 获取群文件系统信息
- **get_group_file_url**: 获取群文件下载链接

### 4. 历史消息获取（1 个工具）
- **get_group_msg_history**: 获取群历史消息

## 技术特点

1. **只读设计**: 所有工具均为只读操作，确保数据安全
2. **完全异步**: 使用 asyncio 和 httpx 实现高性能异步请求
3. **类型安全**: 使用 Pydantic 进行参数验证和类型检查
4. **错误处理**: 完善的异常处理和友好的错误提示
5. **易于配置**: 通过环境变量灵活配置 NapCat 连接
6. **标准协议**: 完全遵循 MCP 协议规范

## 依赖项

- `mcp>=1.0.0` - MCP 协议 SDK
- `httpx>=0.27.0` - 异步 HTTP 客户端
- `pydantic>=2.0.0` - 数据验证

## 快速开始

### 1. 安装依赖
```bash
cd napcat_group_info_mcp
pip install -e .
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置 NAPCAT_HOST 和 NAPCAT_TOKEN
```

### 3. 测试连接
```bash
python test_client.py
```

### 4. 在 Claude Desktop 中配置
编辑配置文件，添加：
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

### 5. 启动使用
重启 Claude Desktop，即可在对话中使用所有工具。

## 使用示例

### 查看群信息
```
帮我查看群 628101497 的详细信息
```

### 获取成员列表
```
获取群 628101497 的所有成员
```

### 查看群文件
```
查看群 628101497 根目录下的文件
```

### 获取历史消息
```
获取群 628101497 最近的 30 条消息
```

## 安全特性

1. **只读操作**: 不提供任何写入、修改、删除功能
2. **权限控制**: 通过 NapCat 的 Token 机制进行鉴权
3. **参数验证**: 所有输入参数都经过严格验证
4. **错误隔离**: 错误不会影响其他工具的正常运行

## 测试说明

项目包含完整的测试脚本 `test_client.py`，可以测试所有 API 功能：

```bash
python test_client.py
```

测试脚本会依次测试：
- 获取群列表
- 获取群详细信息
- 获取群成员列表
- 获取群荣誉信息
- 获取@全体成员剩余次数
- 获取群文件系统信息
- 获取群根目录文件列表
- 获取群历史消息

## 注意事项

1. **NapCat 版本**: 需要 NapCat 4.9.91 或更高版本
2. **OneBot 接口**: 确保 NapCat 已启用 OneBot 接口
3. **网络连接**: 确保 MCP 客户端可以访问 NapCat 服务器
4. **权限要求**: 某些操作可能需要管理员权限
5. **频率限制**: 避免频繁调用，以免被限流

## 扩展建议

如果需要添加更多功能，可以考虑：

1. **群相册功能**: 获取群相册列表、图片等
2. **群公告功能**: 获取群公告信息
3. **群精华消息**: 获取群精华消息列表
4. **群禁言列表**: 获取群禁言成员列表
5. **群荣誉详情**: 获取更详细的群荣誉信息

## 许可证

AGPL-3.0

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 查看文档: README.md, USAGE.md

## 更新日志

### v0.1.0 (2025-01-20)
- ✨ 初始版本发布
- ✅ 实现群聊信息获取（4 个工具）
- ✅ 实现群成员信息获取（2 个工具）
- ✅ 实现群文件获取（4 个工具）
- ✅ 实现历史消息获取（1 个工具）
- ✅ 完整的文档和测试脚本
- ✅ Windows 和 Linux 启动脚本