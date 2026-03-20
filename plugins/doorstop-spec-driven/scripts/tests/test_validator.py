"""Phase 4: validator.py の単体テスト。"""
from __future__ import annotations

import pytest

from helpers import make_item, make_link, make_doc, make_tree

from validator import validate_tree, build_traceability_matrix, compute_coverage


# =========================================================================
# validate_tree
# =========================================================================

class TestValidateTree:
    def test_empty_text_warning(self):
        item = make_item("REQ001", text="")
        tree = make_tree([make_doc("REQ", items=[item])])
        issues = validate_tree(tree)
        assert any("テキストが空" in w for w in issues["warnings"])

    def test_non_empty_text_no_warning(self):
        item = make_item("REQ001", text="要件")
        tree = make_tree([make_doc("REQ", items=[item])])
        issues = validate_tree(tree)
        assert not any("テキストが空" in w for w in issues["warnings"])

    def test_inactive_skipped(self):
        item = make_item("REQ001", text="", active=False)
        tree = make_tree([make_doc("REQ", items=[item])])
        issues = validate_tree(tree)
        assert not any("テキストが空" in w for w in issues["warnings"])

    def test_non_normative_skipped(self):
        item = make_item("REQ001", text="", normative=False)
        tree = make_tree([make_doc("REQ", items=[item])])
        issues = validate_tree(tree)
        assert not any("テキストが空" in w for w in issues["warnings"])

    def test_missing_parent_doc_error(self):
        spec = make_item("SPEC001", text="仕様")
        tree = make_tree([make_doc("SPEC", parent="REQ", items=[spec])])
        issues = validate_tree(tree)
        assert any("親ドキュメント" in e and "見つかりません" in e for e in issues["errors"])

    def test_missing_parent_link_warning(self):
        req = make_item("REQ001", text="要件")
        spec = make_item("SPEC001", text="仕様")  # no links
        tree = make_tree([
            make_doc("REQ", items=[req]),
            make_doc("SPEC", parent="REQ", items=[spec]),
        ])
        issues = validate_tree(tree)
        assert any("リンクがありません" in w for w in issues["warnings"])

    def test_broken_link_error(self):
        req = make_item("REQ001", text="要件")
        spec = make_item("SPEC001", text="仕様",
                         links=[make_link("REQ999")])
        tree = make_tree([
            make_doc("REQ", items=[req]),
            make_doc("SPEC", parent="REQ", items=[spec]),
        ])
        issues = validate_tree(tree)
        assert any("REQ999" in e and "存在しません" in e for e in issues["errors"])

    def test_cross_group_link_warning(self):
        req = make_item("REQ001", text="要件", groups=["AUTH"])
        spec = make_item("SPEC001", text="仕様", groups=["CACHE"],
                         links=[make_link("REQ001")])
        tree = make_tree([
            make_doc("REQ", items=[req]),
            make_doc("SPEC", parent="REQ", items=[spec]),
        ])
        issues = validate_tree(tree)
        assert any("クロスグループリンク" in w for w in issues["warnings"])

    def test_same_group_no_cross_warning(self):
        req = make_item("REQ001", text="要件", groups=["AUTH"])
        spec = make_item("SPEC001", text="仕様", groups=["AUTH"],
                         links=[make_link("REQ001")])
        tree = make_tree([
            make_doc("REQ", items=[req]),
            make_doc("SPEC", parent="REQ", items=[spec]),
        ])
        issues = validate_tree(tree)
        assert not any("クロスグループリンク" in w for w in issues["warnings"])

    def test_strict_uncovered_parent_warning(self):
        req1 = make_item("REQ001", text="要件1")
        req2 = make_item("REQ002", text="要件2")
        spec = make_item("SPEC001", text="仕様",
                         links=[make_link("REQ001")])
        tree = make_tree([
            make_doc("REQ", items=[req1, req2]),
            make_doc("SPEC", parent="REQ", items=[spec]),
        ])
        issues = validate_tree(tree, strict=True)
        assert any("REQ002" in w and "リンクがありません" in w for w in issues["warnings"])

    def test_derived_impl_error(self):
        spec = make_item("SPEC001", text="仕様")
        impl = make_item("IMPL001", text="実装", derived=True,
                         links=[make_link("SPEC001")])
        tree = make_tree([
            make_doc("SPEC", items=[spec]),
            make_doc("IMPL", parent="SPEC", items=[impl]),
        ])
        issues = validate_tree(tree)
        assert any("IMPL/TST で derived" in e for e in issues["errors"])

    def test_derived_req_warning(self):
        req = make_item("REQ001", text="派生要件", derived=True)
        tree = make_tree([make_doc("REQ", items=[req])])
        issues = validate_tree(tree)
        assert any("REQ で derived" in w for w in issues["warnings"])

    def test_derived_spec_no_rationale_warning(self):
        spec = make_item("SPEC001", text="仕様の説明", derived=True)
        tree = make_tree([make_doc("SPEC", items=[spec])])
        issues = validate_tree(tree)
        assert any("派生要求の根拠" in w for w in issues["warnings"])

    def test_derived_spec_with_rationale_no_warning(self):
        spec = make_item("SPEC001", text="派生要求の根拠: XXX", derived=True)
        tree = make_tree([make_doc("SPEC", items=[spec])])
        issues = validate_tree(tree)
        assert not any("派生要求の根拠" in w for w in issues["warnings"])

    def test_unreviewed_info(self):
        item = make_item("REQ001", text="要件", reviewed=False)
        tree = make_tree([make_doc("REQ", items=[item])])
        issues = validate_tree(tree)
        assert any("未レビュー" in i for i in issues["info"])

    def test_all_reviewed_no_info(self):
        item = make_item("REQ001", text="要件", reviewed=True)
        tree = make_tree([make_doc("REQ", items=[item])])
        issues = validate_tree(tree)
        assert not any("未レビュー" in i for i in issues["info"])

    def test_valid_tree_no_errors(self, simple_tree):
        issues = validate_tree(simple_tree)
        assert len(issues["errors"]) == 0


