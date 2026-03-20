"""Phase 4: impact_analysis.py の単体テスト。"""
from __future__ import annotations

import pytest

from helpers import make_item, make_link, make_doc, make_tree

from impact_analysis import (
    detect_by_uid,
    detect_suspects,
    analyze_impact,
    _trace_upstream,
    _trace_downstream,
    _generate_actions,
    _generate_action_plan,
)
from _common import build_link_index


# =========================================================================
# detect_by_uid
# =========================================================================

class TestDetectByUid:
    def test_existing(self, simple_tree):
        items = detect_by_uid(simple_tree, ["REQ001", "SPEC001"])
        uids = [str(i.uid) for i in items]
        assert "REQ001" in uids
        assert "SPEC001" in uids

    def test_missing_uid_warning(self, simple_tree, capsys):
        items = detect_by_uid(simple_tree, ["NONEXIST"])
        assert len(items) == 0
        captured = capsys.readouterr()
        assert "NONEXIST" in captured.err

    def test_mixed(self, simple_tree, capsys):
        items = detect_by_uid(simple_tree, ["REQ001", "NONEXIST"])
        assert len(items) == 1
        assert str(items[0].uid) == "REQ001"


# =========================================================================
# detect_suspects
# =========================================================================

class TestDetectSuspects:
    def test_returns_parents(self, suspect_tree):
        """suspect の原因（変更された親アイテム）を返す。"""
        suspects = detect_suspects(suspect_tree)
        uids = [str(s.uid) for s in suspects]
        assert "REQ001" in uids

    def test_no_suspects(self, simple_tree):
        suspects = detect_suspects(simple_tree)
        assert len(suspects) == 0


# =========================================================================
# _trace_upstream / _trace_downstream
# =========================================================================

class TestTraceUpstream:
    def test_basic(self, simple_tree):
        _, parents_idx = build_link_index(simple_tree)
        result = []
        _trace_upstream("SPEC001", parents_idx, result, visited=set())
        uids = [e["uid"] for e in result]
        assert "REQ001" in uids

    def test_depth_limit(self):
        items = [make_item(f"X{i:03d}",
                           links=[make_link(f"X{i-1:03d}")] if i > 0 else [],
                           stamp_value=f"s{i}",
                           text=f"item {i}")
                 for i in range(15)]
        tree = make_tree([make_doc("X", items=items)])
        _, parents_idx = build_link_index(tree)
        result = []
        _trace_upstream("X014", parents_idx, result, visited=set())
        assert len(result) <= 11


class TestTraceDownstream:
    def test_basic(self, simple_tree):
        children_idx, _ = build_link_index(simple_tree)
        result = []
        _trace_downstream("REQ001", children_idx, result, visited=set())
        uids = [e["uid"] for e in result]
        assert "SPEC001" in uids

    def test_includes_references(self, simple_tree):
        children_idx, _ = build_link_index(simple_tree)
        result = []
        _trace_downstream("SPEC001", children_idx, result, visited=set())
        for entry in result:
            if entry["prefix"] == "IMPL":
                assert "references" in entry


# =========================================================================
# analyze_impact
# =========================================================================

class TestAnalyzeImpact:
    def test_upstream_downstream(self, simple_tree):
        changed = detect_by_uid(simple_tree, ["SPEC001"])
        results = analyze_impact(simple_tree, changed)
        assert len(results) == 1
        r = results[0]
        assert r["uid"] == "SPEC001"
        assert len(r["upstream"]) >= 1
        assert len(r["downstream"]) >= 1

    def test_suspect_children(self, suspect_tree):
        changed = detect_suspects(suspect_tree)
        results = analyze_impact(suspect_tree, changed)
        assert len(results) >= 1
        r = results[0]
        # REQ001 changed, SPEC001 is suspect child
        suspect_uids = [s["uid"] for s in r["suspect_children"]]
        assert "SPEC001" in suspect_uids

    def test_actions_generation(self, simple_tree):
        changed = detect_by_uid(simple_tree, ["SPEC001"])
        results = analyze_impact(simple_tree, changed)
        r = results[0]
        assert len(r["actions"]) >= 1
        assert any("review" in a or "レビュー" in a for a in r["actions"])

    def test_action_plan_structure(self, simple_tree):
        changed = detect_by_uid(simple_tree, ["SPEC001"])
        results = analyze_impact(simple_tree, changed)
        ap = results[0]["action_plan"]
        assert "review_commands" in ap
        assert "clear_commands" in ap
        assert "files_to_check" in ap
        assert "validation" in ap
        assert len(ap["review_commands"]) >= 1


# =========================================================================
# _generate_actions
# =========================================================================

class TestGenerateActions:
    def test_with_suspect_impl(self):
        item = make_item("SPEC001", text="仕様")
        suspects = [{"uid": "IMPL001", "prefix": "IMPL",
                     "groups": [], "text": "実装", "ref": "src/x.py"}]
        actions = _generate_actions(item, "SPEC", [], suspects)
        assert any("review" in a or "レビュー" in a for a in actions)
        assert any("IMPL001" in a and "実装を確認" in a for a in actions)

    def test_with_suspect_tst(self):
        item = make_item("SPEC001", text="仕様")
        suspects = [{"uid": "TST001", "prefix": "TST",
                     "groups": [], "text": "テスト", "ref": ""}]
        actions = _generate_actions(item, "SPEC", [], suspects)
        assert any("TST001" in a and "テストを確認" in a for a in actions)

    def test_non_suspect_downstream(self):
        item = make_item("SPEC001", text="仕様")
        downstream = [{"uid": "IMPL001", "prefix": "IMPL",
                       "groups": [], "text": "実装", "ref": "src/x.py",
                       "references": [], "depth": 0}]
        actions = _generate_actions(item, "SPEC", downstream, [])
        assert any("IMPL001" in a and "整合" in a for a in actions)


# =========================================================================
# _generate_action_plan
# =========================================================================

class TestGenerateActionPlan:
    def test_structure(self):
        item = make_item("SPEC001", text="仕様",
                         references=[{"path": "docs/spec.md", "type": "file"}])
        suspects = [{"uid": "IMPL001", "prefix": "IMPL",
                     "groups": [], "text": "実装", "ref": "src/x.py",
                     "references": [{"path": "src/x.py", "type": "file"}]}]
        downstream = []
        ap = _generate_action_plan(item, "SPEC", downstream, suspects, ".")
        assert "review_commands" in ap
        assert "clear_commands" in ap
        assert "docs/spec.md" in ap["files_to_check"]
        assert "src/x.py" in ap["files_to_check"]

    def test_no_suspects(self):
        item = make_item("SPEC001", text="仕様")
        ap = _generate_action_plan(item, "SPEC", [], [], ".")
        assert len(ap["clear_commands"]) == 0
        assert len(ap["review_commands"]) == 1
