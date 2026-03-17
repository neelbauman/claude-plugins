---
name: adopt
description: >
  既存プロジェクトに仕様駆動開発を初期導入するフロー。
  「仕様駆動開発を導入したい」「既存コードに仕様を付けたい」
  「Doorstopを導入して」「SDDを始めたい」
  のような初期導入リクエストでトリガーする。
  コード→ドキュメントの逆引き仕様化を行う。鉄則1の例外フロー。
---

# [F] 初期導入フロー

## 初動

1. **共通ルールを読む**: `${CLAUDE_PLUGIN_ROOT}/references/common_rules.md`
2. **フロー手順を読む**: `${CLAUDE_PLUGIN_ROOT}/references/flows/initial_adoption.md`
3. **操作リファレンスを読む**: `${CLAUDE_PLUGIN_ROOT}/references/doorstop_reference.md`
4. **アイテムの書き方を読む**: `${CLAUDE_PLUGIN_ROOT}/references/item_writing_guide.md`

> **注意**: このフローは鉄則1「コードを書く前に設計文書を書く」の唯一の例外。
> 既存コードから逆引きで仕様を抽出する。

## 概要

既にコードが存在するプロジェクトに仕様駆動開発を導入するフロー。
コードを読み解き、要件・設計文書・IMPL/TST紐付けを構築する。

## セットアップ

```bash
uv add doorstop --dev
uv add markdown --dev
uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/init_project.py <project-dir> --profile standard --no-git-init

# NFRドキュメントも作成する場合:
uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/init_project.py <project-dir> --profile standard --with-nfr --no-git-init
```

## フロー

フロー手順の詳細は `${CLAUDE_PLUGIN_ROOT}/references/flows/initial_adoption.md` に従う。

要約:
1. プロジェクト初期化
2. コード読解
3. 用語辞書作成
4. REQ抽出（コードから逆引き）
5. 設計文書作成
6. IMPL/TST紐付け
7. ベースライン確立・検証
8. 以後は通常フロー（new/change/bugfix等）に移行
