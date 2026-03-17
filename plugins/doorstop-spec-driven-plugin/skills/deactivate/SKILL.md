---
name: deactivate
description: >
  機能削除・要件取り下げを行うフロー。
  「〜を削除して」「〜を廃止して」「この機能はもう要らない」
  「要件を取り下げたい」のような非活性化リクエストでトリガーする。
  物理削除ではなく active: false によるソフトデリートと連鎖処理を行う。
---

# [G] 非活性化フロー

## 初動

1. **共通ルールを読む**: `${CLAUDE_PLUGIN_ROOT}/references/common_rules.md`
2. **フロー手順を読む**: `${CLAUDE_PLUGIN_ROOT}/references/flows/deactivation.md`
3. **操作リファレンスを読む**: `${CLAUDE_PLUGIN_ROOT}/references/doorstop_reference.md`

## 概要

機能削除や要件取り下げの要望があったときのフロー。
アイテムは物理削除せず、`active: false` で管理する。

## フロー

フロー手順の詳細は `${CLAUDE_PLUGIN_ROOT}/references/flows/deactivation.md` に従う。

要約:
1. 影響確認（`trace_query.py chain <UID>`）
2. ユーザー確認（非活性化対象と影響範囲を提示）
3. チェーン非活性化（`doorstop_ops.py deactivate-chain <UID>`）
4. 検証（`validate_and_report.py --strict`）
5. 報告

再活性化: `doorstop_ops.py activate-chain <UID>`
