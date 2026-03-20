# doorstop-spec-driven

Claude Code プラグイン — Doorstop による仕様駆動開発（Specification-Driven Development）

要件定義から設計・実装・テスト・検証まで、ソフトウェア開発の全ライフサイクルをトレーサビリティ付きで管理します。

## コンセプト

```
要件(REQ) → 設計(SPEC) → 実装(IMPL) → テスト(TST)
                ↑ トレーサビリティで全階層がリンク
```

「なぜこの実装があるのか」「この要件はどこで検証されているか」を常に追跡できる状態を維持しながら開発を進めます。エージェントが Doorstop の操作を自律的に行うため、ユーザーは Doorstop のコマンドを覚える必要はありません。

## 前提条件

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (Python パッケージマネージャ)

## インストール

```bash
claude plugins add /path/to/doorstop-spec-driven
```

開発中のローカルテストには `--plugin-dir` を使います。

```bash
claude --plugin-dir /path/to/doorstop-spec-driven
```

プラグインを有効化した後、`/reload-plugins` で再読み込みできます。

## プロファイル

プロジェクト規模に応じて 3 つのプロファイルから選択します。

### lite — 小規模開発

個人開発、単体ライブラリ向け。最小限のドキュメント階層。

```
REQ → SPEC → IMPL / TST
               ↑
             ADR（任意）
```

### standard — 中規模開発

チーム開発、複数サブシステム向け。基本設計と詳細設計を分離。

```
REQ / NFR → ARCH → SPEC → IMPL / TST
                            ↑
                          ADR（任意）
```

### full — 大規模開発

規制産業、V 字モデル準拠向け。テストレベルとの対応を明確化。

```
REQ / NFR → HLD → LLD → IMPL / TST
                          ↑
                        ADR（任意）
```

V 字モデル対応:

| 設計層 | テストレベル |
|--------|------------|
| REQ | 受入テスト (acceptance) |
| HLD | 結合テスト (integration) |
| LLD | 単体テスト (unit) |

## スキル一覧

プラグインが提供するスキル（コマンド）の一覧です。Claude Code 上で `/doorstop-spec-driven:<name>` として呼び出します。

### 開発ライフサイクル

| スキル | 呼び出し | 説明 |
|--------|---------|------|
| **init** | `/doorstop-spec-driven:init` | 新規プロジェクトの初期化。プロファイル選択 → ドキュメントツリー作成 → 最初の REQ 登録 |
| **adopt** | `/doorstop-spec-driven:adopt` | 既存プロジェクトに SDD を導入。コードから逆引きで仕様を抽出 |
| **new** | `/doorstop-spec-driven:new <要望>` | 新機能を追加。REQ 登録 → 設計 → 実装 → テスト → 検証のフルサイクル |
| **change** | `/doorstop-spec-driven:change <変更内容>` | 既存機能を変更。影響分析 → 設計更新 → 実装修正 → 検証 |
| **bugfix** | `/doorstop-spec-driven:bugfix <バグ説明>` | バグを修正。原因特定 → 仕様/実装バグ判別 → 修正 → 再発防止テスト |
| **deactivate** | `/doorstop-spec-driven:deactivate <UID>` | 機能を非活性化（ソフトデリート）。チェーン全体を `active: false` に |

### 管理・運用

| スキル | 呼び出し | 説明 |
|--------|---------|------|
| **triage** | `/doorstop-spec-driven:triage` | バックログの優先度付け・スコープ確定 |
| **report** | `/doorstop-spec-driven:report` | 状況確認。カバレッジ、suspect 数、ダッシュボード起動 |
| **release** | `/doorstop-spec-driven:release <version>` | リリース前の品質ゲート。全チェック実行 → ベースライン作成 |
| **adr** | `/doorstop-spec-driven:adr <判断概要>` | 設計判断を ADR に記録。議論の要約 → 代替案 → 決定事項 |

### 自動トリガー

以下のスキルは、ユーザーの発話内容から Claude が自動的に判断して起動します。

