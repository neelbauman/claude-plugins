# 共通ルール

すべてのフローで守るべき鉄則・規約・禁止事項。

## 鉄則

1. **コードを書く前に設計文書を書く。** 初期導入時（adopt フロー）のみ例外
2. **振る舞いの定義が必要な文書には `gherkin` 属性で書く。** Given/When/Then 形式。テストケースに直結させる
3. **テストを書いたらTSTを書く。** テストコードとTSTアイテムは常にペア
4. **変更したらimpact_analysisを回す。** 変更の影響を把握してから修正に入る
5. **バリデーションを最後に必ず実行する。** リンク漏れやカバレッジ低下を放置しない
6. 仕様変更時は `validate_and_report.py --serve` を使いダッシュボードを起動し、レビューをユーザーに促す
7. **関連アイテムの探索には `trace_query.py` を使う。** doorstop YAMLをgrepしない。ファイルパスからの逆引きは `chain --file` を使う
8. **派生要求は設計層のみで使う。** `derived: true` + 根拠明記。IMPL/TSTでの使用は禁止
9. **外部ファイル紐付けには `references` を使う。** `ref` ではなく `references` 属性。最大2–3ファイル
10. **仕様変更のコミットはドキュメント層ごとに分ける。** 詳細は `${CLAUDE_PLUGIN_ROOT}/references/concepts/commit_convention.md` を参照
11. **新ドメイン概念には用語辞書を更新する。** `glossary.py add` で用語を追加し、`glossary.py check` で表記ゆれを検出する。詳細は `${CLAUDE_PLUGIN_ROOT}/references/concepts/glossary.md` を参照
12. **設計判断は ADR に記録する。** 技術選定やアーキテクチャ変更時、およびユーザーとの議論で方針が確定したとき。詳細は `${CLAUDE_PLUGIN_ROOT}/references/concepts/adr.md` を参照

## エージェントの振る舞い規約

- **仕様書の構造化**: 序文、背景、用語定義、章の見出しなど「システムが直接実装する要件ではないもの」には `--non-normative` を指定してアイテムを作成すること。
- **報告の簡潔化**: 内部構造は見せず、成果物ベースでユーザーに報告すること。
- **ツリー構造の動的判断**: 初動で `doorstop.build()` を呼び、存在する文書に基づいて振る舞いを動的に決定する。ツリー構造をハードコードしない。
- **最下位設計文書** = IMPL/TSTがリンクする直接の親（lite/standard: SPEC、full: LLD）。

## プロファイル

| プロファイル | 階層 | 適用場面 |
|---|---|---|
| `lite` | REQ → SPEC → IMPL/TST · ADR | 小規模（単体ライブラリ、個人開発） |
| `standard` | REQ/NFR → ARCH → SPEC → IMPL/TST · ADR | 中規模（複数サブシステム、チーム開発） |
| `full` | REQ/NFR → HLD → LLD → IMPL/TST · ADR | 大規模（規制産業、V字モデル準拠） |

詳細は `${CLAUDE_PLUGIN_ROOT}/profiles/*.yml` および `${CLAUDE_PLUGIN_ROOT}/references/concepts/traceability_and_profiles.md` を参照。

## スクリプトパス

すべてのスクリプトは `${CLAUDE_PLUGIN_ROOT}/scripts/` にある。実行は `uv run python ${CLAUDE_PLUGIN_ROOT}/scripts/<script>.py <project-dir> ...` の形式。

## 禁止事項

- ユーザーにDoorstop操作を要求する
- 設計文書なしでコードを書き始める（adopt フローを除く）
- doorstop YAMLファイルをgrep/手動検索する（`trace_query.py` を使う）
- IMPL/TSTで `derived: true` を使う
- `ref` 属性を使う（`references` に統一）
- suspect未解消のまま次のタスクに移る
- ツリーに存在しない文書タイプを作成しようとする

## リファレンス

| ドキュメント | 内容 |
|---|---|
| `${CLAUDE_PLUGIN_ROOT}/references/doorstop_reference.md` | doorstop_ops.pyによるDoorstop操作・属性・スクリプトリファレンス |
| `${CLAUDE_PLUGIN_ROOT}/references/item_writing_guide.md` | アイテム記述テンプレート（REQ/SPEC/IMPL/TST） |
| `${CLAUDE_PLUGIN_ROOT}/references/diagram_and_image_guide.md` | 図表・画像・数式の挿入ガイド |
| `${CLAUDE_PLUGIN_ROOT}/references/scaling_strategy.md` | プロジェクト規模別の導入・運用ガイド |
| `${CLAUDE_PLUGIN_ROOT}/references/concepts/traceability_and_profiles.md` | トレーサビリティ・プロファイル・ライフサイクル概念 |
| `${CLAUDE_PLUGIN_ROOT}/references/concepts/commit_convention.md` | コミット粒度規約 |
| `${CLAUDE_PLUGIN_ROOT}/references/concepts/nfr.md` | FR/NFR（機能要件・非機能要件）の分類と運用 |
| `${CLAUDE_PLUGIN_ROOT}/references/concepts/adr.md` | ADR（設計判断記録）連携 |
| `${CLAUDE_PLUGIN_ROOT}/references/concepts/glossary.md` | 用語辞書（ユビキタス言語）の運用概念 |
| `${CLAUDE_PLUGIN_ROOT}/references/glossary_reference.md` | glossary.py スクリプトリファレンス |
| `${CLAUDE_PLUGIN_ROOT}/references/concepts/ci_integration.md` | CI連携の概念 |
