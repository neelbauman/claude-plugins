---
name: doorstop-spec-driven:init
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

依存関係のインストールと初期化:

```bash
uv add doorstop --dev
uv add markdown --dev
```

```
sdd_init(project_dir, profile="standard", with_nfr=False)
```

NFR ドキュメントも作成する場合は `with_nfr=True` を指定。

### 3. 用語辞書の初期設定

プロジェクト固有のドメイン用語があれば登録する。

```
sdd_glossary_add(project_dir, term="用語", definition="定義")
```

詳細は `${CLAUDE_SKILL_DIR}/../references/concepts/glossary.md` を参照。

### 4. 最初の REQ 登録

ユーザーと対話的に最初の要件を登録する。

```
sdd_add_item(project_dir, document="REQ", text="## 概要\n[要件の説明]\n\n## 受入基準\n- [ ] 基準1", group="GROUP", priority="high")
```

### 5. 検証

```
sdd_validate(project_dir)
```

### 6. 報告

初期化結果を報告する:
- 作成されたドキュメントツリー構造
- 登録された REQ の数
- 次のステップ（`/doorstop-spec-driven:new` で開発を開始）

---

## リファレンス

- **アイテムテンプレート**: `${CLAUDE_SKILL_DIR}/../references/item_writing_guide.md`
- **CLI フォールバック**: `${CLAUDE_SKILL_DIR}/../references/command_reference.md`
- **Doorstop 詳細**: `${CLAUDE_SKILL_DIR}/../references/doorstop_reference.md`
