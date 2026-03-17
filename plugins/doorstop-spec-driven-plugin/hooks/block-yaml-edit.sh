#!/bin/bash
# Doorstop YAML ファイルの直接編集をブロックするフック
# doorstop_ops.py 経由での操作を強制する（鉄則7の機械的強制）
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# .doorstop.yml 設定ファイルは除外（init_project.py が直接操作する）
BASENAME=$(basename "$FILE_PATH")
if [[ "$BASENAME" == ".doorstop.yml" ]]; then
  exit 0
fi

# Doorstop アイテム YAML（REQ001.yml, SPEC002.yml 等）の直接編集をブロック
if [[ "$FILE_PATH" == *.yml ]] || [[ "$FILE_PATH" == *.yaml ]]; then
  # doorstop ディレクトリ配下かどうかを判定
  # 典型的パターン: docs/reqs/REQ001.yml, specification/specs/SPEC001.yml 等
  if echo "$FILE_PATH" | grep -qiE '/(reqs?|specs?|arch|hld|lld|impl|tst|tests?|adr|nfr)/[A-Z]+[0-9]+\.ya?ml$'; then
    echo "Doorstop アイテム YAML は直接編集できません。doorstop_ops.py 経由で操作してください。" >&2
    exit 2
  fi
fi

exit 0
