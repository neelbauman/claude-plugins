---
name: release
description: >
  リリース前の品質チェック・ゲート判定を行うフロー。
  「リリースしたい」「リリースチェックして」「リリース前の確認」
  「出荷判定」のようなリリースゲートリクエストでトリガーする。
---

# リリースゲートフロー

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
