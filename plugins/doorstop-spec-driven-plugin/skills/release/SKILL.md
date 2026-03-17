---
name: release
description: >
  リリース前の品質チェック・ゲート判定を行うフロー。
  「リリースしたい」「リリースチェックして」「リリース前の確認」
  「出荷判定」のようなリリースゲートリクエストでトリガーする。
---

# [E] リリースゲートフロー

## 初動

1. **共通ルールを読む**: `${CLAUDE_PLUGIN_ROOT}/references/common_rules.md`
2. **フロー手順を読む**: `${CLAUDE_PLUGIN_ROOT}/references/flows/release_gate.md`
3. **操作リファレンスを読む**: `${CLAUDE_PLUGIN_ROOT}/references/doorstop_reference.md`

## 概要

リリース前の必須チェックリストを実行し、品質ゲートの合否を判定する。

## フロー

フロー手順の詳細は `${CLAUDE_PLUGIN_ROOT}/references/flows/release_gate.md` に従う。

必須チェック（この順序で実行）:
1. **バリデーションエラー 0件** — `validate_and_report.py <dir> --strict`
2. **全カバレッジ 100%** — `trace_query.py <dir> coverage`
3. **suspect 0件** — `impact_analysis.py <dir> --detect-suspects`
4. **テスト全件パス** — プロジェクトのテストランナー
5. **未レビュー 0件** — `trace_query.py <dir> status`（警告のみ）
6. **ベースライン作成** — `baseline_manager.py <dir> create <version> --tag`（推奨）
