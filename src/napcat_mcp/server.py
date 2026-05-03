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
    group_id: int = Field(description="群号")

class GroupHonorParam(GroupIdParam):
    type: str = Field(default="all", description="荣誉类型 (talkative/performer/legend/strong_newbie/emotion/all)")

class GroupMemberInfoParam(BaseModel):
    group_id: int = Field(description="群号")
    user_id: int = Field(description="用户 QQ 号")

class GroupFilesByFolderParam(BaseModel):
    group_id: int = Field(description="群号")
    folder_id: str = Field(default="", description="文件夹 ID")

class GroupFileUrlParam(BaseModel):
    group_id: int = Field(description="群号")
    file_id: str = Field(description="文件 ID")
    busid: int = Field(default=0, description="文件类型")

class GroupMsgHistoryParam(BaseModel):
    group_id: int = Field(description="群号")
    message_seq: int = Field(default=0, description="起始消息序号")
    count: int = Field(default=20, description="获取数量")

class FriendMsgHistoryParam(BaseModel):
    user_id: int = Field(description="用户 QQ 号")
    message_seq: int = Field(default=0, description="起始消息序号")
    count: int = Field(default=20, description="获取数量")

class SendMsgParam(BaseModel):
    message_type: str = Field(description="消息类型 (group/private)")
    user_id: Optional[int] = Field(default=None, description="用户 QQ 号")
    group_id: Optional[int] = Field(default=None, description="群号")
    message: str = Field(description="消息内容")
    auto_escape: bool = Field(default=False, description="是否自动转义")

class SendGroupMsgParam(BaseModel):
    group_id: int = Field(description="群号")
    message: str = Field(description="消息内容")
    auto_escape: bool = Field(default=False, description="是否自动转义")

class SendPrivateMsgParam(BaseModel):
    user_id: int = Field(description="用户 QQ 号")
    message: str = Field(description="消息内容")
    auto_escape: bool = Field(default=False, description="是否自动转义")

class DeleteMsgParam(BaseModel):
    message_id: int = Field(description="消息 ID")

class GetMsgParam(BaseModel):
    message_id: int = Field(description="消息 ID")

class GetForwardMsgParam(BaseModel):
    message_id: int = Field(description="消息 ID")

class SendGroupForwardMsgParam(BaseModel):
    group_id: int = Field(description="群号")
    messages: str = Field(description="合并转发消息内容（JSON 字符串）")

class MarkMsgAsReadParam(BaseModel):
    message_id: int = Field(description="消息 ID")

class SetGroupKickParam(BaseModel):
    group_id: int = Field(description="群号")
    user_id: int = Field(description="用户 QQ 号")
    reject_add_request: bool = Field(default=False, description="是否拒绝加群请求")

class SetGroupBanParam(BaseModel):
    group_id: int = Field(description="群号")
    user_id: int = Field(description="用户 QQ 号")
    duration: int = Field(default=1800, description="禁言时长（秒）")

class SetGroupWholeBanParam(BaseModel):
    group_id: int = Field(description="群号")
    enable: bool = Field(default=True, description="是否开启全员禁言")

class SetGroupAdminParam(BaseModel):
    group_id: int = Field(description="群号")
    user_id: int = Field(description="用户 QQ 号")
    enable: bool = Field(default=True, description="是否设置为管理员")

class SetGroupCardParam(BaseModel):
    group_id: int = Field(description="群号")
    user_id: int = Field(description="用户 QQ 号")
    card: str = Field(default="", description="群名片")

class SetGroupNameParam(BaseModel):
    group_id: int = Field(description="群号")
    group_name: str = Field(description="新群名称")

class SetGroupLeaveParam(BaseModel):
    group_id: int = Field(description="群号")
    is_dismiss: bool = Field(default=False, description="是否解散群")

class SetGroupSpecialTitleParam(BaseModel):
    group_id: int = Field(description="群号")
    user_id: int = Field(description="用户 QQ 号")
    special_title: str = Field(default="", description="群头衔")
    duration: int = Field(default=-1, description="有效期（秒）")

class SetGroupAddRequestParam(BaseModel):
    flag: str = Field(description="加群请求 flag")
    sub_type: str = Field(default="add", description="请求类型 (add/invite)")
    approve: bool = Field(default=True, description="是否同意")
    reason: str = Field(default="", description="拒绝理由")

