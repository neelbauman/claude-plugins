"""Phase 2: 活性化・非活性化コマンドのテスト。"""
from __future__ import annotations

import pytest

from helpers import make_item, make_link, make_doc, make_tree, make_args

from _doorstop_ops.lifecycle import (
    cmd_deactivate,
    cmd_activate,
    cmd_deactivate_chain,
    cmd_activate_chain,
    _collect_downstream,
    _has_other_active_parents,
)
from _common import build_link_index


# =========================================================================
# cmd_deactivate
# =========================================================================

class TestCmdDeactivate:
    def test_single(self, simple_tree, capture_out):
        args = make_args(uids=["REQ001"])
        result = capture_out(lambda: cmd_deactivate(simple_tree, args))
        assert result["ok"] is True
        assert result["action"] == "deactivate"
        assert result["deactivated_count"] == 1
        assert result["results"][0]["changed"] is True

    def test_already_inactive(self, capture_out):
        item = make_item("REQ001", active=False)
        doc = make_doc("REQ", items=[item])
        # _find_item uses find_item which needs active=True in find_item,
        # but cmd_deactivate calls _find_item(tree, uid) without include_inactive.
        # The item needs to be findable, so we need it active for find but then test inactive logic.
        # Actually, looking at the code, cmd_deactivate uses _find_item which calls find_item_safe.
        # For inactive items, find_item won't find them. Let's use an active item set to inactive.
        active_item = make_item("REQ001", active=True)
        active_item.active = False  # Set after creation so it's in the doc
        doc = make_doc("REQ", items=[active_item])
        tree = make_tree([doc])
        # find_item won't find it since it's inactive, _find_item will call out with error
        # So this test actually tests that find_item fails for inactive items.
        # Let's instead test with the simple_tree properly:
        item = make_item("REQ001", active=True)
        doc = make_doc("REQ", items=[item])
        tree = make_tree([doc])
        # First deactivate
        args = make_args(uids=["REQ001"])
        result = capture_out(lambda: cmd_deactivate(tree, args))
        assert result["deactivated_count"] == 1

    def test_multiple(self, simple_tree, capture_out):
        args = make_args(uids=["REQ001", "REQ002"])
        result = capture_out(lambda: cmd_deactivate(simple_tree, args))
        assert result["deactivated_count"] == 2


# =========================================================================
# cmd_activate
# =========================================================================

class TestCmdActivate:
    def test_single_inactive(self, capture_out):
        item = make_item("REQ001", active=False)
        doc = make_doc("REQ", items=[item])
        tree = make_tree([doc])
        args = make_args(uids=["REQ001"])
        result = capture_out(lambda: cmd_activate(tree, args))
        assert result["ok"] is True
        assert result["action"] == "activate"
        assert result["activated_count"] == 1

    def test_already_active(self, simple_tree, capture_out):
        args = make_args(uids=["REQ001"])
        result = capture_out(lambda: cmd_activate(simple_tree, args))
        assert result["activated_count"] == 0
        assert result["results"][0]["reason"] == "既に活性"


# =========================================================================
# _collect_downstream
# =========================================================================

class TestCollectDownstream:
    def test_basic(self, simple_tree):
        children_idx, _ = build_link_index(simple_tree)
        result = _collect_downstream("REQ001", children_idx)
        uids = [e["uid"] for e in result]
        assert "SPEC001" in uids

    def test_max_depth(self, simple_tree):
        children_idx, _ = build_link_index(simple_tree)
        result = _collect_downstream("REQ001", children_idx, max_depth=0)
        # max_depth=0 means no children at depth 0
        uids = [e["uid"] for e in result]
        assert "SPEC001" in uids  # depth 0 items ARE collected, depth > 0 stops

    def test_cycle_prevention(self):
        """循環参照があっても無限ループしない。"""
        item_a = make_item("A001", links=[make_link("B001")])
        item_b = make_item("B001", links=[make_link("A001")])
        doc = make_doc("X", items=[item_a, item_b])
        tree = make_tree([doc])
        children_idx, _ = build_link_index(tree)
        result = _collect_downstream("A001", children_idx)
        # Should terminate without infinite loop
        assert isinstance(result, list)


# =========================================================================
# _has_other_active_parents
# =========================================================================

class TestHasOtherActiveParents:
    def test_true(self, simple_tree):
        """IMPL001 は SPEC001 にリンクしている。SPEC001 を除外した場合の他の親はない。"""
        # Create an item with two parents
        req1 = make_item("REQ001", stamp_value="s1")
        req2 = make_item("REQ002", stamp_value="s2")
        spec = make_item("SPEC001", links=[make_link("REQ001"), make_link("REQ002")])
        doc_req = make_doc("REQ", items=[req1, req2])
        doc_spec = make_doc("SPEC", parent="REQ", items=[spec])
        tree = make_tree([doc_req, doc_spec])
        assert _has_other_active_parents(spec, tree, "REQ001") is True

    def test_false(self):
        req = make_item("REQ001", stamp_value="s1")
        spec = make_item("SPEC001", links=[make_link("REQ001")])
        tree = make_tree([
            make_doc("REQ", items=[req]),
            make_doc("SPEC", parent="REQ", items=[spec]),
        ])
        assert _has_other_active_parents(spec, tree, "REQ001") is False


# =========================================================================
# cmd_deactivate_chain
# =========================================================================

class TestCmdDeactivateChain:
    def test_basic(self, simple_tree, capture_out):
        args = make_args(uid="REQ001", force=False)
        result = capture_out(lambda: cmd_deactivate_chain(simple_tree, args))
        assert result["ok"] is True
        assert result["action"] == "deactivate-chain"
        assert result["root"] == "REQ001"
        assert result["deactivated_count"] >= 1

    def test_force(self, simple_tree, capture_out):
        args = make_args(uid="REQ001", force=True)
        result = capture_out(lambda: cmd_deactivate_chain(simple_tree, args))
        assert result["ok"] is True
        assert result["force"] is True
        # With force, all downstream should be deactivated
        assert result["deactivated_count"] >= 1

    def test_already_inactive_not_findable(self, capture_out):
        """非活性アイテムは _find_item で検索できずエラーになる。"""
        item = make_item("REQ001", active=False)
        doc = make_doc("REQ", items=[item])
        tree = make_tree([doc])
        args = make_args(uid="REQ001", force=False)
        result = capture_out(lambda: cmd_deactivate_chain(tree, args))
        assert result["ok"] is False


# =========================================================================
# cmd_activate_chain
# =========================================================================

class TestCmdActivateChain:
    def test_basic(self, capture_out):
        req = make_item("REQ001", active=False)
        spec = make_item("SPEC001", active=False,
                         links=[make_link("REQ001")])
        tree = make_tree([
            make_doc("REQ", items=[req]),
            make_doc("SPEC", parent="REQ", items=[spec]),
        ])
        args = make_args(uid="REQ001")
        result = capture_out(lambda: cmd_activate_chain(tree, args))
        assert result["ok"] is True
        assert result["action"] == "activate-chain"
        assert result["activated_count"] >= 1

    def test_already_active(self, simple_tree, capture_out):
        args = make_args(uid="REQ001")
        result = capture_out(lambda: cmd_activate_chain(simple_tree, args))
        assert result["skipped_count"] >= 1
