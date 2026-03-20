"""init_project を MCP ツールとしてラップする。"""

import contextlib
import io
import os
import sys

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP):
    """init 系の MCP ツールを登録する。"""

    @mcp.tool()
    def sdd_init(
        project_dir: str,
        profile: str = "lite",
        digits: int = 3,
        separator: str = "",
        docs_dir: str = "./specification",
        no_git_init: bool = False,
        with_nfr: bool = False,
    ) -> dict:
        """Doorstop 仕様駆動開発プロジェクトを初期化する。

        Args:
            project_dir: プロジェクトルートディレクトリ
            profile: プロファイル（lite/standard/full）
            digits: アイテムUIDの桁数
            separator: プレフィックスと番号の区切り文字
            docs_dir: ドキュメントツリーのベースディレクトリ
            no_git_init: gitリポジトリの初期化をスキップ
            with_nfr: 非機能要件（NFR）ドキュメントを作成する
        """
        project_dir = os.path.abspath(project_dir)
        saved_cwd = os.getcwd()
        try:
            # init_project.py の main() は argparse.parse_args() を使うため、
            # sys.argv を差し替えて呼び出す
            argv_backup = sys.argv
            sys.argv = [
                "init_project.py", project_dir,
                "--profile", profile,
                "--digits", str(digits),
                "--docs-dir", docs_dir,
            ]
            if separator:
                sys.argv += ["--separator", separator]
            if no_git_init:
                sys.argv.append("--no-git-init")
            if with_nfr:
                sys.argv.append("--with-nfr")

            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    from ..init_project import main as init_main
                    init_main()
            except SystemExit:
                pass
            finally:
                sys.argv = argv_backup

            output = buf.getvalue()
            return {
                "ok": True,
                "action": "init",
                "project_dir": project_dir,
                "profile": profile,
                "output": output,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            os.chdir(saved_cwd)
