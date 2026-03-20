#!/usr/bin/env python3
"""SDD MCP Server — Doorstop 仕様駆動開発の MCP ツールサーバー。

FastMCP (Python SDK) で stdio MCP サーバーを実装し、
既存の cmd_* 関数を直接呼び出す構造化ツールを提供する。
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "sdd",
    instructions=(
        "仕様駆動開発（Specification-Driven Development）ツールサーバー。"
        "Doorstop によるトレーサビリティ管理の全操作を MCP ツールとして提供する。"
    ),
)

# 各モジュールのツールを登録
from .doorstop_tools import register as register_doorstop
from .trace_tools import register as register_trace
from .validate_tools import register as register_validate
from .impact_tools import register as register_impact
from .baseline_tools import register as register_baseline
from .glossary_tools import register as register_glossary
from .init_tools import register as register_init

register_doorstop(mcp)
register_trace(mcp)
register_validate(mcp)
register_impact(mcp)
register_baseline(mcp)
register_glossary(mcp)
register_init(mcp)

def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
