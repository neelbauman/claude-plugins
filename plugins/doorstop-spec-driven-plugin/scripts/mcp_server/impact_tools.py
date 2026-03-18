"""impact_analysis を MCP ツールとしてラップする。"""

import os

from mcp.server.fastmcp import FastMCP

from ._adapter import get_tree


def register(mcp: FastMCP):
    """impact 系の MCP ツールを登録する。"""

    @mcp.tool()
    def sdd_impact(
        project_dir: str,
        changed_uids: list[str] | None = None,
        detect_suspects: bool = False,
    ) -> dict:
        """変更影響分析を実行する。

        Args:
            project_dir: プロジェクトルート
            changed_uids: 変更されたアイテムのUID リスト（手動指定）
            detect_suspects: suspect リンクから変更アイテムを自動検出
        """
        if not changed_uids and not detect_suspects:
            return {"ok": False, "error": "changed_uids または detect_suspects を指定してください"}

        project_dir = os.path.abspath(project_dir)
        saved_cwd = os.getcwd()
        try:
            os.chdir(project_dir)
            tree = get_tree(project_dir)

            from impact_analysis import detect_by_uid, detect_suspects as _detect_suspects, analyze_impact

            changed_map = {}
            if changed_uids:
                for item in detect_by_uid(tree, changed_uids):
                    changed_map[str(item.uid)] = item
            if detect_suspects:
                for item in _detect_suspects(tree):
                    changed_map[str(item.uid)] = item

            changed_items = list(changed_map.values())
            if not changed_items:
                return {
                    "ok": True,
                    "action": "impact",
                    "message": "変更されたアイテムは検出されませんでした",
                    "changed_count": 0,
                    "results": [],
                }

            results = analyze_impact(tree, changed_items, project_dir)
            return {
                "ok": True,
                "action": "impact",
                "changed_count": len(changed_items),
                "results": results,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            os.chdir(saved_cwd)
