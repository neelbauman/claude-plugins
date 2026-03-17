---
name: new
description: >
  新機能の追加・新要件の実装を行う仕様駆動開発フロー。
  「〜を作って」「〜を実装して」「新機能を追加して」「〜が欲しい」
  のような新規開発リクエストでトリガーする。
  REQ登録→設計策定→実装→テスト→トレーサビリティ検証の全サイクルを自律的に実行する。
context: fork
---

# 新規開発フロー

## 鉄則

1. コードを書く前に設計文書を書く（adopt フローのみ例外）
2. 振る舞い定義には `gherkin` 属性で Given/When/Then を書く
3. テストを書いたら TST を書く（常にペア）
4. 変更したら `impact_analysis.py` を回す
5. 最後に `validate_and_report.py --strict` を必ず実行する
6. 仕様変更時は `--serve` でダッシュボードを起動しレビューを促す
7. 関連アイテムの探索には `trace_query.py` を使う（YAML を grep しない）
8. 派生要求（`derived: true`）は設計層のみ。IMPL/TST では禁止
9. 外部ファイル紐付けには `references` を使う（`ref` は非推奨）
10. 仕様変更のコミットはドキュメント層ごとに分ける
11. 新ドメイン概念には `glossary.py add` で用語辞書を更新する
12. 重要な設計判断は ADR に記録する

## エージェント規約

- 非規範的アイテム（見出し・背景）は `--non-normative` で作成
- 報告は成果物ベースで簡潔に（Doorstop 内部構造は見せない）
- 初動で `doorstop_ops.py <dir> tree` を実行し、ツリー構造を動的に把握する
- 最下位設計文書 = IMPL/TST がリンクする直接の親（lite: SPEC, standard: SPEC, full: LLD）

## プロファイル

| プロファイル | 階層 |
|---|---|
| lite | REQ → SPEC → IMPL/TST · ADR |
| standard | REQ/NFR → ARCH → SPEC → IMPL/TST · ADR |
| full | REQ/NFR → HLD → LLD → IMPL/TST · ADR |

## スクリプト実行形式

`uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/<script>.py <project-dir> ...`

---

## フロー

### 1. 理解

ユーザーの要望を要件文に変換する。曖昧な場合のみ確認。

### 2. 分類

機能グループと優先度を決定（既存グループ or 新規、`--priority` を設定）。FR（機能要件）か NFR（非機能要件）かを判別する（判断基準は `${CLAUDE_PLUGIN_ROOT}/references/concepts/nfr.md` を参照）。

### 3. 用語確認

新しいドメイン概念が登場する場合、`glossary.py add` で用語辞書を更新し、`glossary.py sync` で REQ に反映する（詳細は `${CLAUDE_PLUGIN_ROOT}/references/concepts/glossary.md`）。

### 4. REQ 登録

```bash
doorstop_ops.py <dir> add -d REQ -t "要件文" -g GROUP --priority high
```

### 5. 設計策定

設計文書を上位から順に作成し、親へリンク。派生要求は `derived: true`。NFR 制約がある場合は設計文書から NFR アイテムへもリンクする。振る舞いの定義が必要な文書には **gherkin 属性** に Given/When/Then 形式でシナリオを記述する。

**lite プロファイル:**
1. 各 REQ に対して 1 つ以上の SPEC を作成
2. SPEC → REQ のリンクを張る

**standard プロファイル:**
1. 各 REQ に対して 1 つ以上の ARCH を作成（コンポーネント設計）
2. 各 ARCH に対して 1 つ以上の SPEC を作成（モジュール設計）
3. ARCH → REQ、SPEC → ARCH のリンクを張る

**full プロファイル:**
1. 各 REQ に対して 1 つ以上の HLD を作成（サブシステム設計）
2. 各 HLD に対して 1 つ以上の LLD を作成（モジュール設計）
3. HLD → REQ、LLD → HLD のリンクを張る

### 6. 実装・テスト

最下位設計文書に従ってコードとテストを書く（編集の順序は問わない）。gherkin のシナリオを TST のテストケースに変換する。

