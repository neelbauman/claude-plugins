---
name: doorstop-spec-driven:report
description: >
  プロジェクトの状況確認・レポート生成を行うフロー。
  「状況を教えて」「カバレッジは？」「suspectある？」「レポートを見せて」
  「ダッシュボードを起動して」のような状況確認リクエストでトリガーする。
argument-hint: "[概要|カバレッジ|suspect一覧|ダッシュボード]"
allowed-tools: Read, Grep, Glob, Bash
context: fork
model: sonnet
---

# レポートフロー

共通ルールは `${CLAUDE_SKILL_DIR}/../_shared/rules.md` を参照。

ユーザーの要望: $ARGUMENTS

---

## 照会系 MCP ツール

| やりたいこと | MCP ツール |
|---|---|
| プロジェクト全体サマリ | `sdd_status(project_dir)` |
| 特定 UID のチェーン | `sdd_chain(project_dir, uid="UID")` |
| ファイルからチェーン逆引き | `sdd_chain(project_dir, file="path")` |
| カバレッジ詳細 | `sdd_coverage(project_dir, group="GROUP")` |
| suspect 一覧 | `sdd_suspects(project_dir)` |
| リンク漏れ検出 | `sdd_gaps(project_dir, document="IMPL")` |
| 優先度付きバックログ | `sdd_backlog(project_dir, group="GROUP")` |
| バリデーション | `sdd_validate(project_dir)` |
| 影響分析 | `sdd_impact(project_dir, detect_suspects=True)` |

## ベースライン管理

| やりたいこと | MCP ツール |
|---|---|
| ベースライン一覧 | `sdd_baseline_list(project_dir)` |
| バージョン間差分 | `sdd_baseline_diff(project_dir, v1="v1", v2="v2")` |

## ダッシュボード（ブラウザ表示）

```bash
uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/reporting/validate_and_report.py <dir> --serve [--port 8080]
```

## 静的 HTML レポート

```bash
uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/reporting/validate_and_report.py <dir> --output-dir ./reports --strict
```

---

ユーザーへの報告は技術用語を避け、件数・カバレッジ・suspect 数を平易に伝える。

## リファレンス

- **CLI フォールバック**: `${CLAUDE_SKILL_DIR}/../references/command_reference.md`
- **Doorstop 詳細**: `${CLAUDE_SKILL_DIR}/../references/doorstop_reference.md`
