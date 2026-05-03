"""
NapCat Full MCP Server
封装 NapCat 所有 HTTP API 的 MCP 服务器（支持 HTTP 和 WebSocket 双模式）
"""

import asyncio
import json
import os
from typing import Any, Optional, Set

from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field

from .napcat_client import NapCatClient


# ============================================================================
# 配置
# ============================================================================

ALLOWED_GROUPS: Optional[Set[int]] = None
READONLY_MODE: bool = False
DISABLED_TOOLS: Set[str] = set()

allowed_groups_str = os.getenv("ALLOWED_GROUPS", "").strip()

if not allowed_groups_str or allowed_groups_str.lower() in ("all", "*"):
    ALLOWED_GROUPS = None
    print("✓ 权限配置: 允许访问所有群")
else:
    try:
        ALLOWED_GROUPS = set(int(g.strip()) for g in allowed_groups_str.split(",") if g.strip())
        print(f"✓ 权限配置: 只允许访问群 {', '.join(map(str, sorted(ALLOWED_GROUPS)))}")
    except ValueError:
        print(f"警告: ALLOWED_GROUPS 环境变量格式错误: {allowed_groups_str}")
        print("警告: 将允许访问所有群")
        ALLOWED_GROUPS = None

readonly_str = os.getenv("READONLY_MODE", "false").strip().lower()
READONLY_MODE = readonly_str in ("true", "1", "yes")
if READONLY_MODE:
    print("✓ 只读模式: 已启用")
else:
    print("✓ 读写模式: 已启用")

disabled_str = os.getenv("DISABLED_TOOLS", "").strip()
if disabled_str:
    DISABLED_TOOLS = set(t.strip() for t in disabled_str.split(",") if t.strip())
    print(f"✓ 禁用工具: {', '.join(sorted(DISABLED_TOOLS))}")
else:
    print("✓ 禁用工具: 无")


def is_group_allowed(group_id: int) -> bool:
    if ALLOWED_GROUPS is None:
        return True
    return group_id in ALLOWED_GROUPS


# ============================================================================
# 请求参数模型
# ============================================================================

class GroupIdParam(BaseModel):
    group_id: int = Field(description="Group ID")

class GroupHonorParam(GroupIdParam):
    type: str = Field(default="all", description="Honor type (talkative/performer/legend/strong_newbie/emotion/all)")

class GroupMemberInfoParam(BaseModel):
    group_id: int = Field(description="Group ID")
    user_id: int = Field(description="User QQ number")

class GroupFilesByFolderParam(BaseModel):
    group_id: int = Field(description="Group ID")
    folder_id: str = Field(default="", description="Folder ID")

class GroupFileUrlParam(BaseModel):
    group_id: int = Field(description="Group ID")
    file_id: str = Field(description="File ID")
    busid: int = Field(default=0, description="File type")

class GroupMsgHistoryParam(BaseModel):
    group_id: int = Field(description="Group ID")
    message_seq: int = Field(default=0, description="Starting message sequence number")
    count: int = Field(default=20, description="Count to retrieve")

class FriendMsgHistoryParam(BaseModel):
    user_id: int = Field(description="User QQ number")
    message_seq: int = Field(default=0, description="Starting message sequence number")
    count: int = Field(default=20, description="Count to retrieve")

class SendMsgParam(BaseModel):
    message_type: str = Field(description="Message type (group/private)")
    user_id: Optional[int] = Field(default=None, description="User QQ number")
    group_id: Optional[int] = Field(default=None, description="Group ID")
    message: str = Field(description="Message content")
    auto_escape: bool = Field(default=False, description="Whether to auto-escape")

class SendGroupMsgParam(BaseModel):
    group_id: int = Field(description="Group ID")
    message: str = Field(description="Message content")
    auto_escape: bool = Field(default=False, description="Whether to auto-escape")

class SendPrivateMsgParam(BaseModel):
    user_id: int = Field(description="User QQ number")
    message: str = Field(description="Message content")
    auto_escape: bool = Field(default=False, description="Whether to auto-escape")

class DeleteMsgParam(BaseModel):
    message_id: int = Field(description="Message ID")

