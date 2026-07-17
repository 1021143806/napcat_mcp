import json

from napcat_mcp.server import GetForwardMsgParam, serialize_tool_result


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


def test_forward_message_id_schema_is_string():
    schema = GetForwardMsgParam.model_json_schema()
    assert schema["properties"]["message_id"]["type"] == "string"


def test_forward_message_id_keeps_19_digit_precision():
    message_id = "7663414735448210388"
    assert GetForwardMsgParam(message_id=message_id).message_id == message_id


def test_forward_message_id_accepts_legacy_integer_input():
    assert GetForwardMsgParam(message_id=12345).message_id == "12345"