class UploadGroupFileParam(BaseModel):
    group_id: int = Field(description="群号")
    file: str = Field(description="文件路径")
    name: str = Field(description="文件名")
    folder_id: str = Field(default="", description="文件夹 ID")

class DeleteGroupFileParam(BaseModel):
    group_id: int = Field(description="群号")
    file_id: str = Field(description="文件 ID")
    busid: int = Field(default=0, description="文件类型")

class SendGroupNoticeParam(BaseModel):
    group_id: int = Field(description="群号")
    title: str = Field(description="公告标题")
    content: str = Field(description="公告内容")

class SetEssenceMsgParam(BaseModel):
    message_id: int = Field(description="消息 ID")

class DeleteEssenceMsgParam(BaseModel):
    message_id: int = Field(description="消息 ID")

class GetStrangerInfoParam(BaseModel):
    user_id: int = Field(description="用户 QQ 号")
    no_cache: bool = Field(default=False, description="是否不使用缓存")

class SendLikeParam(BaseModel):
    user_id: int = Field(description="用户 QQ 号")
    times: int = Field(default=1, description="点赞次数")

class SetFriendAddRequestParam(BaseModel):
    flag: str = Field(description="好友请求 flag")
    approve: bool = Field(default=True, description="是否同意")
    remark: str = Field(default="", description="好友备注")

class GetCookiesParam(BaseModel):
    domain: str = Field(default="", description="域名")

class GetCredentialsParam(BaseModel):
    domain: str = Field(default="", description="域名")

class OcrImageParam(BaseModel):
    image: str = Field(description="图片路径或 base64")

class GetImageParam(BaseModel):
    file: str = Field(description="图片文件路径")

class GetRecordParam(BaseModel):
    file: str = Field(description="语音文件路径")
    out_format: str = Field(default="mp3", description="输出格式")