### 7. IMPL/TST 登録

`doorstop_ops.py add` でそれぞれ登録し、最下位設計にリンク。

### 8. レビュー

```bash
doorstop_ops.py <dir> chain-review <UID>
```

### 9. 検証

```bash
validate_and_report.py <dir> --strict
```

エラー 0 件を目指す。

### 10. コミット

ドキュメント層ごとにコミットを分ける。順序はプロジェクトの慣習に従う。

```bash
git add docs/reqs/REQ0XX.yml
git commit -m "spec: add REQ0XX [GROUP]"

git add docs/specs/SPEC0XX.yml
git commit -m "spec: add SPEC0XX for REQ0XX"

git add src/module.py docs/impl/IMPL0XX.yml
git commit -m "impl: IMPL0XX [summary]"

git add tests/test_module.py docs/tst/TST0XX.yml
git commit -m "test: TST0XX [summary]"
```

### 11. ベースライン更新

リリースポイントで `baseline_manager.py create <version> --tag`。

### 12. 報告

成果物ベースで簡潔に報告。

> **ADR**: どの段階でも重要な意思決定があれば ADR を作成する（`doorstop_ops.py add -d ADR ...`）。
> 詳細は `${CLAUDE_PLUGIN_ROOT}/references/concepts/adr.md` を参照。

---

## コマンドクイックリファレンス

```bash
# アイテム追加
doorstop_ops.py <dir> add -d <DOC> -t "テキスト" -g GROUP [--priority P] [--links UID...]

# gherkin 付きで追加
doorstop_ops.py <dir> add -d SPEC -t "仕様" -g GROUP --links REQ001 \
  --gherkin "Scenario: 正常系\n  Given ...\n  When ...\n  Then ..."

# リンク
doorstop_ops.py <dir> link <child-UID> <parent-UID>

# 一括レビュー
doorstop_ops.py <dir> chain-review <UID>

# 検証
validate_and_report.py <dir> --strict

# 影響分析
impact_analysis.py <dir> --detect-suspects

# ツリー構造確認
doorstop_ops.py <dir> tree
```

詳細は `${CLAUDE_PLUGIN_ROOT}/references/doorstop_reference.md` を参照。

---

## アイテムテンプレート（簡易版）

### REQ

```bash
doorstop_ops.py <dir> add -d REQ \
  -t "## 概要
[1-2文で要件を述べる]

## 受入基準
- [ ] 基準1
- [ ] 基準2" \
  -g GROUP --priority high
```

### SPEC（gherkin 付き）

```bash
doorstop_ops.py <dir> add -d SPEC \
  -t "## インターフェース
[API・関数シグネチャ]

## 振る舞い
[正常系・異常系の動作]

## エッジケース
[境界値・例外]" \
  --header "機能名" -g GROUP --links REQ001 \
  --gherkin "Scenario: 正常系
  Given 前提条件
  When 操作
  Then 期待結果

Scenario: 異常系
  Given 前提条件
  When エラーを引き起こす操作
  Then エラーが返る"
```

### IMPL

```bash
doorstop_ops.py <dir> add -d IMPL \
  -t "## 実装概要
[実装の説明]

## 設計判断
[なぜこの実装にしたか]" \
  -g GROUP \
  --references '[{"path":"src/module.py","type":"file"}]' --links SPEC001
```

### TST

```bash
doorstop_ops.py <dir> add -d TST \
  -t "## 目的
[何を検証するか]

## 検証観点
- TC-1: [テストケース1]
- TC-2: [テストケース2]" \
  -g GROUP \
  --references '[{"path":"tests/test_module.py","type":"file"}]' --links SPEC001
```

standard/full では `--test-level unit|integration|acceptance` を設定する。

詳細なテンプレートは `${CLAUDE_PLUGIN_ROOT}/references/item_writing_guide.md` を参照。

---

## 報告テンプレート

```
[GROUP] 機能名を実装しました。
  - src/xxx.py — 実装概要
  - tests/test_xxx.py — テストN件（全件パス）
  - トレーサビリティ: 全リンク済み、カバレッジ100%
```
