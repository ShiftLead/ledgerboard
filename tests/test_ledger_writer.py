"""The ledger writer (``ledgerboard/ledger.py``, SPEC *The ledger writer*): what its fixtures do not show —
its imports, the UTC clock, the in-process resolver, a failed write or move, the link rewriter, and running
as a module."""

import ast
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ledgerboard import Refused  # noqa: E402
from ledgerboard import ledger as W  # noqa: E402

README = "# Ledger\n\nLedgerboard: 2\n"
E1 = ("## TD-001: The parser drops a trailing comment\n\n**Priority:** Medium\n**Added:** 2026-01-02\n"
      "**Status:** Open\n\n**Why:** a comment at the end of a file is lost.\n")


def ledger(tmp: str, **extra: str) -> str:
    d = os.path.join(tmp, "ledger")
    os.makedirs(d)
    for name, text in {"README.md": README, "TD-001.md": E1, **extra}.items():
        Path(d, name).write_text(text)
    return d


def run(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = W.main(list(argv))
        except SystemExit as e:
            code = e.code
    return code, out.getvalue(), err.getvalue()


class Boundary(unittest.TestCase):
    def test_imports_no_git_network_or_process(self):
        tree = ast.parse((ROOT / "ledgerboard" / "ledger.py").read_text(encoding="utf-8"))
        names = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        names |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        self.assertLessEqual(names, {"__future__", "argparse", "json", "os", "re", "sys", "collections", "datetime", "board"})

    def test_the_header_and_no_shebang(self):
        first = (ROOT / "ledgerboard" / "ledger.py").read_text(encoding="utf-8").splitlines()[:2]
        self.assertTrue(first[0].startswith("# ledgerboard v"))
        self.assertIn("SYNCED FILE — canonical copy: ShiftLead/ledgerboard ledgerboard/ledger.py", first[1])


class Clock(unittest.TestCase):
    def test_the_default_date_is_the_utc_clock(self):
        self.assertEqual(W._today(None), datetime.now(timezone.utc).date().isoformat())

    def test_an_aware_datetime_is_its_utc_date(self):
        late = datetime(2026, 1, 15, 23, 30, tzinfo=timezone(timedelta(hours=-5)))
        self.assertEqual(W._today(late), "2026-01-16")

    def test_a_naive_datetime_is_refused(self):
        with self.assertRaises(W.Unusable):
            W._today(datetime(2026, 1, 15, 12, 0))  # noqa: DTZ001  # naive on purpose

    def test_a_note_is_dated_by_the_utc_clock(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = ledger(tmp)
            plan = W.plan_edit(W.Ledger.open(d), "note", "TD-001", words="looked again")
            day = datetime.now(timezone.utc).date().isoformat()
            self.assertIn(f"- {day}: looked again\n", plan.changes[os.path.join(d, "TD-001.md")])


class InProcess(unittest.TestCase):
    def test_the_resolver_is_a_callback(self):
        asked = []

        def resolve(item):
            asked.append(item)
            return {"state": "open", "status": "Open"}

        with tempfile.TemporaryDirectory() as tmp:
            led = W.Ledger.open(ledger(tmp))
            plan = W.plan_edit(led, "set", "TD-001", fields={"Blocked by": "other-repo#TD-9"}, resolve=resolve,
                               today="2026-01-15")
            self.assertIn("other-repo#TD-9", asked)
            self.assertIn("**Blocked by:** other-repo#TD-9\n", next(iter(plan.changes.values())))

    def test_needs_comes_before_a_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = ledger(tmp)
            code, out, _ = run("set", "TD-1", "--blocked-by", "other-repo#TD-9, TD-040", "--ledger", d,
                               "--today", "2026-01-15", "--json")
            self.assertEqual(code, 3)
            self.assertIn('"needs": ["other-repo#TD-9"]', out)
            self.assertEqual(Path(d, "TD-001.md").read_text(), E1)

    def test_a_bad_resolved_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = ledger(tmp)
            bad = os.path.join(tmp, "r.json")
            Path(bad).write_text('{"TD-9": {"state": "open"}}')
            code, _, err = run("--pickable", "--ledger", d, "--resolved", bad, "--today", "2026-01-15")
            self.assertEqual(code, 2)
            self.assertIn("<repo>#TD-n", err)

    def test_a_refusal_is_raised_in_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            led = W.Ledger.open(ledger(tmp))
            with self.assertRaises(Refused):
                W.plan_edit(led, "set", "TD-001", fields={"Type": "chore"}, today="2026-01-15")


class Write(unittest.TestCase):
    def test_a_failed_write_exits_4_and_keeps_the_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = ledger(tmp)
            with mock.patch("ledgerboard.board.os.replace", side_effect=OSError("read-only")):
                code, _, err = run("set", "TD-1", "--priority", "High", "--ledger", d, "--today", "2026-01-15")
            self.assertEqual(code, 4)
            self.assertIn("every file restored", err)
            self.assertEqual(Path(d, "TD-001.md").read_text(), E1)
            self.assertEqual(sorted(os.listdir(d)), ["README.md", "TD-001.md"])

    def test_a_failed_move_restores_the_file_and_makes_no_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = ledger(tmp)
            real, old = os.unlink, os.path.join(d, "TD-001.md")

            def unlink(path):  # the old file's removal fails; every other unlink (the rollback's) is real
                if path == old:
                    raise OSError("busy")
                real(path)
            with mock.patch("ledgerboard.board.os.unlink", side_effect=unlink):
                code, _, err = run("archive", "TD-1", "--why", "fixed", "--ledger", d, "--today", "2026-01-15")
            self.assertEqual(code, 4, err)
            self.assertEqual(Path(d, "TD-001.md").read_text(), E1)
            self.assertFalse(Path(d, "archive").exists())

    def test_a_failed_rename_takes_back_the_directory_it_made(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = ledger(tmp)
            with mock.patch("ledgerboard.board.os.replace", side_effect=OSError("read-only")):
                code, _, _ = run("archive", "TD-1", "--why", "fixed", "--ledger", d, "--today", "2026-01-15")
            self.assertEqual(code, 4)
            self.assertEqual(sorted(os.listdir(d)), ["README.md", "TD-001.md"])

    def test_plain_output_is_the_path_and_its_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = ledger(tmp)
            code, out, _ = run("set", "TD-1", "--priority", "High", "--ledger", d, "--today", "2026-01-15")
            self.assertEqual((code, out.splitlines()), (0, [os.path.join(d, "TD-001.md")]))

    def test_a_newer_major_is_not_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = ledger(tmp, **{"README.md": "# Ledger\n\nLedgerboard: 9\n"})
            code, _, err = run("--pickable", "--ledger", d, "--today", "2026-01-15")
            self.assertEqual(code, 2)
            self.assertIn("not read", err)


class Relink(unittest.TestCase):
    def test_a_moved_file_keeps_its_targets(self):
        got = W.relink("[a](../plans/x.md#y) [b](TD-002.md \"t\") [c](dir/)", "docs/ledger", "docs/ledger/archive")
        self.assertEqual(got, "[a](../../plans/x.md#y) [b](../TD-002.md \"t\") [c](../dir/)")

    def test_what_is_left(self):
        text = ("[u](https://example.com/x.md) [m](mailto:a@example.com) [abs](/x.md) [h](#why) `[c](x.md)`\n"
                "```\n[f](x.md)\n```\n")
        self.assertEqual(W.relink(text, "docs/ledger", "docs/ledger/archive"), text)

    def test_every_link_form_moves(self):
        got = W.relink("[a](../n.md 'q') [b](<../my n.md>) [c](../n.md (p))\n[ref]: ../n.md#x\n",
                       "docs/ledger", "docs/ledger/archive")
        self.assertEqual(got, "[a](../../n.md 'q') [b](<../../my n.md>) [c](../../n.md (p))\n[ref]: ../../n.md#x\n")

    def test_a_fence_in_a_list_item_is_code(self):
        text = "- a step:\n\n      ```\n      [f](../n.md)\n      ```\n"
        self.assertEqual(W.relink(text, "docs/ledger", "docs/ledger/archive"), text)

    def test_a_link_to_a_moved_file_follows_it(self):
        got = W.relink("[x](ledger/TD-001.md#why) [y](ledger/TD-002.md)", "docs", "docs",
                       {"docs/ledger/TD-001.md": "docs/ledger/archive/TD-001.md"})
        self.assertEqual(got, "[x](ledger/archive/TD-001.md#why) [y](ledger/TD-002.md)")


class Moves(unittest.TestCase):
    def test_a_successor_in_another_repo_is_resolved_in_process(self):
        e2 = E1.replace("TD-001: The parser", "TD-002: After the parser").replace(
            "**Status:** Open\n", "**Status:** Open\n**Blocked by:** TD-001\n")
        with tempfile.TemporaryDirectory() as tmp:
            led = W.Ledger.open(ledger(tmp, **{"TD-002.md": e2}))
            asked = []

            def resolve(item):
                asked.append(item)
                return {"state": "open", "status": "Open"}
            plan = W.plan_archive(led, "TD-1", "the tool repo covers it", superseded_by="tools#TD-4",
                                  resolve=resolve, today="2026-01-15")
            self.assertIn("tools#TD-4", asked)
            self.assertEqual(plan.info["rewired"], ["TD-002"])
            self.assertIn("**Blocked by:** tools#TD-4", plan.changes[os.path.join(led.path, "TD-002.md")])
            self.assertIsNone(plan.changes[os.path.join(led.path, "TD-001.md")])


class MoveInputs(unittest.TestCase):
    def test_a_moved_entry_keeps_its_links_to_itself(self):
        e1 = E1.replace("is lost.", "is lost; [the fix](TD-001.md#fix).")
        with tempfile.TemporaryDirectory() as tmp:
            led = W.Ledger.open(ledger(tmp, **{"TD-001.md": e1}))
            arch = W.plan_archive(led, "TD-1", "fixed", today="2026-01-15")
            self.assertIn("[the fix](TD-001.md#fix)", arch.changes[os.path.join(led.path, "archive", "TD-001.md")])
            ren = W.plan_renumber(led, "TD-1", "TD-9", today="2026-01-15")
            self.assertIn("[the fix](TD-009.md#fix)", ren.changes[os.path.join(led.path, "TD-009.md")])

    def test_id_zero_and_an_empty_why_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = ledger(tmp)
            for argv in (["renumber", "TD-1", "--id", "TD-0"], ["archive", "TD-1", "--why", " "]):
                code, _, _ = run(*argv, "--ledger", d, "--today", "2026-01-15")
                self.assertEqual(code, 2, argv)
            self.assertEqual(sorted(os.listdir(d)), ["README.md", "TD-001.md"])


class Module(unittest.TestCase):
    def test_run_as_a_module(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = ledger(tmp)
            r = subprocess.run([sys.executable, "-m", "ledgerboard.ledger", "--summary", "--ledger", d,
                                "--today", "2026-01-15"], cwd=ROOT, capture_output=True, text=True, timeout=60, check=False)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("| TD-001 | The parser drops a trailing comment |", r.stdout)


if __name__ == "__main__":
    unittest.main()
