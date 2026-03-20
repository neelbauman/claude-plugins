"""Phase 3: チェーン・コンテキスト・関連ファイル照会のテスト。"""
from __future__ import annotations

import pytest

from helpers import make_item, make_link, make_doc, make_tree, make_args

from _trace_query.chain import (
    _find_items_by_file,
    _trace_up,
    _trace_down,
    cmd_chain,
    cmd_context,
    cmd_related_files,
)
from _common import build_link_index


# =========================================================================
# _find_items_by_file
# =========================================================================

class TestFindItemsByFile:
    def test_exact_path(self, simple_tree):
        results = _find_items_by_file(simple_tree, "src/auth.py")
        uids = [str(item.uid) for item, _ in results]
        assert "IMPL001" in uids

    def test_suffix_match(self, simple_tree):
        """ファイル名のサフィックスでマッチ。"""
        results = _find_items_by_file(simple_tree, "auth.py")
        uids = [str(item.uid) for item, _ in results]
        assert "IMPL001" in uids

    def test_not_found(self, simple_tree):
        results = _find_items_by_file(simple_tree, "nonexistent.py")
        assert len(results) == 0

    def test_backslash_normalization(self, simple_tree):
        """Windowsパスの正規化。"""
        results = _find_items_by_file(simple_tree, "src\\auth.py")
        uids = [str(item.uid) for item, _ in results]
        assert "IMPL001" in uids


# =========================================================================
# _trace_up / _trace_down
# =========================================================================

class TestTraceUp:
    def test_basic(self, simple_tree):
        _, parents_idx = build_link_index(simple_tree)
        result = []
        _trace_up("SPEC001", parents_idx, result, visited=set())
        uids = [e["uid"] for e in result]
        assert "REQ001" in uids

    def test_depth_limit(self):
        """depth > 10 で停止する。"""
        # Create a chain of 15 items
        items = []
        docs = []
        for i in range(15):
            uid = f"X{i:03d}"
            links = [make_link(f"X{i - 1:03d}")] if i > 0 else []
            items.append(make_item(uid, links=links, stamp_value=f"s{i}"))
        doc = make_doc("X", items=items)
        tree = make_tree([doc])
        _, parents_idx = build_link_index(tree)
        result = []
        _trace_up("X014", parents_idx, result, visited=set())
        # Should not trace all 14 levels due to depth limit of 10
        assert len(result) <= 11


class TestTraceDown:
    def test_basic(self, simple_tree):
        children_idx, _ = build_link_index(simple_tree)
        result = []
        _trace_down("REQ001", children_idx, result, visited=set())
        uids = [e["uid"] for e in result]
        assert "SPEC001" in uids

    def test_cycle_prevention(self):
        a = make_item("A001", links=[make_link("B001")], stamp_value="sa")
        b = make_item("B001", links=[make_link("A001")], stamp_value="sb")
        tree = make_tree([make_doc("X", items=[a, b])])
        children_idx, _ = build_link_index(tree)
        result = []
        _trace_down("A001", children_idx, result, visited=set())
        assert isinstance(result, list)  # No infinite loop


# =========================================================================
# cmd_chain
# =========================================================================

class TestCmdChain:
    def test_by_uid(self, simple_tree, capture_out):
        args = make_args(uid="SPEC001", file=None)
        result = capture_out(lambda: cmd_chain(simple_tree, args))
        assert result["ok"] is True
        assert result["action"] == "chain"
        assert result["mode"] == "by_uid"
        assert len(result["upstream"]) >= 1
        assert len(result["downstream"]) >= 1

    def test_by_file(self, simple_tree, capture_out):
        args = make_args(uid=None, file="src/auth.py")
        result = capture_out(lambda: cmd_chain(simple_tree, args))
        assert result["ok"] is True
        assert result["mode"] == "by_file"
        assert result["matched_count"] >= 1

    def test_uid_not_found(self, simple_tree, capture_out):
        args = make_args(uid="NONEXIST", file=None)
        result = capture_out(lambda: cmd_chain(simple_tree, args))
        assert result["ok"] is False

    def test_file_not_found(self, simple_tree, capture_out):
        args = make_args(uid=None, file="nonexistent.py")
        result = capture_out(lambda: cmd_chain(simple_tree, args))
        assert result["ok"] is False

    def test_no_uid_no_file(self, simple_tree, capture_out):
        args = make_args(uid=None, file=None)
        result = capture_out(lambda: cmd_chain(simple_tree, args))
        assert result["ok"] is False


# =========================================================================
# cmd_context
# =========================================================================

class TestCmdContext:
    def test_all_fields(self, simple_tree, capture_out):
        args = make_args(uid="SPEC001")
        result = capture_out(lambda: cmd_context(simple_tree, args))
        assert result["ok"] is True
        assert result["action"] == "context"
        assert result["target"]["uid"] == "SPEC001"
        assert "upstream" in result
        assert "downstream" in result
        assert "related_files" in result
        assert "health" in result

    def test_upstream_has_req(self, simple_tree, capture_out):
        args = make_args(uid="SPEC001")
        result = capture_out(lambda: cmd_context(simple_tree, args))
        upstream_uids = [e["uid"] for e in result["upstream"]]
        assert "REQ001" in upstream_uids

    def test_downstream_has_impl_tst(self, simple_tree, capture_out):
        args = make_args(uid="SPEC001")
        result = capture_out(lambda: cmd_context(simple_tree, args))
        downstream_uids = [e["uid"] for e in result["downstream"]]
        assert "IMPL001" in downstream_uids
        assert "TST001" in downstream_uids

    def test_related_files(self, simple_tree, capture_out):
        args = make_args(uid="SPEC001")
        result = capture_out(lambda: cmd_context(simple_tree, args))
        files = result["related_files"]
        assert "src/auth.py" in files["source"]
        assert "tests/test_auth.py" in files["test"]

    def test_health_no_suspects(self, simple_tree, capture_out):
        args = make_args(uid="SPEC001")
        result = capture_out(lambda: cmd_context(simple_tree, args))
        assert result["health"]["suspect_count"] == 0

    def test_health_with_suspects(self, suspect_tree, capture_out):
        args = make_args(uid="SPEC001")
        result = capture_out(lambda: cmd_context(suspect_tree, args))
        assert result["health"]["suspect_count"] >= 1

    def test_gherkin_present(self, simple_tree, capture_out):
        args = make_args(uid="SPEC001")
        result = capture_out(lambda: cmd_context(simple_tree, args))
        assert result["target"]["gherkin"] is not None
        assert "Given" in result["target"]["gherkin"]

    def test_not_found(self, simple_tree, capture_out):
        args = make_args(uid="NONEXIST")
        result = capture_out(lambda: cmd_context(simple_tree, args))
        assert result["ok"] is False


# =========================================================================
# cmd_related_files
# =========================================================================

class TestCmdRelatedFiles:
    def test_by_uid(self, simple_tree, capture_out):
        args = make_args(uid="SPEC001", file=None)
        result = capture_out(lambda: cmd_related_files(simple_tree, args))
        assert result["ok"] is True
        assert result["action"] == "related-files"
        assert result["mode"] == "by_uid"
        # Should contain IMPL and TST files
        all_files = []
        for files in result["files"].values():
            all_files.extend(files)
        assert "src/auth.py" in all_files

    def test_by_file(self, simple_tree, capture_out):
        args = make_args(uid=None, file="src/auth.py")
        result = capture_out(lambda: cmd_related_files(simple_tree, args))
        assert result["ok"] is True
        assert result["mode"] == "by_file"
        assert len(result["matched_uids"]) >= 1
