# CLI フォールバックリファレンス

MCP ツールが利用できない場合の CLI コマンド一覧。
全コマンドは `uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/<script>.py <project-dir> ...` 形式で実行する。

---

## doorstop_ops.py — CRUD 操作

### アイテム追加

```bash
doorstop_ops.py <dir> add -d <DOC> -t "テキスト" -g GROUP \
  [--priority P] [--links UID...] [--header "見出し"] \
  [--gherkin "Scenario: ..."] [--non-normative] \
  [--references '[{"path":"src/x.py","type":"file"}]']
```

### アイテム更新

```bash
doorstop_ops.py <dir> update <UID> \
  [-t "テキスト"] [--gherkin "..."] [--priority P] [--status S] \
  [--references '[...]']
```

### リンク管理

```bash
doorstop_ops.py <dir> link <child-UID> <parent-UID>
doorstop_ops.py <dir> unlink <child-UID> <parent-UID>
```

### レビュー・クリア

```bash
doorstop_ops.py <dir> review <UID> [<UID2> ...]
doorstop_ops.py <dir> clear <UID> [<UID2> ...]
doorstop_ops.py <dir> chain-review <UID>
doorstop_ops.py <dir> chain-clear <UID>
```

### 活性化・非活性化

```bash
doorstop_ops.py <dir> activate <UID> [<UID2> ...]
doorstop_ops.py <dir> deactivate <UID> [<UID2> ...]
doorstop_ops.py <dir> activate-chain <UID>
doorstop_ops.py <dir> deactivate-chain <UID> [--force]
```

### レベル変更

```bash
doorstop_ops.py <dir> reorder <UID> --level <N.N>
```

### 照会

```bash
doorstop_ops.py <dir> tree
doorstop_ops.py <dir> find "キーワード"
```

---

## trace_query.py — トレーサビリティ照会

```bash
trace_query.py <dir> status
trace_query.py <dir> chain <UID>
trace_query.py <dir> chain --file <path>
trace_query.py <dir> coverage [--group GROUP]
trace_query.py <dir> suspects
trace_query.py <dir> gaps [--document IMPL]
trace_query.py <dir> backlog [--group GROUP] [-d NFR]
```

---

## impact_analysis.py — 影響分析

```bash
impact_analysis.py <dir> --changed <UID>
impact_analysis.py <dir> --detect-suspects [--json PATH]
```

---

## validate_and_report.py — 検証・レポート

```bash
validate_and_report.py <dir> --strict
validate_and_report.py <dir> --output-dir ./reports --strict
validate_and_report.py <dir> --serve [--port 8080]
```

---

## baseline_manager.py — ベースライン管理

```bash
baseline_manager.py <dir> create <name> [--tag]
baseline_manager.py <dir> list
baseline_manager.py <dir> diff <v1> <v2>
baseline_manager.py <dir> diff <v1> HEAD
```

---

## glossary.py — 用語辞書

```bash
glossary.py <dir> add "用語" "定義"
glossary.py <dir> list
glossary.py <dir> check
glossary.py <dir> sync
```

---

## init_project.py — プロジェクト初期化

```bash
init_project.py <dir> --profile <lite|standard|full> [--with-nfr] [--no-git-init]
```
