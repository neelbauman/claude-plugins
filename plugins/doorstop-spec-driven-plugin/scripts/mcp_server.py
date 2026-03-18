#!/usr/bin/env python3
"""SDD MCP Server — Doorstop 仕様駆動開発の MCP ツールサーバー。

FastMCP (Python SDK) で stdio MCP サーバーを実装し、
既存の cmd_* 関数を直接呼び出す構造化ツールを提供する。
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "sdd",
    version="1.0.0",
    instructions=(
        "仕様駆動開発（Specification-Driven Development）ツールサーバー。"
        "Doorstop によるトレーサビリティ管理の全操作を MCP ツールとして提供する。"
    ),
)

# 各モジュールのツールを登録
from mcp_server.doorstop_tools import register as register_doorstop
from mcp_server.trace_tools import register as register_trace
from mcp_server.validate_tools import register as register_validate
from mcp_server.impact_tools import register as register_impact
from mcp_server.baseline_tools import register as register_baseline
from mcp_server.glossary_tools import register as register_glossary
from mcp_server.init_tools import register as register_init

register_doorstop(mcp)
register_trace(mcp)
register_validate(mcp)
register_impact(mcp)
register_baseline(mcp)
register_glossary(mcp)
register_init(mcp)

if __name__ == "__main__":
    mcp.run(transport="stdio")
