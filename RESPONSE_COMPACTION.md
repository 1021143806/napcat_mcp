# MCP response compaction

NapCat's OneBot history payload repeats transport metadata and `raw_message` for every
message and every nested merged-forward node. Large list APIs also repeat identical
JSON field names on every row. These shapes are useful for event consumers, but waste
LLM context when returned as MCP text content.

## Compact mode (default)

- History, single-message, and merged-forward results keep `seq`, `id`, `time`,
  `user_id`, display `name`, and structured `message`.
- Nested merged-forward message records are compacted recursively.
- Group members, groups, and friends use a self-describing `columns` + `rows` table.
- Other responses retain their existing shape (with nested message records compacted).
- JSON remains UTF-8 and whitespace-free.

Set `NAPCAT_RESPONSE_MODE=full` (aliases: `raw`, `lossless`) to return the exact
NapCat data object without field compaction.

## Dedicated lightweight reader

`read_group_messages(group_id, count)` is intentionally separate from
`get_group_msg_history`. It returns a plain-text timeline with date headings and lines
like `HH:MM display name: content`. It omits message IDs/sequences, QQ IDs when a display
name is available, event metadata, attachment URLs, and file fields. Text is emitted
directly while non-text segments become short markers such as `[图片]`, `[回复]`, or
`[转发消息]`. Use the detailed history tool only for pagination or follow-up operations.
The count is bounded to 1-100.

A live 17-message sample measured 12,887 B raw, 4,765 B in the existing compact JSON,
and 1,065 B through the lightweight reader (91.7% below raw and 77.6% below compact).

## Real deployment benchmark

Measured against a live NapCat instance on 2026-07-20; message contents were never
printed or copied from the server:

| Tool | Before | After | Reduction |
|---|---:|---:|---:|
| `get_group_list` | 1,112 B | 480 B | 56.8% |
| `get_group_member_list` (333 rows) | 108,657 B | 26,491 B | 75.6% |
| `get_group_msg_history` (184 rows) | 146,520 B | 54,602 B | 62.7% |

The deployed Claude instance returned a 20-message result in 5,736 bytes with the
stable keys `seq,id,time,user_id,name,message`, versus 15,421 bytes for the sampled
uncompacted response.
