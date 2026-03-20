---
name: bugfix
description: >
  バグの修正を行うフロー。
  「〜が動かない」「エラーが出る」「クラッシュする」「TypeError」「例外が発生」
  「スタックトレース」「不具合がある」「〜がおかしい」「バグを直して」
  のような症状・障害報告でトリガーする。
  「修正して」単体は曖昧なため対象外（change を参照）。
  原因特定→仕様/実装バグ判別→修正→再発防止テスト→検証を自律的に実行する。
argument-hint: "<バグの説明>"
context: fork
hooks:
  Stop:
    - hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/hooks/stop-validate.sh"
---

# バグ修正フロー

共通ルールは `${CLAUDE_SKILL_DIR}/../_shared/rules.md` を参照。

ユーザーの要望: $ARGUMENTS

---

## フロー

### 0. 初動確認

プロジェクト構造を把握する。

```
sdd_tree(project_dir)
```

### 1. 原因特定

バグの再現条件を確認し、関連するコード・設計文書・アイテムを特定する。

```
sdd_chain(project_dir, file="path/to/buggy_file.py")
sdd_find(project_dir, query="関連キーワード")
```

### 2. 仕様バグか実装バグかを判別

| 種別 | 定義 | 対応 |
|---|---|---|
| **仕様バグ** | 設計通りに動作しているが、ユーザーの期待と異なる | → `/doorstop-spec-driven:change` フローへ移行 |
| **実装バグ** | 設計と実装が乖離している | → 以下のステップを続行 |

判別方法：
1. SPEC（または ARCH/HLD/LLD）のアイテムを読み、仕様上の期待動作を確認
2. 実際の動作と仕様を比較
3. 仕様通りなら**仕様バグ**、仕様と異なるなら**実装バグ**

### 3. コード修正

実装バグの場合、SPEC に記述された仕様に合致するようにコードを修正する。

- 仕様に曖昧さがある場合は、修正と併せて SPEC のエッジケースや振る舞いを明確化する
- 修正範囲が広がる場合は `sdd_impact(project_dir, changed_uids=["UID"])` で影響を確認

### 4. 再発防止テスト追加

バグの再現テストを書き、修正後に通ることを確認する。

- テストは「バグが再発した場合に検知できる」ことが目的
- Gherkin がある SPEC の場合、再現シナリオを gherkin 属性に追記することも検討

### 5. IMPL/TST 登録・更新

```
sdd_add_item(project_dir, document="TST", text="再現テスト説明", group="GROUP",
             references=[{"path":"tests/test_xxx.py","type":"file"}], links=["SPEC001"])
sdd_update_item(project_dir, uid="IMPL001", text="更新後のテキスト（バグ修正の経緯を追記）")
```

### 6. 検証

```
sdd_validate(project_dir)
```

**バリデーション失敗時**: エラーメッセージから原因を特定して修正。よくある原因:
- 新規 TST のリンク漏れ → `sdd_link` で補完
- 未レビュー → `sdd_chain_review` で一括レビュー
- SPEC 修正による suspect → 変更確認済みなら `sdd_chain_clear` で解消

### 7. コミット

ドキュメント層ごとにコミットを分ける（規約は `/doorstop-spec-driven:conventions` を参照）。

### 8. 報告

修正内容と再発防止策を報告する。

---

## リファレンス

- **TST テンプレート**: `${CLAUDE_SKILL_DIR}/../references/item_writing_guide.md`
- **CLI フォールバック**: `${CLAUDE_SKILL_DIR}/../references/command_reference.md`
- **Doorstop 詳細**: `${CLAUDE_SKILL_DIR}/../references/doorstop_reference.md`
