---
name: doorstop-spec-driven:triage
description: >
  要件の優先度付け・バックログ整理・スコープ確定を行うフロー。
  「何から手をつけるか」「優先順位を決めたい」「バックログを整理して」
  「スコープを確定したい」「次に何を実装すべきか」
  のようなトリアージリクエストでトリガーする。
argument-hint: "[グループ名 or 省略で全体]"
model: sonnet
---

# トリアージフロー

共通ルールは `${CLAUDE_SKILL_DIR}/../_shared/rules.md` を参照。

ユーザーの要望: $ARGUMENTS

---

## フロー

### 0. 初動確認

```
sdd_tree(project_dir)
```

### 1. バックログ確認

```
sdd_backlog(project_dir)
sdd_backlog(project_dir, group="GROUP")
```

REQ を優先度順に一覧表示する。NFR のバックログも確認する場合は `document="NFR"` を指定。

### 2. 優先度設定

```
sdd_update_item(project_dir, uid="REQ001", priority="high")
```

### 3. 未着手の特定

カバレッジ 0 の REQ（設計・実装が未作成）を特定する。

```
sdd_coverage(project_dir)
sdd_coverage(project_dir, group="GROUP")
```

### 4. ユーザーへの提示

未着手 REQ を優先度順に提示し、次に着手するものを確認する。

### 5. ベースライン確認

```
sdd_baseline_list(project_dir)
```

### 6. スコープ合意後

```
sdd_baseline_create(project_dir, name="v1.0-scope")
```

## 優先度の値

| 値 | 意味 | 典型的な使用場面 |
|---|---|---|
| `critical` | 今すぐ必要。これがないとリリースできない | セキュリティ、コアとなる機能 |
| `high` | 今回のリリースに含めたい | 主要機能、ユーザーが期待する機能 |
| `medium` | できれば今回、次回でも可（デフォルト） | 拡張機能、利便性向上 |
| `low` | 将来対応。今回はスコープ外 | Nice-to-have、実験的機能 |

## 完了基準

全アクティブ REQ/NFR に priority が設定され、今回の対象スコープが合意されていること。

---

## リファレンス

- **CLI フォールバック**: `${CLAUDE_SKILL_DIR}/../references/command_reference.md`
- **Doorstop 詳細**: `${CLAUDE_SKILL_DIR}/../references/doorstop_reference.md`
