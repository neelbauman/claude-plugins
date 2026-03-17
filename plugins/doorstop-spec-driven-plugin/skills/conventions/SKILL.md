---
name: conventions
description: >
  SDD のコミット規約・命名規約を提供する背景知識。
  コミット作成時やドキュメント層ごとの分割が必要なときに自動参照される。
  「コミットの仕方」「命名規約」「コミット粒度」に関する質問にも対応。
user-invocable: false
---

# SDD コミット・命名規約

## コミット粒度

ドキュメント層ごとにコミットを分ける。

| プレフィックス | 対象 | 例 |
|---|---|---|
| `spec:` | REQ, ARCH, HLD, SPEC, LLD, NFR | `spec: add REQ001 [auth]` |
| `impl:` | IMPL + ソースコード | `impl: IMPL001 JWT authentication` |
| `test:` | TST + テストコード | `test: TST001 auth flow` |
| `fix:` | バグ修正 | `fix: IMPL001 token expiry` |
| `adr:` | ADR | `adr: ADR003 choose JWT over session` |

## コミット順序

1. 仕様層（REQ → 設計）
2. 実装層（IMPL + コード）
3. テスト層（TST + テストコード）
4. suspect 解消（chain-clear 結果）

詳細は `${CLAUDE_PLUGIN_ROOT}/references/concepts/commit_convention.md` を参照。