- **new** — 「〜を作って」「〜を実装して」「〜が欲しい」
- **change** — 「〜を変更して」「〜を修正して」「リファクタリングして」
- **bugfix** — 「バグを直して」「〜が動かない」「エラーが出る」
- **adr** — 議論で設計方針が確定したとき
- **report** — 「状況を教えて」「カバレッジは？」

以下のスキルはユーザーが明示的に呼び出す必要があります（`disable-model-invocation`）。

- **deactivate** — 機能削除は意図的な操作のみ
- **release** — リリースゲートは明示的な判断

## クイックスタート

### 1. 新規プロジェクトを始める

```
/doorstop-spec-driven:init
```

プロファイル（lite / standard / full）を聞かれるので選択します。Doorstop のセットアップとドキュメントツリーの作成が自動で行われます。

### 2. 機能を実装する

```
/doorstop-spec-driven:new ユーザー認証機能を追加して
```

または自然言語で話しかけるだけでも OK:

```
ユーザー認証機能を追加して
```

エージェントが以下を自律的に実行します:

1. 要件（REQ）の登録
2. 設計文書（SPEC 等）の作成
3. ソースコード・テストコードの実装
4. IMPL / TST アイテムの登録・リンク
5. トレーサビリティの検証

### 3. 既存プロジェクトに導入する

```
/doorstop-spec-driven:adopt
```

既存のコードから逆引きで仕様を抽出し、トレーサビリティを構築します。

### 4. 状況を確認する

```
/doorstop-spec-driven:report
```

カバレッジ、suspect（整合性の問題）、バリデーション結果を確認できます。ダッシュボード（Web UI）も起動できます。

### 5. リリースする

```
/doorstop-spec-driven:release v1.0.0
```

品質ゲート（バリデーション、カバレッジ 100%、suspect 0 件、テスト全件パス）を確認し、ベースラインを作成します。

## エージェント

| エージェント | 説明 |
|-------------|------|
| **sdd-advisor** | SDD の概念・運用についての質問に自動応答する助言エージェント。プロファイルの選び方、Doorstop の属性、トレーサビリティの考え方などを回答 |

SDD に関する質問をすると自動的に起動します。

```
仕様駆動開発でのコミットの粒度はどうすべき？
```

## Hooks

プラグインには以下のフックが組み込まれています。

| イベント | 内容 |
|---------|------|
| **PreToolUse** (Edit / Write) | Doorstop アイテム YAML の直接編集をブロック。`doorstop_ops.py` 経由の操作を強制 |
| **SessionStart** (compact) | コンテキスト圧縮後に SDD の基本ルールを再注入 |
| **Stop** (new / change / bugfix / adopt) | `validate_and_report.py --strict` の実行忘れを防止 |

## 鉄則 12 か条

すべてのスキルで共通して適用されるルールです。

1. **コードを書く前に設計文書を書く**（adopt のみ例外）
2. 振る舞い定義には **gherkin** 属性で Given/When/Then を書く
3. テストを書いたら **TST を書く**（常にペア）
4. 変更したら **impact_analysis.py** を回す
5. 最後に **validate_and_report.py --strict** を必ず実行する
6. 仕様変更時は **ダッシュボード** を起動しレビューを促す
7. 関連アイテムの探索には **trace_query.py** を使う（YAML を直接 grep しない）
8. 派生要求（`derived: true`）は**設計層のみ**。IMPL/TST では禁止
9. 外部ファイル紐付けには **references** を使う（`ref` は非推奨）
10. 仕様変更のコミットは**ドキュメント層ごとに分ける**
11. 新ドメイン概念には **glossary.py add** で用語辞書を更新する
12. 重要な設計判断は **ADR に記録する**

## ディレクトリ構成

