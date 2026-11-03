"""The board writer (``ledgerboard/board.py``, SPEC *The board writer*): what its fixtures do not show —
its imports, both-or-neither writes, usage errors, and the same bytes loading as a subpackage."""

import ast
import contextlib
import importlib.util
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ledgerboard import board as B  # noqa: E402

BOARD = ("# Board\n\n## Needs the user\n\n"
         "- [ ] act 2026-01-10 (n/a) — Merge it. Context: PR #12. Due: 2026-01-20.\n"
         "- [x] act 2026-01-02 (n/a) — Tag it. Context: none. Due: 2026-01-05. Closed: 2026-01-06.\n")


def run(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = B.main(list(argv))
        except SystemExit as e:
            code = e.code
    return code, out.getvalue(), err.getvalue()


class Boundary(unittest.TestCase):
    def test_imports_no_git_network_or_process(self):
        tree = ast.parse((ROOT / "ledgerboard" / "board.py").read_text(encoding="utf-8"))
        names = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        names |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        self.assertLessEqual(names, {"__future__", "argparse", "json", "os", "re", "sys", "tempfile",
                                     "collections", "dataclasses", "datetime"})

    def test_the_header_and_no_shebang(self):
        first = (ROOT / "ledgerboard" / "board.py").read_text(encoding="utf-8").splitlines()[:2]
        self.assertTrue(first[0].startswith("# ledgerboard v"))
        self.assertIn("SYNCED FILE — canonical copy: ShiftLead/ledgerboard ledgerboard/board.py", first[1])

    def test_the_same_bytes_load_as_a_subpackage(self):
        with tempfile.TemporaryDirectory() as tmp:
            pkg = Path(tmp) / "host" / "ledgerboard"
            pkg.mkdir(parents=True)
            for f in ("__init__.py", "board.py"):
                (pkg / f).write_bytes((ROOT / "ledgerboard" / f).read_bytes())
            (pkg.parent / "__init__.py").write_text("")
            sys.path.insert(0, tmp)
            try:
                mod = importlib.import_module("host.ledgerboard.board")
                self.assertTrue(hasattr(mod, "plan_add"))
            finally:
                sys.path.remove(tmp)
                for name in [n for n in sys.modules if n == "host" or n.startswith("host.")]:
                    del sys.modules[name]


class BothOrNeither(unittest.TestCase):
    def test_a_failed_rename_restores_every_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            board, arch = os.path.join(tmp, "board.md"), os.path.join(tmp, "archive.md")
            Path(board).write_text(BOARD)
            Path(arch).write_text("# Archive\n")
            plan = B.plan_archive(board, arch)
            real = os.replace
            calls = []

            def flaky(src, dst):
                calls.append(dst)
                if len(calls) == 2:
                    raise OSError("disk full")
                real(src, dst)

            with mock.patch.object(B.os, "replace", flaky):
                with self.assertRaises(OSError):
                    B.apply(plan)
            self.assertEqual(Path(board).read_text(), BOARD)
            self.assertEqual(Path(arch).read_text(), "# Archive\n")
            self.assertEqual(sorted(os.listdir(tmp)), ["archive.md", "board.md"])  # no temporary file left

    def test_a_failed_rename_removes_a_file_it_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            board, arch = os.path.join(tmp, "board.md"), os.path.join(tmp, "archive.md")
            Path(board).write_text(BOARD)
            plan = B.Plan("archive", None, {arch: "# Archive\n", board: "changed\n"})  # the new file first
            real = os.replace

            def flaky(src, dst):
                if dst == board:
                    raise OSError("read-only")
                real(src, dst)

            with mock.patch.object(B.os, "replace", flaky):
                with self.assertRaises(OSError):
                    B.apply(plan)
            self.assertEqual(Path(board).read_text(), BOARD)
            self.assertEqual(os.listdir(tmp), ["board.md"])

    def test_the_command_says_so_and_exits_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = os.path.join(tmp, "board.md")
            Path(board).write_text(BOARD)
            with mock.patch.object(B.os, "replace", side_effect=OSError("no")):
                code, _, err = run("done", "--board", board, "--line", "5", "--expect", "act", "--today", "2026-01-15")
            self.assertEqual(code, 1)
            self.assertIn("every file restored", err)
            self.assertEqual(Path(board).read_text(), BOARD)

    def test_a_plan_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = os.path.join(tmp, "board.md")
            Path(board).write_text(BOARD)
            code, out, _ = run("done", "--board", board, "--line", "5", "--expect", "act", "--plan")
            self.assertEqual(code, 0)
            self.assertIn('"changes"', out)
            self.assertEqual(Path(board).read_text(), BOARD)


class Review(unittest.TestCase):
    def test_a_new_file_takes_the_umask_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            rank = os.path.join(tmp, "rank.yml")
            old = os.umask(0o022)
            try:
                B.apply(B.plan_rank(rank, "rank", {"TD-1": "5"}))
            finally:
                os.umask(old)
            self.assertEqual(os.stat(rank).st_mode & 0o777, 0o644)

    def test_the_archive_is_written_before_the_board(self):
        with tempfile.TemporaryDirectory() as tmp:
            board, arch = os.path.join(tmp, "board.md"), os.path.join(tmp, "archive.md")
            Path(board).write_text(BOARD)
            self.assertEqual(list(B.plan_archive(board, arch).changes), [arch, board])

    def test_a_board_that_is_its_own_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = os.path.join(tmp, "board.md")
            Path(board).write_text(BOARD)
            with self.assertRaisesRegex(B.Refused, "one file"):
                B.plan_archive(board, os.path.join(tmp, ".", "board.md"))

    def test_rank_actions_match_their_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            rank = os.path.join(tmp, "rank.yml")
            with self.assertRaisesRegex(B.Refused, "prune removes"):
                B.plan_rank(rank, "prune", {"TD-1": "5"})
            with self.assertRaisesRegex(B.Refused, "join sets"):
                B.plan_rank(rank, "join", {"TD-1": None})
            with self.assertRaisesRegex(B.Refused, "set twice"):
                B._pairs(["TD-1=5", "TD-1=6"], [])
            with self.assertRaisesRegex(B.Refused, "twice"):
                B._pairs(["TD-1=5"], ["TD-1"])


class Usage(unittest.TestCase):
    def test_an_option_the_action_does_not_take(self):
        code, _, err = run("done", "--board", "b.md", "--line", "1", "--expect", "x", "--to", "2026-01-01")
        self.assertEqual(code, 2)
        self.assertIn("done does not take --to", err)

    def test_a_missing_option(self):
        code, _, err = run("reply", "--board", "b.md", "--line", "1", "--expect", "x", "--text", "hi")
        self.assertEqual(code, 2)
        self.assertIn("reply needs --by", err)

    def test_decide_takes_one_answer(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = os.path.join(tmp, "board.md")
            Path(board).write_text(BOARD)
            code, _, err = run("decide", "--board", board, "--line", "5", "--expect", "act",
                               "--answer", "a", "--answer", "b")
            self.assertEqual(code, 3)
            self.assertIn("one --answer", err)

    def test_a_bad_today(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = os.path.join(tmp, "board.md")
            Path(board).write_text(BOARD)
            code, _, err = run("done", "--board", board, "--line", "5", "--expect", "act", "--today", "2026-1-5")
            self.assertEqual(code, 3)
            self.assertIn("--today", err)

    def test_plain_output_is_the_subject_then_the_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = os.path.join(tmp, "board.md")
            Path(board).write_text(BOARD)
            code, out, _ = run("done", "--board", board, "--line", "5", "--expect", "act", "--today", "2026-01-15")
            self.assertEqual(code, 0)
            self.assertEqual(out.splitlines(), ["ledgerboard: done Merge it. (session n/a)", board])


class Module(unittest.TestCase):
    def test_run_as_a_module(self):
        spec = importlib.util.find_spec("ledgerboard.board")
        self.assertIsNotNone(spec)


if __name__ == "__main__":
    unittest.main()
