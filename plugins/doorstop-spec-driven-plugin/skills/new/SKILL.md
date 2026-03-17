---
name: new
description: >
  新機能の追加・新要件の実装を行う仕様駆動開発フロー。
  「〜を作って」「〜を実装して」「新機能を追加して」「〜が欲しい」
  のような新規開発リクエストでトリガーする。
  REQ登録→設計策定→実装→テスト→トレーサビリティ検証の全サイクルを自律的に実行する。
---

# [A] 新規開発フロー

## 初動

1. **共通ルールを読む**: `${CLAUDE_PLUGIN_ROOT}/references/common_rules.md`
2. **フロー手順を読む**: `${CLAUDE_PLUGIN_ROOT}/references/flows/new_development.md`
3. **操作リファレンスを読む**: `${CLAUDE_PLUGIN_ROOT}/references/doorstop_reference.md`
4. **アイテムの書き方を読む**: `${CLAUDE_PLUGIN_ROOT}/references/item_writing_guide.md`

## 概要

ユーザーが新機能の追加や新要件の実装を要望したときのフロー。
REQ→設計→実装→テストの全サイクルを自律的に実行する。

## フロー

フロー手順の詳細は `${CLAUDE_PLUGIN_ROOT}/references/flows/new_development.md` に従う。

要約:
1. 要件理解 → REQ登録
2. 設計策定（プロファイルに応じた階層）
3. 実装・テスト
4. IMPL/TST登録
5. レビュー・検証
6. コミット・報告
