"""doorstop_ops の cmd_* を MCP ツールとしてラップする。"""

from mcp.server.fastmcp import FastMCP

from ..core._doorstop_ops.crud import cmd_add, cmd_update, cmd_reorder, cmd_link, cmd_unlink
from ..core._doorstop_ops.lifecycle import cmd_activate, cmd_deactivate, cmd_activate_chain, cmd_deactivate_chain
from ..core._doorstop_ops.review import cmd_clear, cmd_review, cmd_chain_review, cmd_chain_clear
from ..core._doorstop_ops.query import cmd_list, cmd_groups, cmd_tree, cmd_find

from ._adapter import call_cmd, call_cmd_write


def register(mcp: FastMCP):
    """doorstop_ops 系の MCP ツールを登録する。"""

    @mcp.tool()
    def sdd_tree(project_dir: str) -> dict:
        """Doorstop ドキュメントツリーの構造を表示する。"""
        return call_cmd(cmd_tree, project_dir, {})

    @mcp.tool()
    def sdd_add_item(
        project_dir: str,
        document: str,
        text: str,
        header: str | None = None,
        group: str | None = None,
        level: str | None = None,
        insert: str | None = None,
        ref: str | None = None,
        references: str | None = None,
        priority: str | None = None,
        test_level: str | None = None,
        non_normative: bool = False,
        derived: bool = False,
        gherkin: str | None = None,
        links: list[str] | None = None,
    ) -> dict:
        """Doorstop アイテムを追加する。

        Args:
            project_dir: プロジェクトルートディレクトリ
            document: ドキュメント（REQ/SPEC/ARCH/HLD/LLD/IMPL/TST/ADR/NFR）
            text: アイテムのテキスト
            header: ヘッダー
            group: 機能グループ
            level: レベル
            insert: 指定レベルに挿入
            ref: 参照ファイルパス（非推奨、references を使用）
            references: 外部ファイル紐付け（JSON文字列。例: '[{"path":"src/mod.py","type":"file"}]'）
            priority: 優先度（critical/high/medium/low/none/done）
            test_level: テスト粒度（unit/integration/acceptance）
            non_normative: 非規範的アイテム（見出し等）として追加
            derived: 派生要求として追加
            gherkin: Gherkin シナリオ（Given/When/Then 形式）
            links: リンク先UID のリスト
        """
        return call_cmd_write(cmd_add, project_dir, {
            "document": document, "text": text, "header": header,
            "group": group, "level": level, "insert": insert,
            "ref": ref, "references": references, "priority": priority,
            "test_level": test_level, "non_normative": non_normative,
            "derived": derived, "gherkin": gherkin, "links": links,
        })

    @mcp.tool()
    def sdd_update_item(
        project_dir: str,
        uid: str,
        text: str | None = None,
        header: str | None = None,
        group: str | None = None,
        ref: str | None = None,
        references: str | None = None,
        priority: str | None = None,
        test_level: str | None = None,
        gherkin: str | None = None,
        set_normative: bool = False,
        set_non_normative: bool = False,
    ) -> dict:
        """Doorstop アイテムを更新する。

        Args:
            project_dir: プロジェクトルートディレクトリ
            uid: 更新対象UID
            text: 新テキスト
            header: 新ヘッダー
            group: 新グループ
            ref: 新参照パス（非推奨）
            references: 外部ファイル紐付け（JSON文字列）
            priority: 優先度の変更
            test_level: テスト粒度の変更
            gherkin: Gherkin シナリオ
            set_normative: 規範的アイテムに設定
            set_non_normative: 非規範的アイテムに設定
        """
        return call_cmd_write(cmd_update, project_dir, {
            "uid": uid, "text": text, "header": header,
            "group": group, "ref": ref, "references": references,
            "priority": priority, "test_level": test_level,
            "gherkin": gherkin, "set_normative": set_normative,
            "set_non_normative": set_non_normative,
        })

    @mcp.tool()
    def sdd_reorder(project_dir: str, uid: str, level: str) -> dict:
        """アイテムのレベルを変更し、他を自動で再配置する。"""
        return call_cmd_write(cmd_reorder, project_dir, {"uid": uid, "level": level})

    @mcp.tool()
    def sdd_link(project_dir: str, child_uid: str, parent_uid: str) -> dict:
        """子アイテムから親アイテムへのリンクを追加する。"""
        return call_cmd_write(cmd_link, project_dir, {"child": child_uid, "parent": parent_uid})

    @mcp.tool()
    def sdd_unlink(project_dir: str, child_uid: str, parent_uid: str) -> dict:
        """子アイテムから親アイテムへのリンクを削除する。"""
        return call_cmd_write(cmd_unlink, project_dir, {"child": child_uid, "parent": parent_uid})

    @mcp.tool()
    def sdd_clear(project_dir: str, uids: list[str]) -> dict:
        """指定アイテムの suspect を解消する。"""
        return call_cmd_write(cmd_clear, project_dir, {"uids": uids})

    @mcp.tool()
    def sdd_review(project_dir: str, uids: list[str]) -> dict:
        """指定アイテムをレビュー済みにする。"""
        return call_cmd_write(cmd_review, project_dir, {"uids": uids})

    @mcp.tool()
    def sdd_chain_review(project_dir: str, uids: list[str]) -> dict:
        """アイテムとその祖先（上流）を一括でレビュー済みにする。"""
        return call_cmd_write(cmd_chain_review, project_dir, {"uids": uids})

    @mcp.tool()
    def sdd_chain_clear(project_dir: str, uids: list[str]) -> dict:
        """アイテムとその子孫（下流）の suspect を一括解消する。"""
        return call_cmd_write(cmd_chain_clear, project_dir, {"uids": uids})

    @mcp.tool()
    def sdd_deactivate(project_dir: str, uids: list[str]) -> dict:
        """アイテムを非活性化する（active: false）。"""
        return call_cmd_write(cmd_deactivate, project_dir, {"uids": uids})

    @mcp.tool()
    def sdd_activate(project_dir: str, uids: list[str]) -> dict:
        """アイテムを活性化する（active: true）。"""
        return call_cmd_write(cmd_activate, project_dir, {"uids": uids})

    @mcp.tool()
    def sdd_deactivate_chain(project_dir: str, uid: str, force: bool = False) -> dict:
        """リンクチェーン全体を非活性化する。

        Args:
            project_dir: プロジェクトルート
            uid: 起点UID
            force: 他に活性な親があっても強制的に非活性化
        """
        return call_cmd_write(cmd_deactivate_chain, project_dir, {"uid": uid, "force": force})

    @mcp.tool()
    def sdd_activate_chain(project_dir: str, uid: str) -> dict:
        """リンクチェーン全体を活性化する。"""
        return call_cmd_write(cmd_activate_chain, project_dir, {"uid": uid})

    @mcp.tool()
    def sdd_list(project_dir: str, document: str | None = None, group: str | None = None) -> dict:
        """アイテム一覧を取得する。"""
        return call_cmd(cmd_list, project_dir, {"document": document, "group": group})

    @mcp.tool()
    def sdd_groups(project_dir: str) -> dict:
        """グループ一覧を取得する。"""
        return call_cmd(cmd_groups, project_dir, {})

    @mcp.tool()
    def sdd_find(project_dir: str, query: str) -> dict:
        """テキスト検索でアイテムを探す。"""
        return call_cmd(cmd_find, project_dir, {"query": query})
