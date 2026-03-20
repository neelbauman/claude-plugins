#!/bin/bash
# セッション開始時に Doorstop プロジェクトを検出し、サマリを表示する
# .doorstop.yml が見つからなければサイレント終了

# Doorstop プロジェクトかどうかを判定
if ! find . -maxdepth 3 -name ".doorstop.yml" -print -quit 2>/dev/null | grep -q .; then
  exit 0
fi

echo "【SDD】Doorstop プロジェクトを検出しました。プロジェクトサマリを取得中..."

# trace_query.py status でサマリを表示
if command -v uv &>/dev/null; then
  uv run python "${CLAUDE_PLUGIN_ROOT}/scripts/core/trace_query.py" . status 2>/dev/null || echo "（サマリ取得をスキップ）"
else
  python "${CLAUDE_PLUGIN_ROOT}/scripts/core/trace_query.py" . status 2>/dev/null || echo "（サマリ取得をスキップ）"
fi

echo ""
echo "【SDD リマインダー】"
echo "  - Doorstop YAML は doorstop_ops.py 経由で操作する"
echo "  - 最後に validate_and_report.py --strict を実行する"
echo "  - YAML を直接 grep/edit しない"
