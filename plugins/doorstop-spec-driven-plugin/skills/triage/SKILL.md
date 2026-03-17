---
name: triage
description: >
  要件の優先度付け・バックログ整理・スコープ確定を行うフロー。
  「何から手をつけるか」「優先順位を決めたい」「バックログを整理して」
  「スコープを確定したい」「次に何を実装すべきか」
  のようなトリアージリクエストでトリガーする。
argument-hint: "[グループ名]"
allowed-tools: Read, Grep, Glob, Bash
model: sonnet
---

# トリアージフロー

共通ルールは `${CLAUDE_SKILL_DIR}/../_shared/rules.md` を参照。

ユーザーの要望: $ARGUMENTS

---

## フロー

### 1. バックログ確認

```bash
trace_query.py <dir> backlog
trace_query.py <dir> backlog --group <GROUP>

# NFR（非機能要件）のバックログも確認
trace_query.py <dir> backlog -d NFR
```

REQ を優先度順に一覧表示する。

### 2. 優先度設定

```bash
doorstop_ops.py <dir> update REQ001 --priority high
```

### 3. 未着手の特定

カバレッジ 0 の REQ（設計・実装が未作成）を特定する。

```bash
trace_query.py <dir> coverage
trace_query.py <dir> coverage --group <GROUP>
```

### 4. ユーザーへの提示

未着手 REQ を優先度順に提示し、次に着手するものを確認する。

### 5. ベースライン確認

```bash
baseline_manager.py <dir> list
```

### 6. スコープ合意後

```bash
baseline_manager.py <dir> create <name>
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

## コマンドクイックリファレンス

```bash
# バックログ確認
trace_query.py <dir> backlog [--group GROUP] [-d NFR]

# 優先度更新
doorstop_ops.py <dir> update <UID> --priority <critical|high|medium|low>

# カバレッジ確認
trace_query.py <dir> coverage [--group GROUP]

# REQ 追加（優先度付き）
doorstop_ops.py <dir> add -d REQ -t "要件文" -g GROUP --priority high

# ベースライン
baseline_manager.py <dir> list
baseline_manager.py <dir> create <name>
```

詳細は `${CLAUDE_PLUGIN_ROOT}/references/doorstop_reference.md` を参照。
