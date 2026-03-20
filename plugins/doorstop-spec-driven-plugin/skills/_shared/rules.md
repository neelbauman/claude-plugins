# 共通ルール

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
13. **Doorstop YAML を Edit/Write で直接編集しない** — 必ず MCP ツール (`sdd_add_item`, `sdd_update_item` 等) または CLI (`doorstop_ops.py`) 経由で操作する。フックにより直接編集はブロックされる

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

**MCP ツール（推奨）**: `sdd_*` ツールを直接呼び出す（MCP サーバー `sdd` 経由）。

**CLI フォールバック**: `uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/<script>.py <project-dir> ...`

### MCP ツール一覧

| カテゴリ | MCP ツール | 概要 |
|---|---|---|
| **CRUD** | `sdd_add_item` | アイテム追加 |
| | `sdd_update_item` | アイテム更新 |
| | `sdd_link` / `sdd_unlink` | リンク管理 |
| | `sdd_reorder` | レベル変更 |
| **レビュー** | `sdd_clear` / `sdd_review` | suspect解消・レビュー |
| | `sdd_chain_review` / `sdd_chain_clear` | チェーン一括 |
| **活性化** | `sdd_activate` / `sdd_deactivate` | 単体 |
| | `sdd_activate_chain` / `sdd_deactivate_chain` | チェーン |
| **照会** | `sdd_status` | プロジェクトサマリ |
| | `sdd_chain` | チェーン表示・ファイル逆引き |
| | `sdd_context` | 全文脈一括取得 |
| | `sdd_search` | 属性フィルタ付き検索 |
| | `sdd_coverage` / `sdd_suspects` / `sdd_gaps` | 品質メトリクス |
| | `sdd_backlog` | 優先度順バックログ |
| | `sdd_list` / `sdd_groups` / `sdd_find` / `sdd_tree` | 一覧・検索 |
| **検証** | `sdd_validate` | バリデーション |
| **影響分析** | `sdd_impact` | 変更影響分析 |
| **ベースライン** | `sdd_baseline_create` / `sdd_baseline_list` / `sdd_baseline_diff` | スナップショット管理 |
| **用語辞書** | `sdd_glossary_add` / `sdd_glossary_list` / `sdd_glossary_check` 等 | 用語管理 |
| **初期化** | `sdd_init` | プロジェクト初期化 |
