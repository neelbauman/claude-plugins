"""baseline_manager を MCP ツールとしてラップする。"""

from mcp.server.fastmcp import FastMCP

from scripts.core.baseline_manager import cmd_create, cmd_list, cmd_diff

from ._adapter import call_cmd


def register(mcp: FastMCP):
    """baseline 系の MCP ツールを登録する。"""

    @mcp.tool()
    def sdd_baseline_create(
        project_dir: str,
        name: str,
        tag: bool = False,
        tag_name: str | None = None,
        force: bool = False,
    ) -> dict:
        """ベースライン（スナップショット）を作成する。

        Args:
            project_dir: プロジェクトルート
            name: ベースライン名（例: v1.0, sprint-3）
            tag: Git タグを付ける
            tag_name: Git タグ名（省略時はベースライン名を使用）
            force: 既存ベースラインを上書き
        """
        return call_cmd(cmd_create, project_dir, {
            "name": name, "tag": tag, "tag_name": tag_name, "force": force,
        })

    @mcp.tool()
    def sdd_baseline_list(project_dir: str) -> dict:
        """ベースライン一覧を表示する。"""
        return call_cmd(cmd_list, project_dir, {})

    @mcp.tool()
    def sdd_baseline_diff(project_dir: str, v1: str, v2: str) -> dict:
        """2つのベースライン間の差分を表示する。v2 に HEAD を指定すると現在の状態と比較。

        Args:
            project_dir: プロジェクトルート
            v1: 比較元ベースライン名
            v2: 比較先ベースライン名（HEAD で現在の状態と比較）
        """
        return call_cmd(cmd_diff, project_dir, {"baseline1": v1, "baseline2": v2})
