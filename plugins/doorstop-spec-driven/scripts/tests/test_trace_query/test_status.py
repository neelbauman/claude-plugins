"""Phase 3: 概況・カバレッジ・ギャップ照会のテスト。"""
from __future__ import annotations

import pytest

from helpers import make_item, make_link, make_doc, make_tree, make_args

from _trace_query.status import cmd_status, cmd_coverage, cmd_gaps


# =========================================================================
# cmd_status
# =========================================================================

class TestCmdStatus:
    def test_doc_stats(self, simple_tree, capture_out):
        args = make_args()
        result = capture_out(lambda: cmd_status(simple_tree, args))
        assert result["ok"] is True
        assert result["action"] == "status"
        assert "REQ" in result["documents"]
        assert "SPEC" in result["documents"]
        assert result["documents"]["REQ"]["count"] == 3

    def test_total_items(self, simple_tree, capture_out):
        args = make_args()
        result = capture_out(lambda: cmd_status(simple_tree, args))
        assert result["total_items"] == 12

    def test_coverage(self, simple_tree, capture_out):
        args = make_args()
        result = capture_out(lambda: cmd_status(simple_tree, args))
        # SPEC -> REQ should be 100% covered
        assert "SPEC -> REQ" in result["coverage"]
        assert result["coverage"]["SPEC -> REQ"]["percentage"] == 100.0

    def test_groups(self, simple_tree, capture_out):
        args = make_args()
        result = capture_out(lambda: cmd_status(simple_tree, args))
        assert "AUTH" in result["groups"]
        assert "CACHE" in result["groups"]

    def test_suspect_count(self, suspect_tree, capture_out):
        args = make_args()
        result = capture_out(lambda: cmd_status(suspect_tree, args))
        assert result["total_suspects"] >= 1

    def test_empty_tree(self, empty_tree, capture_out):
        args = make_args()
        result = capture_out(lambda: cmd_status(empty_tree, args))
        assert result["ok"] is True
        assert result["total_items"] == 0


# =========================================================================
# cmd_coverage
# =========================================================================

class TestCmdCoverage:
    def test_basic(self, simple_tree, capture_out):
        args = make_args(group=None, detail=False)
        result = capture_out(lambda: cmd_coverage(simple_tree, args))
        assert result["ok"] is True
        assert result["action"] == "coverage"
        assert "SPEC -> REQ" in result["relations"]

    def test_100_percent(self, simple_tree, capture_out):
        args = make_args(group=None, detail=False)
        result = capture_out(lambda: cmd_coverage(simple_tree, args))
        rel = result["relations"]["SPEC -> REQ"]
        assert rel["percentage"] == 100.0
        assert rel["covered"] == rel["total"]

    def test_partial_coverage(self, capture_out):
        req1 = make_item("REQ001", text="要件1", stamp_value="s1")
        req2 = make_item("REQ002", text="要件2", stamp_value="s2")
        spec1 = make_item("SPEC001", text="仕様1",
                          links=[make_link("REQ001", stamp="s1")])
        # REQ002 は未カバー
        tree = make_tree([
            make_doc("REQ", items=[req1, req2]),
            make_doc("SPEC", parent="REQ", items=[spec1]),
        ])
        args = make_args(group=None, detail=False)
        result = capture_out(lambda: cmd_coverage(tree, args))
        rel = result["relations"]["SPEC -> REQ"]
        assert rel["percentage"] == 50.0
        assert len(rel["uncovered_items"]) == 1
        assert rel["uncovered_items"][0]["uid"] == "REQ002"

    def test_group_filter(self, simple_tree, capture_out):
        args = make_args(group="AUTH", detail=False)
        result = capture_out(lambda: cmd_coverage(simple_tree, args))
        assert result["ok"] is True

    def test_detail_flag(self, simple_tree, capture_out):
        args = make_args(group=None, detail=True)
        result = capture_out(lambda: cmd_coverage(simple_tree, args))
        for key, rel in result["relations"].items():
            if rel["covered"] > 0:
                assert rel["covered_map"] is not None

    def test_zero_items(self, capture_out):
        tree = make_tree([
            make_doc("REQ", items=[]),
            make_doc("SPEC", parent="REQ", items=[]),
        ])
        args = make_args(group=None, detail=False)
        result = capture_out(lambda: cmd_coverage(tree, args))
        assert result["ok"] is True


# =========================================================================
# cmd_gaps
# =========================================================================

class TestCmdGaps:
    def test_missing_links(self, capture_out):
        """親リンクなしの SPEC アイテム。"""
        spec = make_item("SPEC001", text="仕様")
        tree = make_tree([
            make_doc("REQ", items=[make_item("REQ001", text="要件")]),
            make_doc("SPEC", parent="REQ", items=[spec]),
        ])
        args = make_args(document=None, group=None)
        result = capture_out(lambda: cmd_gaps(tree, args))
        assert result["ok"] is True
        assert len(result["missing_links"]) >= 1
        assert result["missing_links"][0]["uid"] == "SPEC001"

    def test_missing_refs(self, capture_out):
        """IMPL にreferences未設定。"""
        impl = make_item("IMPL001", text="実装",
                         links=[make_link("SPEC001")])
        spec = make_item("SPEC001", text="仕様", stamp_value="s1")
        tree = make_tree([
            make_doc("SPEC", items=[spec]),
            make_doc("IMPL", parent="SPEC", items=[impl]),
        ])
        args = make_args(document=None, group=None)
        result = capture_out(lambda: cmd_gaps(tree, args))
        assert len(result["missing_refs"]) >= 1

    def test_orphan_items(self, capture_out):
        """子ドキュメントから参照されていない SPEC。"""
        req = make_item("REQ001", text="要件", stamp_value="s1")
        spec = make_item("SPEC001", text="仕様",
                         links=[make_link("REQ001", stamp="s1")],
                         stamp_value="s_spec1")
        # IMPL exists but doesn't link to SPEC001
        impl = make_item("IMPL001", text="実装")
        tree = make_tree([
            make_doc("REQ", items=[req]),
            make_doc("SPEC", parent="REQ", items=[spec]),
            make_doc("IMPL", parent="SPEC", items=[impl]),
        ])
        args = make_args(document=None, group=None)
        result = capture_out(lambda: cmd_gaps(tree, args))
        orphan_uids = [o["uid"] for o in result["orphan_items"]]
        assert "SPEC001" in orphan_uids

    def test_document_filter(self, simple_tree, capture_out):
        args = make_args(document="IMPL", group=None)
        result = capture_out(lambda: cmd_gaps(simple_tree, args))
        # Only IMPL items should be checked
        for item in result["missing_links"] + result["missing_refs"]:
            assert item["prefix"] == "IMPL"

    def test_group_filter(self, simple_tree, capture_out):
        args = make_args(document=None, group="AUTH")
        result = capture_out(lambda: cmd_gaps(simple_tree, args))
        assert result["ok"] is True

    def test_no_gaps(self, simple_tree, capture_out):
        """全リンク・ref が正常なツリーではギャップが少ない。"""
        args = make_args(document=None, group=None)
        result = capture_out(lambda: cmd_gaps(simple_tree, args))
        assert result["ok"] is True
        assert result["missing_links"] == []
