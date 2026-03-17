---
name: adopt
description: >
  既存プロジェクトに仕様駆動開発を初期導入するフロー。
  「仕様駆動開発を導入したい」「既存コードに仕様を付けたい」
  「Doorstopを導入して」「SDDを始めたい」
  のような初期導入リクエストでトリガーする。
  コード→ドキュメントの逆引き仕様化を行う。鉄則1の例外フロー。
argument-hint: "[プロジェクトパス]"
context: fork
hooks:
  Stop:
    - hooks:
        - type: prompt
          prompt: "validate_and_report.py --strict を実行してエラー0件を確認しましたか？"
          model: haiku
---

# 初期導入フロー（既存プロジェクトへの適用）

> **注意**: このフローは鉄則1「コードを書く前に設計文書を書く」の唯一の例外。
> 既存コードから逆引きで仕様を抽出する。

共通ルールは `${CLAUDE_SKILL_DIR}/../_shared/rules.md` を参照（鉄則1はこのフローでは例外）。

ユーザーの要望: $ARGUMENTS

---

## セットアップ

```bash
uv add doorstop --dev
uv add markdown --dev
uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/init_project.py <project-dir> --profile standard --no-git-init

# NFR ドキュメントも作成する場合:
uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/init_project.py <project-dir> --profile standard --with-nfr --no-git-init
```

## フロー

### 1. プロジェクト初期化

`init_project.py` でプロファイルに応じたドキュメントツリーを作成する。

### 2. コード読解

既存コードの構造・機能・テストを把握する。

### 3. 用語辞書作成

プロジェクト固有のドメイン用語を棚卸しし、REQ 先頭に非規範的アイテムとして用語定義を作成する（詳細は `${CLAUDE_PLUGIN_ROOT}/references/concepts/glossary.md`）。

### 4. REQ 抽出

実装されている機能を要件として文書化（実態を記述、理想ではなく）。FR / NFR の分類も行う（判断基準は `${CLAUDE_PLUGIN_ROOT}/references/concepts/nfr.md`）。

### 5. 設計文書作成

コードの実態に基づいて SPEC（+ARCH）を作成。gherkin 属性に振る舞いシナリオを記述する。

### 6. IMPL 紐付け

既存コードを IMPL アイテムとして登録し、`references` で紐づけ。

### 7. TST 紐付け

既存テストを TST アイテムとして登録し、`references` で紐づけ。

### 8. ベースライン確立

全アイテムの clear & review を実行。

```bash
doorstop_ops.py <dir> chain-clear <root-UID>
doorstop_ops.py <dir> chain-review <root-UID>
```

### 9. 検証

```bash
validate_and_report.py <dir> --strict
```

### 10. 移行完了

以後は通常フロー（new/change/bugfix 等）に移行。

## 注意事項

- 一度にすべて網羅しなくてよい。主要機能から段階的に導入する
- 既存テストがない機能は TST アイテムのみ作成し、テストは後日追加でもよい
- ベースライン確立前の suspect は過渡期ノイズであり、一括 clear する

## 段階的導入の目安

| 規模 | Phase 1 の対象 |
|------|---------------|
| 小規模（~1万行） | 全機能（全量一括でも可能） |
| 中規模（1-10万行） | 主要サブシステム2-3個 |
| 大規模（10万行~） | 最も変更頻度の高いモジュール群 |

詳細は `${CLAUDE_PLUGIN_ROOT}/references/scaling_strategy.md` を参照。

---

## コマンドクイックリファレンス

```bash
# プロジェクト初期化
init_project.py <dir> --profile <lite|standard|full> [--with-nfr] [--no-git-init]

# アイテム追加
doorstop_ops.py <dir> add -d <DOC> -t "テキスト" -g GROUP [--links UID...]

# 非規範的アイテム追加
doorstop_ops.py <dir> add -d <DOC> -t "テキスト" --non-normative

# リンク
doorstop_ops.py <dir> link <child-UID> <parent-UID>

# 一括 clear & review
doorstop_ops.py <dir> chain-clear <UID>
doorstop_ops.py <dir> chain-review <UID>

# 検証
validate_and_report.py <dir> --strict
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
  -g GROUP --priority medium
```

### SPEC（gherkin 付き）

```bash
doorstop_ops.py <dir> add -d SPEC \
  -t "## インターフェース
[API・関数シグネチャ]

## 振る舞い
[正常系・異常系の動作]" \
  --header "機能名" -g GROUP --links REQ001 \
  --gherkin "Scenario: 正常系
  Given 前提条件
  When 操作
  Then 期待結果"
```

### IMPL

```bash
doorstop_ops.py <dir> add -d IMPL \
  -t "## 実装概要
[実装の説明]" \
  -g GROUP \
  --references '[{"path":"src/module.py","type":"file"}]' --links SPEC001
```

### TST

```bash
doorstop_ops.py <dir> add -d TST \
  -t "## 目的
[何を検証するか]

## 検証観点
- TC-1: [テストケース1]" \
  -g GROUP \
  --references '[{"path":"tests/test_module.py","type":"file"}]' --links SPEC001
```

詳細なテンプレートは `${CLAUDE_PLUGIN_ROOT}/references/item_writing_guide.md` を参照。
