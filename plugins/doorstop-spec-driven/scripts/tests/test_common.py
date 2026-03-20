"""Phase 1: _common.py の単体テスト。

全コマンドモジュールが依存する基盤ユーティリティのテスト。
"""
from __future__ import annotations

import pytest

from helpers import make_item, make_link, make_doc, make_tree

from _common import (
    out,
    truncate_text,
    get_groups,
    get_ref,
    get_references,
    get_references_display,
    is_derived,
    is_normative,
    find_item,
    find_doc_prefix,
    is_suspect,
    build_link_index,
    get_priority,
    item_summary,
    item_to_dict,
    build_doc_file_map,
)


# =========================================================================
# out()
# =========================================================================

class TestOut:
    def test_ok_exits_0(self, capture_out):
        result = capture_out(lambda: out({"ok": True, "msg": "hello"}))
        assert result["ok"] is True
        assert result["msg"] == "hello"

    def test_error_exits_1(self, monkeypatch, capsys):
        exit_codes = []
        monkeypatch.setattr("sys.exit", lambda c: (_ for _ in ()).throw(SystemExit(c)))

        with pytest.raises(SystemExit) as exc:
            out({"ok": False, "error": "fail"})
        assert exc.value.code == 1

    def test_default_ok_exits_0(self, monkeypatch, capsys):
        monkeypatch.setattr("sys.exit", lambda c: (_ for _ in ()).throw(SystemExit(c)))
        with pytest.raises(SystemExit) as exc:
            out({"data": 42})
        assert exc.value.code == 0

    def test_json_format(self, capture_out):
        result = capture_out(lambda: out({"ok": True, "日本語": "テスト"}))
        assert result["日本語"] == "テスト"


# =========================================================================
# truncate_text()
# =========================================================================

class TestTruncateText:
    def test_short_text(self):
        assert truncate_text("hello", 10) == "hello"

    def test_exact_limit(self):
        assert truncate_text("12345", 5) == "12345"

    def test_long_text(self):
        result = truncate_text("abcdefghij", 5)
        assert result == "abcde...[TRUNCATED]"

    def test_empty(self):
        assert truncate_text("", 10) == ""


# =========================================================================
# get_groups()
# =========================================================================

class TestGetGroups:
    def test_list(self):
        item = make_item("X001", groups=["AUTH", "CACHE"])
        assert get_groups(item) == ["AUTH", "CACHE"]

    def test_empty_list_returns_default(self):
        item = make_item("X001", groups=[])
        assert get_groups(item, default=["未分類"]) == ["未分類"]

    def test_empty_list_no_default(self):
        item = make_item("X001", groups=[])
        assert get_groups(item) == []

    def test_string(self):
        item = make_item("X001")
        item._attrs["groups"] = "AUTH, CACHE"
        assert get_groups(item) == ["AUTH", "CACHE"]

    def test_none(self):
        item = make_item("X001")
        item._attrs["groups"] = None
        assert get_groups(item) == []

    def test_default_none(self):
        item = make_item("X001")
        item._attrs["groups"] = None
        assert get_groups(item, default=["X"]) == ["X"]

    def test_attribute_error(self):
        """get() メソッドがないオブジェクト。"""

        class NoGet:
            pass

        assert get_groups(NoGet()) == []


# =========================================================================
# get_ref()
# =========================================================================

class TestGetRef:
    def test_present(self):
        item = make_item("X001", ref="src/main.py")
        assert get_ref(item) == "src/main.py"

    def test_empty(self):
        item = make_item("X001", ref="")
        assert get_ref(item) == ""

    def test_attribute_error(self):
        class NoRef:
            pass

        assert get_ref(NoRef()) == ""


# =========================================================================
# get_references()
# =========================================================================

class TestGetReferences:
    def test_references_list(self):
        refs = [{"path": "src/a.py", "type": "file"}]
        item = make_item("X001", references=refs)
        assert get_references(item) == refs

    def test_empty_fallback_to_ref(self):
        item = make_item("X001", ref="src/b.py")
        result = get_references(item)
        assert result == [{"path": "src/b.py", "type": "file"}]

    def test_no_ref(self):
        item = make_item("X001")
        assert get_references(item) == []


# =========================================================================
# get_references_display()
# =========================================================================

