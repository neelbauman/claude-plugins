---
name: report
description: >
  プロジェクトの状況確認・レポート生成を行うフロー。
  「状況を教えて」「カバレッジは？」「suspectある？」「レポートを見せて」
  「ダッシュボードを起動して」のような状況確認リクエストでトリガーする。
argument-hint: "[status|coverage|suspects|dashboard]"
allowed-tools: Read, Grep, Glob, Bash
context: fork
model: sonnet
---

# レポートフロー

共通ルールは `${CLAUDE_SKILL_DIR}/../_shared/rules.md` を参照。

ユーザーの要望: $ARGUMENTS

---

## コマンド一覧

### 照会系（trace_query.py）

| やりたいこと | コマンド |
|---|---|
| プロジェクト全体サマリ | `trace_query.py <dir> status` |
| 特定 UID のチェーン | `trace_query.py <dir> chain <UID>` |
| ファイルからチェーン逆引き | `trace_query.py <dir> chain --file <path>` |
| カバレッジ詳細 | `trace_query.py <dir> coverage [--group GROUP]` |
| suspect 一覧 | `trace_query.py <dir> suspects` |
| リンク漏れ検出 | `trace_query.py <dir> gaps [--document IMPL]` |
| 優先度付きバックログ | `trace_query.py <dir> backlog [--group GROUP]` |

### CRUD 操作（doorstop_ops.py）

| やりたいこと | コマンド |
|---|---|
| アイテム追加 | `doorstop_ops.py <dir> add -d <DOC> -t "テキスト" ...` |
| アイテム更新 | `doorstop_ops.py <dir> update <UID> -t "テキスト"` |
| リンク / リンク解除 | `doorstop_ops.py <dir> link / unlink` |
| クリア / レビュー | `doorstop_ops.py <dir> clear / review` |
| チェーン一括 | `doorstop_ops.py <dir> chain-review / chain-clear` |
| 非活性化（単体） | `doorstop_ops.py <dir> deactivate <UID> [<UID2> ...]` |
| 非活性化（チェーン） | `doorstop_ops.py <dir> deactivate-chain <UID> [--force]` |
| 活性化（チェーン） | `doorstop_ops.py <dir> activate-chain <UID>` |

### 検証・レポート

| やりたいこと | コマンド |
|---|---|
| 静的 HTML レポート | `validate_and_report.py <dir> --output-dir ./reports --strict` |
| ダッシュボード | `validate_and_report.py <dir> --serve [--port 8080]` |
| 影響分析 | `impact_analysis.py <dir> --detect-suspects [--json PATH]` |

### ベースライン管理

| やりたいこと | コマンド |
|---|---|
| ベースライン作成 | `baseline_manager.py <dir> create <name> [--tag]` |
| ベースライン一覧 | `baseline_manager.py <dir> list` |
| バージョン間差分 | `baseline_manager.py <dir> diff <v1> <v2>` |
| 現在との差分 | `baseline_manager.py <dir> diff <v1> HEAD` |

---

ユーザーへの報告は技術用語を避け、件数・カバレッジ・suspect 数を平易に伝える。

詳細は `${CLAUDE_PLUGIN_ROOT}/references/doorstop_reference.md` を参照。