# =========================================================================
# build_traceability_matrix
# =========================================================================

class TestBuildTraceabilityMatrix:
    def test_basic_structure(self, simple_tree):
        matrix, prefixes = build_traceability_matrix(simple_tree)
        assert "REQ" in prefixes
        assert "SPEC" in prefixes
        assert len(matrix) >= 3  # At least 3 REQ rows

    def test_matrix_has_req_items(self, simple_tree):
        matrix, prefixes = build_traceability_matrix(simple_tree)
        for row in matrix:
            assert "REQ" in row  # Every row should have a REQ item

    def test_matrix_has_children(self, simple_tree):
        matrix, _ = build_traceability_matrix(simple_tree)
        spec_found = any("SPEC" in row for row in matrix)
        assert spec_found

    def test_multiple_children_expand_rows(self):
        req = make_item("REQ001", text="要件")
        spec1 = make_item("SPEC001", text="仕様1",
                          links=[make_link("REQ001")])
        spec2 = make_item("SPEC002", text="仕様2",
                          links=[make_link("REQ001")])
        tree = make_tree([
            make_doc("REQ", items=[req]),
            make_doc("SPEC", parent="REQ", items=[spec1, spec2]),
        ])
        matrix, _ = build_traceability_matrix(tree)
        # REQ001 has 2 SPEC children, so there should be 2 rows
        rows_with_req001 = [r for r in matrix if "REQ" in r and str(r["REQ"].uid) == "REQ001"]
        assert len(rows_with_req001) == 2


# =========================================================================
# compute_coverage
# =========================================================================

class TestComputeCoverage:
    def test_all_covered(self, simple_tree):
        coverage = compute_coverage(simple_tree)
        for key, cov in coverage.items():
            assert cov["percentage"] == 100.0
            assert cov["uncovered"] == 0

    def test_partial(self):
        req1 = make_item("REQ001", text="要件1")
        req2 = make_item("REQ002", text="要件2")
        spec1 = make_item("SPEC001", text="仕様1",
                          links=[make_link("REQ001")])
        tree = make_tree([
            make_doc("REQ", items=[req1, req2]),
            make_doc("SPEC", parent="REQ", items=[spec1]),
        ])
        coverage = compute_coverage(tree)
        cov = coverage["SPEC → REQ"]
        assert cov["total"] == 2
        assert cov["covered"] == 1
        assert cov["percentage"] == 50.0
        assert "REQ002" in cov["uncovered_items"]

    def test_by_group(self, simple_tree):
        coverage = compute_coverage(simple_tree)
        for key, cov in coverage.items():
            assert "by_group" in cov
            if cov["by_group"]:
                for group_name, group_cov in cov["by_group"].items():
                    assert "total" in group_cov
                    assert "covered" in group_cov
                    assert "percentage" in group_cov

    def test_no_parent_doc(self):
        """親ドキュメントがないルートドキュメントはカバレッジ計算対象外。"""
        req = make_item("REQ001", text="要件")
        tree = make_tree([make_doc("REQ", items=[req])])
        coverage = compute_coverage(tree)
        assert len(coverage) == 0

    def test_zero_items_in_parent(self):
        tree = make_tree([
            make_doc("REQ", items=[]),
            make_doc("SPEC", parent="REQ", items=[]),
        ])
        coverage = compute_coverage(tree)
        # Empty parent still creates an entry with 0/0
        cov = coverage["SPEC → REQ"]
        assert cov["total"] == 0
        assert cov["covered"] == 0
        assert cov["percentage"] == 0.0
