---
name: bugfix
description: >
  バグの修正を行うフロー。
  「バグを直して」「〜が動かない」「エラーが出る」「不具合がある」
  「〜がおかしい」のようなバグ修正リクエストでトリガーする。
  原因特定→仕様/実装バグ判別→修正→再発防止テスト→検証を自律的に実行する。
---

# [C] バグ修正フロー

## 初動

1. **共通ルールを読む**: `${CLAUDE_PLUGIN_ROOT}/references/common_rules.md`
2. **フロー手順を読む**: `${CLAUDE_PLUGIN_ROOT}/references/flows/bugfix.md`
3. **操作リファレンスを読む**: `${CLAUDE_PLUGIN_ROOT}/references/doorstop_reference.md`

## 概要

バグの報告や修正要望があったときのフロー。
仕様バグか実装バグかを判別し、適切な修正手順に進む。

## フロー

フロー手順の詳細は `${CLAUDE_PLUGIN_ROOT}/references/flows/bugfix.md` に従う。

要約:
1. 原因特定（`trace_query.py chain --file`）
2. 仕様バグ vs 実装バグの判別
   - 仕様バグ → `/doorstop-spec-driven:change` フローへ移行
   - 実装バグ → 以下を続行
3. コード修正
4. 再発防止テスト追加
5. IMPL更新・検証
6. コミット・報告