```
doorstop-spec-driven/
├── .claude-plugin/
│   └── plugin.json           # プラグインマニフェスト
├── agents/
│   └── sdd-advisor.md        # SDD 助言エージェント
├── skills/                   # スキル定義
│   ├── _shared/rules.md      # 全スキル共通ルール
│   ├── init/                 # プロジェクト初期化
│   ├── adopt/                # 既存プロジェクト導入
│   ├── new/                  # 新機能開発
│   ├── change/               # 既存機能変更
│   ├── bugfix/               # バグ修正
│   ├── toggle-activation/    # 非活性化・活性化
│   ├── triage/               # 優先度付け
│   ├── report/               # レポート生成
│   ├── release/              # リリースゲート
│   ├── adr/                  # 設計判断記録
│   └── conventions/          # コミット規約（背景知識）
├── hooks/
│   ├── hooks.json            # フック設定
│   └── block-yaml-edit.sh    # YAML 直接編集ブロック
├── profiles/                 # プロファイル定義
│   ├── lite.yml
│   ├── standard.yml
│   └── full.yml
├── scripts/                  # Python スクリプト群
│   ├── init_project.py       # プロジェクト初期化
│   ├── publish_docs.py       # HTML ドキュメント出力
│   ├── bulk_import.py        # 一括インポート
│   ├── core/                 # コア機能
│   │   ├── doorstop_ops.py   # CRUD 統一 CLI
│   │   ├── trace_query.py    # トレーサビリティ照会
│   │   ├── validator.py      # バリデーション・カバレッジ
│   │   ├── baseline_manager.py # ベースライン管理
│   │   ├── impact_analysis.py  # 変更影響分析
│   │   └── glossary.py       # 用語辞書管理
│   ├── reporting/            # HTML レポート・ダッシュボード
│   └── server/               # ダッシュボード Web アプリ
├── references/               # リファレンスドキュメント
└── tests/                    # テストスイート
```

## コアスクリプト

エージェントがスキル実行時に内部的に使用するスクリプトです。ユーザーが直接実行する必要はありませんが、CI 連携などで活用できます。

| スクリプト | 役割 |
|-----------|------|
| `doorstop_ops.py` | アイテムの CRUD、リンク管理、レビュー、活性化/非活性化 |
| `trace_query.py` | トレーサビリティチェーンの照会、カバレッジ、suspect 検出、バックログ |
| `validator.py` | ツリー全体のバリデーション + カバレッジ計算 |
| `impact_analysis.py` | 変更の影響範囲を自動検出（Git diff 対応） |
| `baseline_manager.py` | 仕様のスナップショット管理（バージョン間差分） |
| `glossary.py` | ドメイン用語の一元管理 |
| `validate_and_report.py` | バリデーション + HTML レポート + ダッシュボード |

すべてのスクリプトは JSON 形式で結果を返します。

```json
{"ok": true, "data": { ... }}
{"ok": false, "error": "エラーメッセージ"}
```

## CI 連携

`validate_and_report.py` を CI パイプラインに組み込むことで、仕様の整合性を自動チェックできます。

```yaml
# GitHub Actions の例
- name: Validate specifications
  run: |
    uv run python path/to/validate_and_report.py . --strict
```

詳細は `references/concepts/ci_integration.md` を参照してください。

## リファレンスドキュメント

`references/` 配下に詳細なガイドがあります。sdd-advisor エージェントに質問すると、これらのドキュメントを参照して回答します。

| ドキュメント | 内容 |
|-------------|------|
| `doorstop_reference.md` | Doorstop 属性・コマンドの完全リファレンス |
| `item_writing_guide.md` | REQ/SPEC/IMPL/TST の記述テンプレートと実例 |
| `scaling_strategy.md` | プロジェクト規模別の導入戦略 |
| `diagram_and_image_guide.md` | 図表・画像をアイテムに埋め込む方法 |
| `concepts/traceability_and_profiles.md` | トレーサビリティの概念・プロファイル比較 |
| `concepts/adr.md` | ADR の書き方 |
| `concepts/nfr.md` | 非機能要件（NFR）の分類 |
| `concepts/commit_convention.md` | Git コミット規約 |
| `concepts/ci_integration.md` | CI パイプライン連携 |

## ライセンス

MIT
