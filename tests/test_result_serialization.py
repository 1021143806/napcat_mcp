import json
import time

import pytest

from napcat_mcp.server import (
    GetForwardMsgParam,
    ReadGroupMessagesParam,
    compact_tool_result,
    render_group_messages_light,
    serialize_tool_result,
)


def test_tool_result_uses_compact_lossless_json():
    result = {
        "messages": [
            {
                "message": [
                    {
                        "type": "forward",
                        "data": {
                            "id": "7663414735448210388",
                            "content": [{"sender": {"nickname": "測試"}, "message": []}],
                        },
                    }
                ]
            }
        ]
    }

    serialized = serialize_tool_result(result)

    assert json.loads(serialized) == result
    assert "\n" not in serialized
    assert '": ' not in serialized
    assert len(serialized) < len(json.dumps(result, ensure_ascii=False, indent=2))


def test_history_compaction_removes_duplicate_event_metadata(monkeypatch):
    monkeypatch.delenv("NAPCAT_RESPONSE_MODE", raising=False)
    result = {
        "messages": [{
            "self_id": 10000,
            "user_id": 12345,
            "time": 1700000000,
            "message_id": 88,
            "message_seq": 99,
            "real_id": 88,
            "message_type": "group",
            "sender": {"user_id": 12345, "nickname": "Nick", "card": "Card", "role": "member"},
            "raw_message": "hello",
            "post_type": "message",
            "group_id": 67890,
            "group_name": "Group",
            "message": [{"type": "text", "data": {"text": "hello"}}],
        }]
    }

    compact = compact_tool_result("get_group_msg_history", result)

    assert compact == {
        "messages": [{
            "seq": 99,
            "id": 88,
            "time": 1700000000,
            "user_id": 12345,
            "name": "Card",
            "message": [{"type": "text", "data": {"text": "hello"}}],
        }],
        "count": 1,
    }
    assert len(serialize_tool_result(result, "get_group_msg_history")) < len(serialize_tool_result(result))


def test_merged_forward_nodes_are_compacted_recursively(monkeypatch):
    monkeypatch.delenv("NAPCAT_RESPONSE_MODE", raising=False)
    node = {
        "user_id": 12345,
        "time": 1700000000,
        "message_id": 88,
        "message_seq": 99,
        "sender": {"nickname": "Nick", "card": ""},
        "raw_message": "nested",
        "message": [{"type": "text", "data": {"text": "nested"}}],
    }
    result = {"messages": [{**node, "message": [{"type": "forward", "data": {"content": [node]}}]}]}

    compact = compact_tool_result("get_forward_msg", result)
    nested = compact["messages"][0]["message"][0]["data"]["content"][0]

    assert nested["name"] == "Nick"
    assert "sender" not in nested
    assert "raw_message" not in nested


def test_member_list_uses_columns_and_rows(monkeypatch):
    monkeypatch.delenv("NAPCAT_RESPONSE_MODE", raising=False)
    members = [
        {"group_id": 1, "user_id": 2, "nickname": "A", "card": "", "role": "member", "age": 0},
        {"group_id": 1, "user_id": 3, "nickname": "B", "card": "Bee", "role": "admin", "age": 0},
    ]

    compact = compact_tool_result("get_group_member_list", members)

    assert compact["columns"] == ["user_id", "nickname", "card", "role"]
    assert compact["rows"] == [[2, "A", "", "member"], [3, "B", "Bee", "admin"]]
    assert compact["count"] == 2


def test_full_response_mode_is_lossless(monkeypatch):
    monkeypatch.setenv("NAPCAT_RESPONSE_MODE", "full")
    result = {"messages": [{"raw_message": "keep me", "message": []}]}
    assert compact_tool_result("get_group_msg_history", result) is result



def test_light_reader_is_plain_text_without_machine_ids(monkeypatch):
    monkeypatch.setattr("napcat_mcp.server.time.localtime", lambda _: time.struct_time((2026, 7, 23, 8, 9, 0, 3, 204, -1)))
    result = {"messages": [{
        "message_id": 975974245,
        "message_seq": 975974245,
        "time": 1784675799,
        "user_id": 2819915628,
        "sender": {"nickname": "旅途不息", "card": ""},
        "message": [
            {"type": "reply", "data": {"id": "123"}},
            {"type": "text", "data": {"text": "你好\n世界"}},
            {"type": "image", "data": {"url": "https://very-long.example/image", "file": "secret.jpg"}},
        ],
    }]}

    rendered = render_group_messages_light(result)

    assert rendered == "2026-07-23\n08:09 旅途不息: [回复]你好\\n世界[图片]"
    assert "975974245" not in rendered
    assert "2819915628" not in rendered
    assert "https://" not in rendered
    assert "secret.jpg" not in rendered


def test_light_reader_count_is_bounded():
    assert ReadGroupMessagesParam(group_id=1, count=100).count == 100
    with pytest.raises(ValueError):
        ReadGroupMessagesParam(group_id=1, count=101)


def test_forward_message_id_schema_is_string():
    schema = GetForwardMsgParam.model_json_schema()
    assert schema["properties"]["message_id"]["type"] == "string"


def test_forward_message_id_keeps_19_digit_precision():
    message_id = "7663414735448210388"
    assert GetForwardMsgParam(message_id=message_id).message_id == message_id


def test_forward_message_id_accepts_legacy_integer_input():
    assert GetForwardMsgParam(message_id=12345).message_id == "12345"
