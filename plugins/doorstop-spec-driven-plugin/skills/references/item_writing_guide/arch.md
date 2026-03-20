# ARCH（基本設計）— Architecture を定義する（standardプロファイル）

ARCHはコンポーネント分割、コンポーネント間インターフェース、データフロー、
技術選定を定義する。「何を作るか」ではなく「どう構成するか」に焦点を当てる。
加えて、「**なぜこの構成にしたのか**」の設計根拠を記述し、
アーキテクチャ判断の追跡可能性を確保する。
fullプロファイルではHLD（High-Level Design）が同等の役割を担う。

## テンプレート

```yaml
active: true
derived: false
groups:
  - CACHE
header: |
  キャッシュサブシステム構成
level: 1.0
links:
- REQ001: <fingerprint>
normative: true
reviewed: null
text: |
  ## コンポーネント構成

  ```mermaid
  graph TD
    A[bs.Spot Factory] -->|DI| B[core.Spot Engine]
    B --> C[TaskDBBase]
    B --> D[SerializerProtocol]
    B --> E[BlobStorageBase]
    B --> F[StoragePolicyProtocol]
    B --> G[LimiterProtocol]
    B --> H[LifecyclePolicy]
  ```

  ## コンポーネント責務

  | コンポーネント | 責務 | インターフェース |
  |---|---|---|
  | core.Spot | キャッシュエンジン。キー生成→検索→実行→保存の制御 | `mark()`, `cached_run()` |
  | TaskDBBase | メタデータ永続化。キャッシュキーによる検索と保存 | `find_by_key()`, `insert()` |
  | SerializerProtocol | データのシリアライズ/デシリアライズ | `pack()`, `unpack()` |
  | BlobStorageBase | 大規模データの外部ストレージ保存 | `save()`, `load()`, `delete()` |
  | StoragePolicyProtocol | Blob保存の判定ポリシー | `should_save_as_blob()` |

  ## データフロー

  ```mermaid
  sequenceDiagram
    participant User as ユーザーコード
    participant Spot as core.Spot
    participant DB as TaskDB
    participant Ser as Serializer
    participant Blob as BlobStorage

    User->>Spot: fn(args)
    Spot->>DB: find_by_key(cache_key)
    alt キャッシュヒット
      DB-->>Spot: cached_data
      Spot->>Ser: unpack(data)
    else キャッシュミス
      Spot->>Spot: fn(args) 実行
      Spot->>Ser: pack(result)
      Spot->>DB: insert(metadata)
      opt Blob保存
        Spot->>Blob: save(key, data)
      end
    end
    Spot-->>User: result
  ```

  ## 設計根拠

  ### 駆動要因

  以下の品質特性と制約がこのアーキテクチャを形成した:

  - **拡張性**: ユーザーがストレージやシリアライザを差し替えたい
    → 全コンポーネントをProtocol/ABCで抽象化し、DI構成とした
  - **ゼロ設定**: ライブラリとして即座に使えること
    → ファクトリ関数（`bs.Spot()`）でデフォルト実装を自動ワイヤリング
  - **非同期IO**: 大規模データ保存がユーザーコードをブロックしないこと
    → ThreadPoolExecutorによるバックグラウンド永続化を分離

  ### なぜこのコンポーネント分割か

  キャッシュエンジン（core.Spot）を中心に、永続化関心事（DB, Storage, Serializer）と
  制御関心事（Policy, Limiter, Lifecycle）を分離した。

  - **永続化と制御の分離**: 保存先の変更（ローカル↔S3）が制御ロジックに影響しないため
  - **単一ファクトリへのDI集約**: 構成の複雑さをユーザーから隠蔽し、
    テスト時のモック差し替えも容易にするため
  - **Policy のプロトコル化**: 閾値判定ロジックの差し替えを可能にし、
    ユースケースごとの柔軟な設定を実現するため

  ### 検討した代替構成

  - **モノリシック構成**（全機能を1クラスに集約）: シンプルだが、
    ストレージ差し替え時にキャッシュロジックまで変更が波及するため棄却
  - **イベント駆動構成**（保存をイベントバスで分離）: 柔軟だが、
    ライブラリとしてはオーバーヘッドが大きく、デバッグも困難なため棄却

  > **関連ADR**: ADR001（シリアライザ選定）、ADR008（DB DI）等を参照。
  > 個別の技術選定判断はADRに記録し、ここでは構成全体の根拠を記述する。

  ## 技術選定

  | 技術領域 | 選定 | 理由 |
  |---|---|---|
  | メタデータDB | SQLite | ゼロ設定、組み込み可能、十分な性能 |
  | シリアライズ | MessagePack | JSONより高速・コンパクト、バイナリ対応 |
  | ストレージ | ローカルファイル / S3 | 小規模はローカル、大規模はS3で透過切替 |

  ## 非機能要件方針

  - **性能**: キャッシュヒット時のオーバーヘッドは1ms以内
  - **スレッド安全性**: `default_wait=False` 時はThreadPoolExecutorで非同期IO
  - **拡張性**: 全コンポーネントはProtocol/ABCで抽象化、DI差し替え可能
```

## ポイント

| セクション | 目的 |
|---|---|
| コンポーネント構成 | システムの構成要素と関係を図示（Mermaid推奨） |
| コンポーネント責務 | 各コンポーネントの責務とインターフェース |
| データフロー | コンポーネント間のデータの流れ（シーケンス図推奨） |
| **設計根拠** | **なぜこの構成にしたか。駆動要因・分割理由・代替案と棄却理由** |
| 技術選定 | 採用技術とその理由 |
| 非機能要件方針 | 性能、セキュリティ、スケーラビリティの目標値 |

> **ARCHとSPECの書き分け基準**:
> ARCH はコンポーネント **間** の設計（外から見た構造）、
> SPEC はコンポーネント **内** の設計（中の実装方針）。
> 「このインターフェースを通じて何をやりとりするか」はARCH、
> 「このインターフェースの中でどう処理するか」はSPEC。
>
> **ARCHとADRの書き分け基準**:
> ADR は**個別の設計判断**の記録（「なぜMessagePackか」「なぜDIか」）、
> ARCH の設計根拠は**構成全体の根拠**（「なぜこのコンポーネント分割か」「何がこの構造を駆動したか」）。
> 個別判断はADRに書き、ARCHからADRを参照する形で連携する。
