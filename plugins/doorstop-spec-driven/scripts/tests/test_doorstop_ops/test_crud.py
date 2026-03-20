"""Phase 2: CRUD・リンク操作コマンドのテスト。"""
from __future__ import annotations

import json

import pytest

from helpers import make_item, make_link, make_doc, make_tree, make_args

from _doorstop_ops.crud import cmd_add, cmd_update, cmd_reorder, cmd_link, cmd_unlink


# =========================================================================
# cmd_add
# =========================================================================

class TestCmdAdd:
    def _base_args(self, **overrides):
        defaults = dict(
            document="SPEC", text="新しい仕様", header=None, group=None,
            level=None, insert=None, ref=None, references=None,
            priority=None, test_level=None, non_normative=False,
            derived=False, gherkin=None, links=None,
        )
        defaults.update(overrides)
        return make_args(**defaults)

    def test_basic(self, simple_tree, capture_out):
        args = self._base_args(text="テスト仕様")
        result = capture_out(lambda: cmd_add(simple_tree, args))
        assert result["ok"] is True
        assert result["action"] == "add"
        assert result["item"]["text"] == "テスト仕様"

    def test_with_header(self, simple_tree, capture_out):
        args = self._base_args(text="内容", header="見出し")
        result = capture_out(lambda: cmd_add(simple_tree, args))
        assert result["item"]["header"] == "見出し"

    def test_with_group(self, simple_tree, capture_out):
        args = self._base_args(text="内容", group="AUTH,CACHE")
        result = capture_out(lambda: cmd_add(simple_tree, args))
        assert result["item"]["groups"] == ["AUTH", "CACHE"]

    def test_with_ref(self, simple_tree, capture_out):
        args = self._base_args(text="内容", ref="src/new.py")
        result = capture_out(lambda: cmd_add(simple_tree, args))
        # ref is set on the item
        assert result["ok"] is True

    def test_with_references_json(self, simple_tree, capture_out):
        refs = [{"path": "src/mod.py", "type": "file"}]
        args = self._base_args(text="内容", references=json.dumps(refs))
        result = capture_out(lambda: cmd_add(simple_tree, args))
        assert result["ok"] is True

    def test_with_priority(self, simple_tree, capture_out):
        args = self._base_args(text="内容", priority="critical")
        result = capture_out(lambda: cmd_add(simple_tree, args))
        assert result["item"]["priority"] == "critical"

    def test_with_test_level(self, simple_tree, capture_out):
        args = self._base_args(document="TST", text="テスト", test_level="unit")
        result = capture_out(lambda: cmd_add(simple_tree, args))
        assert result["ok"] is True

    def test_non_normative(self, simple_tree, capture_out):
        args = self._base_args(text="見出し", non_normative=True)
        result = capture_out(lambda: cmd_add(simple_tree, args))
        assert result["item"]["normative"] is False

    def test_derived(self, simple_tree, capture_out):
        args = self._base_args(text="派生要求")
        args.derived = True
        result = capture_out(lambda: cmd_add(simple_tree, args))
        assert result["ok"] is True

    def test_with_gherkin(self, simple_tree, capture_out):
        args = self._base_args(text="仕様", gherkin="Given X\nWhen Y\nThen Z")
        result = capture_out(lambda: cmd_add(simple_tree, args))
        assert result["ok"] is True

    def test_with_links(self, simple_tree, capture_out):
        args = self._base_args(text="仕様", links=["REQ001"])
        result = capture_out(lambda: cmd_add(simple_tree, args))
        assert result["ok"] is True
        assert "REQ001" in result["item"]["links"]

    def test_with_level(self, simple_tree, capture_out):
        args = self._base_args(text="仕様", level="2.1")
        result = capture_out(lambda: cmd_add(simple_tree, args))
        assert result["ok"] is True

    def test_with_insert(self, simple_tree, capture_out):
        args = self._base_args(text="挿入仕様", insert="1.5")
        result = capture_out(lambda: cmd_add(simple_tree, args))
        assert result["ok"] is True


