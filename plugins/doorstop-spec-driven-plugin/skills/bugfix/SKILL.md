---
name: bugfix
description: >
  バグの修正を行うフロー。
  「バグを直して」「〜が動かない」「エラーが出る」「不具合がある」
  「〜がおかしい」のようなバグ修正リクエストでトリガーする。
  原因特定→仕様/実装バグ判別→修正→再発防止テスト→検証を自律的に実行する。
argument-hint: "<バグの説明>"
context: fork
hooks:
  Stop:
    - hooks:
        - type: prompt
          prompt: "validate_and_report.py --strict を実行してエラー0件を確認しましたか？"
          model: haiku
---

# バグ修正フロー

共通ルールは `${CLAUDE_SKILL_DIR}/../_shared/rules.md` を参照。

ユーザーの要望: $ARGUMENTS

---

## フロー

### 1. 原因特定

バグの再現条件を確認し、関連するコード・設計文書・アイテムを特定する。

```bash
# ファイルパスから関連アイテムを逆引き
trace_query.py <dir> chain --file <buggy-file-path>

# テキスト検索で関連アイテムを探す
doorstop_ops.py <dir> find "関連キーワード"
```

### 2. 仕様バグか実装バグかを判別

| 種別 | 定義 | 対応 |
|---|---|---|
| **仕様バグ** | 設計通りに動作しているが、ユーザーの期待と異なる | → `/doorstop-spec-driven:change` フローへ移行 |
| **実装バグ** | 設計と実装が乖離している | → 以下のステップを続行 |

判別方法：
1. SPEC（または ARCH/HLD/LLD）のアイテムを読み、仕様上の期待動作を確認
2. 実際の動作と仕様を比較
3. 仕様通りなら**仕様バグ**、仕様と異なるなら**実装バグ**

### 3. コード修正

実装バグの場合、SPEC に記述された仕様に合致するようにコードを修正する。

- 仕様に曖昧さがある場合は、修正と併せて SPEC のエッジケースや振る舞いを明確化する
- 修正範囲が広がる場合は `impact_analysis.py --changed <UID>` で影響を確認

### 4. 再発防止テスト追加

バグの再現テストを書き、修正後に通ることを確認する。

- テストは「バグが再発した場合に検知できる」ことが目的
- Gherkin がある SPEC の場合、再現シナリオを gherkin 属性に追記することも検討

### 5. IMPL 更新

必要に応じて IMPL アイテムの text を更新する。バグ修正の経緯や設計判断を記録。

```bash
doorstop_ops.py <dir> update IMPL001 -t "更新後のテキスト（バグ修正の経緯を追記）"
```

### 6. 検証

```bash
# テスト実行
uv run pytest tests/ -x -q

# トレーサビリティ検証
validate_and_report.py <dir> --strict
```

### 7. コミット

ドキュメント層ごとにコミットを分ける。順序はプロジェクトの慣習に従う。

```bash
# テスト + TST アイテム
git add tests/test_xxx.py docs/tst/TST0XX.yml
git commit -m "test: TST0XX regression test for [bug summary]"

# バグ修正 + IMPL アイテム更新
git add src/module.py docs/impl/IMPL001.yml
git commit -m "fix: IMPL001 [bug summary]"

# SPEC 明確化がある場合
git add docs/specs/SPEC001.yml
git commit -m "spec: clarify SPEC001 edge case for [bug]"
```

### 8. 報告

修正内容と再発防止策を報告する。

---

## コマンドクイックリファレンス

```bash
# チェーン逆引き（ファイルから）
trace_query.py <dir> chain --file <path>

# テキスト検索
doorstop_ops.py <dir> find "キーワード"

# TST 追加
doorstop_ops.py <dir> add -d TST -t "テスト説明" -g GROUP \
  --references '[{"path":"tests/test_xxx.py","type":"file"}]' --links SPEC001

# アイテム更新
doorstop_ops.py <dir> update <UID> -t "テキスト"

# 影響分析
impact_analysis.py <dir> --changed <UID>

# 検証
validate_and_report.py <dir> --strict
```

詳細は `${CLAUDE_PLUGIN_ROOT}/references/doorstop_reference.md` を参照。

---

## TST テンプレート（簡易版）

```bash
doorstop_ops.py <dir> add -d TST \
  -t "## 目的
バグ再現テスト: [バグの概要]

## 検証観点
- TC-1: [再現手順と期待結果]" \
  -g GROUP \
  --references '[{"path":"tests/test_xxx.py","type":"file"}]' --links SPEC001
```

詳細なテンプレートは `${CLAUDE_PLUGIN_ROOT}/references/item_writing_guide.md` を参照。

---

## 報告テンプレート

```
[GROUP] バグを修正しました。
  - 原因: [仕様バグ/実装バグ] — [原因の説明]
  - 修正: src/xxx.py — [修正内容]
  - 再発防止: tests/test_xxx.py — テスト追加
  - トレーサビリティ: 全リンク済み、suspect 0件
```
