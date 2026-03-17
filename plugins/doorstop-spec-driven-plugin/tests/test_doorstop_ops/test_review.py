"""Phase 2: レビュー・suspect解消コマンドのテスト。"""
from __future__ import annotations

import pytest

from helpers import make_item, make_link, make_doc, make_tree, make_args

from _doorstop_ops.review import cmd_clear, cmd_review, cmd_chain_review, cmd_chain_clear


# =========================================================================
# cmd_clear
# =========================================================================

class TestCmdClear:
    def test_suspect_links(self, suspect_tree, capture_out):
        args = make_args(uids=["SPEC001"])
        result = capture_out(lambda: cmd_clear(suspect_tree, args))
        assert result["ok"] is True
        assert result["action"] == "clear"
        assert result["count"] >= 1
        assert any(c["link"] == "REQ001" for c in result["cleared"])

    def test_no_suspect(self, simple_tree, capture_out):
        """stamp が一致している場合は何もクリアしない。"""
        args = make_args(uids=["SPEC001"])
        result = capture_out(lambda: cmd_clear(simple_tree, args))
        assert result["ok"] is True
        assert result["count"] == 0

    def test_multiple_items(self, suspect_tree, capture_out):
        args = make_args(uids=["SPEC001", "SPEC002"])
        result = capture_out(lambda: cmd_clear(suspect_tree, args))
        assert result["ok"] is True
        # SPEC001 has suspect, SPEC002 does not
        assert result["count"] >= 1


# =========================================================================
# cmd_review
# =========================================================================

class TestCmdReview:
    def test_single(self, simple_tree, capture_out):
        args = make_args(uids=["REQ001"])
        result = capture_out(lambda: cmd_review(simple_tree, args))
        assert result["ok"] is True
        assert result["action"] == "review"
        assert "REQ001" in result["reviewed"]

    def test_multiple(self, simple_tree, capture_out):
        args = make_args(uids=["REQ001", "REQ002", "REQ003"])
        result = capture_out(lambda: cmd_review(simple_tree, args))
        assert len(result["reviewed"]) == 3


# =========================================================================
# cmd_chain_review
# =========================================================================

class TestCmdChainReview:
    def test_traverses_upstream(self, simple_tree, capture_out):
        """SPEC001 をチェーンレビューすると、上流の REQ001 もレビューされる。"""
        args = make_args(uids=["SPEC001"])
        result = capture_out(lambda: cmd_chain_review(simple_tree, args))
        assert result["ok"] is True
        assert result["action"] == "chain-review"
        assert result["scope"] == "upstream"
        # SPEC001 と REQ001 の両方がレビューされる
        assert "SPEC001" in result["reviewed"]
        assert "REQ001" in result["reviewed"]

    def test_root_item_only(self, capture_out):
        """リンクのない REQ のチェーンレビューは自身のみ。"""
        req = make_item("REQ001", text="要件")
        tree = make_tree([make_doc("REQ", items=[req])])
        args = make_args(uids=["REQ001"])
        result = capture_out(lambda: cmd_chain_review(tree, args))
        assert result["chain_size"] == 1
        assert "REQ001" in result["reviewed"]


# =========================================================================
# cmd_chain_clear
# =========================================================================

class TestCmdChainClear:
    def test_traverses_downstream(self, suspect_tree, capture_out):
        """REQ001 をチェーンクリアすると、下流の SPEC001 のsuspectも解消される。"""
        args = make_args(uids=["REQ001"])
        result = capture_out(lambda: cmd_chain_clear(suspect_tree, args))
        assert result["ok"] is True
        assert result["action"] == "chain-clear"
        assert result["scope"] == "downstream"
        # SPEC001 の suspect リンクが解消されるはず
        assert result["chain_size"] >= 2

    def test_no_suspects_in_chain(self, simple_tree, capture_out):
        """全リンクが正常な場合は cleared が空。"""
        args = make_args(uids=["REQ001"])
        result = capture_out(lambda: cmd_chain_clear(simple_tree, args))
        assert result["ok"] is True
        assert len(result["cleared"]) == 0
