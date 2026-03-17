---
name: report
description: >
  プロジェクトの状況確認・レポート生成を行うフロー。
  「状況を教えて」「カバレッジは？」「suspectある？」「レポートを見せて」
  「ダッシュボードを起動して」のような状況確認リクエストでトリガーする。
---

# [D] レポートフロー

## 初動

1. **共通ルールを読む**: `${CLAUDE_PLUGIN_ROOT}/references/common_rules.md`
2. **フロー手順を読む**: `${CLAUDE_PLUGIN_ROOT}/references/flows/report.md`
3. **操作リファレンスを読む**: `${CLAUDE_PLUGIN_ROOT}/references/doorstop_reference.md`

## 概要

ユーザーが状況確認を要望したときのフロー。
trace_query.py や validate_and_report.py を使って照会・レポート生成する。

## フロー

フロー手順の詳細は `${CLAUDE_PLUGIN_ROOT}/references/flows/report.md` に従う。

主要コマンド:
| やりたいこと | コマンド |
|---|---|
| プロジェクト全体サマリ | `trace_query.py <dir> status` |
| 特定UIDのチェーン | `trace_query.py <dir> chain <UID>` |
| ファイルからチェーン逆引き | `trace_query.py <dir> chain --file <path>` |
| カバレッジ詳細 | `trace_query.py <dir> coverage [--group GROUP]` |
| suspect一覧 | `trace_query.py <dir> suspects` |
| リンク漏れ検出 | `trace_query.py <dir> gaps [--document IMPL]` |
| 優先度付きバックログ | `trace_query.py <dir> backlog [--group GROUP]` |
| 静的HTMLレポート | `validate_and_report.py <dir> --output-dir ./reports --strict` |
| ダッシュボード | `validate_and_report.py <dir> --serve [--port 8080]` |
| 影響分析 | `impact_analysis.py <dir> --detect-suspects [--json PATH]` |
