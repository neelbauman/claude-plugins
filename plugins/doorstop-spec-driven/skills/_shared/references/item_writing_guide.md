# Doorstop アイテム記述ガイド — 詳細テンプレート

## 概要

Doorstop の `text` フィールドは **Markdown** をサポートしている。
1行の要約だけでなく、構造化された詳細な記述を行うことで、
仕様の正確性・レビュー効率・トレーサビリティが大幅に向上する。

本ガイドでは各層（REQ / SPEC / IMPL / TST）の詳細な書き方テンプレートと
実例を示す。

---

## 共通ルール

- `header` は **短い見出し**（20文字以内推奨）
- `text` に **Markdown で詳細を記述**する
- `groups` で機能グループを横断分類する（リスト型）
- `priority` で優先度を設定する（REQ/NFRのみ。`critical` / `high` / `medium` / `low` / `none` / `done`）
- `level` でドキュメント内の階層を表現する
- YAMLのリテラルブロック `|` を使い、複数行テキストを記述する
- `ref` は非推奨 — 外部ファイル紐付けには `references` を使う

---

## ドキュメント種別ごとのテンプレート

| ドキュメント種別 | 説明 | ガイド |
|---|---|---|
| **REQ** | 要件 — What を定義する | [req.md](./item_writing_guide/req.md) |
| **NFR** | 非機能要件 — どの品質水準かを定義する | [nfr.md](./item_writing_guide/nfr.md) |
| **Non-normative** | 見出し・コンテキスト — 文脈を提供する | [non_normative.md](./item_writing_guide/non_normative.md) |
| **ADR** | 決定 — Why を定義する | [adr.md](./item_writing_guide/adr.md) |
| **ARCH** | 基本設計（standard） — Architecture を定義する | [arch.md](./item_writing_guide/arch.md) |
| **HLD** | 基本設計（full） — Architecture を定義する | [hld.md](./item_writing_guide/hld.md) |
| **LLD** | 詳細設計（full） — How を定義する | [lld.md](./item_writing_guide/lld.md) |
| **SPEC** | 仕様 — How を定義する | [spec.md](./item_writing_guide/spec.md) |
| **IMPL** | 実装 — 実装の生きた記録 | [impl.md](./item_writing_guide/impl.md) |
| **TST** | テスト — Verify を定義する | [tst.md](./item_writing_guide/tst.md) |

## 横断的ガイダンス

| トピック | ガイド |
|---|---|
| Why の書き分け・level・groups・derived・マルチリンク | [practical_guidance.md](./item_writing_guide/practical_guidance.md) |
| 詳細度の判断基準・Markdown記法・YAML注意事項 | [formatting.md](./item_writing_guide/formatting.md) |
