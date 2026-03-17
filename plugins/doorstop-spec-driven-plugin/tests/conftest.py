"""共通フィクスチャ — 全テストモジュールで使用される。"""
from __future__ import annotations

import json
import sys

import pytest

from helpers import make_item, make_link, make_doc, make_tree


# ---------------------------------------------------------------------------
# out() キャプチャ用フィクスチャ
# ---------------------------------------------------------------------------

@pytest.fixture
def capture_out(monkeypatch, capsys):
    """out() が呼ばれた際の JSON 出力をキャプチャして dict で返す。

    使い方::

        result = capture_out(lambda: cmd_list(tree, args))
        assert result["ok"] is True
    """
    def mock_exit(code):
        raise SystemExit(code)

    monkeypatch.setattr(sys, "exit", mock_exit)

    def run(fn):
        with pytest.raises(SystemExit):
            fn()
        captured = capsys.readouterr()
        return json.loads(captured.out)

    return run


# ---------------------------------------------------------------------------
# 標準テストツリー: REQ → SPEC → IMPL / TST
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_tree():
    """REQ→SPEC→IMPL/TST の4ドキュメント、各3アイテム、リンク済みの標準テストツリー。"""
    # REQ items
    req1 = make_item("REQ001", text="ユーザー認証機能", header="認証",
                     groups=["AUTH"], priority="high", stamp_value="s_req1")
    req2 = make_item("REQ002", text="キャッシュ管理", header="キャッシュ",
                     groups=["CACHE"], priority="medium", stamp_value="s_req2")
    req3 = make_item("REQ003", text="ログ出力", header="ログ",
                     groups=["LOG"], priority="low", stamp_value="s_req3")

    # SPEC items (linked to REQ)
    spec1 = make_item("SPEC001", text="パスワードハッシュ仕様", header="ハッシュ",
                      groups=["AUTH"], priority="high",
                      links=[make_link("REQ001", stamp="s_req1")],
                      stamp_value="s_spec1",
                      gherkin="Given ユーザーがパスワードを入力\nWhen 認証を実行\nThen ハッシュ一致で成功")
    spec2 = make_item("SPEC002", text="LRUキャッシュ仕様", header="LRU",
                      groups=["CACHE"], priority="medium",
                      links=[make_link("REQ002", stamp="s_req2")],
                      stamp_value="s_spec2")
    spec3 = make_item("SPEC003", text="構造化ログ仕様", header="構造化ログ",
                      groups=["LOG"], priority="low",
                      links=[make_link("REQ003", stamp="s_req3")],
                      stamp_value="s_spec3")

    # IMPL items (linked to SPEC)
    impl1 = make_item("IMPL001", text="auth.py 実装", header="",
                      groups=["AUTH"],
                      links=[make_link("SPEC001", stamp="s_spec1")],
                      ref="src/auth.py",
                      references=[{"path": "src/auth.py", "type": "file"}],
                      stamp_value="s_impl1")
    impl2 = make_item("IMPL002", text="cache.py 実装", header="",
                      groups=["CACHE"],
                      links=[make_link("SPEC002", stamp="s_spec2")],
                      ref="src/cache.py",
                      references=[{"path": "src/cache.py", "type": "file"}],
                      stamp_value="s_impl2")
    impl3 = make_item("IMPL003", text="logger.py 実装", header="",
                      groups=["LOG"],
                      links=[make_link("SPEC003", stamp="s_spec3")],
                      ref="src/logger.py",
                      references=[{"path": "src/logger.py", "type": "file"}],
                      stamp_value="s_impl3")

    # TST items (linked to SPEC)
    tst1 = make_item("TST001", text="認証テスト", header="",
                     groups=["AUTH"],
                     links=[make_link("SPEC001", stamp="s_spec1")],
                     ref="tests/test_auth.py",
                     references=[{"path": "tests/test_auth.py", "type": "file"}],
                     stamp_value="s_tst1")
    tst2 = make_item("TST002", text="キャッシュテスト", header="",
                     groups=["CACHE"],
                     links=[make_link("SPEC002", stamp="s_spec2")],
                     ref="tests/test_cache.py",
                     references=[{"path": "tests/test_cache.py", "type": "file"}],
                     stamp_value="s_tst2")
    tst3 = make_item("TST003", text="ログテスト", header="",
                     groups=["LOG"],
                     links=[make_link("SPEC003", stamp="s_spec3")],
                     ref="tests/test_logger.py",
                     references=[{"path": "tests/test_logger.py", "type": "file"}],
                     stamp_value="s_tst3")

    req_doc = make_doc("REQ", parent=None, items=[req1, req2, req3])
    spec_doc = make_doc("SPEC", parent="REQ", items=[spec1, spec2, spec3])
    impl_doc = make_doc("IMPL", parent="SPEC", items=[impl1, impl2, impl3])
    tst_doc = make_doc("TST", parent="SPEC", items=[tst1, tst2, tst3])

    return make_tree([req_doc, spec_doc, impl_doc, tst_doc])


@pytest.fixture
def empty_tree():
    """空のツリー。"""
    return make_tree([])


@pytest.fixture
def suspect_tree():
    """suspect リンクを含むツリー。"""
    req1 = make_item("REQ001", text="要件A", stamp_value="new_stamp")
    spec1 = make_item("SPEC001", text="仕様A",
                      links=[make_link("REQ001", stamp="old_stamp")],
                      stamp_value="s_spec1")
    spec2 = make_item("SPEC002", text="仕様B（正常）",
                      links=[make_link("REQ001", stamp="new_stamp")],
                      stamp_value="s_spec2")

    req_doc = make_doc("REQ", parent=None, items=[req1])
    spec_doc = make_doc("SPEC", parent="REQ", items=[spec1, spec2])
    return make_tree([req_doc, spec_doc])
