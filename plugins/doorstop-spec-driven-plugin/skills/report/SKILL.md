---
name: report
description: >
  プロジェクトの状況確認・レポート生成を行うフロー。
  「状況を教えて」「カバレッジは？」「suspectある？」「レポートを見せて」
  「ダッシュボードを起動して」のような状況確認リクエストでトリガーする。
---

# レポートフロー

## 鉄則

1. コードを書く前に設計文書を書く（adopt フローのみ例外）
2. 振る舞い定義には `gherkin` 属性で Given/When/Then を書く
3. テストを書いたら TST を書く（常にペア）
4. 変更したら `impact_analysis.py` を回す
5. 最後に `validate_and_report.py --strict` を必ず実行する
6. 仕様変更時は `--serve` でダッシュボードを起動しレビューを促す
7. 関連アイテムの探索には `trace_query.py` を使う（YAML を grep しない）
8. 派生要求（`derived: true`）は設計層のみ。IMPL/TST では禁止
9. 外部ファイル紐付けには `references` を使う（`ref` は非推奨）
10. 仕様変更のコミットはドキュメント層ごとに分ける
11. 新ドメイン概念には `glossary.py add` で用語辞書を更新する
12. 重要な設計判断は ADR に記録する

## エージェント規約

- 非規範的アイテム（見出し・背景）は `--non-normative` で作成
- 報告は成果物ベースで簡潔に（Doorstop 内部構造は見せない）
- 初動で `doorstop_ops.py <dir> tree` を実行し、ツリー構造を動的に把握する
- 最下位設計文書 = IMPL/TST がリンクする直接の親（lite: SPEC, standard: SPEC, full: LLD）

## プロファイル

| プロファイル | 階層 |
|---|---|
| lite | REQ → SPEC → IMPL/TST · ADR |
| standard | REQ/NFR → ARCH → SPEC → IMPL/TST · ADR |
| full | REQ/NFR → HLD → LLD → IMPL/TST · ADR |

## スクリプト実行形式

`uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/<script>.py <project-dir> ...`

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