class GetMsgParam(BaseModel):
    message_id: int = Field(description="Message ID")

class GetForwardMsgParam(BaseModel):
    message_id: int = Field(description="Message ID")

class SendGroupForwardMsgParam(BaseModel):
    group_id: int = Field(description="Group ID")
    messages: str = Field(description="Forward message content (JSON string)")

class MarkMsgAsReadParam(BaseModel):
    message_id: int = Field(description="Message ID")

class SetGroupKickParam(BaseModel):
    group_id: int = Field(description="Group ID")
    user_id: int = Field(description="User QQ number")
    reject_add_request: bool = Field(default=False, description="Whether to reject join request")

class SetGroupBanParam(BaseModel):
    group_id: int = Field(description="Group ID")
    user_id: int = Field(description="User QQ number")
    duration: int = Field(default=1800, description="Mute duration (seconds)")

class SetGroupWholeBanParam(BaseModel):
    group_id: int = Field(description="Group ID")
    enable: bool = Field(default=True, description="Whether to enable whole-group mute")

class SetGroupAdminParam(BaseModel):
    group_id: int = Field(description="Group ID")
    user_id: int = Field(description="User QQ number")
    enable: bool = Field(default=True, description="Whether to set as admin")

class SetGroupCardParam(BaseModel):
    group_id: int = Field(description="Group ID")
    user_id: int = Field(description="User QQ number")
    card: str = Field(default="", description="Group card")

class SetGroupNameParam(BaseModel):
    group_id: int = Field(description="Group ID")
    group_name: str = Field(description="New group name")

class SetGroupLeaveParam(BaseModel):
    group_id: int = Field(description="Group ID")
    is_dismiss: bool = Field(default=False, description="Whether to dismiss group")

class SetGroupSpecialTitleParam(BaseModel):
    group_id: int = Field(description="Group ID")
    user_id: int = Field(description="User QQ number")
    special_title: str = Field(default="", description="Group special title")
    duration: int = Field(default=-1, description="Duration (seconds)")

class SetGroupAddRequestParam(BaseModel):
    flag: str = Field(description="Join request flag")
    sub_type: str = Field(default="add", description="Request type (add/invite)")
    approve: bool = Field(default=True, description="Whether to approve")
    reason: str = Field(default="", description="Rejection reason")

class UploadGroupFileParam(BaseModel):
    group_id: int = Field(description="Group ID")
    file: str = Field(description="File path")
    name: str = Field(description="File name")
    folder_id: str = Field(default="", description="Folder ID")

class DeleteGroupFileParam(BaseModel):
    group_id: int = Field(description="Group ID")
    file_id: str = Field(description="File ID")
    busid: int = Field(default=0, description="File type")

class SendGroupNoticeParam(BaseModel):
    group_id: int = Field(description="Group ID")
    title: str = Field(description="Announcement title")
    content: str = Field(description="Announcement content")

class SetEssenceMsgParam(BaseModel):
    message_id: int = Field(description="Message ID")

class DeleteEssenceMsgParam(BaseModel):
    message_id: int = Field(description="Message ID")

class GetStrangerInfoParam(BaseModel):
    user_id: int = Field(description="User QQ number")
    no_cache: bool = Field(default=False, description="Whether to skip cache")

class SendLikeParam(BaseModel):
    user_id: int = Field(description="User QQ number")
    times: int = Field(default=1, description="Like count")

class SetFriendAddRequestParam(BaseModel):
    flag: str = Field(description="Friend request flag")
    approve: bool = Field(default=True, description="Whether to approve")
    remark: str = Field(default="", description="Friend remark")

class GetCookiesParam(BaseModel):
    domain: str = Field(default="", description="Domain")

class GetCredentialsParam(BaseModel):
    domain: str = Field(default="", description="Domain")

class OcrImageParam(BaseModel):
    image: str = Field(description="Image path or base64")

class GetImageParam(BaseModel):
    file: str = Field(description="Image file path")

class GetRecordParam(BaseModel):
    file: str = Field(description="Voice file path")
    out_format: str = Field(default="mp3", description="Output format")

