---
name: adr
description: >
  設計判断・意思決定をADR（Architecture Decision Record）に記録するフロー。
  「ADRを書いて」「判断を記録して」「なぜこうしたか残したい」
  「設計方針を記録して」のような意思決定記録リクエストでトリガーする。
  ユーザーとの議論で方針が確定したときにも自動的にトリガーする。
---

# [H] 意思決定記録フロー

## 初動

1. **共通ルールを読む**: `${CLAUDE_PLUGIN_ROOT}/references/common_rules.md`
2. **フロー手順を読む**: `${CLAUDE_PLUGIN_ROOT}/references/flows/decision_record.md`
3. **操作リファレンスを読む**: `${CLAUDE_PLUGIN_ROOT}/references/doorstop_reference.md`

## 概要

ユーザーとの議論・検討・レビューの結果として意思決定が確定したとき、
その判断根拠をADRに記録する。

## トリガーシグナル

以下の場合にこのフローを使う:
- ユーザーとの議論で設計方針が決まった
- 複数の代替案を比較検討し、1つを採用した
- 既存の設計判断を覆す変更を行った
- 「なぜこうしたのか」を将来のために残すべきと判断した
- ユーザーが明示的にADRの作成を依頼した

ADRを書かなくてよいケース:
- 自明な実装判断（標準ライブラリ使用など）
- 一時的な回避策（IMPL の TODO に記録）
- コードを読めば理由が明らかな変更

## フロー

フロー手順の詳細は `${CLAUDE_PLUGIN_ROOT}/references/flows/decision_record.md` に従う。

要約:
1. 議論の要約（課題・選択肢・決定事項・根拠・トレードオフ）
2. 関連アイテムの特定
3. ADR作成（`doorstop_ops.py add -d ADR`）
4. 本文記述（コンテキスト→決定→結果→棄却代替案）
5. レビュー・ステータス設定
6. 報告
