---
name: init
description: >
  新規（グリーンフィールド）プロジェクトに仕様駆動開発を導入するフロー。
  「プロジェクトを始めたい」「ゼロから仕様駆動開発を始めたい」
  「新しいプロジェクトを初期化して」「SDD環境をセットアップして」
  のような新規プロジェクト初期化リクエストでトリガーする。
  adopt との違い: adopt は既存コードからの逆引き、init はゼロから始める。
argument-hint: "<プロジェクトパス> [--profile lite|standard|full]"
---

# 新規プロジェクト初期化フロー

共通ルールは `${CLAUDE_SKILL_DIR}/../_shared/rules.md` を参照。

ユーザーの要望: $ARGUMENTS

---

## adopt との違い

| | init（このフロー） | adopt |
|---|---|---|
| 対象 | 新規プロジェクト（コードなし） | 既存プロジェクト（コードあり） |
| 方向 | 要件 → 設計 → 実装（トップダウン） | コード → 仕様（ボトムアップ逆引き） |
| 鉄則1 | 適用（設計を先に書く） | 例外（コードから仕様を抽出） |

## フロー

### 1. プロファイル選択

ユーザーにプロファイル（lite / standard / full）を確認する。判断基準:

| プロファイル | 適用場面 |
|---|---|
| lite | 小規模（単体ライブラリ、個人開発） |
| standard | 中規模（複数サブシステム、チーム開発） |
| full | 大規模（規制産業、V字モデル準拠） |

### 2. プロジェクト初期化

```bash
uv add doorstop --dev
uv add markdown --dev
uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/init_project.py <project-dir> --profile <lite|standard|full>

# NFR ドキュメントも作成する場合:
uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/init_project.py <project-dir> --profile <profile> --with-nfr
```

### 3. 用語辞書の初期設定

プロジェクト固有のドメイン用語があれば、REQ 先頭に非規範的アイテムとして用語定義を作成する。

```bash
# 用語辞書に追加
uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/glossary.py <project-dir> add "用語" "定義"
```

詳細は `${CLAUDE_PLUGIN_ROOT}/references/concepts/glossary.md` を参照。

### 4. 最初の REQ 登録

ユーザーと対話的に最初の要件を登録する。

```bash
doorstop_ops.py <dir> add -d REQ \
  -t "## 概要
[要件の説明]

## 受入基準
- [ ] 基準1
- [ ] 基準2" \
  -g GROUP --priority high
```

### 5. 検証

```bash
validate_and_report.py <dir> --strict
```

### 6. 報告

初期化結果を報告する:
- 作成されたドキュメントツリー構造
- 登録された REQ の数
- 次のステップ（`/doorstop-spec-driven:new` で開発を開始）

---

## コマンドクイックリファレンス

```bash
# プロジェクト初期化
init_project.py <dir> --profile <lite|standard|full> [--with-nfr]

# ツリー構造確認
doorstop_ops.py <dir> tree

# アイテム追加
doorstop_ops.py <dir> add -d <DOC> -t "テキスト" -g GROUP [--priority P]

# 非規範的アイテム追加
doorstop_ops.py <dir> add -d <DOC> -t "テキスト" --non-normative

# 用語辞書
glossary.py <dir> add "用語" "定義"

# 検証
validate_and_report.py <dir> --strict
```

詳細は `${CLAUDE_PLUGIN_ROOT}/references/doorstop_reference.md` を参照。
