---
name: triage
description: >
  要件の優先度付け・バックログ整理・スコープ確定を行うフロー。
  「何から手をつけるか」「優先順位を決めたい」「バックログを整理して」
  「スコープを確定したい」「次に何を実装すべきか」
  のようなトリアージリクエストでトリガーする。
---

# [T] トリアージフロー

## 初動

1. **共通ルールを読む**: `${CLAUDE_PLUGIN_ROOT}/references/common_rules.md`
2. **フロー手順を読む**: `${CLAUDE_PLUGIN_ROOT}/references/flows/triage.md`
3. **操作リファレンスを読む**: `${CLAUDE_PLUGIN_ROOT}/references/doorstop_reference.md`

## 概要

「何を先に作るか決めたい」「バックログを整理したい」というときのフロー。
優先度付け、未着手REQの特定、スコープ合意を行う。

## フロー

フロー手順の詳細は `${CLAUDE_PLUGIN_ROOT}/references/flows/triage.md` に従う。

要約:
1. バックログ確認（`trace_query.py backlog`）
2. 優先度設定
3. 未着手REQの特定
4. ユーザーへの提示・スコープ合意
5. ベースライン作成（必要に応じて）
