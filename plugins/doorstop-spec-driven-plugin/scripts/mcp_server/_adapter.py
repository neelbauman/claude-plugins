"""cmd_* 関数を MCP ツールから呼び出すためのアダプター。

既存の cmd_* 関数は out() で JSON を stdout に出力して sys.exit() する設計のため、
stdout をキャプチャし SystemExit をキャッチして結果を dict で返す。
"""

import argparse
import contextlib
import io
import json
import os
import threading

import doorstop

# ツリーキャッシュ（同一プロセス内で doorstop.build() の繰り返し呼び出しを最適化）
_tree_cache: dict[str, tuple] = {}  # project_dir -> (tree, cwd)
_tree_lock = threading.Lock()


def get_tree(project_dir: str):
    """プロジェクトディレクトリの Doorstop ツリーを取得する（キャッシュ付き）。"""
    project_dir = os.path.abspath(project_dir)
    with _tree_lock:
        if project_dir in _tree_cache:
            tree, _ = _tree_cache[project_dir]
            return tree
        saved_cwd = os.getcwd()
        try:
            os.chdir(project_dir)
            tree = doorstop.build()
            _tree_cache[project_dir] = (tree, project_dir)
            return tree
        finally:
            os.chdir(saved_cwd)


def invalidate_cache(project_dir: str | None = None):
    """ツリーキャッシュを無効化する。書き込み操作後に呼び出す。"""
    with _tree_lock:
        if project_dir:
            _tree_cache.pop(os.path.abspath(project_dir), None)
        else:
            _tree_cache.clear()


def call_cmd(cmd_func, project_dir: str, args_dict: dict) -> dict:
    """cmd_* 関数を呼び出し、JSON 出力を dict で返す。

    cmd_* 関数は out() 経由で JSON を stdout に出力し sys.exit() するため、
    stdout をキャプチャし SystemExit をキャッチする。
    """
    project_dir = os.path.abspath(project_dir)
    ns = argparse.Namespace(**args_dict)

    saved_cwd = os.getcwd()
    try:
        os.chdir(project_dir)
        tree = get_tree(project_dir)

        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                cmd_func(tree, ns)
        except SystemExit:
            pass

        output = buf.getvalue().strip()
        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                return {"ok": True, "raw_output": output}
        return {"ok": True, "message": "コマンドが正常に完了しました"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        os.chdir(saved_cwd)


def call_cmd_no_tree(cmd_func, project_dir: str, args_dict: dict) -> dict:
    """ツリーを引数に取らない cmd_* 関数用アダプター（glossary 等）。"""
    project_dir = os.path.abspath(project_dir)
    args_dict["project_dir"] = project_dir
    ns = argparse.Namespace(**args_dict)

    saved_cwd = os.getcwd()
    try:
        os.chdir(project_dir)

        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                cmd_func(ns)
        except SystemExit:
            pass

        output = buf.getvalue().strip()
        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                return {"ok": True, "raw_output": output}
        return {"ok": True, "message": "コマンドが正常に完了しました"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        os.chdir(saved_cwd)


def call_cmd_write(cmd_func, project_dir: str, args_dict: dict) -> dict:
    """書き込み操作用アダプター。実行後にキャッシュを無効化する。"""
    result = call_cmd(cmd_func, project_dir, args_dict)
    invalidate_cache(project_dir)
    return result
