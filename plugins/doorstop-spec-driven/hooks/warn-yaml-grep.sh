#!/bin/bash
# Doorstop ディレクトリ内の YAML を直接 Grep する操作をブロック（鉄則7 の機械的強制）
INPUT=$(cat)
PATTERN=$(echo "$INPUT" | jq -r '.tool_input.pattern // empty')
PATH_ARG=$(echo "$INPUT" | jq -r '.tool_input.path // empty')
GLOB_ARG=$(echo "$INPUT" | jq -r '.tool_input.glob // empty')

# パスが Doorstop ディレクトリ配下の YAML を指している場合をブロック
if echo "$PATH_ARG" | grep -qiE '/(reqs?|specs?|arch|hld|lld|impl|tst|tests?|adr|nfr)/'; then
  echo "Doorstop YAML の直接 Grep はブロックされています（鉄則7）。" >&2
  echo "代わりに以下のコマンドを使用してください:" >&2
  echo "  - テキスト検索: uv run python \${CLAUDE_PLUGIN_ROOT}/scripts/core/doorstop_ops.py <dir> find \"キーワード\"" >&2
  echo "  - 属性検索: uv run python \${CLAUDE_PLUGIN_ROOT}/scripts/core/trace_query.py <dir> search \"パターン\"" >&2
  exit 2
fi

# glob が YAML を指し、かつパスが Doorstop ディレクトリの場合もブロック
if echo "$GLOB_ARG" | grep -qiE '\.ya?ml'; then
  if echo "$PATH_ARG" | grep -qiE '/(reqs?|specs?|arch|hld|lld|impl|tst|tests?|adr|nfr)'; then
    echo "Doorstop YAML の直接 Grep はブロックされています（鉄則7）。" >&2
    echo "trace_query.py search または doorstop_ops.py find を使用してください。" >&2
    exit 2
  fi
fi

exit 0
