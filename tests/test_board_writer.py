"""The board writer (``ledgerboard/board.py``, SPEC *The board writer*): what its fixtures do not show —
its imports, both-or-neither writes and the move on close, usage errors, the id's draw, a board a fixture cannot
hold (an empty directory, an unreadable ``README.md``), and the same bytes loading as a subpackage."""

import ast
import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import ledgerboard as L  # noqa: E402
from ledgerboard import board as B  # noqa: E402

README = "# Board\n\nLedgerboard: 3\nPeople: pat\n"
ID = "2026-01-10-a1000001"
ITEM = L.item_file("Merge it", "2026-01-20", "2026-01-10", None, None, "PR #12", kind="act")
ARCHIVED = os.path.join("archive", "2026-01", f"{ID}.md")  # where a close on 2026-01-15 moves it
V2_BOARD = ("# Board\n\n## Needs the user\n\n"
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


def make_board(root: str, files: dict[str, str] | None = None, readme: str | None = README) -> str:
    """A v3 board at ``<root>/board``: its README.md (none when None) and ``files`` (path to text, relative to
    the board; default the one open item ``ID``)."""
    d = os.path.join(root, "board")
    os.makedirs(d)
    if readme is not None:
        Path(d, "README.md").write_text(readme)
    for rel, text in (files if files is not None else {f"{ID}.md": ITEM}).items():
        os.makedirs(os.path.dirname(os.path.join(d, rel)), exist_ok=True)
        Path(d, rel).write_text(text)
    return d


def snapshot(d: str) -> dict[str, str]:
    """Every file under ``d``, by its relative path."""
    return {str(p.relative_to(d)): p.read_text() for p in sorted(Path(d).rglob("*")) if p.is_file()}


class Boundary(unittest.TestCase):
    def test_imports_no_git_network_or_process(self):
        tree = ast.parse((ROOT / "ledgerboard" / "board.py").read_text(encoding="utf-8"))
        names = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        names |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        self.assertLessEqual(names, {"__future__", "argparse", "json", "os", "re", "secrets", "sys", "tempfile",
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
            one, two = os.path.join(tmp, "one.md"), os.path.join(tmp, "two.md")
            Path(one).write_text("one\n")
            Path(two).write_text("two\n")
            plan = B.Plan("reply", None, {one: "one changed\n", two: "two changed\n"})
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
            self.assertEqual((Path(one).read_text(), Path(two).read_text()), ("one\n", "two\n"))
            self.assertEqual(sorted(os.listdir(tmp)), ["one.md", "two.md"])  # no temporary file left

    def test_a_failed_rename_removes_a_file_it_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            old, new = os.path.join(tmp, "old.md"), os.path.join(tmp, "new.md")
            Path(old).write_text("old\n")
            plan = B.Plan("done", None, {new: "new\n", old: "changed\n"})  # the new file first

            def flaky(src, dst):
                if dst == old:
                    raise OSError("read-only")
                os.rename(src, dst)

            with mock.patch.object(B.os, "replace", flaky):
                with self.assertRaises(OSError):
                    B.apply(plan)
            self.assertEqual(Path(old).read_text(), "old\n")
            self.assertEqual(os.listdir(tmp), ["old.md"])

    def test_the_command_says_so_and_exits_4(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = make_board(tmp)
            before = snapshot(board)
            with mock.patch.object(B.os, "replace", side_effect=OSError("no")):
                code, _, err = run("done", "--board", board, "--id", ID, "--today", "2026-01-15")
            self.assertEqual(code, 4)
            self.assertIn("every file restored", err)
            self.assertEqual(snapshot(board), before)
            self.assertFalse(os.path.exists(os.path.join(board, "archive")))  # the month it made is removed

    def test_a_plan_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = make_board(tmp)
            before = snapshot(board)
            code, out, _ = run("done", "--board", board, "--id", ID, "--today", "2026-01-15", "--plan")
            self.assertEqual(code, 0)
            got = json.loads(out)
            self.assertEqual([c["path"] for c in got["changes"]],
                             [os.path.join(board, ARCHIVED), os.path.join(board, f"{ID}.md")])
            self.assertIsNone(got["changes"][1]["text"])  # the open file removed
            self.assertEqual(snapshot(board), before)


class ReviewFixes(unittest.TestCase):
    """PR #306's review: ``--board .``, the edits' order, a why ending in marks and spaces."""

    def test_a_board_given_as_dot_is_gated_and_noted(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = make_board(tmp)
            here = os.getcwd()
            os.chdir(board)
            try:
                code, out, _ = run("add", "--board", ".", "--text", "Look later", "--kind", "act", "--due",
                                   "2026-01-30", "--hide-until", "2026-02-20", "--context", "PR #3",
                                   "--today", "2026-01-15", "--id", "2026-01-15-5eed0001", "--json")
            finally:
                os.chdir(here)
            self.assertEqual(code, 0)
            self.assertNotEqual(json.loads(out)["item_notes"], [])  # the new file is seen by the notes and the gate

    def test_an_unknown_id_is_refused_before_the_edits_own_refusals(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = make_board(tmp)
            code, _, err = run("reply", "--board", board, "--id", "2026-01-10-ffffffff", "--text", "hi", "--by", " ")
            self.assertEqual(code, 1)
            self.assertIn("no open item has the id", err)

    def test_a_why_ending_in_marks_and_spaces_has_no_final_period(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = make_board(tmp)
            self.assertEqual(run("done", "--board", board, "--id", ID, "--why", "merged. .", "--today",
                                 "2026-01-15")[0], 0)
            self.assertIn("**Closed:** 2026-01-15 — merged\n", Path(board, ARCHIVED).read_text())


class TheMove(unittest.TestCase):
    """``done``, and a ``decide`` that closes, write the archived file and remove the open one in one write (D2, D7):
    the archived file first, then the removal; nothing left on a failed write."""

    def test_the_archived_file_is_written_before_the_open_one_is_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = make_board(tmp)
            plan = B.plan_edit(board, "done", ID, today="2026-01-15")
            self.assertEqual(list(plan.changes), [os.path.join(board, ARCHIVED), os.path.join(board, f"{ID}.md")])
            steps = []
            real_replace, real_unlink = os.replace, os.unlink

            def replace(src, dst):
                steps.append(("write", os.path.relpath(dst, board)))
                real_replace(src, dst)

            def unlink(path):
                if not os.path.basename(path).startswith(".ledgerboard-"):  # a temporary file's cleanup aside
                    steps.append(("remove", os.path.relpath(path, board)))
                real_unlink(path)

            with mock.patch.object(B.os, "replace", replace), mock.patch.object(B.os, "unlink", unlink):
                B.apply(plan)
            self.assertEqual(steps, [("write", ARCHIVED), ("remove", f"{ID}.md")])
            self.assertEqual(sorted(snapshot(board)), sorted(["README.md", ARCHIVED]))
            self.assertIn("**Closed:** 2026-01-15", Path(board, ARCHIVED).read_text())

    def test_a_failed_removal_leaves_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = make_board(tmp)
            before = snapshot(board)
            real_unlink = os.unlink
            open_file = os.path.join(board, f"{ID}.md")

            def unlink(path):
                if path == open_file:
                    raise OSError("read-only")
                real_unlink(path)

            with mock.patch.object(B.os, "unlink", unlink):
                code, _, err = run("done", "--board", board, "--id", ID, "--today", "2026-01-15")
            self.assertEqual(code, 4, err)
            self.assertEqual(snapshot(board), before)  # the archived file it wrote is removed again
            self.assertEqual(sorted(os.listdir(board)), sorted(["README.md", f"{ID}.md"]))  # and the months it made

    def test_an_archived_file_that_exists_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = make_board(tmp, {f"{ID}.md": ITEM, ARCHIVED: "Notes kept by hand.\n"})
            before = snapshot(board)
            code, _, err = run("done", "--board", board, "--id", ID, "--today", "2026-01-15")
            self.assertEqual(code, 1)
            self.assertIn(f"{board}: {ARCHIVED} exists", err)
            self.assertEqual(snapshot(board), before)


DECIDE_ID = "2026-01-12-a1000007"
DECIDE_ITEM = L.item_file("Go on the export?", "2026-01-20", "2026-01-12", None, None, "TD-1 decision (robin)",
                          kind="decide", answers=["Go", "Not yet"], default=0,
                          detail={"context": "It waits.", "question": "Go?", "recommended": "ready"})
DECIDE_README = "# Board\n\nLedgerboard: 3\nPeople: robin\n"
DECIDE_ARCHIVED = os.path.join("archive", "2026-01", f"{DECIDE_ID}.md")
DECIDE_ENTRY = ("## TD-001: The export\n\n**Priority:** Medium\n**Added:** 2026-01-02\n**Status:** Open\n"
                "**Blocked by:** decision (robin)\n\n**Why:** it is wanted.\n\n**Ask:** say go.\n")


class DecideLift(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.board = make_board(self.tmp.name, {f"{DECIDE_ID}.md": DECIDE_ITEM}, DECIDE_README)
        self.led = os.path.join(self.tmp.name, "ledger")
        os.makedirs(self.led)
        Path(self.led, "README.md").write_text("# Ledger\n\nLedgerboard: 2\n")
        Path(self.led, "TD-001.md").write_text(DECIDE_ENTRY)
        self.before = snapshot(self.board)

    def tearDown(self):
        self.tmp.cleanup()

    def decide(self, *more):
        return run("decide", "--board", self.board, "--id", DECIDE_ID, "--answer", "Go",
                   "--ledger", self.led, "--today", "2026-01-15", *more)

    def test_a_failed_write_keeps_the_board_and_the_ledger(self):
        real = os.replace

        def flaky(src, dst):
            if dst.endswith("TD-001.md"):
                raise OSError("read-only")
            real(src, dst)
        with mock.patch.object(B.os, "replace", flaky):
            code, _, err = self.decide()
        self.assertEqual(code, 4, err)
        self.assertEqual(snapshot(self.board), self.before)
        self.assertEqual(Path(self.led, "TD-001.md").read_text(), DECIDE_ENTRY)

    def test_both_files_are_written_and_the_item_moves(self):
        code, out, err = self.decide()
        self.assertEqual(code, 0, err)
        self.assertFalse(os.path.exists(os.path.join(self.board, f"{DECIDE_ID}.md")))
        self.assertIn("**Closed:** 2026-01-15 — lifted", Path(self.board, DECIDE_ARCHIVED).read_text())
        self.assertIn('gate lifted: decision (robin) — by robin; answer "Go"', Path(self.led, "TD-001.md").read_text())

    def test_a_ledger_it_cannot_use_exits_2_as_the_ledger_writer_does(self):
        v1 = os.path.join(self.tmp.name, "technical_debt.md")
        Path(v1).write_text("# Ledger\n\n" + DECIDE_ENTRY)
        code, _, err = run("decide", "--board", self.board, "--id", DECIDE_ID, "--answer", "Go",
                           "--ledger", v1, "--today", "2026-01-15")
        self.assertEqual(code, 2, err)
        self.assertIn("v1 ledger", err)
        self.assertEqual(snapshot(self.board), self.before)

    def test_a_refusal_exits_1_never_3(self):
        code, _, err = self.decide("--by", "someone-else")
        self.assertEqual(code, 1, err)

    def test_ledger_and_board_only_are_a_decides(self):
        code, _, err = run("done", "--board", self.board, "--id", DECIDE_ID, "--board-only")
        self.assertEqual(code, 2)
        self.assertIn("done does not take --board-only", err)


SHARED_ID = "2026-01-12-a1000008"
SHARED_ITEM = L.item_file("Go on the parts?", "2026-01-20", "2026-01-12", None, None, "TD-8 decision (robin)",
                          kind="decide", answers=["Go", "Not yet"], default=0, parts=["TD-9", "TD-10"],
                          detail={"context": "It waits.", "question": "Go?", "recommended": "ready"})


def _part(n: int, carrying: bool, parent: bool = False) -> str:
    return (f"## TD-{n:03d}: Part {n}\n\n**Priority:** Medium\n**Added:** 2026-01-02\n**Status:** Open\n"
            + ("**Blocked by:** decision (robin)\n" if carrying else "") + ("" if parent else "**Part of:** TD-008\n")
            + "\n**Why:** it is wanted.\n")


class BoardOnlyLeftOpen(unittest.TestCase):  # v2.7: a --board-only lift that does not close writes nothing (TD-067 D1)
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.board = make_board(self.tmp.name, {f"{SHARED_ID}.md": SHARED_ITEM, f"{DECIDE_ID}.md": DECIDE_ITEM},
                                DECIDE_README)
        self.led = os.path.join(self.tmp.name, "ledger")
        os.makedirs(self.led)
        Path(self.led, "README.md").write_text("# Ledger\n\nLedgerboard: 2\n")
        Path(self.led, "TD-008.md").write_text(_part(8, True, parent=True))
        Path(self.led, "TD-009.md").write_text(_part(9, False))
        Path(self.led, "TD-010.md").write_text(_part(10, True))
        self.before = snapshot(self.board)

    def tearDown(self):
        self.tmp.cleanup()

    def test_the_plan_changes_nothing_and_names_the_entries_left(self):
        plan = B.plan_edit(self.board, "decide", SHARED_ID, answer="Go", by="robin", today="2026-01-15",
                           ledger=self.led, board_only=True)
        self.assertEqual((plan.changes, plan.subject, plan.info["left_open"]), ({}, None, ["TD-8", "TD-10"]))
        self.assertEqual(plan.info["id"], SHARED_ID)
        self.assertEqual(plan.warn, ["left open: TD-8, TD-10 still carry decision (robin)"])
        self.assertEqual(B.apply(plan), [])
        self.assertEqual(snapshot(self.board), self.before)

    def test_the_command_line_exits_0_and_says_so_on_stderr(self):
        code, out, err = run("decide", "--board", self.board, "--id", SHARED_ID, "--answer", "Go",
                             "--by", "robin", "--board-only", "--ledger", self.led, "--today", "2026-01-15")
        self.assertEqual((code, out), (0, ""))
        self.assertIn("left open: TD-8, TD-10 still carry decision (robin)", err)
        self.assertEqual(snapshot(self.board), self.before)

    def test_a_context_entry_nothing_has_lifted_is_left_open(self):
        Path(self.led, "TD-001.md").write_text(DECIDE_ENTRY)
        plan = B.plan_edit(self.board, "decide", DECIDE_ID, answer="Go", by="robin", today="2026-01-15",
                           ledger=self.led, board_only=True)
        self.assertEqual((plan.changes, plan.info["left_open"]), ({}, ["TD-1"]))

    def test_a_waiting_only_answer_still_writes_and_moves(self):
        plan = B.plan_edit(self.board, "decide", SHARED_ID, answer="Not yet", by="robin", today="2026-01-15",
                           ledger=self.led, board_only=True)
        archived = os.path.join(self.board, "archive", "2026-01", f"{SHARED_ID}.md")
        self.assertEqual(list(plan.changes), [archived, os.path.join(self.board, f"{SHARED_ID}.md")])
        self.assertIn("**Closed:** 2026-01-15 — kept waiting", plan.changes[archived])
        self.assertNotIn("left_open", plan.info)


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
        code, _, err = run("done", "--board", "b", "--id", ID, "--to", "2026-01-01")
        self.assertEqual(code, 2)
        self.assertIn("done does not take --to", err)

    def test_a_missing_option(self):
        code, _, err = run("reply", "--board", "b", "--id", ID, "--text", "hi")
        self.assertEqual(code, 2)
        self.assertIn("reply needs --by", err)

    def test_every_edit_needs_its_id(self):
        for action, more in (("snooze", ["--to", "2026-01-29"]), ("due", ["--to", "2026-01-29"]), ("done", []),
                             ("decide", ["--answer", "Go"]), ("reply", ["--text", "hi", "--by", "pat"])):
            code, _, err = run(action, "--board", "b", *more)
            self.assertEqual(code, 2, action)
            self.assertIn(f"{action} needs --id", err)

    def test_the_line_options_are_gone(self):
        for gone in (["--line", "5"], ["--expect", "act"], ["--under", "Needs"]):
            code, _, err = run("done", "--board", "b", "--id", ID, *gone)
            self.assertEqual(code, 2, gone)
            self.assertIn("unrecognized arguments", err)
        code, _, err = run("done", "--board", "b", "--id", ID, "--archive", "a.md")  # v3.0: split's alone
        self.assertEqual(code, 2)
        self.assertIn("done does not take --archive", err)
        code, _, err = run("archive", "--board", "b")
        self.assertEqual(code, 2)
        self.assertIn("invalid choice: 'archive'", err)

    def test_show_prints_text_only(self):
        for flag in ("--json", "--plan"):
            code, out, err = run("show", "--board", "b", flag)
            self.assertEqual((code, out), (2, ""))
            self.assertIn("show prints the board as text: it takes no --json or --plan", err)
        code, _, err = run("list", "--board", "b", "--hidden")
        self.assertEqual(code, 2)
        self.assertIn("list does not take --hidden", err)

    def test_decide_takes_one_answer(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = make_board(tmp)
            code, _, err = run("decide", "--board", board, "--id", ID, "--answer", "a", "--answer", "b")
            self.assertEqual(code, 1)
            self.assertIn("one --answer", err)

    def test_a_bad_today(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = make_board(tmp)
            code, _, err = run("done", "--board", board, "--id", ID, "--today", "2026-1-5")
            self.assertEqual(code, 2)
            self.assertIn("--today", err)

    def test_plain_output_is_the_subject_then_the_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = make_board(tmp)
            code, out, _ = run("done", "--board", board, "--id", ID, "--today", "2026-01-15")
            self.assertEqual(code, 0)
            self.assertEqual(out.splitlines(), [f"ledgerboard: done {ID} Merge it (session n/a)",
                                                os.path.join(board, ARCHIVED), os.path.join(board, f"{ID}.md")])

    def test_list_plain_names_each_item_by_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = make_board(tmp)
            code, out, _ = run("list", "--board", board, "--today", "2026-01-15")
            self.assertEqual(code, 0)
            self.assertEqual(out, f"{ID}\tdue 2026-01-20\tMerge it\n")


class NoBoardAFixtureHolds(unittest.TestCase):
    """What a fixture's ``before/`` cannot hold (git keeps no empty directory, and every file it holds is
    readable): a write needs a v3 board (D7)."""

    def test_an_empty_directory_has_no_readme(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = make_board(tmp, {}, readme=None)
            code, _, err = run("add", "--board", board, "--text", "Look at it", "--today", "2026-01-15")
            self.assertEqual(code, 1)
            self.assertIn(f"{board}: not a v3 board: no README.md", err)
            self.assertEqual(os.listdir(board), [])
            code, out, _ = run("list", "--board", board, "--json")  # a read takes it: a board with no item
            self.assertEqual((code, json.loads(out)["items"]), (0, []))

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root reads a file whatever its mode")
    def test_an_unreadable_readme(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = make_board(tmp)
            readme = os.path.join(board, "README.md")
            os.chmod(readme, 0)
            try:
                for argv in (["add", "--text", "Look at it", "--today", "2026-01-15"],
                             ["done", "--id", ID, "--today", "2026-01-15"]):
                    code, _, err = run(argv[0], "--board", board, *argv[1:])
                    self.assertEqual(code, 1, argv)
                    self.assertIn(f"{board}: not a v3 board: README.md unreadable", err)
            finally:
                os.chmod(readme, 0o644)
            self.assertEqual(sorted(os.listdir(board)), sorted(["README.md", f"{ID}.md"]))


class Draw(unittest.TestCase):
    """``add`` without ``--id`` draws the nonce (``secrets.token_hex(4)``) and draws again while the id is held,
    at most 8 times in all (D3)."""

    TODAY = "2026-01-15"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        held_open = L.item_file("Held open", None, self.TODAY, None, None, "none", kind="fyi")
        held_closed = held_open.rstrip("\n") + "\n**Closed:** 2026-01-15\n"
        self.board = make_board(self.tmp.name, {
            f"{ID}.md": ITEM,
            f"{self.TODAY}-11111111.md": held_open,  # an open item's
            f"archive/2026-01/{self.TODAY}-22222222.md": held_closed,  # an archived item's
            f"{self.TODAY}-33333333.md": "Notes kept by hand, not an item.\n",  # a file no item is read from
        })
        self.before = snapshot(self.board)

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, draws: list[str]) -> tuple[tuple[int, str, str], mock.Mock]:
        with mock.patch.object(B, "_draw", side_effect=draws) as drawn:
            got = run("add", "--board", self.board, "--kind", "act", "--text", "Rotate the key", "--context", "TD-3",
                      "--due", "2026-01-22", "--today", self.TODAY, "--json")
        return got, drawn

    def test_the_draw_is_four_random_bytes(self):
        with mock.patch.object(B.secrets, "token_hex", return_value="0000000a") as token:
            self.assertEqual(B._draw(), "0000000a")
        token.assert_called_once_with(4)

    def test_a_first_draw_is_taken(self):
        (code, out, err), drawn = self.add(["0000000a", "0000000b"])
        self.assertEqual(code, 0, err)
        self.assertEqual(drawn.call_count, 1)
        got = json.loads(out)
        self.assertEqual(got["id"], f"{self.TODAY}-0000000a")
        self.assertEqual(got["paths"], [os.path.join(self.board, f"{self.TODAY}-0000000a.md")])
        self.assertIn("## Rotate the key\n", Path(self.board, f"{self.TODAY}-0000000a.md").read_text())

    def test_a_held_name_is_drawn_again(self):
        (code, out, err), drawn = self.add(["11111111", "22222222", "33333333", "0000000c"])
        self.assertEqual(code, 0, err)
        self.assertEqual(drawn.call_count, 4)  # an open item's, an archived one's and an unread file's names held
        self.assertEqual(json.loads(out)["id"], f"{self.TODAY}-0000000c")
        self.assertEqual(Path(self.board, f"{self.TODAY}-33333333.md").read_text(), "Notes kept by hand, not an item.\n")

    def test_eight_held_names_are_refused(self):
        (code, out, err), drawn = self.add(["11111111", "22222222", "33333333"] * 2 + ["11111111", "22222222",
                                                                                    "0000000d"])
        self.assertEqual(code, 1)
        self.assertEqual(drawn.call_count, 8)
        self.assertEqual(json.loads(out), {"action": "add", "refused": f"{self.board}: no free id after 8 draws"})
        self.assertEqual(snapshot(self.board), self.before)

    def test_a_given_id_draws_nothing(self):
        with mock.patch.object(B, "_draw", side_effect=AssertionError("drawn")):
            code, out, err = run("add", "--board", self.board, "--id", f"{self.TODAY}-0000000e", "--kind", "fyi",
                                 "--text", "The mirror moved", "--context", "none", "--today", self.TODAY, "--json")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["id"], f"{self.TODAY}-0000000e")


class AddParts(unittest.TestCase):  # v2.6: add --parts, a decide's Parts: snapshot (ledgerboard TD-050 B2)
    PART = ("## {}: A build\n\n**Priority:** Medium\n**Status:** Open\n**Blocked by:** decision (pat)\n"
            "**Part of:** {}\n\n**Why:** w.\n\n**Ask:** go?\n")
    NEW = "2026-01-15-5eed0001"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.board = make_board(self.tmp.name, {})
        self.led = os.path.join(self.tmp.name, "ledger")  # ledger/ beside the board
        os.makedirs(self.led)
        Path(self.led, "README.md").write_text("# Ledger\n\nLedgerboard: 2\n")
        Path(self.led, "TD-004.md").write_text("## TD-004: The parent\n\n**Priority:** Medium\n**Status:** Open\n\n**Why:** w.\n")
        Path(self.led, "TD-009.md").write_text(self.PART.format("TD-009", "TD-004"))
        Path(self.led, "TD-010.md").write_text(self.PART.format("TD-010", "TD-005"))  # not Part of TD-4

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, *more, kind="decide", context="TD-4 decision (pat)"):
        return run("add", "--board", self.board, "--id", self.NEW, *(["--kind", kind] if kind else []),
                   "--text", "Go on both?", "--context", context, "--due", "2026-01-20", "--answer", "Go",
                   "--answer", "Not yet",
                   *(["--detail", json.dumps({"context": "c", "question": "q", "recommended": "r"})]
                     if kind == "decide" else []),
                   "--today", "2026-01-15", *more)

    def test_takes_and_defaults(self):
        self.assertLessEqual({"parts", "ledger", "id"}, B.TAKES["add"])
        self.assertEqual(B.DEFAULTS["parts"], [])

    def test_ledger_without_parts_is_a_refusal_not_a_usage_error(self):
        code, _, err = self.add("--ledger", self.led)
        self.assertEqual(code, 1, err)
        self.assertIn("give --parts too", err)

    def test_no_parts_never_reads_a_ledger(self):
        os.rename(self.led, self.led + ".gone")
        code, _, err = self.add()
        self.assertEqual(code, 0, err)
        self.assertNotIn("**Parts:**", Path(self.board, f"{self.NEW}.md").read_text())

    def test_the_checks_run_in_order(self):
        before = snapshot(self.board)
        steps = [  # each refusal is the first failing step's; the board is never written
            ((self.add("--parts", "TD-9,", "--decided", "Go", kind=None)), 1, "a decided item takes none"),  # 1
            ((self.add("--parts", "TD-9,", kind=None)), 1, "empty piece"),  # 1: the options, then the pieces
            ((self.add("--parts", "TD-9", kind="act")), 1, "only a decide lists its parts"),  # 2: before the ledger
            ((self.add("--parts", "TD-9", "--ledger", os.path.join(self.tmp.name, "none"),
                       context="TD-4 decision (pat) — later")), 1, "context: not one entry"),  # 2: the helper
            ((self.add("--parts", "TD-9,TD-10", "--ledger", os.path.join(self.tmp.name, "none"))), 2, "no such ledger"),
            ((self.add("--parts", "TD-9,TD-10", context="TD-4 decision (kim)")), 1,  # 4: before the board's gate
             "the snapshot does not match the ledger: TD-9: does not carry decision (kim); TD-10: not Part of TD-4"),
        ]
        for (code, _, err), want_code, want in steps:
            self.assertEqual(code, want_code, err)
            self.assertIn(want, err)
            self.assertEqual(snapshot(self.board), before)

    def test_a_matching_snapshot_is_written(self):
        Path(self.led, "TD-010.md").write_text(self.PART.format("TD-010", "TD-004"))
        code, _, err = self.add("--parts", "TD-10", "--parts", "TD-9")
        self.assertEqual(code, 0, err)
        text = Path(self.board, f"{self.NEW}.md").read_text()
        self.assertIn("**Context:** TD-4 decision (pat)\n**Parts:** TD-9, TD-10\n**Due:**", text)


class HideNotes(unittest.TestCase):
    """``item_notes()`` (v2.4, SPEC *Notes on a hide*) and how the writer reports them."""

    LATE = "hide-late: Hide until: 2026-01-29 is after Due: 2026-01-20, so the item stays hidden past its deadline"

    def notes(self, line: str, today: str = "2026-01-15") -> list[str]:
        return L.item_notes(L.parse_board(line, warn=False)[0], date.fromisoformat(today))

    def test_the_rules(self):
        act = "- [ ] act 2026-01-10 (n/a) — Merge it. Context: PR #12. Due: 2026-01-20."
        self.assertEqual(self.notes(act), [])
        self.assertEqual(self.notes(act + " Hide until: 2026-01-18."), [])
        self.assertEqual(self.notes(act + " Hide until: 2026-01-20."), [])  # shows on its due date
        self.assertEqual(self.notes(act + " Hide until: 2026-01-29."), [self.LATE])
        # the day before D it is still hidden; on D the hide is spent
        self.assertEqual(self.notes(act + " Hide until: 2026-01-16.", "2026-01-15"), [])
        self.assertEqual(self.notes(act + " Hide until: 2026-01-16.", "2026-01-16"),
                         ["hide-spent: Hide until: 2026-01-16 has come, so it hides nothing; a snooze replaces it"])
        # spent, the late hide says only that it is spent: the rules exclude each other
        self.assertEqual(self.notes(act + " Hide until: 2026-01-29.", "2026-01-30"),
                         ["hide-spent: Hide until: 2026-01-29 has come, so it hides nothing; a snooze replaces it"])
        decided = ("- [ ] decide 2026-01-10 (n/a) — Pick one. Context: TD-7. Due: 2026-01-20. Hide until: 2026-01-29. "
                   "Answers: a | b. Decided: a (2026-01-12).")
        self.assertEqual(self.notes(decided),
                         ["hide-spent: a decided item is never hidden, so Hide until: 2026-01-29 hides nothing"])

    def test_a_note_is_no_fault(self):
        line = "- [ ] act 2026-01-10 (n/a) — Merge it. Context: PR #12. Due: 2026-01-20. Hide until: 2026-01-29."
        self.assertIsNone(L.item_problem(line))
        faults = [w for _, w in L.board_problems(V2_BOARD.replace(V2_BOARD.splitlines()[4], line), V2_BOARD)
                  if not w.startswith("ℹ")]  # the gate's own ℹ notes (no People:) are no fault either
        self.assertEqual(faults, [])

    def test_text_mode_prints_each_note_on_stderr_and_exits_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = make_board(tmp)
            code, out, err = run("snooze", "--board", board, "--id", ID, "--to", "2026-01-29", "--today", "2026-01-15")
            self.assertEqual(code, 0)
            self.assertIn("**Hide until:** 2026-01-29\n", Path(board, f"{ID}.md").read_text())
            self.assertEqual(out.splitlines()[-1], os.path.join(board, f"{ID}.md"))
            self.assertEqual(err.splitlines(), [f"{ID}: ℹ " + self.LATE])

    def test_a_plan_carries_them_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = make_board(tmp)
            code, out, _ = run("snooze", "--board", board, "--id", ID, "--to", "2026-01-29", "--today", "2026-01-15",
                               "--plan")
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out)["item_notes"], [{"id": ID, "note": self.LATE}])
            self.assertEqual(Path(board, f"{ID}.md").read_text(), ITEM)

    def test_which_writes_carry_the_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            board = make_board(tmp)
            _, out, _ = run("reply", "--board", board, "--id", ID, "--text", "ok", "--by", "pat",
                            "--today", "2026-01-15", "--plan")
            self.assertEqual(json.loads(out)["item_notes"], [])
            _, out, _ = run("done", "--board", board, "--id", ID, "--today", "2026-01-15", "--plan")
            got = json.loads(out)
            self.assertNotIn("item_notes", got)
            self.assertEqual(got["id"], ID)
            _, out, _ = run("add", "--board", board, "--id", "2026-01-15-0000000f", "--text", "Look at it",
                            "--due", "2026-01-20", "--today", "2026-01-15", "--json")
            got = json.loads(out)
            self.assertEqual(got["item_notes"], [])
            self.assertEqual(got["id"], "2026-01-15-0000000f")
            self.assertNotIn("line", got)


class Module(unittest.TestCase):
    def test_run_as_a_module(self):
        spec = importlib.util.find_spec("ledgerboard.board")
        self.assertIsNotNone(spec)


if __name__ == "__main__":
    unittest.main()
