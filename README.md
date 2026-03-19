# neelbauman-plugins

Claude Code プラグインマーケットプレイス。

## マーケットプレイスの追加

このリポジトリをマーケットプレイスとして Claude Code に登録します。

```bash
claude plugins marketplace add https://github.com/neelbauman/claude-plugins.git
```

登録が完了すると、マーケットプレイス名 `neelbauman-plugins` でプラグインを参照できるようになります。

### 登録の確認

```bash
claude plugins marketplace list
```

### スコープ指定

デフォルトはユーザースコープです。プロジェクト単位で管理したい場合は `--scope` を指定します。

```bash
claude plugins marketplace add https://github.com/neelbauman/claude-plugins.git --scope project
```

| スコープ | 適用範囲 |
|---------|---------|
| `user` | すべてのプロジェクト（デフォルト） |
| `project` | 現在のプロジェクトのみ |
| `local` | ローカル環境のみ（Git 管理外） |

## プラグインのインストール

### インストール

```bash
claude plugins install <plugin-name>@neelbauman-plugins
```

例：

```bash
claude plugins install doorstop-spec-driven@neelbauman-plugins
```

インストール後、Claude Code を再起動するかセッション内で `/reload-plugins` を実行すると反映されます。

### 有効化・無効化

```bash
# 無効化
claude plugins disable doorstop-spec-driven@neelbauman-plugins

# 有効化
claude plugins enable doorstop-spec-driven@neelbauman-plugins
```

### アップデート

```bash
claude plugins update doorstop-spec-driven@neelbauman-plugins
```

マーケットプレイス全体を最新化してからアップデートする場合：

```bash
claude plugins marketplace update neelbauman-plugins
claude plugins update doorstop-spec-driven@neelbauman-plugins
```

### アンインストール

```bash
claude plugins uninstall doorstop-spec-driven@neelbauman-plugins
```

## 利用可能なプラグイン

| プラグイン | 説明 |
|-----------|------|
| [doorstop-spec-driven](./plugins/doorstop-spec-driven-plugin/) | 仕様駆動開発（SDD）プラグイン。Doorstop による要件 → 仕様 → 実装 → テストの全ライフサイクルをエージェントが自律的に管理する |

## マーケットプレイスの削除

```bash
claude plugins marketplace remove neelbauman-plugins
```
