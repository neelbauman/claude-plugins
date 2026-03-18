#!/bin/bash
# Stop フック: スキル終了時に validate_and_report.py --strict を実行し、
# エラーまたは suspect がある場合はブロックする

echo "【SDD 検証】validate_and_report.py --strict を自動実行中..."

# validate_and_report.py を実行
if command -v uv &>/dev/null; then
  OUTPUT=$(uv run python "${CLAUDE_PLUGIN_ROOT}/scripts/reporting/validate_and_report.py" . --strict --json 2>&1)
  EXIT_CODE=$?
else
  OUTPUT=$(python "${CLAUDE_PLUGIN_ROOT}/scripts/reporting/validate_and_report.py" . --strict --json 2>&1)
  EXIT_CODE=$?
fi

echo "$OUTPUT"

# バリデーションエラー（exit code 1）の場合はブロック
if [[ $EXIT_CODE -ne 0 ]]; then
  echo "" >&2
  echo "【SDD 検証失敗】バリデーションエラーが検出されました。" >&2
  echo "エラーを解消してから再度スキルを完了してください。" >&2
  exit 2
fi

# suspect チェック（impact_analysis.py --detect-suspects）
echo ""
echo "【SDD 検証】suspect チェック中..."
if command -v uv &>/dev/null; then
  SUSPECT_OUTPUT=$(uv run python "${CLAUDE_PLUGIN_ROOT}/scripts/core/impact_analysis.py" . --detect-suspects 2>&1)
  SUSPECT_CODE=$?
else
  SUSPECT_OUTPUT=$(python "${CLAUDE_PLUGIN_ROOT}/scripts/core/impact_analysis.py" . --detect-suspects 2>&1)
  SUSPECT_CODE=$?
fi

# suspect が検出された場合（出力に "変更アイテム: 0件" でなければ suspect あり）
if echo "$SUSPECT_OUTPUT" | grep -q "変更アイテム: [1-9]"; then
  echo "$SUSPECT_OUTPUT"
  echo "" >&2
  echo "【SDD 検証失敗】suspect が検出されました。" >&2
  echo "chain-clear で suspect を解消してから再度スキルを完了してください。" >&2
  exit 2
fi

echo "【SDD 検証完了】エラー 0件、suspect 0件 ✓"
exit 0