class SetQQProfileParam(BaseModel):
    nickname: str = Field(default="", description="Nickname")
    personal_note: str = Field(default="", description="Personal note")
    sex: str = Field(default="", description="Gender (male/female/unknown)")


# ============================================================================
# MCP 服务器
# ============================================================================

app = Server("napcat-full-mcp")


async def get_client() -> NapCatClient:
    return NapCatClient()


# ============================================================================
# 写入型工具列表
# ============================================================================

WRITE_TOOLS = {
    "send_msg", "send_group_msg", "send_private_msg", "delete_msg",
    "send_group_forward_msg", "mark_msg_as_read",
    "set_group_kick", "set_group_ban", "set_group_whole_ban", "set_group_admin",
    "set_group_card", "set_group_name", "set_group_leave", "set_group_special_title",
    "set_group_add_request", "upload_group_file", "delete_group_file",
    "send_group_notice", "set_essence_msg", "delete_essence_msg",
    "send_like", "set_friend_add_request", "set_qq_profile",
}


# ============================================================================
# 工具定义
# ============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # Group info (read-only)
        Tool(name="get_group_info", description="Get group detailed information", inputSchema=GroupIdParam.model_json_schema()),
        Tool(name="get_group_list", description="Get list of all joined groups", inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),
        Tool(name="get_group_honor_info", description="Get group honor information", inputSchema=GroupHonorParam.model_json_schema()),
        Tool(name="get_group_at_all_remain", description="Get remaining @all count for group", inputSchema=GroupIdParam.model_json_schema()),
        Tool(name="get_group_info_ex", description="Get group detailed information (extended)", inputSchema=GroupIdParam.model_json_schema()),
        Tool(name="get_group_member_list", description="Get group member list", inputSchema=GroupIdParam.model_json_schema()),
        Tool(name="get_group_member_info", description="Get specified group member detailed info", inputSchema=GroupMemberInfoParam.model_json_schema()),
        Tool(name="get_group_root_files", description="Get group root directory file list", inputSchema=GroupIdParam.model_json_schema()),
        Tool(name="get_group_files_by_folder", description="Get file list in specified group folder", inputSchema=GroupFilesByFolderParam.model_json_schema()),
        Tool(name="get_group_file_system_info", description="Get group file system information", inputSchema=GroupIdParam.model_json_schema()),
        Tool(name="get_group_file_url", description="Get group file download URL", inputSchema=GroupFileUrlParam.model_json_schema()),
        Tool(name="get_group_msg_history", description="Get group message history", inputSchema=GroupMsgHistoryParam.model_json_schema()),
        Tool(name="get_group_announcement_list", description="Get group announcement list", inputSchema=GroupIdParam.model_json_schema()),
        Tool(name="get_essence_msg_list", description="Get group essence message list", inputSchema=GroupIdParam.model_json_schema()),
        Tool(name="get_group_system_msg", description="Get group system messages", inputSchema=GroupIdParam.model_json_schema()),
        Tool(name="get_group_ignore_add_request", description="Get group ignored join requests", inputSchema=GroupIdParam.model_json_schema()),
        # Message sending and management
        Tool(name="send_msg", description="Send message (generic)", inputSchema=SendMsgParam.model_json_schema()),
        Tool(name="send_group_msg", description="Send group message", inputSchema=SendGroupMsgParam.model_json_schema()),
        Tool(name="send_private_msg", description="Send private message", inputSchema=SendPrivateMsgParam.model_json_schema()),
        Tool(name="delete_msg", description="Recall message", inputSchema=DeleteMsgParam.model_json_schema()),
        Tool(name="get_msg", description="Get message details", inputSchema=GetMsgParam.model_json_schema()),
        Tool(name="get_forward_msg", description="Get forward message", inputSchema=GetForwardMsgParam.model_json_schema()),
        Tool(name="send_group_forward_msg", description="Send group forward message", inputSchema=SendGroupForwardMsgParam.model_json_schema()),
        Tool(name="mark_msg_as_read", description="Mark message as read", inputSchema=MarkMsgAsReadParam.model_json_schema()),
        # Group management
        Tool(name="set_group_kick", description="Kick member from group", inputSchema=SetGroupKickParam.model_json_schema()),
        Tool(name="set_group_ban", description="Mute group member", inputSchema=SetGroupBanParam.model_json_schema()),
        Tool(name="set_group_whole_ban", description="Mute all members in group", inputSchema=SetGroupWholeBanParam.model_json_schema()),
        Tool(name="set_group_admin", description="Set group admin", inputSchema=SetGroupAdminParam.model_json_schema()),
        Tool(name="set_group_card", description="Set group member card", inputSchema=SetGroupCardParam.model_json_schema()),
        Tool(name="set_group_name", description="Set group name", inputSchema=SetGroupNameParam.model_json_schema()),
        Tool(name="set_group_leave", description="Leave or dismiss group", inputSchema=SetGroupLeaveParam.model_json_schema()),
        Tool(name="set_group_special_title", description="Set group special title", inputSchema=SetGroupSpecialTitleParam.model_json_schema()),
        Tool(name="set_group_add_request", description="Handle group join request", inputSchema=SetGroupAddRequestParam.model_json_schema()),
        Tool(name="upload_group_file", description="Upload group file", inputSchema=UploadGroupFileParam.model_json_schema()),
        Tool(name="delete_group_file", description="Delete group file", inputSchema=DeleteGroupFileParam.model_json_schema()),
        Tool(name="send_group_notice", description="Send group announcement", inputSchema=SendGroupNoticeParam.model_json_schema()),
        Tool(name="set_essence_msg", description="Set essence message", inputSchema=SetEssenceMsgParam.model_json_schema()),
        Tool(name="delete_essence_msg", description="Delete essence message", inputSchema=DeleteEssenceMsgParam.model_json_schema()),
        # Friends / Users
        Tool(name="get_friend_list", description="Get friend list", inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),
        Tool(name="get_stranger_info", description="Get stranger information", inputSchema=GetStrangerInfoParam.model_json_schema()),
        Tool(name="get_friend_msg_history", description="Get friend message history", inputSchema=FriendMsgHistoryParam.model_json_schema()),
        Tool(name="send_like", description="Send like", inputSchema=SendLikeParam.model_json_schema()),
        Tool(name="set_friend_add_request", description="Handle friend request", inputSchema=SetFriendAddRequestParam.model_json_schema()),
        # System management
        Tool(name="get_login_info", description="Get login account information", inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),
        Tool(name="get_status", description="Get running status", inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),
        Tool(name="get_version_info", description="Get version information", inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),
        Tool(name="get_cookies", description="Get cookies", inputSchema=GetCookiesParam.model_json_schema()),
        Tool(name="get_csrf_token", description="Get CSRF token", inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),
        Tool(name="get_credentials", description="Get credentials", inputSchema=GetCredentialsParam.model_json_schema()),
        # Napcat extensions
        Tool(name="ocr_image", description="OCR image recognition", inputSchema=OcrImageParam.model_json_schema()),
        Tool(name="get_image", description="Get image information", inputSchema=GetImageParam.model_json_schema()),
        Tool(name="get_record", description="Get voice record information", inputSchema=GetRecordParam.model_json_schema()),
        Tool(name="can_send_image", description="Check if can send image", inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),
        Tool(name="can_send_record", description="Check if can send voice record", inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),
        Tool(name="get_online_client", description="Get online client list", inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),
        Tool(name="set_qq_profile", description="Set QQ profile", inputSchema=SetQQProfileParam.model_json_schema()),
    ]


