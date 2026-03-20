---
name: change
description: >
  既存の仕様・設計・実装に対する意図的な変更を行うフロー。
  「仕様を変えたい」「振る舞いを変えたい」「機能を改善して」「リファクタリングして」
  「〜を変更して」「〜を修正して」「インターフェースを変えたい」
  のような意図的な仕様変更・機能改善リクエストでトリガーする。
  仕様変更を伴わないバグ修正（症状報告）は bugfix を参照。
  影響分析→設計更新→実装・テスト修正→検証の手順で進める。
argument-hint: "<変更内容の説明>"
context: fork
hooks:
  Stop:
    - hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/hooks/stop-validate.sh"
---

# 変更フロー

共通ルールは `${CLAUDE_SKILL_DIR}/../_shared/rules.md` を参照。

ユーザーの要望: $ARGUMENTS

---

## フロー

### 0. 初動確認

プロジェクト構造を把握する。

```
sdd_tree(project_dir)
```

### 1. 現状把握

変更対象の関連アイテムを特定し、現在のトレーサビリティチェーンを把握する。

```
sdd_chain(project_dir, uid="UID")
sdd_chain(project_dir, file="path/to/file.py")
```

確認事項：
- 変更対象のアイテムはどの層か（REQ / 設計 / IMPL / TST）
- 上流（なぜ存在するか）と下流（何に影響するか）の範囲

### 2. 影響分析

```
sdd_impact(project_dir, changed_uids=["UID"])
```

| 影響範囲 | 対応 |
|---|---|
| 下流の IMPL/TST のみ | そのまま続行 |
| 設計文書にも影響 | 上位から順に修正 |
| 他グループにも影響 | ユーザーに報告しスコープ確認 |

### 3. ADR の検討

設計判断が変わる場合は既存 ADR を `superseded` に更新し、新 ADR を作成する。
詳細は `${CLAUDE_SKILL_DIR}/../references/concepts/adr.md` を参照。

### 4. 設計更新

上位から順に修正する。設計文書の変更は下流の suspect を発生させるため、最初に設計を確定させてから実装・テストに進む。

- **lite**: SPEC を修正
- **standard**: ARCH → SPEC の順に修正
- **full**: HLD → LLD の順に修正

```
sdd_update_item(project_dir, uid="SPEC001", text="更新後の仕様", gherkin="更新後のシナリオ")
```

### 5. 実装・テスト修正

最終的に整合性が取れていれば、仕様・テスト・実装の編集順序は問わない。

- IMPL の `references` 先（ソースコード）を修正
- TST の `references` 先（テストコード）を修正
- 新たなエッジケースがあればテスト追加

### 6. IMPL/TST 更新・suspect 解消

```
sdd_update_item(project_dir, uid="IMPL001", text="更新後の実装説明")
sdd_update_item(project_dir, uid="TST001", text="更新後のテスト説明")
sdd_chain_review(project_dir, uids=["REQ001"])
sdd_chain_clear(project_dir, uids=["REQ001"])
```

### 7. 用語辞書の確認

変更によりドメイン用語の意味が変わった場合、用語辞書を更新する。
詳細は `${CLAUDE_SKILL_DIR}/../references/concepts/glossary.md` を参照。

### 8. 検証

```
sdd_validate(project_dir)
sdd_impact(project_dir, detect_suspects=True)
```

エラー 0 件、suspect 0 件を確認する。

**バリデーション失敗時**: エラーメッセージから原因を特定して修正。よくある原因:
- suspect 残存 → 変更を確認済みなら `sdd_chain_clear` で解消
- リンク漏れ → `sdd_link` で補完
- 新規アイテムの未レビュー → `sdd_chain_review` で一括レビュー

### 9. コミット

ドキュメント層ごとにコミットを分ける（規約は `/doorstop-spec-driven:conventions` を参照）。

### 10. 報告

影響範囲と修正結果を報告。suspect 0 件を確認する。

---

## リファレンス

- **アイテムテンプレート**: `${CLAUDE_SKILL_DIR}/../references/item_writing_guide.md`
- **CLI フォールバック**: `${CLAUDE_SKILL_DIR}/../references/command_reference.md`
- **Doorstop 詳細**: `${CLAUDE_SKILL_DIR}/../references/doorstop_reference.md`
