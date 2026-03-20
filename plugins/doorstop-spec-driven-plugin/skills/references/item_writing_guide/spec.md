# SPEC（仕様）— How を定義する

SPEC はコンポーネントの内部設計を定義する。
インターフェース（API シグネチャ）、振る舞い（処理フロー・アルゴリズム）、
パラメータ仕様、エラーハンドリング、エッジケースを記述し、
加えて「**なぜこの設計にしたか**」の設計判断を記録する。
「何をやりとりするか」ではなく「**中でどう処理するか**」に焦点を当てる。

### プロファイルによる役割の違い

| プロファイル | 上位文書 | SPEC の役割 |
|---|---|---|
| **lite** | REQ | 基本設計＋詳細設計を兼ねる |
| **standard** | ARCH | 詳細設計に特化する |
| **full** | — | LLD（Low-Level Design）が同等の役割を担う |

---

## テンプレート（複雑度「高」）

```yaml
active: true
derived: false
gherkin: |
  Scenario: 基本キャッシュ動作
    Given 空のDBとLocalStorageが初期化されている
    When @spot.mark() でデコレートされた関数を同一引数で2回呼び出す
    Then 1回目は関数が実行されキャッシュされる
    And 2回目はキャッシュから結果が返り関数は実行されない

  Scenario: sync/async 自動判定
    Given sync関数が定義されている
    When @spot.mark() でデコレートする
    Then _execute_sync() に委譲される

  Scenario: ジェネレータ関数の拒否
    Given ジェネレータ関数が定義されている
    When @spot.mark() を適用する
    Then ConfigurationError が送出される

  Scenario: version によるキャッシュ無効化
    Given version="v1" でキャッシュが作成されている
    When version="v2" に変更して同一引数で呼び出す
    Then キャッシュミスとなり関数が再実行される
groups:
  - CACHE
header: |
  mark デコレータ
level: 1.0
links:
- REQ001: <fingerprint>
normative: true
reviewed: null
text: |
  ## インターフェース

  ```python
  @spot.mark(
      save_blob: bool | None = None,
      keygen: KeyGen | None = None,
      version: str = "",
      content_type: ContentType = ContentType.PYTHON_OBJECT,
      serializer: SerializerProtocol | None = None,
      save_sync: bool | None = None,
      retention: str | None = None,
      hooks: list[HookBase] | None = None,
  )
  def my_func(x, y): ...
  ```

  ## 振る舞い

  ### 基本フロー

  1. デコレータが対象関数をラップする
  2. 呼び出し時にキャッシュキーを生成する
  3. DBからキャッシュを検索する
  4. **ヒット時**: デシリアライズして結果を返す（関数は実行しない）
  5. **ミス時**: 関数を実行し、結果をシリアライズしてDB/Blobに保存する

  ### sync/async 自動判定

  - `inspect.iscoroutinefunction(fn)` で判定する
  - sync関数 → `_execute_sync()` に委譲
  - async関数 → `_execute_async()` に委譲

  ## パラメータ詳細

  | パラメータ | デフォルト | 説明 |
  |---|---|---|
  | `save_blob` | `None` | `None`: StoragePolicy に委譲、`True`: 強制Blob保存、`False`: DB内保存 |
  | `keygen` | `None` | キャッシュキー生成のカスタマイズ。特定引数の除外等 |
  | `version` | `""` | バージョン文字列。変更するとキャッシュが無効化される |
  | `content_type` | `PYTHON_OBJECT` | セマンティックなコンテンツ種別 |
  | `serializer` | `None` | `None`: Spotのデフォルトを使用。関数単位でオーバーライド可能 |
  | `save_sync` | `None` | `None`: Spotのデフォルト（`default_wait`）に従う |
  | `retention` | `None` | ライフサイクルポリシーの保持期間（例: `"30d"`, `"1y"`） |
  | `hooks` | `None` | 関数単位のフックリスト |

  ## エラーハンドリング

  - ジェネレータ関数を渡した場合 → `ConfigurationError` を送出
  - シリアライズ失敗時 → `SerializationError` を送出
  - Blob保存失敗（`save_sync=False`） → ERROR ログに記録、例外は送出しない

  ## 設計判断

  ### デコレータファクトリパターンの採用

  `@mark` と `@mark()` の両方をサポートするため、二段階デコレータファクトリを採用した。
  Flask の `@app.route` 等で広く使われるパターンであり、ユーザーの学習コストが低い。

  **棄却した代替案**: メタクラスベースの登録方式。宣言的だがデバッグが困難なため棄却。

  ### sync/async 分岐をデコレーション時に行う理由

  呼び出し時に毎回 `iscoroutinefunction()` で判定する方式も可能だが、
  ランタイムオーバーヘッドをゼロにするため、デコレーション時に確定させる方式を選択した。
  動的に async に切り替えるケースは実用上ないと判断した。

  > **ADR との使い分け**: 上記の判断はこの SPEC の文脈でのみ意味を持つ局所的な判断である。
  > もしシリアライザ選定のように複数コンポーネントに影響し、代替案の検討が重い判断であれば、
  > ADR に切り出す。

  ## エッジケース

  - ラップされた関数の `__name__`, `__doc__`, `inspect.signature` は保持される
  - デコレータの多重適用は未定義動作とする
  - `version` が空文字の場合と未指定の場合は同一とみなす
```

