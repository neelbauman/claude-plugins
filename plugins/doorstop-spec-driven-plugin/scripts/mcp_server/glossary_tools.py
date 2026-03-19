"""glossary を MCP ツールとしてラップする。"""

from mcp.server.fastmcp import FastMCP

from scripts.core.glossary import cmd_add, cmd_update, cmd_remove, cmd_list, cmd_check, cmd_unused

from ._adapter import call_cmd_no_tree


def register(mcp: FastMCP):
    """glossary 系の MCP ツールを登録する。"""

    @mcp.tool()
    def sdd_glossary_add(
        project_dir: str,
        term: str,
        definition: str,
        aliases: str | None = None,
        context: str | None = None,
        code: str | None = None,
    ) -> dict:
        """用語辞書に用語を追加する。

        Args:
            project_dir: プロジェクトルート
            term: 用語名
            definition: 定義
            aliases: エイリアス（カンマ区切り）
            context: コンテキスト（グループ名等）
            code: コード上の表現（クラス名、変数名等）
        """
        return call_cmd_no_tree(cmd_add, project_dir, {
            "term": term, "definition": definition,
            "aliases": aliases, "context": context, "code": code,
        })

    @mcp.tool()
    def sdd_glossary_update(
        project_dir: str,
        term: str,
        definition: str | None = None,
        aliases: str | None = None,
        context: str | None = None,
        code: str | None = None,
    ) -> dict:
        """用語辞書の用語定義を更新する。"""
        return call_cmd_no_tree(cmd_update, project_dir, {
            "term": term, "definition": definition,
            "aliases": aliases, "context": context, "code": code,
        })

    @mcp.tool()
    def sdd_glossary_remove(project_dir: str, term: str) -> dict:
        """用語辞書から用語を削除する。"""
        return call_cmd_no_tree(cmd_remove, project_dir, {"term": term})

    @mcp.tool()
    def sdd_glossary_list(project_dir: str, context: str | None = None) -> dict:
        """用語辞書の全用語を一覧表示する。"""
        return call_cmd_no_tree(cmd_list, project_dir, {"context": context})

    @mcp.tool()
    def sdd_glossary_check(project_dir: str) -> dict:
        """REQ/SPEC本文で表記ゆれ・エイリアス使用を検出する。"""
        return call_cmd_no_tree(cmd_check, project_dir, {})

    @mcp.tool()
    def sdd_glossary_unused(project_dir: str) -> dict:
        """定義済みだが仕様書で使われていない用語を検出する。"""
        return call_cmd_no_tree(cmd_unused, project_dir, {})
