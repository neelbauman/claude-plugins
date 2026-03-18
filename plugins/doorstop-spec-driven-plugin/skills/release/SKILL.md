---
name: release
description: >
  リリース前の品質チェック・ゲート判定を行うフロー。
  「リリースしたい」「リリースチェックして」「リリース前の確認」
  「出荷判定」のようなリリースゲートリクエストでトリガーする。
argument-hint: "<バージョン名>"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
context: fork
model: sonnet
---

# リリースゲートフロー

共通ルールは `${CLAUDE_SKILL_DIR}/../_shared/rules.md` を参照。

リリースバージョン: $ARGUMENTS

---

## 必須チェック

| # | チェック | 必須 | コマンド |
|---|---|---|---|
| 1 | バリデーションエラー 0 件 | はい | `validate_and_report.py <dir> --strict` |
| 2 | 全カバレッジ 100% | はい | `trace_query.py <dir> coverage` |
| 3 | suspect 0 件 | はい | `impact_analysis.py <dir> --detect-suspects` |
| 4 | テスト全件パス | はい | プロジェクトのテストランナー |
| 5 | 未レビュー 0 件 | 警告のみ | `trace_query.py <dir> status` |
| 6 | ベースライン作成 | 推奨 | `baseline_manager.py <dir> create <version> --tag` |

## フロー

### 1. 静的検証（Doorstop）

```bash
validate_and_report.py <dir> --strict
```

ツリー全体のバリデーション。全リンクの完全性チェック。

### 2. カバレッジ確認

```bash
trace_query.py <dir> coverage
```

グループ別カバレッジが全て 100% であること。

### 3. suspect 確認

```bash
impact_analysis.py <dir> --detect-suspects
```

suspect 0 件であること。

### 4. テスト実行

TST アイテムの `references` が指すテストコードを実行する。

### 5. レビュー状況確認

```bash
trace_query.py <dir> status
```

未レビューアイテムがある場合は警告を出す。

### 6. ベースライン作成

全必須チェックがパスしたら、ベースラインを作成する。

```bash
baseline_manager.py <dir> create <version> --tag
```

### 7. 報告

結果をユーザーに報告する（パス/失敗の件数と詳細）。

---

## コマンドクイックリファレンス

### MCP ツール（推奨）

| 操作 | MCP ツール |
|---|---|
| バリデーション | `sdd_validate(project_dir)` |
| カバレッジ | `sdd_coverage(project_dir)` |
| suspect 検出 | `sdd_impact(project_dir, detect_suspects=True)` |
| ステータス確認 | `sdd_status(project_dir)` |
| ベースライン作成 | `sdd_baseline_create(project_dir, name, tag=True)` |
| ベースライン一覧 | `sdd_baseline_list(project_dir)` |

### CLI フォールバック

```bash
# バリデーション
validate_and_report.py <dir> --strict

# カバレッジ
trace_query.py <dir> coverage

# suspect 検出
impact_analysis.py <dir> --detect-suspects

# ステータス確認
trace_query.py <dir> status

# ベースライン作成
baseline_manager.py <dir> create <version> --tag

# ベースライン一覧
baseline_manager.py <dir> list
```

詳細は `${CLAUDE_PLUGIN_ROOT}/references/doorstop_reference.md` を参照。
