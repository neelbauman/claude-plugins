---
name: change
description: >
  既存の仕様・設計・実装に対する意図的な変更を行うフロー。
  「仕様を変えたい」「振る舞いを変えたい」「機能を改善して」「リファクタリングして」
  「〜を変更して」「〜を修正して」「インターフェースを変えたい」
  のような意図的な仕様変更・機能改善リクエストでトリガーする。
  仕様変更を伴わないバグ修正（症状報告）は bugfix を参照。
  影響分析→設計更新→実装・テスト修正→検証の手順で進める。
argument-hint: "<変更内容の説明>"
context: fork
hooks:
  Stop:
    - hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/hooks/stop-validate.sh"
---

# 変更フロー

共通ルールは `${CLAUDE_SKILL_DIR}/../_shared/rules.md` を参照。

ユーザーの要望: $ARGUMENTS

---

## フロー

### 1. 現状把握

変更対象の関連アイテムを特定し、現在のトレーサビリティチェーンを把握する。

```bash
# UID が分かっている場合
trace_query.py <dir> chain <UID>

# ファイルパスから逆引きする場合
trace_query.py <dir> chain --file <path>
```

確認事項：
- 変更対象のアイテムはどの層か（REQ / 設計 / IMPL / TST）
- 上流（なぜ存在するか）と下流（何に影響するか）の範囲

### 2. 影響分析

```bash
# 変更予定のアイテムを指定して影響範囲を分析
impact_analysis.py <dir> --changed <UID>

# 既に変更を加えた場合は suspect 自動検出
impact_analysis.py <dir> --detect-suspects
```

| 影響範囲 | 対応 |
|---|---|
| 下流の IMPL/TST のみ | そのまま続行 |
| 設計文書にも影響 | 上位から順に修正 |
| 他グループにも影響 | ユーザーに報告しスコープ確認 |

### 3. ADR の検討

設計判断が変わる場合は既存 ADR を `superseded` に更新し、新 ADR を作成する。
詳細は `${CLAUDE_PLUGIN_ROOT}/references/concepts/adr.md` を参照。

### 4. 設計更新

上位から順に修正する。設計文書の変更は下流の suspect を発生させるため、最初に設計を確定させてから実装・テストに進む。

- **lite**: SPEC を修正
- **standard**: ARCH → SPEC の順に修正
- **full**: HLD → LLD の順に修正

```bash
doorstop_ops.py <dir> update SPEC001 -t "更新後の仕様テキスト"
doorstop_ops.py <dir> update SPEC001 --gherkin "更新後の Gherkin シナリオ"
```

### 5. 実装・テスト修正

最終的に整合性が取れていれば、仕様・テスト・実装の編集順序は問わない。

- IMPL の `references` 先（ソースコード）を修正
- TST の `references` 先（テストコード）を修正
- 新たなエッジケースがあればテスト追加

### 6. IMPL/TST 更新・suspect 解消

```bash
doorstop_ops.py <dir> update IMPL001 -t "更新後の実装説明"
doorstop_ops.py <dir> update TST001 -t "更新後のテスト説明"

# チェーン全体を一括レビュー + suspect 解消
doorstop_ops.py <dir> chain-review <UID>
doorstop_ops.py <dir> chain-clear <UID>
```

### 7. 用語辞書の確認

変更によりドメイン用語の意味が変わった場合、REQ 先頭の用語定義アイテムを更新する。
詳細は `${CLAUDE_PLUGIN_ROOT}/references/concepts/glossary.md` を参照。

### 8. 検証

```bash
validate_and_report.py <dir> --strict
impact_analysis.py <dir> --detect-suspects
```

エラー 0 件、suspect 0 件を確認する。

### 9. コミット

ドキュメント層ごとにコミットを分ける。順序はプロジェクトの慣習に従う。

```bash
git add docs/specs/SPEC001.yml
git commit -m "spec: update SPEC001 [change description]"

git add src/module.py docs/impl/IMPL001.yml
git commit -m "impl: update IMPL001 follow SPEC001 change"

git add tests/test_module.py docs/tst/TST001.yml
git commit -m "test: update TST001 follow SPEC001 change"

git add docs/impl/IMPL001.yml docs/tst/TST001.yml
git commit -m "spec: clear suspects IMPL001 TST001"
```

### 10. 報告

影響範囲と修正結果を報告。suspect 0 件を確認する。

---

## コマンドクイックリファレンス

### MCP ツール（推奨）

| 操作 | MCP ツール |
|---|---|
| アイテム更新 | `sdd_update_item(project_dir, uid, text, gherkin)` |
| 影響分析 | `sdd_impact(project_dir, changed_uids=[UID])` |
| suspect 自動検出 | `sdd_impact(project_dir, detect_suspects=True)` |
| チェーン確認 | `sdd_chain(project_dir, uid=UID)` / `sdd_chain(project_dir, file=PATH)` |
| 一括レビュー | `sdd_chain_review(project_dir, uids)` |
| suspect 一括解消 | `sdd_chain_clear(project_dir, uids)` |
| 検証 | `sdd_validate(project_dir)` |

### CLI フォールバック

```bash
# アイテム更新
doorstop_ops.py <dir> update <UID> -t "テキスト" [--gherkin "..."]

# 影響分析
impact_analysis.py <dir> --changed <UID>
impact_analysis.py <dir> --detect-suspects

# チェーン確認
trace_query.py <dir> chain <UID>
trace_query.py <dir> chain --file <path>

# チェーン一括レビュー・suspect 解消
doorstop_ops.py <dir> chain-review <UID>
doorstop_ops.py <dir> chain-clear <UID>

# 検証
validate_and_report.py <dir> --strict
```

詳細は `${CLAUDE_PLUGIN_ROOT}/references/doorstop_reference.md` を参照。

---

## 報告テンプレート

```
[GROUP] SPEC001 の仕様を変更しました。
  - 変更内容: ...
  - 影響範囲: IMPL001, TST001（修正済み）
  - テスト: 全件パス
  - トレーサビリティ: suspect 0件、カバレッジ 100%
```