class TestGetReferencesDisplay:
    def test_file_type(self):
        item = make_item("X001", references=[{"path": "src/a.py", "type": "file"}])
        assert get_references_display(item) == "src/a.py"

    def test_non_file_type(self):
        item = make_item("X001", references=[{"path": "http://example.com", "type": "url"}])
        assert get_references_display(item) == "http://example.com (url)"

    def test_empty(self):
        item = make_item("X001")
        assert get_references_display(item) == ""

    def test_multiple(self):
        item = make_item("X001", references=[
            {"path": "src/a.py", "type": "file"},
            {"path": "docs/spec.md", "type": "doc"},
        ])
        assert get_references_display(item) == "src/a.py, docs/spec.md (doc)"


# =========================================================================
# is_derived()
# =========================================================================

class TestIsDerived:
    def test_true(self):
        item = make_item("X001", derived=True)
        assert is_derived(item) is True

    def test_false(self):
        item = make_item("X001", derived=False)
        assert is_derived(item) is False

    def test_missing(self):
        class NoDerived:
            pass

        assert is_derived(NoDerived()) is False


# =========================================================================
# is_normative()
# =========================================================================

class TestIsNormative:
    def test_default_true(self):
        item = make_item("X001", normative=True)
        assert is_normative(item) is True

    def test_explicit_false(self):
        item = make_item("X001", normative=False)
        assert is_normative(item) is False

    def test_string_false(self):
        item = make_item("X001")
        item._attrs["normative"] = "false"
        assert is_normative(item) is False

    def test_missing(self):
        class NoNormative:
            pass

        assert is_normative(NoNormative()) is True


# =========================================================================
# find_item()
# =========================================================================

class TestFindItem:
    def test_active_item(self, simple_tree):
        item = find_item(simple_tree, "REQ001")
        assert str(item.uid) == "REQ001"

    def test_returns_none(self, simple_tree):
        assert find_item(simple_tree, "NONEXIST") is None

    def test_inactive_excluded(self):
        inactive = make_item("REQ001", active=False)
        doc = make_doc("REQ", items=[inactive])
        tree = make_tree([doc])
        assert find_item(tree, "REQ001", include_inactive=False) is None

    def test_inactive_included(self):
        inactive = make_item("REQ001", active=False)
        doc = make_doc("REQ", items=[inactive])
        tree = make_tree([doc])
        item = find_item(tree, "REQ001", include_inactive=True)
        assert str(item.uid) == "REQ001"


# =========================================================================
# find_doc_prefix()
# =========================================================================

class TestFindDocPrefix:
    def test_normal(self, simple_tree):
        item = find_item(simple_tree, "SPEC001")
        assert find_doc_prefix(simple_tree, item) == "SPEC"

    def test_inactive_item(self):
        inactive = make_item("REQ001", active=False)
        doc = make_doc("REQ", items=[inactive])
        tree = make_tree([doc])
        assert find_doc_prefix(tree, inactive) == "REQ"


# =========================================================================
# is_suspect()
# =========================================================================

class TestIsSuspect:
    def test_stamp_mismatch(self, suspect_tree):
        spec1 = find_item(suspect_tree, "SPEC001")
        assert is_suspect(spec1, suspect_tree) is True

    def test_stamp_match(self, suspect_tree):
        spec2 = find_item(suspect_tree, "SPEC002")
        assert is_suspect(spec2, suspect_tree) is False

    def test_no_stamp(self):
        req = make_item("REQ001", stamp_value="s1")
        spec = make_item("SPEC001", links=[make_link("REQ001", stamp=None)])
        tree = make_tree([
            make_doc("REQ", items=[req]),
            make_doc("SPEC", parent="REQ", items=[spec]),
        ])
        assert is_suspect(spec, tree) is False

    def test_empty_stamp(self):
        req = make_item("REQ001", stamp_value="s1")
        spec = make_item("SPEC001", links=[make_link("REQ001", stamp="")])
        tree = make_tree([
            make_doc("REQ", items=[req]),
            make_doc("SPEC", parent="REQ", items=[spec]),
        ])
        assert is_suspect(spec, tree) is False

    def test_parent_not_found(self):
        spec = make_item("SPEC001", links=[make_link("NONEXIST", stamp="old")])
        tree = make_tree([make_doc("SPEC", items=[spec])])
        assert is_suspect(spec, tree) is False

    def test_no_links(self):
        item = make_item("REQ001")
        tree = make_tree([make_doc("REQ", items=[item])])
        assert is_suspect(item, tree) is False


