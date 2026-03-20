# LLD（詳細設計）— How を定義する（fullプロファイル）

LLDはSPECと同等の役割だが、V字モデルの用語に合わせてLLD（Low-Level Design）と呼称する。
HLDで定義されたコンポーネントの内部設計を定義し、
**単体テスト（unit test）に対応する設計レベル**である。

## テンプレート

```yaml
active: true
derived: false
gherkin: |
  Scenario: 有効なJWTトークンの検証
    Given RS256で署名された有効なJWTトークンがある
    When TokenVerifier.verify(token) を呼び出す
    Then Claims オブジェクトが返り user_id と exp が含まれる

  Scenario: 期限切れトークンの拒否
    Given 有効期限を過ぎたJWTトークンがある
    When TokenVerifier.verify(token) を呼び出す
    Then TokenExpiredError が送出される

  Scenario: 不正署名の拒否
    Given 異なる秘密鍵で署名されたJWTトークンがある
    When TokenVerifier.verify(token) を呼び出す
    Then InvalidSignatureError が送出される

  Scenario: 公開鍵キャッシュの自動更新
    Given キャッシュされた公開鍵の kid がトークンのヘッダと一致しない
    When TokenVerifier.verify(token) を呼び出す
    Then JWK Provider から最新の公開鍵を取得してから検証する
groups:
  - AUTH
header: |
  TokenVerifier
level: 1.0
links:
- HLD001: <fingerprint>
normative: true
reviewed: null
text: |
  ## インターフェース

  ```python
  class TokenVerifier:
      def __init__(
          self,
          jwk_provider: JWKProvider,
          algorithms: list[str] = ["RS256"],
          leeway: int = 30,  # 秒
      ) -> None: ...

      def verify(self, token: str) -> Claims:
          """JWT トークンを検証し、Claims を返す。

          Raises:
              TokenExpiredError: トークンが有効期限切れ
              InvalidSignatureError: 署名が不正
              MalformedTokenError: トークン形式が不正
          """
          ...
  ```

  ## 振る舞い

  ### 検証フロー

  1. トークンのヘッダから `kid`（Key ID）を抽出する
  2. `JWKProvider` から対応する公開鍵を取得する（キャッシュ優先）
  3. 署名を検証する
  4. `exp`（有効期限）を現在時刻 + `leeway` と比較する
  5. **成功時**: Claims オブジェクトを返す
  6. **失敗時**: 種別に応じた例外を送出する

  ### 公開鍵キャッシュ戦略

  - 初回アクセス時に JWK エンドポイントから取得しキャッシュする
  - `kid` が不一致の場合のみ再取得する（鍵ローテーション対応）
  - 再取得は最大60秒に1回に制限する（DoS防止）

  ## パラメータ詳細

  | パラメータ | デフォルト | 説明 |
  |---|---|---|
  | `algorithms` | `["RS256"]` | 許可する署名アルゴリズム。`none` は常に拒否 |
  | `leeway` | `30` | 有効期限の許容誤差（秒）。クロック差を吸収 |

  ## エラーハンドリング

  | エラー | 条件 | HTTP ステータス |
  |---|---|---|
  | `TokenExpiredError` | `exp + leeway < now` | 401 |
  | `InvalidSignatureError` | 署名不一致 | 401 |
  | `MalformedTokenError` | ヘッダ/ペイロードのデコード失敗 | 400 |

  ## 設計判断

  ### `leeway` パラメータのデフォルト値

  30秒に設定した。RFC 7519 では具体的な推奨値を定めていないが、
  NTP同期が前提の環境ではクロック差は通常数秒以内であり、
  30秒は十分なマージンを持ちつつ、期限切れトークンの悪用リスクを抑える妥当な値と判断した。

  **棄却した代替案**: `leeway=0`（厳密モード）をデフォルトにする案。
  クロック差によるユーザー体験の劣化リスクが高いため棄却。

  ### 例外の階層設計

  `TokenExpiredError`, `InvalidSignatureError`, `MalformedTokenError` を
  個別の例外クラスとし、共通基底クラス `TokenVerificationError` を持たせた。
  呼び出し側が「全部まとめてキャッチ」も「種別ごとに分岐」もできるようにするため。

  ## エッジケース

  - `alg: none` のトークンは常に拒否する（alg confusion attack 防止）
  - JWK エンドポイント到達不能時はキャッシュ済みの鍵でフォールバック
  - キャッシュも空の場合は `JWKUnavailableError` を送出
```

## ポイント

LLDはSPECと同じセクション構成を使うが、以下の点が異なる：

| 観点 | SPEC（lite/standard） | LLD（full） |
|---|---|---|
| 上位文書 | REQ（lite）/ ARCH（standard） | HLD |
| V字モデル対応 | 暗黙的 | 明示的（単体テストレベルに対応） |
| `gherkin` | 推奨 | 推奨（テストケースへの直接変換を重視） |
| 想定規模 | 小〜中規模 | 大規模、規制産業 |
