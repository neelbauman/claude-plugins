---
name: doorstop-spec-driven:release
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

| # | チェック | 必須 | MCP ツール |
|---|---|---|---|
| 1 | バリデーションエラー 0 件 | はい | `sdd_validate(project_dir)` |
| 2 | 全カバレッジ 100% | はい | `sdd_coverage(project_dir)` |
| 3 | suspect 0 件 | はい | `sdd_impact(project_dir, detect_suspects=True)` |
| 4 | テスト全件パス | はい | プロジェクトのテストランナー |
| 5 | 未レビュー 0 件 | 警告のみ | `sdd_status(project_dir)` |
| 6 | ベースライン作成 | 推奨 | `sdd_baseline_create(project_dir, name, tag=True)` |

## フロー

### 1. 静的検証（Doorstop）

```
sdd_validate(project_dir)
```

ツリー全体のバリデーション。全リンクの完全性チェック。

### 2. カバレッジ確認

```
sdd_coverage(project_dir)
```

グループ別カバレッジが全て 100% であること。

### 3. suspect 確認

```
sdd_impact(project_dir, detect_suspects=True)
```

suspect 0 件であること。

### 4. テスト実行

TST アイテムの `references` が指すテストコードを実行する。

### 5. レビュー状況確認

```
sdd_status(project_dir)
```

未レビューアイテムがある場合は警告を出す。

### 6. ベースライン作成

全必須チェックがパスしたら、ベースラインを作成する。

```
sdd_baseline_create(project_dir, name="v1.0", tag=True)
```

### 7. 報告

結果をユーザーに報告する（パス/失敗の件数と詳細）。

**チェック失敗時**: 失敗した項目とその原因を報告し、修正方法を提案する。リリースゲートを強制通過させない。

---

## リファレンス

- **CLI フォールバック**: `${CLAUDE_SKILL_DIR}/../references/command_reference.md`
- **Doorstop 詳細**: `${CLAUDE_SKILL_DIR}/../references/doorstop_reference.md`
