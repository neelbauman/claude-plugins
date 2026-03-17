---
name: change
description: >
  既存の仕様・設計・実装に対する変更を行うフロー。
  「〜を変更して」「〜を修正して」「仕様を変えたい」「リファクタリングして」
  「〜を改善して」のような既存機能の変更リクエストでトリガーする。
  影響分析→設計更新→実装・テスト修正→検証の手順で進める。
---

# [B] 変更フロー

## 初動

1. **共通ルールを読む**: `${CLAUDE_PLUGIN_ROOT}/references/common_rules.md`
2. **フロー手順を読む**: `${CLAUDE_PLUGIN_ROOT}/references/flows/change.md`
3. **操作リファレンスを読む**: `${CLAUDE_PLUGIN_ROOT}/references/doorstop_reference.md`

## 概要

既存の仕様・設計・実装に対する変更要望があったときのフロー。
影響分析から始め、設計更新→実装・テスト修正→検証を行う。

## フロー

フロー手順の詳細は `${CLAUDE_PLUGIN_ROOT}/references/flows/change.md` に従う。

要約:
1. 現状把握（`trace_query.py chain`）
2. 影響分析（`impact_analysis.py --changed`）
3. 設計更新（上位から順に）
4. 実装・テスト修正
5. IMPL/TST更新・suspect解消
6. 検証・コミット・報告
