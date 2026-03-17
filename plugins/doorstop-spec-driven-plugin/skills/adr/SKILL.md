---
name: adr
description: >
  設計判断・意思決定をADR（Architecture Decision Record）に記録するフロー。
  「ADRを書いて」「判断を記録して」「なぜこうしたか残したい」
  「設計方針を記録して」のような意思決定記録リクエストでトリガーする。
  ユーザーとの議論で方針が確定したときにも自動的にトリガーする。
argument-hint: "<判断の概要>"
allowed-tools: Read, Grep, Glob, Bash
---

# 意思決定記録フロー

共通ルールは `${CLAUDE_SKILL_DIR}/../_shared/rules.md` を参照。

ユーザーの要望: $ARGUMENTS

---

## トリガーシグナル

以下の場合にこのフローを使う:
- ユーザーとの議論で設計方針が決まった（「この方向で行こう」「こうしよう」等）
- 複数の代替案を比較検討し、1つを採用した
- 既存の設計判断を覆す変更を行った
- 「なぜこうしたのか」を将来のために残すべきと判断した
- ユーザーが明示的に ADR の作成を依頼した

ADR を書かなくてよいケース:
- 自明な実装判断（標準ライブラリの使用、命名規約の適用等）
- 一時的な回避策（IMPL の TODO に記録する）
- コードを読めば理由が明らかな変更

## フロー

### 1. 議論の要約

会話の中から以下の要素を抽出する：

| 要素 | 説明 |
|---|---|
| **課題** | 何が問題だったか |
| **検討した選択肢** | 議論に上がった代替案 |
| **決定事項** | 最終的に採用した方針 |
| **根拠** | なぜその判断に至ったか |
| **トレードオフ** | 受け入れた妥協点 |

### 2. 関連アイテムの特定

```bash
# 変更されたファイルから逆引き
trace_query.py <dir> chain --file <path>

# UID が分かっている場合
trace_query.py <dir> chain <UID>
```

### 3. ADR の作成

```bash
doorstop_ops.py <dir> add -d ADR \
  -t "ADR本文（下記テンプレートに従う）" \
  --header "判断の短い見出し" \
  -g <GROUP> \
  --links <関連アイテムUID...>
```

### 4. ADR 本文の記述

以下のセクション構成で `text` を記述する。**棄却された代替案とその理由**を必ず含める。

```markdown
## コンテキスト（背景）

この判断が必要になった背景。何が問題だったか。

## 決定

採用した具体的な方針。何をどう変えるか。

## 結果（トレードオフ）

- **メリット**: 決定による利点
- **デメリット**: 受け入れた妥協点・制約

## 棄却された代替案

- **案X**: 概要。棄却理由
- **案Y**: 概要。棄却理由
```

### 5. レビューとステータス設定

```bash
# レビュー済みにする
doorstop_ops.py <dir> review <ADR_UID>
```

ステータスは通常 `accepted`（デフォルト）。
提案段階でユーザーの承認を待つ場合は `proposed` に設定する。

```bash
doorstop_ops.py <dir> update <ADR_UID> --status proposed
```

### 6. 既存 ADR の更新（判断を覆す場合）

既存の意思決定を覆す場合は、旧 ADR を `superseded` に更新してから新 ADR を作成する。

```bash
doorstop_ops.py <dir> update ADR001 --status superseded
doorstop_ops.py <dir> add -d ADR -t "新しい判断..." --links ADR001 SPEC001
```

### 7. 報告

```
ADR054 を作成しました。
  - 判断: [1行要約]
  - 関連: SPEC007, IMPL007
  - ステータス: accepted
```

## エージェントへの指針

### いつ ADR を提案すべきか

以下のシグナルを会話中に検出した場合、ADR の作成をユーザーに提案する：

- ユーザーが「こっちの方がいい」「こうしよう」と方針を決定した
- 複数の選択肢を比較検討した議論が収束した
- 「なぜ」「どうして」の議論が深まり、非自明な判断に至った
- 既存の ADR に記録された判断と異なる方針を採用した

### 提案の仕方

```
この意思決定を ADR に記録しますか？
- 判断: [1行要約]
- 代替案: [棄却した案の列挙]
```

ユーザーが同意した場合のみ作成する。

---

## コマンドクイックリファレンス

```bash
# ADR 追加
doorstop_ops.py <dir> add -d ADR -t "本文" --header "見出し" -g GROUP --links UID...

# ステータス更新
doorstop_ops.py <dir> update <ADR_UID> --status <proposed|accepted|superseded|deprecated>

# レビュー
doorstop_ops.py <dir> review <ADR_UID>

# チェーン確認
trace_query.py <dir> chain <UID>
trace_query.py <dir> chain --file <path>
```

詳細は `${CLAUDE_PLUGIN_ROOT}/references/doorstop_reference.md` を参照。

---

## ADR テンプレート

```bash
doorstop_ops.py <dir> add -d ADR \
  -t "## コンテキスト（背景）
[この判断が必要になった背景]

## 決定
[採用した具体的な方針]

## 結果（トレードオフ）
- **メリット**: [利点]
- **デメリット**: [妥協点]

## 棄却された代替案
- **案1**: [概要]。[棄却理由]
- **案2**: [概要]。[棄却理由]" \
  --header "[判断の短い見出し]" \
  -g GROUP \
  --links <関連UID...>
```

詳細は `${CLAUDE_PLUGIN_ROOT}/references/concepts/adr.md` を参照。
