---
name: doorstop-spec-driven:deactivate
description: >
  機能削除・要件取り下げを行うフロー。
  「〜を削除して」「〜を廃止して」「この機能はもう要らない」
  「要件を取り下げたい」のような非活性化リクエストでトリガーする。
  物理削除ではなく active: false によるソフトデリートと連鎖処理を行う。
disable-model-invocation: true
argument-hint: "<対象UID または機能名>"
---

# 非活性化フロー

共通ルールは `${CLAUDE_SKILL_DIR}/../_shared/rules.md` を参照。

対象: $ARGUMENTS

---

## フロー

### 0. 初動確認

```
sdd_tree(project_dir)
```

### 1. 影響確認

```
sdd_chain(project_dir, uid="UID")
```

下流アイテムを確認する。

### 2. ユーザー確認

非活性化対象と影響範囲をユーザーに提示し、合意を得る。

### 3. チェーン非活性化

```
sdd_deactivate_chain(project_dir, uid="UID")
```

- 下流アイテムのうち、他に活性な親を持たないものも連鎖的に非活性化される
- 他に活性な親があっても強制する場合は `force=True`

### 4. 検証

```
sdd_validate(project_dir)
```

**バリデーション失敗時**: 非活性化により孤立したリンクがないか確認。必要に応じて `sdd_unlink` でリンクを解除する。

### 5. 報告

非活性化されたアイテム数と影響範囲を報告する。

## 再活性化

取り下げた要件を復活させる場合:

```
sdd_activate_chain(project_dir, uid="UID")
```

## 注意事項

- 物理削除（YAML ファイルの削除）は行わない。`active: false` で管理する
- 非活性化アイテムはカバレッジ計算やバリデーションから除外される
- `sdd_baseline_diff` で非活性化の記録を追跡できる

---

## リファレンス

- **CLI フォールバック**: `${CLAUDE_SKILL_DIR}/../references/command_reference.md`
- **Doorstop 詳細**: `${CLAUDE_SKILL_DIR}/../references/doorstop_reference.md`
