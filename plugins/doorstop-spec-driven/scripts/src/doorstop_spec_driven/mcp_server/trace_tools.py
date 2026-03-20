"""trace_query の cmd_* を MCP ツールとしてラップする。"""

from mcp.server.fastmcp import FastMCP

from ..core._trace_query.chain import cmd_chain, cmd_context, cmd_related_files
from ..core._trace_query.status import cmd_status, cmd_coverage, cmd_gaps
from ..core._trace_query.search import cmd_search
from ..core._trace_query.quality import cmd_suspects, cmd_backlog

from ._adapter import call_cmd


def register(mcp: FastMCP):
    """trace_query 系の MCP ツールを登録する。"""

    @mcp.tool()
    def sdd_status(project_dir: str) -> dict:
        """プロジェクト全体のサマリ（件数・カバレッジ・suspect数）を表示する。"""
        return call_cmd(cmd_status, project_dir, {})

    @mcp.tool()
    def sdd_chain(
        project_dir: str,
        uid: str | None = None,
        file: str | None = None,
    ) -> dict:
        """指定UIDの上流→下流チェーン全体を表示する。file指定でファイルからの逆引きも可能。

        Args:
            project_dir: プロジェクトルート
            uid: 起点UID（file と排他）
            file: ファイルパスから逆引き（uid と排他）
        """
        return call_cmd(cmd_chain, project_dir, {"uid": uid, "file": file})

    @mcp.tool()
    def sdd_context(project_dir: str, uid: str) -> dict:
        """指定UIDの全文脈情報を一括取得する（target/upstream/downstream/files/health）。"""
        return call_cmd(cmd_context, project_dir, {"uid": uid})

    @mcp.tool()
    def sdd_related_files(
        project_dir: str,
        uid: str | None = None,
        file: str | None = None,
    ) -> dict:
        """関連ファイルパスをドキュメント層別に取得する。"""
        return call_cmd(cmd_related_files, project_dir, {"uid": uid, "file": file})

    @mcp.tool()
    def sdd_coverage(
        project_dir: str,
        group: str | None = None,
        detail: bool = False,
    ) -> dict:
        """カバレッジ詳細を表示する。

        Args:
            project_dir: プロジェクトルート
            group: グループで絞り込み
            detail: カバー元のマッピングも出力
        """
        return call_cmd(cmd_coverage, project_dir, {"group": group, "detail": detail})

    @mcp.tool()
    def sdd_suspects(project_dir: str, group: str | None = None) -> dict:
        """全suspect一覧を表示する。"""
        return call_cmd(cmd_suspects, project_dir, {"group": group})

    @mcp.tool()
    def sdd_gaps(
        project_dir: str,
        document: str | None = None,
        group: str | None = None,
    ) -> dict:
        """リンク漏れ・ref未設定のアイテム一覧を表示する。"""
        return call_cmd(cmd_gaps, project_dir, {"document": document, "group": group})

    @mcp.tool()
    def sdd_backlog(
        project_dir: str,
        document: str | None = None,
        group: str | None = None,
        all_docs: bool = False,
    ) -> dict:
        """優先度順のバックログ一覧を表示する（トリアージ用）。

        Args:
            project_dir: プロジェクトルート
            document: ドキュメントで絞り込み（デフォルト: REQ）
            group: グループで絞り込み
            all_docs: REQ以外のドキュメントも含める
        """
        return call_cmd(cmd_backlog, project_dir, {
            "document": document, "group": group, "all_docs": all_docs,
        })

    @mcp.tool()
    def sdd_search(
        project_dir: str,
        pattern: str | None = None,
        document: str | None = None,
        group: str | None = None,
        priority: str | None = None,
        suspect: bool = False,
        unreviewed: bool = False,
        has_gherkin: bool = False,
        derived: bool = False,
    ) -> dict:
        """属性フィルタ付き高機能検索（正規表現対応）。

        Args:
            project_dir: プロジェクトルート
            pattern: 検索パターン（正規表現、省略時は全件）
            document: ドキュメントで絞り込み（カンマ区切りで複数可）
            group: グループで絞り込み（カンマ区切りで複数可）
            priority: 優先度で絞り込み（カンマ区切り: critical,high,medium,low）
            suspect: suspectアイテムのみ
            unreviewed: 未レビューアイテムのみ
            has_gherkin: gherkin属性を持つアイテムのみ
            derived: 派生要求のみ
        """
        return call_cmd(cmd_search, project_dir, {
            "pattern": pattern, "document": document, "group": group,
            "priority": priority, "suspect": suspect, "unreviewed": unreviewed,
            "has_gherkin": has_gherkin, "derived": derived,
        })
