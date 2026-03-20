#!/bin/bash
# Doorstop CLI の直接実行をブロックするフック
# doorstop_ops.py / trace_query.py 経由での操作を強制する
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [[ -z "$COMMAND" ]]; then
  exit 0
fi

# 許可: uv run python.*doorstop_ops / trace_query / validate_and_report 等（正規の経路）
if echo "$COMMAND" | grep -qE 'uv run python.*doorstop_ops|uv run python.*trace_query|uv run python.*validate_and_report|uv run python.*impact_analysis|uv run python.*baseline_manager|uv run python.*glossary|uv run python.*init_project|uv run python.*mcp_server'; then
  exit 0
fi

# 許可: doorstop publish（HTMLエクスポート用）
if echo "$COMMAND" | grep -qE '^\s*doorstop\s+publish'; then
  exit 0
fi

# ブロック: doorstop add/link/unlink/clear/review/edit/delete/reorder/remove の直接実行
if echo "$COMMAND" | grep -qE '(^|\s|;|&&|\|)doorstop\s+(add|link|unlink|clear|review|edit|delete|reorder|remove)\b'; then
  echo "Doorstop CLI の直接実行はブロックされています。doorstop_ops.py 経由で操作してください。" >&2
  echo "例: uv run python \${CLAUDE_PLUGIN_ROOT}/scripts/core/doorstop_ops.py <dir> add -d REQ -t \"テキスト\"" >&2
  exit 2
fi

exit 0