# =========================================================================
# cmd_update
# =========================================================================

class TestCmdUpdate:
    def _base_args(self, uid, **overrides):
        defaults = dict(
            uid=uid, text=None, header=None, group=None, ref=None,
            references=None, priority=None, test_level=None,
            set_normative=False, set_non_normative=False, gherkin=None,
        )
        defaults.update(overrides)
        return make_args(**defaults)

    def test_update_text(self, simple_tree, capture_out):
        args = self._base_args("REQ001", text="更新されたテキスト")
        result = capture_out(lambda: cmd_update(simple_tree, args))
        assert result["ok"] is True
        assert result["action"] == "update"
        assert result["item"]["text"] == "更新されたテキスト"

    def test_update_header(self, simple_tree, capture_out):
        args = self._base_args("REQ001", header="新しいヘッダー")
        result = capture_out(lambda: cmd_update(simple_tree, args))
        assert result["item"]["header"] == "新しいヘッダー"

    def test_update_group(self, simple_tree, capture_out):
        args = self._base_args("REQ001", group="NEW_GROUP")
        result = capture_out(lambda: cmd_update(simple_tree, args))
        assert result["item"]["groups"] == ["NEW_GROUP"]

    def test_update_priority(self, simple_tree, capture_out):
        args = self._base_args("REQ001", priority="critical")
        result = capture_out(lambda: cmd_update(simple_tree, args))
        assert result["item"]["priority"] == "critical"

    def test_set_non_normative(self, simple_tree, capture_out):
        args = self._base_args("REQ001", set_non_normative=True)
        result = capture_out(lambda: cmd_update(simple_tree, args))
        assert result["item"]["normative"] is False

    def test_set_normative(self, simple_tree, capture_out):
        args = self._base_args("REQ001", set_normative=True)
        result = capture_out(lambda: cmd_update(simple_tree, args))
        assert result["item"]["normative"] is True

    def test_update_gherkin(self, simple_tree, capture_out):
        args = self._base_args("SPEC001", gherkin="Given A\nWhen B\nThen C")
        result = capture_out(lambda: cmd_update(simple_tree, args))
        assert "gherkin" in result["item"]

    def test_none_fields_no_change(self, simple_tree, capture_out):
        """全フィールドNoneの場合、元の値が維持される。"""
        args = self._base_args("REQ001")
        result = capture_out(lambda: cmd_update(simple_tree, args))
        assert result["ok"] is True
        assert result["item"]["text"] == "ユーザー認証機能"


# =========================================================================
# cmd_reorder
# =========================================================================

class TestCmdReorder:
    def test_changes_level(self, simple_tree, capture_out):
        args = make_args(uid="REQ001", level="2.0")
        result = capture_out(lambda: cmd_reorder(simple_tree, args))
        assert result["ok"] is True
        assert result["action"] == "reorder"
        assert result["old_level"] == "1.0"
        assert result["new_level"] == "2.0"


# =========================================================================
# cmd_link
# =========================================================================

class TestCmdLink:
    def test_adds_and_clears(self, simple_tree, capture_out):
        args = make_args(child="SPEC001", parent="REQ002")
        result = capture_out(lambda: cmd_link(simple_tree, args))
        assert result["ok"] is True
        assert result["action"] == "link"
        assert result["child"] == "SPEC001"
        assert result["parent"] == "REQ002"
        assert "REQ002" in result["item"]["links"]


# =========================================================================
# cmd_unlink
# =========================================================================

class TestCmdUnlink:
    def test_unlink_existing(self, simple_tree, capture_out):
        args = make_args(child="SPEC001", parent="REQ001")
        result = capture_out(lambda: cmd_unlink(simple_tree, args))
        assert result["ok"] is True
        assert result["action"] == "unlink"
        assert result["removed_parent"] == "REQ001"

    def test_unlink_nonexistent(self, simple_tree, capture_out):
        args = make_args(child="SPEC001", parent="NONEXIST")
        result = capture_out(lambda: cmd_unlink(simple_tree, args))
        assert result["ok"] is False
