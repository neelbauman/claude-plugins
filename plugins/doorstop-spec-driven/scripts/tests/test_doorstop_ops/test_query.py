"""Phase 2: 読み取り専用照会コマンドのテスト。"""
from __future__ import annotations

import pytest

from helpers import make_item, make_doc, make_tree, make_args

from _doorstop_ops.query import cmd_list, cmd_groups, cmd_tree, cmd_find


# =========================================================================
# cmd_list
# =========================================================================

class TestCmdList:
    def test_all(self, simple_tree, capture_out):
        args = make_args(document=None, group=None)
        result = capture_out(lambda: cmd_list(simple_tree, args))
        assert result["ok"] is True
        assert result["action"] == "list"
        assert result["count"] == 12  # 3 REQ + 3 SPEC + 3 IMPL + 3 TST

    def test_filter_document(self, simple_tree, capture_out):
        args = make_args(document="REQ", group=None)
        result = capture_out(lambda: cmd_list(simple_tree, args))
        assert result["count"] == 3
        assert all(i["prefix"] == "REQ" for i in result["items"])

    def test_filter_group(self, simple_tree, capture_out):
        args = make_args(document=None, group="AUTH")
        result = capture_out(lambda: cmd_list(simple_tree, args))
        assert result["count"] >= 1
        for item in result["items"]:
            assert "AUTH" in item["groups"]

    def test_filter_multiple_groups(self, simple_tree, capture_out):
        args = make_args(document=None, group="AUTH,CACHE")
        result = capture_out(lambda: cmd_list(simple_tree, args))
        for item in result["items"]:
            assert "AUTH" in item["groups"] or "CACHE" in item["groups"]

    def test_empty_result(self, simple_tree, capture_out):
        args = make_args(document="NONEXIST", group=None)
        result = capture_out(lambda: cmd_list(simple_tree, args))
        assert result["count"] == 0


# =========================================================================
# cmd_groups
# =========================================================================

class TestCmdGroups:
    def test_aggregation(self, simple_tree, capture_out):
        args = make_args()
        result = capture_out(lambda: cmd_groups(simple_tree, args))
        assert result["ok"] is True
        assert result["action"] == "groups"
        assert "AUTH" in result["groups"]
        assert "CACHE" in result["groups"]
        assert "LOG" in result["groups"]
        # AUTH should appear in REQ, SPEC, IMPL, TST
        assert result["groups"]["AUTH"]["count"] >= 2

    def test_empty_tree(self, empty_tree, capture_out):
        args = make_args()
        result = capture_out(lambda: cmd_groups(empty_tree, args))
        assert result["groups"] == {}


# =========================================================================
# cmd_tree
# =========================================================================

class TestCmdTree:
    def test_structure(self, simple_tree, capture_out):
        args = make_args()
        result = capture_out(lambda: cmd_tree(simple_tree, args))
        assert result["ok"] is True
        assert result["action"] == "tree"
        assert len(result["documents"]) == 4
        prefixes = [d["prefix"] for d in result["documents"]]
        assert "REQ" in prefixes
        assert "SPEC" in prefixes
        assert "IMPL" in prefixes
        assert "TST" in prefixes

    def test_parent_info(self, simple_tree, capture_out):
        args = make_args()
        result = capture_out(lambda: cmd_tree(simple_tree, args))
        for doc in result["documents"]:
            if doc["prefix"] == "SPEC":
                assert doc["parent"] == "REQ"
            elif doc["prefix"] == "REQ":
                assert doc["parent"] is None or doc["parent"] == ""


# =========================================================================
# cmd_find
# =========================================================================

class TestCmdFind:
    def test_matches_text(self, simple_tree, capture_out):
        args = make_args(query="認証")
        result = capture_out(lambda: cmd_find(simple_tree, args))
        assert result["ok"] is True
        assert result["count"] >= 1
        assert any("認証" in i["text"] for i in result["items"])

    def test_matches_header(self, simple_tree, capture_out):
        args = make_args(query="LRU")
        result = capture_out(lambda: cmd_find(simple_tree, args))
        assert result["count"] >= 1

    def test_case_insensitive(self, capture_out):
        item = make_item("X001", text="Hello World", header="")
        tree = make_tree([make_doc("X", items=[item])])
        args = make_args(query="hello")
        result = capture_out(lambda: cmd_find(tree, args))
        assert result["count"] == 1

    def test_no_results(self, simple_tree, capture_out):
        args = make_args(query="存在しないクエリ文字列XYZ")
        result = capture_out(lambda: cmd_find(simple_tree, args))
        assert result["count"] == 0
