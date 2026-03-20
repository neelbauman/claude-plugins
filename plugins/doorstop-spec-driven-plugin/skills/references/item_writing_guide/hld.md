# HLD（基本設計）— Architecture を定義する（fullプロファイル）

HLDはARCHと同等の役割だが、V字モデルの用語に合わせてHLD（High-Level Design）と呼称する。
サブシステム分割、コンポーネント間インターフェース、データフロー、技術選定を定義し、
**結合テスト（integration test）に対応する設計レベル**である。

## テンプレート

```yaml
active: true
derived: false
groups:
  - AUTH
header: |
  認証サブシステム構成
level: 1.0
links:
- REQ001: <fingerprint>
normative: true
reviewed: null
text: |
  ## サブシステム構成

  ```mermaid
  graph TD
    A[API Gateway] -->|認証ヘッダ| B[AuthService]
    B --> C[TokenVerifier]
    B --> D[SessionStore]
    C --> E[JWK Provider]
    D --> F[Redis]
  ```

  ## サブシステム責務

  | サブシステム | 責務 | 外部インターフェース |
  |---|---|---|
  | AuthService | 認証フロー制御。トークン検証とセッション管理を統括 | `authenticate()`, `logout()` |
  | TokenVerifier | JWT トークンの署名検証と有効期限チェック | `verify(token) → Claims` |
  | SessionStore | セッション状態の永続化（Redis） | `get()`, `set()`, `delete()` |
  | JWK Provider | 外部 IdP から公開鍵を取得・キャッシュ | `get_signing_key(kid)` |

  ## サブシステム間データフロー

  ```mermaid
  sequenceDiagram
    participant GW as API Gateway
    participant Auth as AuthService
    participant TV as TokenVerifier
    participant SS as SessionStore

    GW->>Auth: authenticate(token)
    Auth->>TV: verify(token)
    TV-->>Auth: Claims
    Auth->>SS: set(session_id, claims)
    Auth-->>GW: AuthResult(user_id, session_id)
  ```

  ## 設計根拠

  ### 駆動要因

  - **セキュリティ**: トークン検証は専用コンポーネントに分離し、
    検証ロジックの変更がフロー制御に影響しないようにする
  - **可用性**: セッションストアをRedisに外部化し、
    アプリケーションのスケールアウトを可能にする

  ### 検討した代替構成

  - **モノリシック認証**（1クラスで全機能を担う）: シンプルだが、
    トークン方式の変更時に全体を修正する必要があるため棄却
  - **外部認証サービス委譲**（Auth0等に全面委託）: 運用負荷は下がるが、
    細粒度の認可制御がしにくいため棄却

  ## 技術選定

  | 技術領域 | 選定 | 理由 |
  |---|---|---|
  | トークン方式 | JWT (RS256) | ステートレス検証、公開鍵配布が容易 |
  | セッションストア | Redis | 高速、TTL 自動削除、クラスタ対応 |
  | 鍵管理 | JWK | 鍵ローテーションが容易 |

  ## 非機能要件方針

  - **性能**: トークン検証はp99で10ms以内（公開鍵キャッシュ前提）
  - **可用性**: Redisダウン時はトークン検証のみで動作（グレースフルデグラデーション）
  - **セキュリティ**: トークンの有効期限は最大1時間、リフレッシュトークンは7日
```

## ポイント

HLDはARCHと同じセクション構成を使うが、以下の点が異なる：

| 観点 | ARCH（standard） | HLD（full） |
|---|---|---|
| V字モデル対応 | 暗黙的 | 明示的（結合テストレベルに対応） |
| 下位文書 | SPEC | LLD |
| テスト対応 | TST (test_level=integration) | TST (test_level=integration) |
| 想定規模 | チーム開発 | 多チーム開発、規制産業 |

> **HLDとLLDの書き分け基準:**
> HLD はサブシステム **間** の関係（外部IF、データフロー、技術選定理由、非機能要件の具体値）。
> LLD はサブシステム **内** の設計（関数シグネチャ、アルゴリズム詳細、状態遷移、エラー処理）。
>
> - HLD: 「認証サブシステムはOAuth 2.0 + JWTを採用する」
> - LLD: 「JWTトークン生成はRS256で署名し、有効期限は3600秒」