---

## テンプレート（複雑度「低」）

複雑度が低い SPEC では、インターフェースと振る舞いの要点を簡潔に記述する。
`gherkin` や設計判断セクションは省略できる。

```yaml
active: true
derived: false
groups:
  - CLI
header: |
  version コマンド
level: 3.1
links:
- REQ010: <fingerprint>
normative: true
reviewed: null
text: |
  ## インターフェース

  ```
  beautyspot version [--json]
  ```

  ## 振る舞い

  - `__version__` からバージョン文字列を取得し、`rich.Panel` で表示する
  - `--json` 指定時は `{"version": "X.Y.Z"}` を標準出力に出力する
  - 引数不正時は usage を表示して終了コード 2 で終了する
```

---

## `text` のセクション構成

| セクション | 目的 | 必須度 |
|---|---|---|
| インターフェース | コードレベルのAPI定義（シグネチャ） | 必須 |
| 振る舞い | 処理フローをステップで記述 | 必須 |
| パラメータ詳細 | 各パラメータの意味・デフォルト・挙動を表で整理 | パラメータが多い場合 |
| エラーハンドリング | 異常系の挙動を明示 | 異常系がある場合 |
| **設計判断** | **なぜこのAPI設計/アルゴリズムにしたか。代替案と棄却理由** | 非自明な判断がある場合 |
| エッジケース | 境界条件・未定義動作を記述 | 該当時 |

### 複雑度の判断基準

| 複雑度 | 構成 | 例 |
|---|---|---|
| **低** | インターフェース + 振る舞い（数行） | version コマンド、単純な CRUD |
| **中** | + パラメータ詳細 + エラーハンドリング | ストレージポリシー、LifecyclePolicy |
| **高** | + 設計判断 + エッジケース + gherkin | mark デコレータ、キャッシュキー生成 |

---

## `gherkin` フィールド

### `text` と `gherkin` の役割分担

| | `text` | `gherkin` |
|---|---|---|
| **内容** | 技術仕様（API、アルゴリズム、パラメータ、エラー処理） | 振る舞いシナリオ（Given/When/Then） |
| **対象読者** | 実装者・レビュアー | テスト設計者・ステークホルダー |
| **答える問い** | 「どう実装するか？」 | 「どう振る舞うか？」 |
| **TST への変換** | 間接的（テスト設計に判断が必要） | 直接的（シナリオ ≒ テストケース） |

### 書き方のルール

- 1つの SPEC アイテムに対して、主要な振る舞いを **3〜7 シナリオ** で記述する
- 各シナリオは TST のテストケースに 1:1 で対応させることを目指す
- 正常系 → 異常系 → エッジケースの順で記述する
- 技術的な実装詳細は `text` に書き、`gherkin` はユーザー視点の振る舞いに集中する
- 複雑度が低い SPEC（自明な機能）では `gherkin` を省略してもよい

---

## 隣接層との書き分け基準

### SPEC vs ARCH

ARCH はコンポーネント **間** の設計（外から見た構造）、
SPEC はコンポーネント **内** の設計（中の実装方針）。

| 観点 | ARCH に書く | SPEC に書く |
|---|---|---|
| インターフェース | コンポーネント間の外部 IF | メソッドシグネチャ・パラメータ |
| フロー | コンポーネント間のデータフロー | メソッド内の処理ステップ |
| 判断 | 構成全体の根拠（なぜこの分割か） | 局所的な設計判断（なぜこの API か） |

- 「このインターフェースを通じて何をやりとりするか」→ ARCH
- 「このインターフェースの中でどう処理するか」→ SPEC

### SPEC vs IMPL

SPEC は「**こう動くべき**」を定義し、IMPL は「**こう動かした**」を記録する。

| 観点 | SPEC に書く | IMPL に書く |
|---|---|---|
| 時制 | 設計時（実装前に確定） | 実装後（コードに基づく記録） |
| API | 公開シグネチャと契約 | 実装クラス・メソッドの内部構造 |
| 判断 | API 設計の根拠 | 実装手段の根拠（ライブラリ選択等） |
| 気づき | — | 実装中の発見、技術的負債、仕様への遡上事項 |

SPEC は IMPL が存在しなくても完結する。
IMPL は SPEC を前提として、「仕様をどう実現したか」を補足する。

### SPEC vs ADR

SPEC 内の設計判断は、そのアイテムの文脈でのみ意味を持つ**局所的な判断**。
ADR は複数のコンポーネントや層に影響する**重大な意思決定**。

- SPEC: 「sync/async 分岐をデコレーション時に確定させる」（mark デコレータ内部の話）
- ADR: 「シリアライザに MessagePack を採用する」（ストレージ・DB・テスト戦略に波及）

迷ったらまず SPEC 内に書き、影響範囲が広いと判明した時点で ADR に昇格させる。
