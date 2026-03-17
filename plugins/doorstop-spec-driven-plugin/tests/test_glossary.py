"""Phase 5: glossary.py の単体テスト。"""
from __future__ import annotations

import os

import pytest

from helpers import make_args

from glossary import (
    _glossary_path,
    _load_glossary,
    _save_glossary,
    _find_term,
    cmd_add,
    cmd_update,
    cmd_remove,
    cmd_list,
)


# =========================================================================
# _glossary_path
# =========================================================================

class TestGlossaryPath:
    def test_with_spec_dir(self, tmp_path):
        spec_dir = tmp_path / "specification"
        spec_dir.mkdir()
        path = _glossary_path(str(tmp_path))
        assert "specification" in path
        assert path.endswith("glossary.yml")

    def test_without_spec_dir(self, tmp_path):
        path = _glossary_path(str(tmp_path))
        assert path.endswith("glossary.yml")
        assert "specification" not in path


# =========================================================================
# _load_glossary / _save_glossary
# =========================================================================

class TestLoadSaveGlossary:
    def test_load_empty(self, tmp_path):
        data = _load_glossary(str(tmp_path))
        assert data == {"terms": []}

    def test_save_and_load(self, tmp_path):
        data = {"terms": [{"term": "キャッシュ", "definition": "一時保存"}]}
        _save_glossary(str(tmp_path), data)
        loaded = _load_glossary(str(tmp_path))
        assert len(loaded["terms"]) == 1
        assert loaded["terms"][0]["term"] == "キャッシュ"


# =========================================================================
# _find_term
# =========================================================================

class TestFindTerm:
    def test_case_insensitive(self):
        terms = [{"term": "Cache"}, {"term": "Auth"}]
        idx, t = _find_term(terms, "cache")
        assert idx == 0
        assert t["term"] == "Cache"

    def test_not_found(self):
        terms = [{"term": "Cache"}]
        idx, t = _find_term(terms, "Database")
        assert idx == -1
        assert t is None


# =========================================================================
# cmd_add
# =========================================================================

class TestCmdAdd:
    def test_new_term(self, tmp_path, capture_out):
        args = make_args(
            project_dir=str(tmp_path), term="キャッシュ",
            definition="一時的なデータ保存", aliases=None,
            context=None, code=None,
        )
        result = capture_out(lambda: cmd_add(args))
        assert result["ok"] is True
        assert result["action"] == "add"
        assert result["term"]["term"] == "キャッシュ"
        assert result["total_terms"] == 1

    def test_with_aliases(self, tmp_path, capture_out):
        args = make_args(
            project_dir=str(tmp_path), term="キャッシュ",
            definition="一時保存", aliases="cache,Cache",
            context="性能", code="CacheManager",
        )
        result = capture_out(lambda: cmd_add(args))
        assert result["term"]["aliases"] == ["cache", "Cache"]
        assert result["term"]["context"] == "性能"
        assert result["term"]["code"] == "CacheManager"

    def test_duplicate_error(self, tmp_path, capture_out):
        # First add
        args = make_args(
            project_dir=str(tmp_path), term="キャッシュ",
            definition="定義1", aliases=None, context=None, code=None,
        )
        capture_out(lambda: cmd_add(args))
        # Second add (duplicate)
        args2 = make_args(
            project_dir=str(tmp_path), term="キャッシュ",
            definition="定義2", aliases=None, context=None, code=None,
        )
        result = capture_out(lambda: cmd_add(args2))
        assert result["ok"] is False
        assert "既に定義" in result["error"]


# =========================================================================
# cmd_update
# =========================================================================

class TestCmdUpdate:
    def _add_term(self, tmp_path, capture_out):
        args = make_args(
            project_dir=str(tmp_path), term="キャッシュ",
            definition="旧定義", aliases=None, context=None, code=None,
        )
        capture_out(lambda: cmd_add(args))

    def test_update_existing(self, tmp_path, capture_out):
        self._add_term(tmp_path, capture_out)
        args = make_args(
            project_dir=str(tmp_path), term="キャッシュ",
            definition="新定義", aliases=None, context=None, code=None,
        )
        result = capture_out(lambda: cmd_update(args))
        assert result["ok"] is True
        assert result["term"]["definition"] == "新定義"

    def test_update_not_found(self, tmp_path, capture_out):
        args = make_args(
            project_dir=str(tmp_path), term="存在しない",
            definition="定義", aliases=None, context=None, code=None,
        )
        result = capture_out(lambda: cmd_update(args))
        assert result["ok"] is False


# =========================================================================
# cmd_remove
# =========================================================================

class TestCmdRemove:
    def test_remove_existing(self, tmp_path, capture_out):
        # Add first
        args_add = make_args(
            project_dir=str(tmp_path), term="キャッシュ",
            definition="定義", aliases=None, context=None, code=None,
        )
        capture_out(lambda: cmd_add(args_add))
        # Remove
        args = make_args(project_dir=str(tmp_path), term="キャッシュ")
        result = capture_out(lambda: cmd_remove(args))
        assert result["ok"] is True
        assert result["action"] == "remove"
        assert result["total_terms"] == 0

    def test_remove_not_found(self, tmp_path, capture_out):
        args = make_args(project_dir=str(tmp_path), term="存在しない")
        result = capture_out(lambda: cmd_remove(args))
        assert result["ok"] is False


# =========================================================================
# cmd_list
# =========================================================================

class TestCmdList:
    def test_list_all(self, tmp_path, capture_out):
        # Add two terms
        for term in ["認証", "キャッシュ"]:
            args = make_args(
                project_dir=str(tmp_path), term=term,
                definition=f"{term}の定義", aliases=None,
                context=None, code=None,
            )
            capture_out(lambda: cmd_add(args))
        # List
        args = make_args(project_dir=str(tmp_path), context=None)
        result = capture_out(lambda: cmd_list(args))
        assert result["ok"] is True
        assert result["count"] == 2

    def test_context_filter(self, tmp_path, capture_out):
        args1 = make_args(
            project_dir=str(tmp_path), term="認証",
            definition="定義", aliases=None, context="AUTH", code=None,
        )
        capture_out(lambda: cmd_add(args1))
        args2 = make_args(
            project_dir=str(tmp_path), term="キャッシュ",
            definition="定義", aliases=None, context="CACHE", code=None,
        )
        capture_out(lambda: cmd_add(args2))
        # Filter
        args = make_args(project_dir=str(tmp_path), context="AUTH")
        result = capture_out(lambda: cmd_list(args))
        assert result["count"] == 1
        assert result["terms"][0]["term"] == "認証"
