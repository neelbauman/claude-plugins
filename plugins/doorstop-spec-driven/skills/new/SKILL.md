---
name: doorstop-spec-driven:new
description: >
  新機能の追加・新要件の実装を行う仕様駆動開発フロー。
  「〜を作って」「〜を実装して」「新機能を追加して」「〜が欲しい」
  のような新規開発リクエストでトリガーする。
  REQ登録→設計策定→実装→テスト→トレーサビリティ検証の全サイクルを自律的に実行する。
argument-hint: "<要望の説明>"
context: fork
hooks:
  Stop:
    - hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/hooks/stop-validate.sh"
---

# 新規開発フロー

共通ルールは `${CLAUDE_SKILL_DIR}/../_shared/rules.md` を参照。

ユーザーの要望: $ARGUMENTS

---

## フロー

### 0. 初動確認

プロジェクト構造とプロファイルを把握する。

```
sdd_tree(project_dir)
```

既存グループ・プロファイル・ドキュメント階層を確認してからフローに入る。

### 1. 理解

ユーザーの要望を要件文に変換する。曖昧な場合のみ確認。

### 2. 分類

機能グループと優先度を決定（既存グループ or 新規、`priority` を設定）。FR（機能要件）か NFR（非機能要件）かを判別する（判断基準は `${CLAUDE_SKILL_DIR}/../references/concepts/nfr.md`）。

### 3. 用語確認

新しいドメイン概念が登場する場合:

```
sdd_glossary_add(project_dir, term, definition)
```

詳細は `${CLAUDE_SKILL_DIR}/../references/concepts/glossary.md` を参照。

### 4. REQ 登録

```
sdd_add_item(project_dir, document="REQ", text="要件文", group="GROUP", priority="high")
```

### 5. 設計策定

設計文書を上位から順に作成し、親へリンク。派生要求は `derived: true`。NFR 制約がある場合は設計文書から NFR アイテムへもリンクする。振る舞いの定義が必要な文書には **gherkin** に Given/When/Then 形式でシナリオを記述する。

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

```
sdd_add_item(project_dir, document="SPEC", text="仕様", group="GROUP",
             links=["REQ001"], gherkin="Scenario: ...")
```

### 6. 実装・テスト

最下位設計文書に従ってコードとテストを書く（編集の順序は問わない）。gherkin のシナリオを TST のテストケースに変換する。

### 7. IMPL/TST 登録

```
sdd_add_item(project_dir, document="IMPL", text="実装説明", group="GROUP",
             references=[{"path":"src/module.py","type":"file"}], links=["SPEC001"])
sdd_add_item(project_dir, document="TST", text="テスト説明", group="GROUP",
             references=[{"path":"tests/test_module.py","type":"file"}], links=["SPEC001"])
```

### 8. レビュー

```
sdd_chain_review(project_dir, uids=["REQ001"])
```

### 9. 検証

```
sdd_validate(project_dir)
sdd_impact(project_dir, detect_suspects=True)
```

エラー 0 件・suspect 0 件を確認する。

**バリデーション失敗時**: エラーメッセージを読み、原因（リンク漏れ・未レビュー・suspect 等）を特定して修正。修正後に再度検証を実行する。よくある原因:
- リンク漏れ → `sdd_link` で補完
- suspect → `sdd_chain_clear` で解消（変更を確認済みの場合）
- 未レビュー → `sdd_chain_review` で一括レビュー

### 10. コミット

ドキュメント層ごとにコミットを分ける（規約は `/doorstop-spec-driven:conventions` を参照）。

### 11. 報告

成果物ベースで簡潔に報告。

> **ADR**: どの段階でも重要な意思決定があれば ADR を作成する。
> 詳細は `${CLAUDE_SKILL_DIR}/../references/concepts/adr.md` を参照。

---

## リファレンス

- **アイテムテンプレート**: `${CLAUDE_SKILL_DIR}/../references/item_writing_guide.md`
- **CLI フォールバック**: `${CLAUDE_SKILL_DIR}/../references/command_reference.md`
- **Doorstop 詳細**: `${CLAUDE_SKILL_DIR}/../references/doorstop_reference.md`
