---
name: deactivate
description: >
  機能削除・要件取り下げを行うフロー。
  「〜を削除して」「〜を廃止して」「この機能はもう要らない」
  「要件を取り下げたい」のような非活性化リクエストでトリガーする。
  物理削除ではなく active: false によるソフトデリートと連鎖処理を行う。
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
argument-hint: "<対象UID または機能名>"
---

# 非活性化フロー

共通ルールは `${CLAUDE_SKILL_DIR}/../_shared/rules.md` を参照。

対象: $ARGUMENTS

---

## フロー

### 1. 影響確認

```bash
trace_query.py <dir> chain <UID>
```

下流アイテムを確認する。

### 2. ユーザー確認

非活性化対象と影響範囲をユーザーに提示し、合意を得る。

### 3. チェーン非活性化

```bash
doorstop_ops.py <dir> deactivate-chain <UID>
```

- 下流アイテムのうち、他に活性な親を持たないものも連鎖的に非活性化される
- 他に活性な親があっても強制する場合は `--force`

### 4. 検証

```bash
validate_and_report.py <dir> --strict
```

### 5. 報告

非活性化されたアイテム数と影響範囲を報告する。

## 再活性化

取り下げた要件を復活させる場合:

```bash
doorstop_ops.py <dir> activate-chain <UID>
```

## 注意事項

- 物理削除（YAML ファイルの削除）は行わない。`active: false` で管理する
- 非活性化アイテムはカバレッジ計算やバリデーションから除外される
- `baseline_manager.py diff` で非活性化の記録を追跡できる

---

## コマンドクイックリファレンス

### MCP ツール（推奨）

| 操作 | MCP ツール |
|---|---|
| チェーン確認 | `sdd_chain(project_dir, uid)` |
| チェーン非活性化 | `sdd_deactivate_chain(project_dir, uid, force)` |
| チェーン活性化 | `sdd_activate_chain(project_dir, uid)` |
| 検証 | `sdd_validate(project_dir)` |

### CLI フォールバック

```bash
# チェーン確認
trace_query.py <dir> chain <UID>

# チェーン非活性化
doorstop_ops.py <dir> deactivate-chain <UID> [--force]

# チェーン活性化（復活）
doorstop_ops.py <dir> activate-chain <UID>

# 検証
validate_and_report.py <dir> --strict
```

詳細は `${CLAUDE_PLUGIN_ROOT}/references/doorstop_reference.md` を参照。