class SetQQProfileParam(BaseModel):
    nickname: str = Field(default="", description="昵称")
    personal_note: str = Field(default="", description="个性签名")
    sex: str = Field(default="", description="性别 (male/female/unknown)")


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
        # 群聊信息（只读）
        Tool(name="get_group_info", description="获取群详细信息", inputSchema=GroupIdParam.model_json_schema()),
        Tool(name="get_group_list", description="获取当前账号加入的所有群列表", inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),
        Tool(name="get_group_honor_info", description="获取群荣誉信息", inputSchema=GroupHonorParam.model_json_schema()),
        Tool(name="get_group_at_all_remain", description="获取群@全体成员剩余次数", inputSchema=GroupIdParam.model_json_schema()),
        Tool(name="get_group_info_ex", description="获取群详细信息（扩展版）", inputSchema=GroupIdParam.model_json_schema()),
        Tool(name="get_group_member_list", description="获取群成员列表", inputSchema=GroupIdParam.model_json_schema()),
        Tool(name="get_group_member_info", description="获取指定群成员详细信息", inputSchema=GroupMemberInfoParam.model_json_schema()),
        Tool(name="get_group_root_files", description="获取群根目录文件列表", inputSchema=GroupIdParam.model_json_schema()),
        Tool(name="get_group_files_by_folder", description="获取群指定文件夹内的文件列表", inputSchema=GroupFilesByFolderParam.model_json_schema()),
        Tool(name="get_group_file_system_info", description="获取群文件系统信息", inputSchema=GroupIdParam.model_json_schema()),
        Tool(name="get_group_file_url", description="获取群文件下载链接", inputSchema=GroupFileUrlParam.model_json_schema()),
        Tool(name="get_group_msg_history", description="获取群历史消息", inputSchema=GroupMsgHistoryParam.model_json_schema()),
        Tool(name="get_group_announcement_list", description="获取群公告列表", inputSchema=GroupIdParam.model_json_schema()),
        Tool(name="get_essence_msg_list", description="获取群精华消息列表", inputSchema=GroupIdParam.model_json_schema()),
        Tool(name="get_group_system_msg", description="获取群系统消息", inputSchema=GroupIdParam.model_json_schema()),
        Tool(name="get_group_ignore_add_request", description="获取群忽略的加群请求", inputSchema=GroupIdParam.model_json_schema()),
        # 消息发送与管理
        Tool(name="send_msg", description="发送消息（通用）", inputSchema=SendMsgParam.model_json_schema()),
        Tool(name="send_group_msg", description="发送群消息", inputSchema=SendGroupMsgParam.model_json_schema()),
        Tool(name="send_private_msg", description="发送私聊消息", inputSchema=SendPrivateMsgParam.model_json_schema()),
        Tool(name="delete_msg", description="撤回消息", inputSchema=DeleteMsgParam.model_json_schema()),
        Tool(name="get_msg", description="获取消息详情", inputSchema=GetMsgParam.model_json_schema()),
        Tool(name="get_forward_msg", description="获取合并转发消息", inputSchema=GetForwardMsgParam.model_json_schema()),
        Tool(name="send_group_forward_msg", description="发送群合并转发消息", inputSchema=SendGroupForwardMsgParam.model_json_schema()),
        Tool(name="mark_msg_as_read", description="标记消息已读", inputSchema=MarkMsgAsReadParam.model_json_schema()),
        # 群管理
        Tool(name="set_group_kick", description="群踢人", inputSchema=SetGroupKickParam.model_json_schema()),
        Tool(name="set_group_ban", description="群禁言", inputSchema=SetGroupBanParam.model_json_schema()),
        Tool(name="set_group_whole_ban", description="群全员禁言", inputSchema=SetGroupWholeBanParam.model_json_schema()),
        Tool(name="set_group_admin", description="设置群管理员", inputSchema=SetGroupAdminParam.model_json_schema()),
        Tool(name="set_group_card", description="设置群名片", inputSchema=SetGroupCardParam.model_json_schema()),
        Tool(name="set_group_name", description="设置群名称", inputSchema=SetGroupNameParam.model_json_schema()),
        Tool(name="set_group_leave", description="退群/解散群", inputSchema=SetGroupLeaveParam.model_json_schema()),
        Tool(name="set_group_special_title", description="设置群头衔", inputSchema=SetGroupSpecialTitleParam.model_json_schema()),
        Tool(name="set_group_add_request", description="处理加群请求", inputSchema=SetGroupAddRequestParam.model_json_schema()),
        Tool(name="upload_group_file", description="上传群文件", inputSchema=UploadGroupFileParam.model_json_schema()),
        Tool(name="delete_group_file", description="删除群文件", inputSchema=DeleteGroupFileParam.model_json_schema()),
        Tool(name="send_group_notice", description="发送群公告", inputSchema=SendGroupNoticeParam.model_json_schema()),
        Tool(name="set_essence_msg", description="设置精华消息", inputSchema=SetEssenceMsgParam.model_json_schema()),
        Tool(name="delete_essence_msg", description="删除精华消息", inputSchema=DeleteEssenceMsgParam.model_json_schema()),
        # 好友/用户
        Tool(name="get_friend_list", description="获取好友列表", inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),
        Tool(name="get_stranger_info", description="获取陌生人信息", inputSchema=GetStrangerInfoParam.model_json_schema()),
        Tool(name="get_friend_msg_history", description="获取好友消息历史", inputSchema=FriendMsgHistoryParam.model_json_schema()),
        Tool(name="send_like", description="发送点赞", inputSchema=SendLikeParam.model_json_schema()),
        Tool(name="set_friend_add_request", description="处理好友请求", inputSchema=SetFriendAddRequestParam.model_json_schema()),
        # 系统管理
        Tool(name="get_login_info", description="获取登录号信息", inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),
        Tool(name="get_status", description="获取运行状态", inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),
        Tool(name="get_version_info", description="获取版本信息", inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),
        Tool(name="get_cookies", description="获取 Cookies", inputSchema=GetCookiesParam.model_json_schema()),
        Tool(name="get_csrf_token", description="获取 CSRF Token", inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),
        Tool(name="get_credentials", description="获取认证信息", inputSchema=GetCredentialsParam.model_json_schema()),
        # Napcat 扩展
        Tool(name="ocr_image", description="图片 OCR 识别", inputSchema=OcrImageParam.model_json_schema()),
        Tool(name="get_image", description="获取图片信息", inputSchema=GetImageParam.model_json_schema()),
        Tool(name="get_record", description="获取语音信息", inputSchema=GetRecordParam.model_json_schema()),
        Tool(name="can_send_image", description="检查能否发送图片", inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),
        Tool(name="can_send_record", description="检查能否发送语音", inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),
        Tool(name="get_online_client", description="获取在线客户端列表", inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),
        Tool(name="set_qq_profile", description="设置 QQ 资料卡", inputSchema=SetQQProfileParam.model_json_schema()),
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
