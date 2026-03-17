"""Phase 3: 属性フィルタ付き検索コマンドのテスト。"""
from __future__ import annotations

import pytest

from helpers import make_item, make_link, make_doc, make_tree, make_args

from _trace_query.search import cmd_search


# =========================================================================
# cmd_search
# =========================================================================

class TestCmdSearch:
    def _base_args(self, **overrides):
        defaults = dict(
            pattern=None, document=None, group=None, priority=None,
            suspect=False, unreviewed=False, has_gherkin=False, derived=False,
        )
        defaults.update(overrides)
        return make_args(**defaults)

    def test_text_pattern(self, simple_tree, capture_out):
        args = self._base_args(pattern="認証")
        result = capture_out(lambda: cmd_search(simple_tree, args))
        assert result["ok"] is True
        assert result["count"] >= 1

    def test_regex_pattern(self, simple_tree, capture_out):
        args = self._base_args(pattern="キャッシュ|ログ")
        result = capture_out(lambda: cmd_search(simple_tree, args))
        assert result["count"] >= 2

    def test_invalid_regex(self, simple_tree, capture_out):
        args = self._base_args(pattern="[invalid")
        result = capture_out(lambda: cmd_search(simple_tree, args))
        assert result["ok"] is False

    def test_document_filter(self, simple_tree, capture_out):
        args = self._base_args(document="REQ")
        result = capture_out(lambda: cmd_search(simple_tree, args))
        assert all(i["prefix"] == "REQ" for i in result["items"])

    def test_group_filter(self, simple_tree, capture_out):
        args = self._base_args(group="AUTH")
        result = capture_out(lambda: cmd_search(simple_tree, args))
        assert all("AUTH" in i["groups"] for i in result["items"])

    def test_priority_filter(self, simple_tree, capture_out):
        args = self._base_args(priority="high")
        result = capture_out(lambda: cmd_search(simple_tree, args))
        assert all(i["priority"] == "high" for i in result["items"])

    def test_suspect_filter(self, suspect_tree, capture_out):
        args = self._base_args(suspect=True)
        result = capture_out(lambda: cmd_search(suspect_tree, args))
        assert result["count"] >= 1

    def test_unreviewed_filter(self, simple_tree, capture_out):
        args = self._base_args(unreviewed=True)
        result = capture_out(lambda: cmd_search(simple_tree, args))
        # All items in simple_tree are unreviewed (reviewed=False)
        assert result["count"] >= 1

    def test_derived_filter(self, capture_out):
        req = make_item("REQ001", text="要件", stamp_value="s1")
        spec = make_item("SPEC001", text="派生仕様", derived=True,
                         links=[make_link("REQ001", stamp="s1")])
        spec2 = make_item("SPEC002", text="通常仕様",
                          links=[make_link("REQ001", stamp="s1")])
        tree = make_tree([
            make_doc("REQ", items=[req]),
            make_doc("SPEC", parent="REQ", items=[spec, spec2]),
        ])
        args = self._base_args(derived=True)
        result = capture_out(lambda: cmd_search(tree, args))
        assert result["count"] == 1
        assert result["items"][0]["uid"] == "SPEC001"

    def test_gherkin_filter(self, simple_tree, capture_out):
        args = self._base_args(has_gherkin=True)
        result = capture_out(lambda: cmd_search(simple_tree, args))
        # SPEC001 has gherkin
        assert result["count"] >= 1

    def test_combined_filters(self, simple_tree, capture_out):
        args = self._base_args(document="SPEC", group="AUTH", priority="high")
        result = capture_out(lambda: cmd_search(simple_tree, args))
        assert result["count"] >= 1
        for item in result["items"]:
            assert item["prefix"] == "SPEC"
            assert "AUTH" in item["groups"]
            assert item["priority"] == "high"

    def test_no_pattern_returns_all(self, simple_tree, capture_out):
        args = self._base_args()
        result = capture_out(lambda: cmd_search(simple_tree, args))
        assert result["count"] >= 1

    def test_inactive_excluded(self, capture_out):
        active = make_item("REQ001", text="active item")
        inactive = make_item("REQ002", text="inactive item", active=False)
        tree = make_tree([make_doc("REQ", items=[active, inactive])])
        args = self._base_args()
        result = capture_out(lambda: cmd_search(tree, args))
        uids = [i["uid"] for i in result["items"]]
        assert "REQ001" in uids
        assert "REQ002" not in uids
