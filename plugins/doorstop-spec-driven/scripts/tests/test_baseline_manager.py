"""Phase 5: baseline_manager.py の単体テスト。"""
from __future__ import annotations

import json

import pytest

from helpers import make_item, make_doc, make_tree, make_args

from baseline_manager import (
    _baselines_root,
    _snapshot_item,
    _take_snapshot,
    cmd_create,
    cmd_list,
    cmd_diff,
)


# =========================================================================
# _baselines_root
# =========================================================================

class TestBaselinesRoot:
    def test_from_tree(self, simple_tree):
        root = _baselines_root(simple_tree)
        assert str(root).endswith(".baselines")

    def test_empty_tree(self, empty_tree):
        root = _baselines_root(empty_tree)
        assert str(root).endswith(".baselines")


# =========================================================================
# _snapshot_item
# =========================================================================

class TestSnapshotItem:
    def test_structure(self):
        item = make_item("REQ001", text="要件の内容", header="認証",
                         groups=["AUTH"], priority="high")
        snap = _snapshot_item(item, "REQ")
        assert snap["uid"] == "REQ001"
        assert snap["prefix"] == "REQ"
        assert snap["header"] == "認証"
        assert snap["groups"] == ["AUTH"]
        assert snap["priority"] == "high"
        assert snap["active"] is True
        assert "stamp" in snap
        assert "text_snippet" in snap


# =========================================================================
# _take_snapshot
# =========================================================================

class TestTakeSnapshot:
    def test_captures_all(self, simple_tree):
        snap = _take_snapshot(simple_tree)
        assert "REQ001" in snap
        assert "SPEC001" in snap
        assert "IMPL001" in snap
        assert "TST001" in snap
        assert len(snap) == 12


# =========================================================================
# cmd_create
# =========================================================================

class TestCmdCreate:
    def test_new_baseline(self, simple_tree, capture_out, tmp_path):
        # Override doc paths to use tmp_path
        for doc in simple_tree:
            doc.path = str(tmp_path / doc.prefix.lower())
        args = make_args(name="v1.0", force=False, tag=False, tag_name=None)
        result = capture_out(lambda: cmd_create(simple_tree, args))
        assert result["ok"] is True
        assert result["action"] == "create"
        assert result["name"] == "v1.0"
        assert result["summary"]["total_items"] == 12

    def test_existing_no_force_error(self, simple_tree, capture_out, tmp_path):
        for doc in simple_tree:
            doc.path = str(tmp_path / doc.prefix.lower())
        args = make_args(name="v1.0", force=False, tag=False, tag_name=None)
        capture_out(lambda: cmd_create(simple_tree, args))
        # Second create without force
        result = capture_out(lambda: cmd_create(simple_tree, args))
        assert result["ok"] is False
        assert "既に存在" in result["error"]

    def test_existing_with_force(self, simple_tree, capture_out, tmp_path):
        for doc in simple_tree:
            doc.path = str(tmp_path / doc.prefix.lower())
        args = make_args(name="v1.0", force=False, tag=False, tag_name=None)
        capture_out(lambda: cmd_create(simple_tree, args))
        # Second create with force
        args_force = make_args(name="v1.0", force=True, tag=False, tag_name=None)
        result = capture_out(lambda: cmd_create(simple_tree, args_force))
        assert result["ok"] is True


# =========================================================================
# cmd_list
# =========================================================================

class TestCmdList:
    def test_empty(self, simple_tree, capture_out, tmp_path):
        for doc in simple_tree:
            doc.path = str(tmp_path / doc.prefix.lower())
        args = make_args()
        result = capture_out(lambda: cmd_list(simple_tree, args))
        assert result["ok"] is True
        assert result["baselines"] == []

    def test_with_baselines(self, simple_tree, capture_out, tmp_path):
        for doc in simple_tree:
            doc.path = str(tmp_path / doc.prefix.lower())
        # Create a baseline first
        args_create = make_args(name="v1.0", force=False, tag=False, tag_name=None)
        capture_out(lambda: cmd_create(simple_tree, args_create))
        # List
        args = make_args()
        result = capture_out(lambda: cmd_list(simple_tree, args))
        assert result["ok"] is True
        assert result["count"] == 1
        assert result["baselines"][0]["name"] == "v1.0"


# =========================================================================
# cmd_diff
# =========================================================================

class TestCmdDiff:
    def _create_baseline(self, tree, tmp_path, name, capture_out):
        for doc in tree:
            doc.path = str(tmp_path / doc.prefix.lower())
        args = make_args(name=name, force=False, tag=False, tag_name=None)
        capture_out(lambda: cmd_create(tree, args))

    def test_diff_identical(self, simple_tree, capture_out, tmp_path):
        self._create_baseline(simple_tree, tmp_path, "v1.0", capture_out)
        self._create_baseline(simple_tree, tmp_path, "v2.0", capture_out)
        args = make_args(baseline1="v1.0", baseline2="v2.0")
        result = capture_out(lambda: cmd_diff(simple_tree, args))
        assert result["ok"] is True
        assert result["summary"]["added"] == 0
        assert result["summary"]["removed"] == 0
        assert result["summary"]["changed"] == 0

    def test_diff_head_mode(self, simple_tree, capture_out, tmp_path):
        self._create_baseline(simple_tree, tmp_path, "v1.0", capture_out)
        args = make_args(baseline1="v1.0", baseline2="HEAD")
        result = capture_out(lambda: cmd_diff(simple_tree, args))
        assert result["ok"] is True
        assert result["target"]["name"] == "HEAD"

    def test_diff_not_found(self, simple_tree, capture_out, tmp_path):
        for doc in simple_tree:
            doc.path = str(tmp_path / doc.prefix.lower())
        args = make_args(baseline1="nonexist", baseline2="HEAD")
        result = capture_out(lambda: cmd_diff(simple_tree, args))
        assert result["ok"] is False
