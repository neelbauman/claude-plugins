"""Phase 3: 品質・バックログ照会コマンドのテスト。"""
from __future__ import annotations

import pytest

from helpers import make_item, make_link, make_doc, make_tree, make_args

from _trace_query.quality import cmd_suspects, cmd_backlog, _suggest_action


# =========================================================================
# _suggest_action
# =========================================================================

class TestSuggestAction:
    def test_impl(self):
        item = make_item("IMPL001", text="実装",
                         references=[{"path": "src/main.py", "type": "file"}])
        action = _suggest_action(item, "IMPL")
        assert "IMPL001" in action
        assert "実装を確認" in action
        assert "src/main.py" in action
        assert "doorstop clear" in action

    def test_tst(self):
        item = make_item("TST001", text="テスト",
                         references=[{"path": "tests/test_main.py", "type": "file"}])
        action = _suggest_action(item, "TST")
        assert "テストを確認" in action

    def test_spec(self):
        item = make_item("SPEC001", text="仕様")
        action = _suggest_action(item, "SPEC")
        assert "仕様が親REQの変更と整合するか確認" in action

    def test_other(self):
        item = make_item("REQ001", text="要件")
        action = _suggest_action(item, "REQ")
        assert "確認" in action
        assert "doorstop clear" in action

    def test_no_references(self):
        item = make_item("IMPL001", text="実装")
        action = _suggest_action(item, "IMPL")
        assert "IMPL001" in action
        assert "doorstop clear" in action


# =========================================================================
# cmd_suspects
# =========================================================================

class TestCmdSuspects:
    def test_all(self, suspect_tree, capture_out):
        args = make_args(group=None)
        result = capture_out(lambda: cmd_suspects(suspect_tree, args))
        assert result["ok"] is True
        assert result["action"] == "suspects"
        assert result["count"] >= 1
        # SPEC001 should be in the suspect list
        uids = [s["uid"] for s in result["items"]]
        assert "SPEC001" in uids

    def test_suspect_links_detail(self, suspect_tree, capture_out):
        args = make_args(group=None)
        result = capture_out(lambda: cmd_suspects(suspect_tree, args))
        spec001 = next(s for s in result["items"] if s["uid"] == "SPEC001")
        assert len(spec001["suspect_links"]) >= 1
        assert spec001["suspect_links"][0]["parent_uid"] == "REQ001"

    def test_group_filter(self, capture_out):
        req = make_item("REQ001", text="要件", groups=["AUTH"], stamp_value="new")
        spec_auth = make_item("SPEC001", text="仕様A", groups=["AUTH"],
                              links=[make_link("REQ001", stamp="old")])
        spec_cache = make_item("SPEC002", text="仕様B", groups=["CACHE"],
                               links=[make_link("REQ001", stamp="old")])
        tree = make_tree([
            make_doc("REQ", items=[req]),
            make_doc("SPEC", parent="REQ", items=[spec_auth, spec_cache]),
        ])
        args = make_args(group="AUTH")
        result = capture_out(lambda: cmd_suspects(tree, args))
        uids = [s["uid"] for s in result["items"]]
        assert "SPEC001" in uids
        assert "SPEC002" not in uids

    def test_none(self, simple_tree, capture_out):
        args = make_args(group=None)
        result = capture_out(lambda: cmd_suspects(simple_tree, args))
        assert result["count"] == 0


# =========================================================================
# cmd_backlog
# =========================================================================

class TestCmdBacklog:
    def test_priority_order(self, capture_out):
        items = [
            make_item("REQ001", text="低", priority="low"),
            make_item("REQ002", text="高", priority="high"),
            make_item("REQ003", text="クリティカル", priority="critical"),
        ]
        tree = make_tree([make_doc("REQ", items=items)])
        args = make_args(document=None, group=None, all_docs=False)
        result = capture_out(lambda: cmd_backlog(tree, args))
        assert result["ok"] is True
        uids = [i["uid"] for i in result["items"]]
        assert uids == ["REQ003", "REQ002", "REQ001"]

    def test_default_req_only(self, simple_tree, capture_out):
        args = make_args(document=None, group=None, all_docs=False)
        result = capture_out(lambda: cmd_backlog(simple_tree, args))
        assert all(i["prefix"] == "REQ" for i in result["items"])

    def test_all_docs(self, simple_tree, capture_out):
        args = make_args(document=None, group=None, all_docs=True)
        result = capture_out(lambda: cmd_backlog(simple_tree, args))
        prefixes = {i["prefix"] for i in result["items"]}
        assert len(prefixes) > 1

    def test_group_filter(self, simple_tree, capture_out):
        args = make_args(document=None, group="AUTH", all_docs=False)
        result = capture_out(lambda: cmd_backlog(simple_tree, args))
        assert all("AUTH" in i["groups"] for i in result["items"])

    def test_priority_summary(self, simple_tree, capture_out):
        args = make_args(document=None, group=None, all_docs=False)
        result = capture_out(lambda: cmd_backlog(simple_tree, args))
        assert "priority_summary" in result
        assert "high" in result["priority_summary"]
        assert "medium" in result["priority_summary"]

    def test_document_filter(self, simple_tree, capture_out):
        args = make_args(document="SPEC", group=None, all_docs=False)
        result = capture_out(lambda: cmd_backlog(simple_tree, args))
        assert all(i["prefix"] == "SPEC" for i in result["items"])

    def test_inactive_excluded(self, capture_out):
        active = make_item("REQ001", text="active")
        inactive = make_item("REQ002", text="inactive", active=False)
        tree = make_tree([make_doc("REQ", items=[active, inactive])])
        args = make_args(document=None, group=None, all_docs=False)
        result = capture_out(lambda: cmd_backlog(tree, args))
        uids = [i["uid"] for i in result["items"]]
        assert "REQ001" in uids
        assert "REQ002" not in uids
