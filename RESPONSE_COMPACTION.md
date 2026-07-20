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