# ============================================================================
# 工具实现
# ============================================================================

@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if READONLY_MODE and name in WRITE_TOOLS:
        return [TextContent(type="text", text=f"权限拒绝: 只读模式已启用，工具 '{name}' 不可用")]

    if name in DISABLED_TOOLS:
        return [TextContent(type="text", text=f"权限拒绝: 工具 '{name}' 已被禁用")]

    try:
        async with await get_client() as client:
            result = None
            group_id_to_check = None

            # 群聊信息（只读）
            if name == "get_group_info":
                params = GroupIdParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.get_group_info(params.group_id)

            elif name == "get_group_list":
                all_groups = await client.get_group_list()
                result = [g for g in all_groups if ALLOWED_GROUPS is None or g.get("group_id") in ALLOWED_GROUPS]

            elif name == "get_group_honor_info":
                params = GroupHonorParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.get_group_honor_info(params.group_id, params.type)

            elif name == "get_group_at_all_remain":
                params = GroupIdParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.get_group_at_all_remain(params.group_id)

            elif name == "get_group_info_ex":
                params = GroupIdParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.get_group_info_ex(params.group_id)

            elif name == "get_group_member_list":
                params = GroupIdParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.get_group_member_list(params.group_id)

            elif name == "get_group_member_info":
                params = GroupMemberInfoParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.get_group_member_info(params.group_id, params.user_id)

            elif name == "get_group_root_files":
                params = GroupIdParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.get_group_root_files(params.group_id)

            elif name == "get_group_files_by_folder":
                params = GroupFilesByFolderParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.get_group_files_by_folder(params.group_id, params.folder_id)

            elif name == "get_group_file_system_info":
                params = GroupIdParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.get_group_file_system_info(params.group_id)

            elif name == "get_group_file_url":
                params = GroupFileUrlParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.get_group_file_url(params.group_id, params.file_id, params.busid)

            elif name == "get_group_msg_history":
                params = GroupMsgHistoryParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.get_group_msg_history(params.group_id, params.message_seq, params.count)

            elif name == "get_group_announcement_list":
                params = GroupIdParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.get_group_announcement_list(params.group_id)

            elif name == "get_essence_msg_list":
                params = GroupIdParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.get_essence_msg_list(params.group_id)

            elif name == "get_group_system_msg":
                params = GroupIdParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.get_group_system_msg(params.group_id)

            elif name == "get_group_ignore_add_request":
                params = GroupIdParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.get_group_ignore_add_request(params.group_id)

            # 消息发送与管理
            elif name == "send_msg":
                params = SendMsgParam(**arguments)
                result = await client.send_msg(params.message_type, params.user_id, params.group_id, params.message, params.auto_escape)

            elif name == "send_group_msg":
                params = SendGroupMsgParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.send_group_msg(params.group_id, params.message, params.auto_escape)

            elif name == "send_private_msg":
                params = SendPrivateMsgParam(**arguments)
                result = await client.send_private_msg(params.user_id, params.message, params.auto_escape)

            elif name == "delete_msg":
                params = DeleteMsgParam(**arguments)
                result = await client.delete_msg(params.message_id)

            elif name == "get_msg":
                params = GetMsgParam(**arguments)
                result = await client.get_msg(params.message_id)

            elif name == "get_forward_msg":
                params = GetForwardMsgParam(**arguments)
                result = await client.get_forward_msg(params.message_id)

            elif name == "send_group_forward_msg":
                params = SendGroupForwardMsgParam(**arguments)
                messages = json.loads(params.messages)
                result = await client.send_group_forward_msg(params.group_id, messages)

            elif name == "mark_msg_as_read":
                params = MarkMsgAsReadParam(**arguments)
                result = await client.mark_msg_as_read(params.message_id)

            # 群管理
            elif name == "set_group_kick":
                params = SetGroupKickParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.set_group_kick(params.group_id, params.user_id, params.reject_add_request)

            elif name == "set_group_ban":
                params = SetGroupBanParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.set_group_ban(params.group_id, params.user_id, params.duration)

            elif name == "set_group_whole_ban":
                params = SetGroupWholeBanParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.set_group_whole_ban(params.group_id, params.enable)

            elif name == "set_group_admin":
                params = SetGroupAdminParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.set_group_admin(params.group_id, params.user_id, params.enable)

            elif name == "set_group_card":
                params = SetGroupCardParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.set_group_card(params.group_id, params.user_id, params.card)

            elif name == "set_group_name":
                params = SetGroupNameParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.set_group_name(params.group_id, params.group_name)

            elif name == "set_group_leave":
                params = SetGroupLeaveParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.set_group_leave(params.group_id, params.is_dismiss)

            elif name == "set_group_special_title":
                params = SetGroupSpecialTitleParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.set_group_special_title(params.group_id, params.user_id, params.special_title, params.duration)

            elif name == "set_group_add_request":
                params = SetGroupAddRequestParam(**arguments)
                result = await client.set_group_add_request(params.flag, params.sub_type, params.approve, params.reason)

            elif name == "upload_group_file":
                params = UploadGroupFileParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.upload_group_file(params.group_id, params.file, params.name, params.folder_id)

            elif name == "delete_group_file":
                params = DeleteGroupFileParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.delete_group_file(params.group_id, params.file_id, params.busid)

            elif name == "send_group_notice":
                params = SendGroupNoticeParam(**arguments)
                group_id_to_check = params.group_id
                if not is_group_allowed(group_id_to_check):
                    return [TextContent(type="text", text=f"权限拒绝: 群 {group_id_to_check} 不在允许访问的群列表中")]
                result = await client.send_group_notice(params.group_id, params.title, params.content)

            elif name == "set_essence_msg":
                params = SetEssenceMsgParam(**arguments)
                result = await client.set_essence_msg(params.message_id)

            elif name == "delete_essence_msg":
                params = DeleteEssenceMsgParam(**arguments)
                result = await client.delete_essence_msg(params.message_id)

            # 好友/用户
            elif name == "get_friend_list":
                result = await client.get_friend_list()

            elif name == "get_stranger_info":
                params = GetStrangerInfoParam(**arguments)
                result = await client.get_stranger_info(params.user_id, params.no_cache)

            elif name == "get_friend_msg_history":
                params = FriendMsgHistoryParam(**arguments)
                result = await client.get_friend_msg_history(params.user_id, params.message_seq, params.count)

            elif name == "send_like":
                params = SendLikeParam(**arguments)
                result = await client.send_like(params.user_id, params.times)

            elif name == "set_friend_add_request":
                params = SetFriendAddRequestParam(**arguments)
                result = await client.set_friend_add_request(params.flag, params.approve, params.remark)

            # 系统管理
            elif name == "get_login_info":
                result = await client.get_login_info()

            elif name == "get_status":
                result = await client.get_status()

            elif name == "get_version_info":
                result = await client.get_version_info()

            elif name == "get_cookies":
                params = GetCookiesParam(**arguments)
                result = await client.get_cookies(params.domain)

            elif name == "get_csrf_token":
                result = await client.get_csrf_token()

            elif name == "get_credentials":
                params = GetCredentialsParam(**arguments)
                result = await client.get_credentials(params.domain)

            # Napcat 扩展
            elif name == "ocr_image":
                params = OcrImageParam(**arguments)
                result = await client.ocr_image(params.image)

            elif name == "get_image":
                params = GetImageParam(**arguments)
                result = await client.get_image(params.file)

            elif name == "get_record":
                params = GetRecordParam(**arguments)
                result = await client.get_record(params.file, params.out_format)

            elif name == "can_send_image":
                result = await client.can_send_image()

            elif name == "can_send_record":
                result = await client.can_send_record()

            elif name == "get_online_client":
                result = await client.get_online_client()

            elif name == "set_qq_profile":
                params = SetQQProfileParam(**arguments)
                result = await client.set_qq_profile(params.nickname, params.personal_note, params.sex)

            else:
                return [TextContent(type="text", text=f"未知工具: {name}")]

            formatted_result = json.dumps(result, ensure_ascii=False, indent=2)
            return [TextContent(type="text", text=formatted_result)]

    except Exception as e:
        error_msg = f"工具调用失败 [{name}]: {str(e)}"
        return [TextContent(type="text", text=error_msg)]


async def main():
    """启动 MCP 服务器"""
    from mcp.server.stdio import stdio_server

    print("=" * 60)
    print("NapCat Full MCP Server")
    print("=" * 60)
    if ALLOWED_GROUPS is None:
        print("✓ 权限配置: 允许访问所有群")
    else:
        print(f"✓ 权限配置: 只允许访问群 {', '.join(map(str, sorted(ALLOWED_GROUPS)))}")
    if READONLY_MODE:
        print("✓ 模式: 只读")
    else:
        print("✓ 模式: 读写")
    print("=" * 60)

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
