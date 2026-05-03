"""
NapCat API 客户端
用于与 NapCat OneBot 服务器通信（支持 HTTP 和 WebSocket 双模式）
"""

import os
import asyncio
import json
from typing import Any, Dict, List, Optional

import httpx
import websockets
from websockets.asyncio.client import ClientConnection


class NapCatClient:
    """NapCat API 客户端（HTTP + WebSocket 双模式）"""

    def __init__(self, host: Optional[str] = None, token: Optional[str] = None):
        """
        初始化 NapCat 客户端

        Args:
            host: NapCat 服务器地址，默认从环境变量 NAPCAT_HOST 读取
            token: NapCat 访问令牌，默认从环境变量 NAPCAT_TOKEN 读取
        """
        self.host = host or os.getenv("NAPCAT_HOST", "http://localhost:3000")
        self.token = token or os.getenv("NAPCAT_TOKEN", "")

        # 判断连接模式：http/https -> HTTP 模式，ws/wss -> WebSocket 模式
        self._use_http = self.host.startswith("http://") or self.host.startswith("https://")

        if self._use_http:
            self._http_url = self.host.rstrip("/")
            self._http_client: Optional[httpx.AsyncClient] = None
        else:
            self.ws_url = self.host
            if self.host.startswith("http://"):
                self.ws_url = self.host.replace("http://", "ws://")
            elif self.host.startswith("https://"):
                self.ws_url = self.host.replace("https://", "wss://")
            self._ws: Optional[ClientConnection] = None

        self._request_id = 0

    async def __aenter__(self):
        """异步上下文管理器入口"""
        if self._use_http:
            headers = {"Content-Type": "application/json"}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            self._http_client = httpx.AsyncClient(headers=headers, timeout=30.0)
        else:
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            self._ws = await websockets.connect(self.ws_url, additional_headers=headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self._use_http:
            if self._http_client:
                await self._http_client.aclose()
        else:
            if self._ws:
                await self._ws.close()

    async def call_api(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        调用 NapCat API（自动选择 HTTP 或 WebSocket）

        Args:
            action: API 动作名称
            params: API 参数

        Returns:
            API 响应数据

        Raises:
            Exception: API 调用失败时抛出异常
        """
        if self._use_http:
            return await self._call_api_http(action, params)
        else:
            return await self._call_api_ws(action, params)

    async def _call_api_http(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """通过 HTTP POST 调用 API"""
        if not self._http_client:
            raise RuntimeError("HTTP client not initialized. Use async context manager.")

        url = f"{self._http_url}/{action}"
        payload = params or {}

        try:
            response = await self._http_client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            if data.get("retcode") == 0:
                return data.get("data", {})
            else:
                error_msg = data.get("message", f"API error with retcode {data.get('retcode')}")
                raise Exception(f"API call failed: {error_msg}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise Exception(f"HTTP request error: {str(e)}")
        except Exception as e:
            raise Exception(f"API call error: {str(e)}")

    async def _call_api_ws(self, action: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """通过 WebSocket 调用 API"""
        if not self._ws:
            raise RuntimeError("WebSocket client not initialized. Use async context manager.")

        self._request_id += 1
        request_id = f"req_{self._request_id}"

        payload = {
            "action": action,
            "params": params or {},
            "echo": request_id
        }

        try:
            await self._ws.send(json.dumps(payload))

            while True:
                response_str = await self._ws.recv()
                response = json.loads(response_str)

                if response.get("post_type") == "meta_event":
                    continue

                if response.get("echo") == request_id:
                    if response.get("retcode") == 0:
                        return response.get("data", {})
                    else:
                        error_msg = response.get("message", f"API error with retcode {response.get('retcode')}")
                        raise Exception(f"API call failed: {error_msg}")
                else:
                    continue

        except websockets.exceptions.WebSocketException as e:
            raise Exception(f"WebSocket error: {str(e)}")
        except Exception as e:
            raise Exception(f"API call error: {str(e)}")

    # ============================================================================
    # 群聊信息相关 API（只读）
    # ============================================================================

    async def get_group_info(self, group_id: int) -> Dict[str, Any]:
        return await self.call_api("get_group_info", {"group_id": group_id})

    async def get_group_list(self) -> List[Dict[str, Any]]:
        return await self.call_api("get_group_list")

    async def get_group_honor_info(self, group_id: int, type: str = "all") -> Dict[str, Any]:
        return await self.call_api("get_group_honor_info", {"group_id": group_id, "type": type})

    async def get_group_at_all_remain(self, group_id: int) -> Dict[str, Any]:
        return await self.call_api("get_group_at_all_remain", {"group_id": group_id})

    async def get_group_info_ex(self, group_id: int) -> Dict[str, Any]:
        return await self.call_api("get_group_info_ex", {"group_id": group_id})

    # ============================================================================
    # 群成员信息相关 API（只读）
    # ============================================================================

    async def get_group_member_list(self, group_id: int) -> List[Dict[str, Any]]:
        return await self.call_api("get_group_member_list", {"group_id": group_id})

    async def get_group_member_info(self, group_id: int, user_id: int) -> Dict[str, Any]:
        return await self.call_api("get_group_member_info", {"group_id": group_id, "user_id": user_id})

    # ============================================================================
    # 群文件相关 API（只读）
    # ============================================================================

    async def get_group_root_files(self, group_id: int) -> Dict[str, Any]:
        return await self.call_api("get_group_root_files", {"group_id": group_id})

    async def get_group_files_by_folder(self, group_id: int, folder_id: str = "") -> Dict[str, Any]:
        return await self.call_api("get_group_files_by_folder", {"group_id": group_id, "folder_id": folder_id})

    async def get_group_file_system_info(self, group_id: int) -> Dict[str, Any]:
        return await self.call_api("get_group_file_system_info", {"group_id": group_id})

    async def get_group_file_url(self, group_id: int, file_id: str, busid: int = 0) -> Dict[str, Any]:
        return await self.call_api("get_group_file_url", {"group_id": group_id, "file_id": file_id, "busid": busid})

    # ============================================================================
    # 历史消息相关 API（只读）
    # ============================================================================

    async def get_group_msg_history(self, group_id: int, message_seq: int = 0, count: int = 20) -> Dict[str, Any]:
        return await self.call_api("get_group_msg_history", {"group_id": group_id, "message_seq": message_seq, "count": count})

    async def get_friend_msg_history(self, user_id: int, message_seq: int = 0, count: int = 20) -> Dict[str, Any]:
        return await self.call_api("get_friend_msg_history", {"user_id": user_id, "message_seq": message_seq, "count": count})

    # ============================================================================
    # 群公告相关 API
    # ============================================================================

    async def get_group_announcement_list(self, group_id: int) -> Dict[str, Any]:
        return await self.call_api("_get_group_notice", {"group_id": group_id})

    async def send_group_notice(self, group_id: int, title: str, content: str) -> Dict[str, Any]:
        return await self.call_api("_send_group_notice", {"group_id": group_id, "title": title, "content": content})

    # ============================================================================
    # 群精华消息相关 API
    # ============================================================================

    async def get_essence_msg_list(self, group_id: int) -> Dict[str, Any]:
        return await self.call_api("get_essence_msg_list", {"group_id": group_id})

    async def set_essence_msg(self, message_id: int) -> Dict[str, Any]:
        return await self.call_api("set_essence_msg", {"message_id": message_id})

    async def delete_essence_msg(self, message_id: int) -> Dict[str, Any]:
        return await self.call_api("delete_essence_msg", {"message_id": message_id})

    # ============================================================================
    # 消息发送与管理 API（写入）
    # ============================================================================

    async def send_msg(self, message_type: str, user_id: Optional[int] = None, group_id: Optional[int] = None, message: str = "", auto_escape: bool = False) -> Dict[str, Any]:
        params: Dict[str, Any] = {"message_type": message_type, "message": message, "auto_escape": auto_escape}
        if user_id is not None:
            params["user_id"] = user_id
        if group_id is not None:
            params["group_id"] = group_id
        return await self.call_api("send_msg", params)

    async def send_group_msg(self, group_id: int, message: str, auto_escape: bool = False) -> Dict[str, Any]:
        return await self.call_api("send_group_msg", {"group_id": group_id, "message": message, "auto_escape": auto_escape})

    async def send_private_msg(self, user_id: int, message: str, auto_escape: bool = False) -> Dict[str, Any]:
        return await self.call_api("send_private_msg", {"user_id": user_id, "message": message, "auto_escape": auto_escape})

    async def delete_msg(self, message_id: int) -> Dict[str, Any]:
        return await self.call_api("delete_msg", {"message_id": message_id})

    async def get_msg(self, message_id: int) -> Dict[str, Any]:
        return await self.call_api("get_msg", {"message_id": message_id})

    async def get_forward_msg(self, message_id: int) -> Dict[str, Any]:
        return await self.call_api("get_forward_msg", {"message_id": message_id})

    async def send_group_forward_msg(self, group_id: int, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        return await self.call_api("send_group_forward_msg", {"group_id": group_id, "messages": messages})

    async def mark_msg_as_read(self, message_id: int) -> Dict[str, Any]:
        return await self.call_api("mark_msg_as_read", {"message_id": message_id})

    # ============================================================================
    # 群管理 API（写入）
    # ============================================================================

    async def set_group_kick(self, group_id: int, user_id: int, reject_add_request: bool = False) -> Dict[str, Any]:
        return await self.call_api("set_group_kick", {"group_id": group_id, "user_id": user_id, "reject_add_request": reject_add_request})

    async def set_group_ban(self, group_id: int, user_id: int, duration: int = 1800) -> Dict[str, Any]:
        return await self.call_api("set_group_ban", {"group_id": group_id, "user_id": user_id, "duration": duration})

    async def set_group_whole_ban(self, group_id: int, enable: bool = True) -> Dict[str, Any]:
        return await self.call_api("set_group_whole_ban", {"group_id": group_id, "enable": enable})

    async def set_group_admin(self, group_id: int, user_id: int, enable: bool = True) -> Dict[str, Any]:
        return await self.call_api("set_group_admin", {"group_id": group_id, "user_id": user_id, "enable": enable})

    async def set_group_card(self, group_id: int, user_id: int, card: str = "") -> Dict[str, Any]:
        return await self.call_api("set_group_card", {"group_id": group_id, "user_id": user_id, "card": card})

    async def set_group_name(self, group_id: int, group_name: str) -> Dict[str, Any]:
        return await self.call_api("set_group_name", {"group_id": group_id, "group_name": group_name})

    async def set_group_leave(self, group_id: int, is_dismiss: bool = False) -> Dict[str, Any]:
        return await self.call_api("set_group_leave", {"group_id": group_id, "is_dismiss": is_dismiss})

    async def set_group_special_title(self, group_id: int, user_id: int, special_title: str = "", duration: int = -1) -> Dict[str, Any]:
        return await self.call_api("set_group_special_title", {"group_id": group_id, "user_id": user_id, "special_title": special_title, "duration": duration})

    async def set_group_add_request(self, flag: str, sub_type: str = "add", approve: bool = True, reason: str = "") -> Dict[str, Any]:
        return await self.call_api("set_group_add_request", {"flag": flag, "sub_type": sub_type, "approve": approve, "reason": reason})

    async def upload_group_file(self, group_id: int, file: str, name: str, folder_id: str = "") -> Dict[str, Any]:
        return await self.call_api("upload_group_file", {"group_id": group_id, "file": file, "name": name, "folder_id": folder_id})

    async def delete_group_file(self, group_id: int, file_id: str, busid: int = 0) -> Dict[str, Any]:
        return await self.call_api("delete_group_file", {"group_id": group_id, "file_id": file_id, "busid": busid})

    async def get_group_system_msg(self, group_id: int) -> Dict[str, Any]:
        return await self.call_api("get_group_system_msg", {"group_id": group_id})

    async def get_group_ignore_add_request(self, group_id: int) -> Dict[str, Any]:
        return await self.call_api("get_group_ignore_add_request", {"group_id": group_id})

    # ============================================================================
    # 好友/用户相关 API
    # ============================================================================

    async def get_friend_list(self) -> List[Dict[str, Any]]:
        return await self.call_api("get_friend_list")

    async def get_stranger_info(self, user_id: int, no_cache: bool = False) -> Dict[str, Any]:
        return await self.call_api("get_stranger_info", {"user_id": user_id, "no_cache": no_cache})

    async def send_like(self, user_id: int, times: int = 1) -> Dict[str, Any]:
        return await self.call_api("send_like", {"user_id": user_id, "times": times})

    async def set_friend_add_request(self, flag: str, approve: bool = True, remark: str = "") -> Dict[str, Any]:
        return await self.call_api("set_friend_add_request", {"flag": flag, "approve": approve, "remark": remark})

    # ============================================================================
    # 系统管理 API
    # ============================================================================

    async def get_login_info(self) -> Dict[str, Any]:
        return await self.call_api("get_login_info")

    async def get_status(self) -> Dict[str, Any]:
        return await self.call_api("get_status")

    async def get_version_info(self) -> Dict[str, Any]:
        return await self.call_api("get_version_info")

    async def get_cookies(self, domain: str = "") -> Dict[str, Any]:
        return await self.call_api("get_cookies", {"domain": domain})

    async def get_csrf_token(self) -> Dict[str, Any]:
        return await self.call_api("get_csrf_token")

    async def get_credentials(self, domain: str = "") -> Dict[str, Any]:
        return await self.call_api("get_credentials", {"domain": domain})

    # ============================================================================
    # Napcat 扩展 API
    # ============================================================================

    async def ocr_image(self, image: str) -> Dict[str, Any]:
        return await self.call_api("ocr_image", {"image": image})

    async def get_image(self, file: str) -> Dict[str, Any]:
        return await self.call_api("get_image", {"file": file})

    async def get_record(self, file: str, out_format: str = "mp3") -> Dict[str, Any]:
        return await self.call_api("get_record", {"file": file, "out_format": out_format})

    async def can_send_image(self) -> Dict[str, Any]:
        return await self.call_api("can_send_image")

    async def can_send_record(self) -> Dict[str, Any]:
        return await self.call_api("can_send_record")

    async def get_online_client(self) -> Dict[str, Any]:
        return await self.call_api("get_online_client")

    async def set_qq_profile(self, nickname: str = "", personal_note: str = "", sex: str = "") -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if nickname:
            params["nickname"] = nickname
        if personal_note:
            params["personal_note"] = personal_note
        if sex:
            params["sex"] = sex
        return await self.call_api("set_qq_profile", params)