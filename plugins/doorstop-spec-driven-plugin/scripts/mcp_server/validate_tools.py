"""validate_and_report を MCP ツールとしてラップする。"""

import contextlib
import io
import json
import os
import sys

from mcp.server.fastmcp import FastMCP

from ._adapter import get_tree


def register(mcp: FastMCP):
    """validate 系の MCP ツールを登録する。"""

    @mcp.tool()
    def sdd_validate(project_dir: str, strict: bool = True) -> dict:
        """Doorstop プロジェクトのバリデーションを実行し、結果をJSON で返す。

        Args:
            project_dir: プロジェクトルート
            strict: 全ての親アイテムに子リンクがあることを要求する（デフォルト: True）
        """
        project_dir = os.path.abspath(project_dir)
        saved_cwd = os.getcwd()
        try:
            os.chdir(project_dir)
            tree = get_tree(project_dir)

            from reporting.validate_and_report import main as _validate_main
            from core.validator import validate_tree, compute_coverage
            from core._common import is_normative, get_groups

            issues = validate_tree(tree, strict=strict, project_dir=project_dir)
            coverage = compute_coverage(tree)

            total_items = sum(1 for d in tree for item in d if item.active and is_normative(item))
            reviewed_items = sum(
                1 for d in tree for item in d
                if item.active and item.reviewed and is_normative(item)
            )
            groups = sorted({
                g for doc in tree for item in doc if item.active
                for g in get_groups(item) if g != "(未分類)"
            })

            return {
                "ok": len(issues["errors"]) == 0,
                "action": "validate",
                "documents": {doc.prefix: len([i for i in doc if i.active and is_normative(i)]) for doc in tree},
                "total_items": total_items,
                "groups": groups,
                "review_status": {
                    "total": total_items,
                    "reviewed": reviewed_items,
                },
                "errors": issues["errors"],
                "warnings": issues["warnings"],
                "info": issues["info"],
                "error_count": len(issues["errors"]),
                "warning_count": len(issues["warnings"]),
                "coverage": coverage,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            os.chdir(saved_cwd)
