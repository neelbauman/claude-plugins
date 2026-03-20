---
name: doorstop-spec-driven:adopt
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
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/hooks/stop-validate.sh"
---

# 初期導入フロー（既存プロジェクトへの適用）

> **注意**: このフローは鉄則1「コードを書く前に設計文書を書く」の唯一の例外。
> 既存コードから逆引きで仕様を抽出する。

共通ルールは `${CLAUDE_SKILL_DIR}/../_shared/rules.md` を参照（鉄則1はこのフローでは例外）。

ユーザーの要望: $ARGUMENTS

---

## フロー

### 1. プロジェクト初期化

```
sdd_init(project_dir, profile="standard", with_nfr=False)
```

NFR ドキュメントも作成する場合は `with_nfr=True` を指定。依存関係のインストール:

```bash
uv add doorstop --dev
uv add markdown --dev
```

### 2. コード読解

既存コードの構造・機能・テストを把握する。

### 3. 用語辞書作成

プロジェクト固有のドメイン用語を棚卸しし、用語辞書に登録する。

```
sdd_glossary_add(project_dir, term="用語", definition="定義")
```

詳細は `${CLAUDE_SKILL_DIR}/../references/concepts/glossary.md` を参照。

### 4. REQ 抽出

実装されている機能を要件として文書化（実態を記述、理想ではなく）。FR / NFR の分類も行う（判断基準は `${CLAUDE_SKILL_DIR}/../references/concepts/nfr.md`）。

```
sdd_add_item(project_dir, document="REQ", text="要件文", group="GROUP")
```

### 5. 設計文書作成

コードの実態に基づいて SPEC（+ARCH）を作成。gherkin 属性に振る舞いシナリオを記述する。

```
sdd_add_item(project_dir, document="SPEC", text="仕様", group="GROUP",
             links=["REQ001"], gherkin="Scenario: ...")
```

### 6. IMPL 紐付け

既存コードを IMPL アイテムとして登録し、`references` で紐づけ。

```
sdd_add_item(project_dir, document="IMPL", text="実装説明", group="GROUP",
             references=[{"path":"src/module.py","type":"file"}], links=["SPEC001"])
```

### 7. TST 紐付け

既存テストを TST アイテムとして登録し、`references` で紐づけ。

```
sdd_add_item(project_dir, document="TST", text="テスト説明", group="GROUP",
             references=[{"path":"tests/test_module.py","type":"file"}], links=["SPEC001"])
```

### 8. ベースライン確立

全アイテムの clear & review を実行。

```
sdd_chain_clear(project_dir, uids=["REQ001"])
sdd_chain_review(project_dir, uids=["REQ001"])
```

### 9. 検証

```
sdd_validate(project_dir)
```

**バリデーション失敗時**: ベースライン確立前の suspect は過渡期ノイズであり、一括 clear する。リンク漏れは `sdd_link` で補完。

### 10. 移行完了

以後は通常フロー（new/change/bugfix 等）に移行。

## 注意事項

- 一度にすべて網羅しなくてよい。主要機能から段階的に導入する
- 既存テストがない機能は TST アイテムのみ作成し、テストは後日追加でもよい

## 段階的導入の目安

| 規模 | Phase 1 の対象 |
|------|---------------|
| 小規模（~1万行） | 全機能（全量一括でも可能） |
| 中規模（1-10万行） | 主要サブシステム2-3個 |
| 大規模（10万行~） | 最も変更頻度の高いモジュール群 |

詳細は `${CLAUDE_SKILL_DIR}/../references/scaling_strategy.md` を参照。

---

## リファレンス

- **アイテムテンプレート**: `${CLAUDE_SKILL_DIR}/../references/item_writing_guide.md`
- **CLI フォールバック**: `${CLAUDE_SKILL_DIR}/../references/command_reference.md`
- **Doorstop 詳細**: `${CLAUDE_SKILL_DIR}/../references/doorstop_reference.md`