# =========================================================================
# build_link_index()
# =========================================================================

class TestBuildLinkIndex:
    def test_basic(self, simple_tree):
        children, parents = build_link_index(simple_tree)
        # REQ001 should have SPEC001 as child
        child_uids = [str(c[0].uid) for c in children.get("REQ001", [])]
        assert "SPEC001" in child_uids
        # SPEC001 should have REQ001 as parent
        parent_uids = [str(p[0].uid) for p in parents.get("SPEC001", [])]
        assert "REQ001" in parent_uids

    def test_excludes_inactive(self):
        req = make_item("REQ001", stamp_value="s1")
        spec = make_item("SPEC001", links=[make_link("REQ001")], active=False)
        tree = make_tree([
            make_doc("REQ", items=[req]),
            make_doc("SPEC", parent="REQ", items=[spec]),
        ])
        children, parents = build_link_index(tree, include_inactive=False)
        assert "REQ001" not in children

    def test_includes_inactive(self):
        req = make_item("REQ001", stamp_value="s1")
        spec = make_item("SPEC001", links=[make_link("REQ001")], active=False)
        tree = make_tree([
            make_doc("REQ", items=[req]),
            make_doc("SPEC", parent="REQ", items=[spec]),
        ])
        children, parents = build_link_index(tree, include_inactive=True)
        child_uids = [str(c[0].uid) for c in children.get("REQ001", [])]
        assert "SPEC001" in child_uids


# =========================================================================
# get_priority()
# =========================================================================

class TestGetPriority:
    @pytest.mark.parametrize("val", ["critical", "high", "medium", "low", "none", "done"])
    def test_valid_values(self, val):
        item = make_item("X001", priority=val)
        assert get_priority(item) == val

    def test_default_medium(self):
        item = make_item("X001")
        item._attrs["priority"] = None
        assert get_priority(item) == "medium"

    def test_invalid_value(self):
        item = make_item("X001")
        item._attrs["priority"] = "urgent"
        assert get_priority(item) == "medium"


# =========================================================================
# item_summary()
# =========================================================================

class TestItemSummary:
    def test_all_fields(self, simple_tree):
        item = find_item(simple_tree, "REQ001")
        d = item_summary(item, prefix="REQ", tree=simple_tree)
        assert d["uid"] == "REQ001"
        assert d["prefix"] == "REQ"
        assert d["groups"] == ["AUTH"]
        assert d["priority"] == "high"
        assert d["header"] == "認証"
        assert "ユーザー認証機能" in d["text"]
        assert d["normative"] is True
        assert d["derived"] is False
        assert "suspect" in d

    def test_without_tree_no_suspect(self):
        item = make_item("X001", text="test")
        d = item_summary(item, prefix="REQ")
        assert "suspect" not in d


# =========================================================================
# item_to_dict()
# =========================================================================

class TestItemToDict:
    def test_all_fields(self, simple_tree):
        item = find_item(simple_tree, "SPEC001")
        d = item_to_dict(item, doc_prefix="SPEC", tree=simple_tree)
        assert d["uid"] == "SPEC001"
        assert d["prefix"] == "SPEC"
        assert d["level"] == "1.0"
        assert d["active"] is True
        assert d["reviewed"] is False
        assert "links" in d
        assert "suspect" in d

    def test_with_gherkin(self, simple_tree):
        item = find_item(simple_tree, "SPEC001")
        d = item_to_dict(item, doc_prefix="SPEC")
        assert "gherkin" in d
        assert "Given" in d["gherkin"]

    def test_without_gherkin(self):
        item = make_item("X001", text="test")
        d = item_to_dict(item)
        assert "gherkin" not in d


# =========================================================================
# build_doc_file_map()
# =========================================================================

class TestBuildDocFileMap:
    def test_mapping(self, simple_tree):
        file_map = build_doc_file_map(simple_tree, "/fake")
        # REQ001.yml should be in the map
        found = any("REQ001" in v for v in file_map.values())
        assert found

    def test_both_extensions(self, simple_tree):
        file_map = build_doc_file_map(simple_tree, "/fake")
        # Both .yml and .yaml should be generated
        yml_keys = [k for k in file_map if k.endswith(".yml")]
        yaml_keys = [k for k in file_map if k.endswith(".yaml")]
        assert len(yml_keys) > 0
        assert len(yaml_keys) > 0
