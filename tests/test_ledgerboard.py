"""Unit tests for the ledgerboard package: the properties the fixtures do not show on their own."""

import ast
import hashlib
import importlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import ledgerboard as L  # noqa: E402

TODAY = date(2026, 1, 15)  # the UTC date pickable() and check() take (v2.4)

LEDGER = """# Ledger

## TD-001: One

**Priority:** High
**Blocked by:** far#TD-009

## TD-002: Two

**Priority:** Low
"""


class Purity(unittest.TestCase):
    def test_imports_nothing_that_reaches_outside_the_text(self):
        tree = ast.parse((ROOT / "ledgerboard" / "__init__.py").read_text(encoding="utf-8"))
        names = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        names |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        self.assertLessEqual(names, {"__future__", "logging", "re", "collections", "dataclasses", "datetime", "typing"})

    def test_stdlib_only_and_no_shebang(self):
        first = (ROOT / "ledgerboard" / "__init__.py").read_text(encoding="utf-8").splitlines()[:3]
        self.assertTrue(first[0].startswith("# ledgerboard "))
        self.assertIn("SYNCED FILE — canonical copy: ShiftLead/ledgerboard ledgerboard/__init__.py", first[1])
        self.assertFalse(first[0].startswith("#!"))
        self.assertNotIn("SYNCED FILE", L.__doc__)


class Resolver(unittest.TestCase):
    def test_no_resolver_keeps_the_block(self):
        r = L.pickable(LEDGER, "", today=TODAY)
        self.assertEqual([e["id"] for e in r["blocked"]], ["TD-001"])
        self.assertIn("no resolver", r["entries"][0]["cross_repo"][0]["why"])

    def test_a_tuple_resolver(self):
        r = L.pickable(LEDGER, "", lambda item: ("archived", ""), today=TODAY)
        self.assertEqual([e["id"] for e in r["pickable"]], ["TD-001", "TD-002"])

    def test_a_mapping_resolver_keeps_its_extra_keys(self):
        r = L.pickable(LEDGER, "", lambda item: {"state": "open", "why": "", "root": "/x", "source": "origin/main"}, today=TODAY)
        x = r["entries"][0]["cross_repo"][0]
        self.assertEqual((x["item"], x["state"], x["root"], x["source"]), ("far#TD-009", "open", "/x", "origin/main"))

    def test_an_unknown_state_is_unresolved(self):
        r = L.pickable(LEDGER, "", lambda item: ("maybe", ""), today=TODAY)
        self.assertEqual(r["entries"][0]["cross_repo"][0]["state"], "unresolved")
        self.assertFalse(r["entries"][0]["pickable"])


class OddResolvers(unittest.TestCase):
    def test_odd_output_is_unresolved_never_an_error(self):
        for got in (None, ("open",), ("a", "b", "c"), {"state": "open"}, {"why": None}, {"state": "archived", "why": None}):
            x = L.pickable(LEDGER, "", lambda item, got=got: got, today=TODAY)["entries"][0]["cross_repo"][0]
            self.assertIn(x["state"], ("open", "archived", "unresolved"), got)
            self.assertIsInstance(x["why"], str, got)


class Check(unittest.TestCase):
    def test_a_standing_flag_is_information(self):
        bad = LEDGER.replace("**Priority:** Low", "**Priority:** Low\n**Type:** chore")
        recs = L.check(bad, "", old=bad, today=TODAY)
        self.assertTrue(all(r["level"] == "info" and r["standing"] for r in recs if r["kind"] == "type"))
        recs = L.check(bad, "", old=LEDGER, today=TODAY)
        self.assertTrue(any(r["level"] == "error" and r["kind"] == "type" for r in recs))


class Edits(unittest.TestCase):
    def test_every_edit_keeps_the_item_key(self):
        line = "- [ ] decide 2026-01-05 (session s) — Pick. Due: 2026-01-10. Answers: a | b."
        t = date(2026, 1, 15)
        for action, kw in (("done", {}), ("snooze", {"to": t}), ("decide", {"answer": "a"}),
                           ("reply", {"reply": "ok", "by": "Sam"})):
            self.assertEqual(L.item_key(L.edit_line(line, action, today=t, **kw)), L.item_key(line), action)

    def test_subjects_classify(self):
        for action in L.EDIT_ACTIONS:
            s = L.subject("tool", action, "2026-01-05 (session s) — X. Due: 2026-01-10.", to="2026-01-20", answer="a")
            self.assertEqual(L.subject_kind(s), "edit", s)
        self.assertEqual(L.subject_kind(L.subject("tool", "append", "2026-01-05 (session s) — X.")), "append")
        with self.assertRaises(L.Refused):
            L.subject("tool", "erase", "x")


RANKED = """# Ledger

## TD-001: First

**Priority:** High

## TD-002: Second

**Priority:** Low

## TD-003: Waits on the second

**Priority:** Medium
**Blocked by:** TD-002

## TD-004: Medium

**Priority:** Medium
"""


def _order(ledger, rank_text=None, **kw):
    return [e["id"] for e in L.pickable(ledger, "", rank_text=rank_text, **kw, today=TODAY)["entries"]]


class Rank(unittest.TestCase):
    def test_no_rank_file_is_priority_type_then_id(self):
        # TD-002 (Low) is TD-003's prerequisite: their card sits at TD-003's Medium key, ahead of TD-004
        self.assertEqual(_order(RANKED), ["TD-001", "TD-002", "TD-003", "TD-004"])

    def test_a_lined_card_keeps_its_place_through_a_priority_edit(self):
        rank_text = "TD-004: 0h\n"
        before = _order(RANKED, rank_text)
        self.assertEqual(before, ["TD-004", "TD-001", "TD-002", "TD-003"])
        edited = RANKED.replace("## TD-004: Medium\n\n**Priority:** Medium", "## TD-004: Medium\n\n**Priority:** Low")
        self.assertEqual(_order(edited, rank_text), before)
        # unlined, the same edit moves it
        self.assertEqual(_order(edited)[-1], "TD-004")

    def test_a_newcomer_takes_its_cards_key(self):
        led = RANKED + "\n## TD-005: New build\n\n**Priority:** High\n**Blocked by:** TD-004\n"
        r = L.pickable(led, "", rank_text="TD-004: 3z\n", today=TODAY)
        keys = {e["id"]: (e["key"], e["card_key"]) for e in r["entries"]}
        self.assertEqual(keys["TD-005"], ("1|0|000005", "3z"))
        self.assertEqual([e["id"] for e in r["entries"]][-2:], ["TD-004", "TD-005"])

    def test_the_repo_is_the_implicit_keys_last_component(self):
        r = L.pickable(RANKED, "", repo="far", today=TODAY)
        self.assertEqual(r["entries"][0]["key"], "1|0|000001|far")

    def test_rank_flags_reach_check(self):
        recs = L.check(RANKED, "", old=RANKED, rank_text="TD-1 0h\n", today=TODAY)
        self.assertEqual([(r["kind"], r["level"], r["standing"]) for r in recs if r["kind"] != "status"],
                         [("rank", "error", False)])
        # v2.7: RANKED is a v1 ledger whose entries have no Status, so each carries a status record, ℹ, never standing
        self.assertEqual({(r["level"], r["standing"]) for r in recs if r["kind"] == "status"}, {("info", False)})

    def test_set_rank_round_trips_and_keeps_other_lines(self):
        text = "# head\n# two\nTD-1: 0h\nTD-7: 1|0|000007\nTD-2: 3a\n"
        out = L.set_rank(text, {"TD-9": L.midpoint("0h", "1|0|000007"), "TD-2": None})
        self.assertEqual(out, "# head\n# two\nTD-1: 0h\nTD-9: 0r\nTD-7: 1|0|000007\n")
        self.assertEqual(L.rank(out), ({"TD-1": "0h", "TD-9": "0r", "TD-7": "1|0|000007"}, []))
        self.assertEqual(L.set_rank(out, {}), out)

    def test_midpoints_keep_room(self):
        lo, hi = "1|0|000001", "1|0|000002"
        for _ in range(200):
            m = L.midpoint(lo, hi)
            self.assertLess(L.key_order(lo), L.key_order(m))
            self.assertLess(L.key_order(m), L.key_order(hi))
            hi = m
        top = None
        for _ in range(50):
            m = L.midpoint(None, top)
            if top is not None:
                self.assertLess(L.key_order(m), L.key_order(top))
            top = m

    def test_components_join_both_directions(self):
        led = RANKED + "\n## TD-005: Names the first\n\n**Priority:** Low\n**Blocked by:** TD-001, x#TD-9\n"
        comps = L.components(L.entries(led))
        self.assertEqual([c["ids"] for c in comps], [["TD-001", "TD-005"], ["TD-002", "TD-003"], ["TD-004"]])
        self.assertEqual(comps[0]["cross_repo"], ["x#TD-9"])

    def test_review_findings(self):  # ledgerboard#13's review: each a failing input before its fix
        with self.assertRaises(L.Refused):
            L.midpoint(None, "0")  # nothing sorts below 0; never the invalid "|i"
        self.assertEqual(L.midpoint("a", "a|0|"), "a|0")
        self.assertEqual(L.set_rank("# c\r\nTD-001: 1\r\n", {"TD-001": "2"}), "# c\r\nTD-001: 2\r\n")
        self.assertEqual(L.set_rank("# c\r\nTD-001: 1\r\n", {"TD-002": "2"}), "# c\r\nTD-001: 1\r\nTD-002: 2\r\n")
        with self.assertRaises(L.Refused):
            L.set_rank("", {"TD-002": "\u00e9"})
        led = "## TD-7: low\n\n**Priority:** Low\n\n## TD-008: high\n\n**Priority:** High\n**Blocked by:** TD-007\n"
        self.assertEqual(_order(led), ["TD-7", "TD-008"])
        self.assertEqual(L.pickable(led, "", rank_text="TD-0007: 0h\n", today=TODAY)["entries"][0]["key"], "0h")


def _stamped_runner(tmp: Path) -> Path:
    """A copy of fixtures/run.py alone in ``<tmp>/fixtures/``, its set stamped v1.0 (TD-040): the made-up
    modules below are v1.0, and --check-header checks the set's MANIFEST beside their headers."""
    run = tmp / "fixtures" / "run.py"
    run.parent.mkdir(parents=True)
    shutil.copy2(ROOT / "fixtures" / "run.py", run)
    subprocess.run([sys.executable, str(run), "--stamp", "1.0"], capture_output=True, check=True)
    return run


class Header(unittest.TestCase):
    def test_check_header(self):
        tmpdir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmpdir)
        run = [sys.executable, str(_stamped_runner(tmpdir)), "--check-header", "--module"]
        body = b"# SYNCED FILE\n\"\"\"doc\"\"\"\n"
        ok = f"# ledgerboard v1.0 sha256:{hashlib.sha256(body).hexdigest()}\n".encode() + body
        tmp = tmpdir / "_header_tmp.py"
        tmp.write_bytes(ok)
        self.assertEqual(subprocess.run([*run, str(tmp)], capture_output=True, check=False).returncode, 0)
        tmp.write_bytes(ok + b"# edited\n")
        self.assertEqual(subprocess.run([*run, str(tmp)], capture_output=True, check=False).returncode, 1)


def _stamped(body: bytes, version: str = "1.0") -> bytes:
    return f"# ledgerboard v{version} sha256:{hashlib.sha256(body).hexdigest()}\n".encode() + body


class Package(unittest.TestCase):
    """TD-015: the module is a package, ``ledgerboard/``, vendored whole. Its files import each other
    relatively, so the same bytes load as a top-level package and as a subpackage. A probe file stands in
    for the writers to come, importing the module the way they will."""

    PROBE = b"# probe\nfrom . import item_key\n\nKEY = item_key\n"

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)

    def copy(self, into: Path) -> Path:
        pkg = into / "ledgerboard"
        shutil.copytree(ROOT / "ledgerboard", pkg, ignore=shutil.ignore_patterns("__pycache__"))
        (pkg / "probe.py").write_bytes(self.PROBE)
        return pkg

    def py(self, path: Path, code: str):
        return subprocess.run([sys.executable, "-I", "-c", f"import sys; sys.path.insert(0, {str(path)!r}); {code}"],
                              capture_output=True, text=True, check=False)

    def test_no_module_file_beside_the_package(self):  # Python would prefer the package; a stale file confuses readers
        self.assertFalse((ROOT / "ledgerboard.py").exists())
        self.assertEqual(Path(L.__file__).resolve(), ROOT / "ledgerboard" / "__init__.py")

    def test_loads_as_a_top_level_package(self):
        self.copy(self.tmp)
        r = self.py(self.tmp, "import ledgerboard; from ledgerboard import probe; "
                              "assert probe.KEY is ledgerboard.item_key; print(ledgerboard.__name__)")
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "ledgerboard"), r.stderr)

    def test_loads_as_a_subpackage(self):
        (self.tmp / "outer").mkdir()
        (self.tmp / "outer" / "__init__.py").write_text("")
        self.copy(self.tmp / "outer")
        r = self.py(self.tmp, "from outer import ledgerboard; from outer.ledgerboard import probe; "
                              "assert probe.KEY is ledgerboard.item_key; import sys; "
                              "assert 'ledgerboard' not in sys.modules; print(ledgerboard.__name__)")
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "outer.ledgerboard"), r.stderr)

    def test_the_fixtures_run_against_a_package_copy(self):  # --module takes the directory, its imports resolved
        pkg = self.copy(self.tmp)
        r = subprocess.run([sys.executable, str(ROOT / "fixtures" / "run.py"), "--module", str(pkg)],
                           capture_output=True, text=True, check=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        before = set(sys.modules)
        self.addCleanup(lambda: [sys.modules.pop(m) for m in set(sys.modules) - before])
        spec = importlib.util.spec_from_file_location("_fixture_run", ROOT / "fixtures" / "run.py")
        fixture_run = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixture_run)
        mod = fixture_run.load(pkg)
        self.assertIs(importlib.import_module(mod.__name__ + ".probe").KEY, mod.item_key)

    def test_check_header_reads_every_package_file(self):
        pkg = self.tmp / "ledgerboard"
        pkg.mkdir()
        run = [sys.executable, str(_stamped_runner(self.tmp)), "--check-header", "--module", str(pkg)]

        def check():
            return subprocess.run(run, capture_output=True, text=True, check=False)
        (pkg / "__init__.py").write_bytes(_stamped(b'"""doc"""\n'))
        (pkg / "board.py").write_bytes(_stamped(b"from . import x\n"))
        r = check()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("fixtures: ok (v1.0, 1 files)", r.stdout)
        (pkg / "board.py").write_bytes(_stamped(b"from . import x\n") + b"# edited\n")
        r = check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("board.py", r.stdout)
        (pkg / "board.py").write_bytes(_stamped(b"from . import x\n", "1.1"))
        r = check()
        self.assertEqual(r.returncode, 1)
        self.assertIn("different releases", r.stdout)
        (pkg / "board.py").write_bytes(b"from . import x\n")
        self.assertIn("not a release header", check().stdout)


class Fixtures(unittest.TestCase):
    def test_fixtures_pass(self):
        r = subprocess.run([sys.executable, str(ROOT / "fixtures" / "run.py")], capture_output=True, text=True, check=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)



class AnswerConsequences(unittest.TestCase):
    LINE = ("- [ ] decide 2026-01-05 (session s-1) — Pick. Context: TD-040. Due: 2026-01-20. "
            "Answers: On disk (default) — the next run reads it back | In memory — cold — every time | Not now.")

    def test_labels_consequences_and_the_default_are_read_apart(self):
        text = self.LINE[len("- [ ] "):]
        self.assertEqual(L.parse_answers(text), ["On disk", "In memory", "Not now"])
        self.assertEqual(L.parse_consequences(text), ["the next run reads it back", "cold — every time", ""])
        self.assertEqual(L.parse_default(text), "On disk")

    def test_decided_line_reads_back_as_written(self):
        line = L.decided_line("Pick", "TD-40", ["On disk — the next run reads it back", "Not now"], 0, "On disk", "2026-01-15")
        text = line[len("- [ ] "):].rstrip("\n")
        self.assertEqual(L.parse_answers(text), ["On disk", "Not now"])
        self.assertEqual(L.parse_consequences(text), ["the next run reads it back", ""])
        self.assertEqual(L.parse_default(text), "On disk")

    def test_a_decide_edit_records_the_label_and_keeps_the_consequences(self):
        out = L.edit_line(self.LINE, "decide", answer="In memory", today=date(2026, 1, 15))
        text = out[len("- [ ] "):].rstrip("\n")
        self.assertEqual(L.parse_decided(text), ("In memory", date(2026, 1, 15)))
        self.assertEqual(L.parse_consequences(text), ["the next run reads it back", "cold — every time", ""])
        self.assertEqual(L.item_key(out), L.item_key(self.LINE))

    def test_spacing_around_a_consequence_is_not_part_of_it(self):
        self.assertEqual(L.split_answer("A —   leads on  "), ("A", "leads on", False))
        self.assertEqual(L.split_answer("A (default) — x"), ("A", "x", True))
        self.assertEqual(L.split_answer("A — x (default)"), ("A", "x", True))  # marked whole, as before v1.3
        self.assertEqual(L.split_answer("B —"), ("B", "", False))

    def test_deciding_the_default_keeps_its_mark_and_consequence(self):
        out = L.edit_line(self.LINE, "decide", answer="On disk", today=date(2026, 1, 15))
        text = out[len("- [ ] "):].rstrip("\n")
        self.assertEqual(L.parse_decided(text), ("On disk", date(2026, 1, 15)))
        self.assertEqual(L.parse_default(text), "On disk")
        self.assertEqual(L.parse_consequences(text)[0], "the next run reads it back")

    def test_decided_line_refuses_a_consequence_shaped_like_a_reply(self):
        with self.assertRaises(L.Refused):
            L.decided_line("Pick", "TD-40", ["A — Sam, 2026-01-01: yes", "B"], 0, "A", "2026-01-15")

    def test_a_look_reads_its_labels_with_consequences_beside(self):
        text = "look 2026-01-05 (session s-1) — Renders? Due: 2026-01-20. Answers: Works — ship it | Not right: <what> — fix first."
        self.assertEqual(L.parse_answers(text), ["Works", "Not right: <what>"])
        self.assertTrue(L.is_not_right_form(L.parse_answers(text)[1]))

    def test_decided_line_writes_one_mark_and_no_empty_consequence(self):
        line = L.decided_line("Pick", "TD-40", ["A — x (default)", "B — ", "C"], 0, "A", "2026-01-15")
        self.assertIn("Answers: A (default) — x | B | C.", line)



class Gates(unittest.TestCase):
    """v2.4: `Blocked by`'s gates, and the today pickable() and check() take (SPEC *The ledger*)."""

    UNTIL = "# Ledger\n\n## TD-001: Waits for a date\n\n**Priority:** Low\n**Blocked by:** until 2026-01-15\n"

    def picked(self, today):
        return [e["id"] for e in L.pickable(self.UNTIL, "", today=today)["pickable"]]

    def test_today_is_required(self):
        with self.assertRaises(TypeError):
            L.pickable(self.UNTIL, "")
        with self.assertRaises(TypeError):
            L.check(self.UNTIL, "")

    def test_an_until_holds_before_its_date_and_lifts_on_it(self):
        self.assertEqual(self.picked(date(2026, 1, 14)), [])
        self.assertEqual(self.picked("2026-01-15"), ["TD-001"])

    def test_today_is_the_utc_date(self):
        late = datetime(2026, 1, 14, 23, 30, tzinfo=timezone(timedelta(hours=-5)))  # 04:30 UTC on the 15th
        self.assertEqual(self.picked(late), ["TD-001"])
        for bad in (datetime(2026, 1, 15, 12, 0), "15 Jan", None):  # noqa: DTZ001 — a naive datetime is refused
            with self.subTest(today=bad), self.assertRaises(ValueError):
                L.pickable(self.UNTIL, "", today=bad)

    def test_parse_blocked_keeps_every_block_for_its_callers(self):
        self.assertEqual(L.parse_blocked("TD-1, decision (pat), until 2026-02-01, event (x), hold, soon"),
                         (["TD-1"], ["pat"], ["until 2026-02-01", "event (x)", "hold", "soon"]))
        self.assertEqual(L.parse_blocked("decision (designer), decision (kim) — after it, TD-9"),
                         ([], ["designer", "kim"], []))

    def test_an_ask_removed_is_an_error_on_the_edit(self):
        was = "# Ledger\n\n## TD-001: x\n\n**Priority:** Low\n**Blocked by:** decision (pat)\n\n**Ask:** go?\n"
        now = was.replace("**Ask:** go?", "**Why:** w")
        got = [(r["kind"], r["level"]) for r in L.check(now, "", old=was, today=TODAY) if r["kind"] == "ask-missing"]
        self.assertEqual(got, [("ask-missing", "error")])
        got = [(r["kind"], r["level"]) for r in L.check(now, "", old=now, today=TODAY) if r["kind"] == "ask-missing"]
        self.assertEqual(got, [("ask-missing", "info")])

    def test_a_crlf_entry_reads_its_event_gate_and_section(self):
        led = ("# Ledger\n\n## TD-001: x\n\n**Priority:** Low\n**Blocked by:** event (ships)\n\n"
               "**Ask:** none.\n\n**Event (ships):** it ships.\ncheck: pr-merged acme/tools#3\n").replace("\n", "\r\n")
        self.assertEqual([r["kind"] for r in L.check(led, "", today=TODAY) if r["kind"].startswith(("event", "blocked"))], [])
        self.assertEqual(L.pickable(led, "", today=TODAY)["entries"][0]["blocked_by"], ["event (ships)"])

    def test_a_giant_pr_number_is_refused_not_raised(self):
        self.assertIn("1 to 18", L.parse_check("pr-merged a#" + "9" * 5000)["problem"])

    def test_waits_is_never_a_gate(self):
        led = "# Ledger\n\n## TD-001: x\n\n**Priority:** Low\n**Waits:** until 2027-01-01\n"
        self.assertEqual([e["id"] for e in L.pickable(led, "", today=TODAY)["pickable"]], ["TD-001"])


class Lifts(unittest.TestCase):
    """v2.4: lifting a gate writes the UTC date, and the decide lift composes lift_gate (SPEC *Lifting a gate*)."""

    ENTRY = "## TD-001: x\n\n**Priority:** Low\n**Blocked by:** until 2026-01-15\n\n**Why:** w.\n"
    ITEM = ("- [ ] decide 2026-01-10 (n/a) — Go? Context: TD-002 decision (pat). Due: 2026-01-20. "
            "Answers: Go | Not yet.")
    GATED = "## TD-002: y\n\n**Priority:** Low\n**Blocked by:** decision (pat)\n\n**Ask:** go?\n"

    def test_a_lift_is_dated_by_the_utc_day(self):
        late = datetime(2026, 1, 14, 23, 30, tzinfo=timezone(timedelta(hours=-5)))  # 04:30 UTC on the 15th
        self.assertIn("- 2026-01-15: gate lifted: until 2026-01-15 — by box-1; date reached",
                      L.lift_gate(self.ENTRY, "until 2026-01-15", "box-1", today=late))
        with self.assertRaises(L.Refused):
            L.lift_gate(self.ENTRY, "until 2026-01-15", "box-1", today=datetime(2026, 1, 15, 12, 0))  # noqa: DTZ001

    def test_the_decide_lift_writes_what_lift_gate_writes(self):
        got = L.decide_lift(self.ITEM, {"TD-002": self.GATED}, "go", "pat", TODAY, ["pat"], None)
        self.assertEqual(got, {"TD-002": L.lift_gate(self.GATED, "decision (pat)", "pat", answer="go", today=TODAY)})
        self.assertTrue(L.closes(self.ITEM, "go", got))
        self.assertFalse(L.closes(self.ITEM, "go", {"TD-002": self.GATED}))

    def test_a_lifted_entry_is_pickable(self):
        got = L.decide_lift(self.ITEM, {"TD-002": self.GATED}, "Go", "pat", TODAY, ["pat"], None)["TD-002"]
        self.assertEqual([e["id"] for e in L.pickable("# Ledger\n\n" + got, "", today=TODAY)["pickable"]], ["TD-002"])
        self.assertEqual([r for r in L.check("# Ledger\n\n" + got, "", today=TODAY) if r["level"] == "error"], [])


class Migrate(unittest.TestCase):
    """v2.7 (TD-058 B1): migrate_entry() is pure and never raises for an entry's text; its output is stable."""

    def test_never_raises_and_a_second_run_changes_nothing(self):
        spec = json.loads((ROOT / "fixtures" / "migrate" / "cases.json").read_text(encoding="utf-8"))
        for c in spec["migrate_entry"]:
            for cut in range(0, len(c["text"]) + 1, 7):  # every prefix of every fixture entry, both places
                for archived in (False, True):
                    got = L.migrate_entry(c["text"][:cut], archived=archived, today="2026-11-11",
                                          closed_date="2026-10-20", kinds={"designed": "stage-a"})
                    self.assertEqual(sorted(got), ["changes", "listed", "stops", "text"])
                    if got["changes"]:
                        again = L.migrate_entry(got["text"], archived=archived, today="2026-11-11",
                                                closed_date="2026-10-20", kinds={"designed": "stage-a"})
                        self.assertEqual((again["text"], again["changes"], again["stops"]), (got["text"], [], []))
                        self.assertIsNone(L.status_problem(got["text"], archived=archived))


class DetailRecommended(unittest.TestCase):
    """TD-069: the writer opens a decide's Recommended with its default's label; words that already do are refused."""

    def line(self, recommended):
        return L.item_line("Go on?", "2026-01-20", "2026-01-15", "w-1", None, "TD-4", kind="decide",
                           answers=["Go — it ships", "Not yet"], default=0,
                           detail={"context": "c.", "question": "q?", "recommended": recommended})

    def test_a_recommended_opening_with_the_label_and_its_dash_is_refused(self):
        for words in ("Go — it is ready", "go  —  it is ready", "GO —"):
            with self.assertRaises(L.Refused) as r:
                self.line(words)
            self.assertIn("Go —", str(r.exception))

    def test_the_label_once_is_written(self):
        self.assertIn("**Recommended:** Go — it is ready.", self.line("it is ready"))
        self.assertIn("**Recommended:** Go — Going now is safe.", self.line("Going now is safe"))
        self.assertIn("**Recommended:** Go — Go, since it is ready.", self.line("Go, since it is ready"))


class Parts(unittest.TestCase):
    """v2.6: the writer of a decide's `Parts:` (ledgerboard TD-050 B1) — what the fixtures' JSON cannot carry."""

    DETAIL = {"context": "c.", "question": "q?", "recommended": "go."}
    PART = "## {}: x\n\n**Priority:** Low\n**Status:** Open\n**Blocked by:** decision (pat)\n**Part of:** TD-4\n\n**Why:** w.\n"
    ENTRIES = {"TD-4": "## TD-4: p\n\n**Priority:** Low\n**Status:** Open\n\n**Why:** w.\n",
               "TD-9": PART.format("TD-9"), "TD-10": PART.format("TD-10")}

    def line(self, context="TD-4 decision (pat)", parts=("TD-10", "TD-9")):
        return L.item_line("Go on the builds?", "2026-01-20", "2026-01-15", "w-1", None, context, kind="decide",
                           answers=["Go", "Not yet"], detail=self.DETAIL, parts=list(parts))

    def test_the_line_reads_back_with_its_parts_in_number_order(self):
        got = L.parse_board(self.line(), warn=False)
        self.assertEqual(got[0].parts, ["TD-9", "TD-10"])
        self.assertEqual(L.parts_problems(self.line(), self.ENTRIES), [])

    def test_a_tuple_of_parts_is_a_list(self):
        self.assertIn(" Parts: TD-9, TD-10. Due:", self.line(parts=("TD-9", "TD-10")))

    def test_item_line_and_parts_problems_share_their_line_faults(self):
        for context, parts in (("TD-4, TD-5 decision (pat)", ["TD-9"]), ("TD-4 event (go)", ["TD-9"]),
                               ("TD-4 decision (pat) — later", ["TD-9"]), ("TD-4 decision (pat)", ["TD-9", "TD-009"]),
                               ("TD-4 decision (pat)", ["TD-004"]), ("TD-4 decision (pat)", ["other#TD-9"])):
            with self.assertRaises(L.Refused) as r:
                self.line(context, parts)
            hand = (f"- [ ] decide 2026-01-15 (n/a) — Go? Context: {context}. Parts: {', '.join(parts)}. "
                    "Due: 2026-01-20. Answers: Go | Not yet.")
            self.assertEqual(L.parts_problems(hand, self.ENTRIES), [f"line: {r.exception}"])

    def test_inputs_json_cannot_carry(self):
        line = self.line()
        self.assertEqual(L.parts_problems(line.encode(), self.ENTRIES), [])
        self.assertEqual(L.parts_problems(line, [("TD-9", "x")]), ["TD-4: missing", "TD-9: missing", "TD-10: missing"])
        self.assertEqual(L.parts_problems(line, {**self.ENTRIES, 9: "x", b"TD-9": "x", None: 5}), [])
        for archived in (None, 5, object(), [b"TD-9", 9, ("TD-9",)]):
            self.assertEqual(L.parts_problems(line, self.ENTRIES, archived), [])
        self.assertEqual(L.parts_problems(line, self.ENTRIES, iter(["TD-009"])), ["TD-9: archived"])

        class Raising(dict):
            def items(self):
                raise RuntimeError("a hostile mapping")

        def raising():
            yield "TD-9"
            raise RuntimeError("a hostile iterable")
        self.assertEqual(L.parts_problems(line, Raising(self.ENTRIES)), ["TD-4: missing", "TD-9: missing", "TD-10: missing"])
        self.assertEqual(L.parts_problems(line, self.ENTRIES, raising()), ["TD-9: archived"])

    def test_parts_problems_never_raises(self):
        import random
        rnd = random.Random(2026)
        words = ["TD-4", "TD-9", "TD-009", "TD-10", "TD-١٢", "other#TD-9", "TD-" + "9" * 40, "decision (pat)",
                 "event (x)", "Context:", "Parts:", "Due: 2026-01-20.", "Answers: Go | Not yet.", "Decided: Go (by pat)",
                 "- [ ]", "- [x]", "\n", "  - **Context:** c.", ",", ".", "—", "foo", "(", ")", "#", ""]
        keys = ["TD-4", "TD-9", "TD-009", "TD-10", "x", 9, None, b"TD-9", "TD-" + "1" * 5000]
        values = [self.ENTRIES["TD-4"], self.ENTRIES["TD-9"], "words", None, 5, b"bytes", self.PART.format("TD-009")]
        for _ in range(1500):
            line = "- [ ] decide 2026-01-15 (n/a) — " + " ".join(rnd.choice(words) for _ in range(rnd.randint(0, 14)))
            ents = {rnd.choice(keys): rnd.choice(values) for _ in range(rnd.randint(0, 5))}
            archived = rnd.choice([(), ["TD-9"], "TD-9", None, 5, [None, "TD-4", 5]])
            self.assertIsInstance(L.parts_problems(line, ents, archived), list)
            self.assertIsInstance(L.parts_problems(line.replace("decide 2026-01-15 (n/a) — ", ""), rnd.choice(
                [ents, None, 5, "x"]), archived), list)


if __name__ == "__main__":
    unittest.main()


class LedgerDirectory(unittest.TestCase):
    """v2.0: a ledger as a directory, read back as one text by ``load()`` with the caller's I/O."""

    FILES = {"README.md": "# Ledger\n\nLedgerboard: 2\n",
             "TD-10.md": "## TD-10: Ten\n\n**Priority:** Low\n",
             "TD-002.md": "## TD-002: Two\n\n**Priority:** High\n**Blocked by:** TD-001\n",
             "notes.txt": "not an entry",
             "archive/TD-001.md": "## TD-001: One\n\n**Priority:** High\n"}

    def io(self, files):
        return L._dict_ls(files), files.get

    def test_load_joins_the_readme_then_entries_in_id_order(self):
        led, arc = L.load("", *self.io(self.FILES))
        self.assertEqual([e["id"] for e in L.entries(led)], ["TD-002", "TD-10"])
        self.assertEqual([e["id"] for e in L.entries(arc)], ["TD-001"])
        self.assertTrue(led.startswith("# Ledger\n\nLedgerboard: 2\n\n## TD-002"))
        self.assertEqual(L.format_major(led), 2)
        self.assertIsNone(L.version_problem(led))
        self.assertEqual([e["id"] for e in L.pickable(led, arc, today=TODAY)["pickable"]], ["TD-002", "TD-10"])

    def test_load_reads_a_v1_file_and_its_archive_beside_it(self):
        files = {"docs/technical_debt.md": LEDGER, "docs/technical_debt_archive.md": "## TD-009: x\n"}
        ls = lambda p: None if p.endswith(".md") else sorted(files)  # noqa: E731
        self.assertEqual(L.load("docs/technical_debt.md", ls, files.get), (LEDGER, "## TD-009: x\n"))

    def test_a_missing_readme_or_archive_reads_as_empty(self):
        files = {"TD-001.md": "## TD-001: One\n"}
        self.assertEqual(L.load("", *self.io(files)), ("## TD-001: One\n", ""))

    def test_entry_path_finds_the_one_file_open_or_archived_by_number(self):
        ls, _ = self.io(self.FILES)
        self.assertEqual(L.entry_path("", "TD-2", ls), "TD-002.md")
        self.assertEqual(L.entry_path("", "TD-001", ls), "archive/TD-001.md")
        self.assertIsNone(L.entry_path("", "TD-003", ls))
        self.assertIsNone(L.entry_path("docs/technical_debt.md", "TD-001", lambda p: None))

    def test_split_and_load_round_trip(self):
        files = L.split(LEDGER, "# Archive\n\n## TD-009: Nine\n\nbody\n")
        self.assertEqual(sorted(files), ["README.md", "TD-001.md", "TD-002.md", "archive/TD-009.md"])
        self.assertIn("Ledgerboard: 2", files["README.md"])
        led, arc = L.load("", *self.io(files))
        self.assertEqual(L.entries(led), L.entries(LEDGER))
        self.assertEqual(files["archive/TD-009.md"], "## TD-009: Nine\n\nbody\n")

    def test_split_keeps_a_commented_heading_inside_its_entry(self):
        led = "# L\n\n## TD-001: One\n\nx\n<!--\n## TD-002: Not an entry\n-->\n"
        files = L.split(led, "")
        self.assertEqual(sorted(files), ["README.md", "TD-001.md"])
        self.assertIn("Not an entry", files["TD-001.md"])

    def test_split_refuses_what_it_would_lose(self):
        for led, why in (("# L\n\n## TD-001: One\n\n## Notes\n\nkept nowhere\n", "is not an entry"),
                         ("# L\n\n## TD-001: One\n\n## TD-1: Again\n", "appears twice")):
            with self.assertRaises(L.Refused) as cm:
                L.split(led, "")
            self.assertIn(why, str(cm.exception))

    def test_split_drops_only_the_summary_section(self):
        led = "# L\n\n## Summary\n\n| ID | T |\n|--|--|\n| TD-001 | One |\n\n## TD-001: One\n"
        files = L.split(led, "")
        self.assertNotIn("| TD-001 |", "".join(files.values()))

    def test_split_refuses_a_ledger_that_is_not_v1(self):
        with self.assertRaises(L.Refused):
            L.split("# L\n\nLedgerboard: 3\n\n## TD-001: One\n", "")

    def test_split_keeps_a_fields_line_from_the_summary_section(self):
        led = "# T\n\n## Summary\n\nFields: Area = a | b\n\n| ID |\n|--|\n\n## TD-001: One\n\n**Area:** a\n"
        files = L.split(led, "")
        new, _ = L.load("", *self.io(files))
        self.assertEqual(L.declared(new), L.declared(led))
        self.assertEqual(files["README.md"], "# T\n\nLedgerboard: 2\n\nFields: Area = a | b\n")

    def test_split_refuses_an_entry_with_a_comment_left_open(self):
        led = "# L\n\n## TD-001: One\n\n<!-- unclosed\n\n## TD-002: Two\n"
        with self.assertRaises(L.Refused) as cm:
            L.split(led, "")
        self.assertIn("not closed", str(cm.exception))

    def test_split_takes_entries_in_any_order(self):
        files = L.split("# L\n\n## TD-002: Two\n\n## TD-001: One\n", "")
        self.assertEqual(sorted(files), ["README.md", "TD-001.md", "TD-002.md"])

    def test_v2_problems_names_a_file_that_would_not_read_as_itself(self):
        bad = {"README.md": "# L\n\nLedgerboard: 2\n",
               "TD-001.md": "## TD-001: One\n\n<!-- never closed\n",
               "TD-002.md": "## TD-002: Two\n",
               "TD-007.md": "## TD-008: Wrong number\n",
               "TD-009.md": "no heading\n",
               "archive/TD-2.md": "## TD-2: Again\n"}
        got = L.v2_problems("", *self.io(bad))
        self.assertEqual(len(got), 4, got)
        for name, why in (("TD-001.md", "not closed"), ("TD-007.md", "TD-008"), ("TD-009.md", "none"),
                          ("archive/TD-2.md", "has a file already")):
            self.assertTrue(any(g.startswith(name) and why in g for g in got), (name, got))
        self.assertEqual(L.v2_problems("", *self.io(self.FILES)), [])
        self.assertEqual(L.v2_problems("x.md", lambda p: None, lambda p: None), [])


def _entry(n: int, prio: str = "Medium", *lines: str) -> str:
    return "\n".join([f"## TD-{n:03d}: entry {n}", "", f"**Priority:** {prio}", *lines, ""]) + "\n"


class PartOf(unittest.TestCase):  # v2.1: a part names its parent (ShiftLead ADR 2026-10-27, Part of)
    DESIGN = (_entry(1, "Medium") + _entry(2, "Low", "**Part of:** TD-001 (its build)")
              + _entry(3, "High", "**Part of:** TD-1", "**Blocked by:** TD-002"))
    ARCHIVE = _entry(4, "Medium", "**Part of:** TD-001")

    def kinds(self, led, arc="", old=None):
        return [(r["id"], r["kind"], r["level"]) for r in L.check(led, arc, old=old, today=TODAY)]

    def test_a_parent_with_open_parts_is_not_pickable_and_keeps_its_blockers_apart(self):
        r = L.pickable(self.DESIGN, self.ARCHIVE, today=TODAY)
        rec = {e["id"]: e for e in r["entries"]}
        self.assertFalse(rec["TD-001"]["pickable"])
        self.assertEqual(rec["TD-001"]["parts_open"], ["TD-002", "TD-003"])
        self.assertEqual(rec["TD-001"]["blocked_by"], [])  # parts are not blockers
        self.assertEqual(rec["TD-002"]["part_of"], "TD-001")
        self.assertEqual(rec["TD-003"]["part_of"], "TD-1")  # as written; matched by number
        self.assertEqual([e["id"] for e in r["pickable"]], ["TD-002"])

    def test_a_parent_whose_parts_are_all_archived_is_pickable(self):
        led = _entry(1, "Medium", "**Blocked by:** TD-009") + _entry(2, "Low", "**Part of:** TD-001")
        text = [f for f in L.pickable(led, _entry(9), today=TODAY)["flags"] if "every blocker is archived" in f]
        self.assertIn("still waits on its open parts", text[0])  # review of #22: not "pickable"
        r = L.pickable(_entry(1), self.ARCHIVE, today=TODAY)
        self.assertEqual([e["id"] for e in r["pickable"]], ["TD-001"])
        self.assertEqual(r["entries"][0]["parts_open"], [])

    def test_a_parent_is_ordered_after_its_parts_whatever_its_key(self):
        led = _entry(1, "High") + _entry(2, "Low", "**Part of:** TD-001") + _entry(3, "Medium", "**Part of:** TD-001")
        self.assertEqual(_order(led), ["TD-003", "TD-002", "TD-001"])
        self.assertEqual(_order(led, "TD-001: 0a\nTD-002: 0z\n"), ["TD-002", "TD-003", "TD-001"])  # the parent's line moves the card, not it
        self.assertEqual(_order(self.DESIGN), ["TD-002", "TD-003", "TD-001"])  # TD-003 waits on TD-002

    def test_parts_do_not_inherit_their_parents_blockers(self):
        led = _entry(1, "Medium", "**Blocked by:** TD-009") + _entry(2, "Low", "**Part of:** TD-001") + _entry(9)
        self.assertCountEqual([e["id"] for e in L.pickable(led, "", today=TODAY)["pickable"]], ["TD-002", "TD-009"])

    def test_cards_join_by_part_of(self):
        led = _entry(1) + _entry(2, "Low", "**Part of:** TD-001") + _entry(5, "Low", "**Part of:** TD-007")
        self.assertEqual([(c["ids"], c["others"]) for c in L.components(L.entries(led))],
                         [(["TD-001", "TD-002"], []), (["TD-005"], ["TD-007"])])
        self.assertEqual([c["ids"] for c in L.components(L.entries(self.ARCHIVE + _entry(1)))],
                         [["TD-004", "TD-001"]])

    def test_every_entry_on_a_cycle_carries_its_own_flag(self):
        led = (_entry(1) + _entry(2, "Medium", "**Part of:** TD-001")
               + _entry(3, "Medium", "**Part of:** TD-002", "**Blocked by:** TD-001"))
        self.assertEqual([t for t, k, _ in self.kinds(led) if k == "cycle"], ["TD-001", "TD-002", "TD-003"])
        self.assertTrue(all(lv == "info" for _, k, lv in self.kinds(led, old=led) if k == "cycle"))  # standing
        # an edit to either end fails: the flag on the changed entry is an error, the others standing
        before = led.replace("\n**Blocked by:** TD-001", "")
        self.assertEqual([(t, lv) for t, k, lv in self.kinds(led, old=before) if k == "cycle"],
                         [("TD-001", "info"), ("TD-002", "info"), ("TD-003", "error")])
        before = led.replace("**Part of:** TD-001", "**Status:** Open")
        self.assertIn(("TD-002", "cycle", "error"), self.kinds(led, old=before))
        # an edit that removes the bad id passes
        self.assertNotIn("cycle", [k for _, k, _ in self.kinds(before, old=led)])

    def test_a_part_blocked_by_its_parent_is_a_cycle(self):
        led = _entry(1) + _entry(2, "Medium", "**Part of:** TD-001", "**Blocked by:** TD-001")
        self.assertEqual([t for t, k, _ in self.kinds(led) if k == "cycle"], ["TD-001", "TD-002"])
        self.assertEqual(L.pickable(led, "", today=TODAY)["pickable"], [])

    def test_a_blocked_by_cycle_alone_is_flagged_too(self):
        led = _entry(1, "Medium", "**Blocked by:** TD-002") + _entry(2, "Medium", "**Blocked by:** TD-001")
        self.assertEqual([t for t, k, _ in self.kinds(led) if k == "cycle"], ["TD-001", "TD-002"])

    def test_the_legacy_edge_is_carried_by_the_parent(self):
        led = (_entry(1, "Medium", "**Blocked by:** TD-002, TD-003, TD-009") + _entry(2, "Medium", "**Part of:** TD-001")
               + _entry(3, "Medium", "**Part of:** TD-002") + _entry(9))
        legacy = [r for r in L.check(led, "", today=TODAY) if r["kind"] == "legacy-part"]
        self.assertEqual([(r["id"], r["level"]) for r in legacy], [("TD-001", "info")])
        self.assertIn("TD-002, TD-003", legacy[0]["text"])  # a part and a part's part; TD-009 is a real blocker
        self.assertNotIn("cycle", [k for _, k, _ in self.kinds(led)])  # a parallel edge, no cycle
        # standing: information; the parent changed: an error; only the part changed: the parent's flag stands
        self.assertIn(("TD-001", "legacy-part", "info"), self.kinds(led, old=led))
        self.assertIn(("TD-001", "legacy-part", "error"),
                      self.kinds(led, old=led.replace(", TD-003, TD-009", ", TD-009")))
        self.assertIn(("TD-001", "legacy-part", "info"),
                      self.kinds(led, old=led.replace("**Part of:** TD-002", "**Status:** Open")))

    def test_a_crlf_status_in_the_set_is_no_status_error(self):  # v2.7: the line end is not part of the value
        led = "# Ledger\n\nLedgerboard: 2\n\n" + _entry(1, "Low", "**Status:** Open")
        arc = _entry(2, "Low", "**Status:** Resolved 2026-01-01")
        crlf = lambda t: t.replace("\n", "\r\n")  # noqa: E731
        self.assertEqual([r for r in L.check(crlf(led), crlf(arc), today=TODAY) if r["kind"] == "status"], [])
        bad = [r["id"] for r in L.check(crlf(led.replace("Open", "Built")), crlf(arc), today=TODAY)
               if r["kind"] == "status"]
        self.assertEqual(bad, ["TD-001"])

    def test_what_a_part_of_line_cannot_name(self):
        led = (_entry(1, "Low", "**Part of:** far#TD-005") + _entry(2, "Low", "**Part of:** TD-099")
               + _entry(3, "Low", "**Part of:** TD-008") + _entry(4, "Low", "**Part of:** TD-005, TD-006")
               + _entry(5) + _entry(6) + _entry(7, "Low", "**Part of:** soon"))
        self.assertEqual([(t, k, lv) for t, k, lv in self.kinds(led, _entry(8)) if t != "TD-005" and k != "status"],
                         [("TD-001", "part-of-item", "error"), ("TD-002", "part-of-unknown", "error"),
                          ("TD-003", "part-of-archived", "info"), ("TD-004", "part-of-item", "error"),
                          ("TD-007", "part-of-item", "error")])
        # an unreadable or cross-repo line makes no parent: TD-005 stays pickable
        self.assertIn("TD-005", [e["id"] for e in L.pickable(led, _entry(8), today=TODAY)["pickable"]])

    def test_part_of_is_a_cadence_field(self):
        led = "Fields: Owner = a | b\n\n" + _entry(1) + _entry(2, "Low", "**Part of:** TD-001")
        self.assertNotIn("undeclared-field", [k for _, k, _ in self.kinds(led, old="")])
        self.assertIn("part of", L.CADENCE_FIELDS)

    def test_escaped_from_is_a_cadence_field(self):
        led = "Fields: Owner = a | b\n\n" + _entry(1) + _entry(2, "Low", "**Escaped from:** other#TD-009 — its review missed it")
        self.assertNotIn("undeclared-field", [k for _, k, _ in self.kinds(led, old="")])
        self.assertIn("escaped from", L.CADENCE_FIELDS)

    def test_a_ledger_with_no_part_of_reads_as_before(self):
        r = L.pickable(RANKED, "", today=TODAY)
        self.assertTrue(all(e["part_of"] is None and e["parts_open"] == [] for e in r["entries"]))


class EntryWriters(unittest.TestCase):  # v2.2: one entry's canonical form (ledgerboard TD-005)
    EDIT = ROOT / "fixtures" / "ledger_edit"

    def test_every_canonical_input_reads_back_as_it_was(self):
        for md in sorted(self.EDIT.glob("*.md")):
            text = md.read_text(encoding="utf-8")
            try:
                out = L.canonical(text)
            except L.Refused:
                continue
            with self.subTest(md.name):
                self.assertEqual(L.canonical(out), out)
                self.assertEqual(L.entries(out), L.entries(text))
                files = {"README.md": "Ledgerboard: 2\n", md.name.replace(md.stem, L.entries(out)[0]["id"]): out}
                self.assertEqual(L.v2_problems("", L._dict_ls(files), files.get), [])

    def test_a_section_runs_to_the_next_lead(self):
        body = ("words first\n\n**Why:** a\n\nb\n\n**Fix (to design):** c\n\n**Fix:** d\n- e\n\n- f\n\n"
                "```\n\n**Not:** a lead\n```\n\n**Done when** g")
        got = [(lead, t.split("\n")[-1]) for lead, t in L._entry_sections(body)]
        self.assertEqual(got, [(None, "words first"), ("Why:", "b"), ("Fix (to design):", "**Fix (to design):** c"),
                               ("Fix:", "```"), ("Done when", "**Done when** g")])
        self.assertEqual([L._section_key(x) for x in ("Done when", "Done when:", "Fix (to design):")],
                         ["done when", "done when", "fix (to design)"])

    def test_a_fence_closes_only_on_its_own_kind(self):
        def leads(body):
            return [lead for lead, _ in L._entry_sections(body)]
        self.assertEqual(leads("**Why:** a\n\n~~~\n```\n\n**Z:** in\n~~~\n\n**Fix:** b"), ["Why:", "Fix:"])
        self.assertEqual(leads("**Why:** a\n\n````\n```\n\n**Z:** in\n````\n\n**Fix:** b"), ["Why:", "Fix:"])
        self.assertEqual(leads("**Why:** a\n\n```x``` inline\n\n**Fix:** b"), ["Why:", "Fix:"])
        self.assertEqual(leads("**Why:** a\n\n    ```\n\n**Fix:** b"), ["Why:", "Fix:"])
        self.assertEqual(L._entry_sections("**Why:** a\n   \n\n**Fix:** b")[0], ("Why:", "**Why:** a"))

    def test_a_bold_run_mid_paragraph_opens_no_section(self):
        self.assertEqual([lead for lead, _ in L._entry_sections("**Why:** a\n**Fix:** b")], ["Why:"])

    def test_the_order_is_spelled_as_spec_lists_it_and_others_as_written(self):
        out = L.canonical("## TD-1: x\n\n**ID_TAKE:** ab\n**part-of:** TD-2\n**Zed note:** z\n**priority:** Low\n")
        self.assertEqual(out, "## TD-1: x\n\n**Priority:** Low\n**Id take:** ab\n**Part of:** TD-2\n**Zed note:** z\n")

    def test_id_take_is_a_cadence_field(self):
        led = "Fields: Owner = a | b\n\n" + _entry(1, "Low", "**Id take:** 0123456789abcdef0123456789abcdef")
        self.assertNotIn("undeclared-field", [r["kind"] for r in L.check(led, "", old="", today=TODAY)])
        self.assertIn("id take", L.CADENCE_FIELDS)

    def test_a_new_entry_reads_back_its_fields(self):
        out = L.entry_text("TD-7", "t", {"Kind": "build", "Priority": "High", "Waits": ""}, {"Why": "w"})
        e = L.entries(out)[0]
        self.assertEqual((e["id"], e["fields"]), ("TD-7", {"priority": "High", "kind": "build"}))
        self.assertEqual(L.canonical(out), out)

    def test_every_edit_returns_canonical_form_and_one_entry_file(self):
        spec = json.loads((self.EDIT / "cases.json").read_text(encoding="utf-8"))
        want = json.loads((self.EDIT / "expected.json").read_text(encoding="utf-8"))["edit_entry"]
        for name, got in want.items():
            if "ok" not in got:
                continue
            with self.subTest(name):
                out = got["ok"]
                self.assertEqual(L.canonical(out), out)
                files = {"README.md": "Ledgerboard: 2\n", f"{L.entries(out)[0]['id']}.md": out}
                self.assertEqual(L.v2_problems("", L._dict_ls(files), files.get), [])
        self.assertEqual(sorted(c["name"] for c in spec["edit_entry"]), sorted(want))

    def test_each_action_names_its_arguments(self):
        self.assertEqual(set(L.ENTRY_ACTIONS), set(L._ENTRY_ARGS))

    def test_set_leaves_every_other_field_as_it_was(self):
        text = (self.EDIT / "reordered.md").read_text(encoding="utf-8")
        before = L.entries(text)[0]["fields"]
        after = L.entries(L.edit_entry(text, "set", fields={"Owner": "designer"}))[0]["fields"]
        self.assertEqual({k: v for k, v in after.items() if k != "owner"}, {k: v for k, v in before.items() if k != "owner"})
        self.assertEqual(after["owner"], "designer")

    def test_an_archived_entry_keeps_one_resolved_line_however_often_it_is_reopened(self):
        text = (self.EDIT / "archived.md").read_text(encoding="utf-8")
        for n in range(3):
            text = L.edit_entry(L.edit_entry(text, "reopen", today="2026-02-01", why=f"round {n}"),
                                "archive", today="2026-02-02", why="done", pr=20 + n)
        self.assertEqual(text.count("**Resolved:**"), 1)
        self.assertIn("**Resolved:** 2026-02-02 (PR #22)", text)
        self.assertTrue(L.entries(text)[0]["fields"]["status"].startswith("Resolved 2026-02-02"))

    def test_dates_are_the_callers(self):
        with self.assertRaises(L.Refused):
            L.edit_entry((self.EDIT / "archived.md").read_text(encoding="utf-8"), "reopen", why="x")
        out = L.edit_entry((self.EDIT / "archived.md").read_text(encoding="utf-8"), "reopen", why="x",
                           today=datetime(2026, 2, 1, 13, 5, tzinfo=timezone.utc))
        self.assertIn("**Status:** Open\n", out)
        self.assertIn("- 2026-02-01: reopened — x\n", out)
        self.assertNotIn("13:05", out)

    def test_a_ledger_date_is_the_utc_date_and_a_naive_datetime_is_refused(self):
        text = (self.EDIT / "reordered.md").read_text(encoding="utf-8")
        late = datetime(2026, 2, 1, 22, 30, tzinfo=timezone(timedelta(hours=-5)))  # 03:30 UTC the next day
        naive = datetime(2026, 2, 1, 12, 0)  # noqa: DTZ001 — the one refused
        self.assertIn("- 2026-02-02: late\n", L.edit_entry(text, "note", today=late, words="late"))
        with self.assertRaisesRegex(L.Refused, "naive"):
            L.edit_entry(text, "note", today=naive, words="x")
        with self.assertRaisesRegex(L.Refused, "naive"):
            L.entry_text("TD-1", "t", {"Priority": "Low"}, {},
                         filed={"today": naive, "who": "a", "session": "s", "words": "w"})


    def test_an_id_argument_holds_nothing_after_its_number(self):
        text = (self.EDIT / "reordered.md").read_text(encoding="utf-8")
        for action, args in (("renumber", {"new": "TD-10\n"}), ("rename_ref", {"old": "TD-12", "new": "TD-8\n"}),
                             ("archive", {"why": "x", "superseded_by": "TD-9\n", "today": "2026-02-01"})):
            with self.subTest(action), self.assertRaises(L.Refused):
                L.edit_entry(text, action, **args)

    def test_a_parent_archived_ahead_of_its_parts_is_an_error_no_edit_demotes(self):
        led = _entry(1) + _entry(2, "Low", "**Part of:** TD-001") + _entry(3, "Low", "**Part of:** TD-001")
        after = _entry(2, "Low", "**Part of:** TD-001") + _entry(3, "Low", "**Part of:** TD-001")
        got = [r for r in L.check(after, _entry(1), old=led, today=TODAY) if r["kind"] == "archive-open-parts"]
        self.assertEqual([(r["id"], r["level"], r["standing"]) for r in got], [("TD-001", "error", False)])
        self.assertIn("TD-002, TD-003 are still Part of it", got[0]["text"])
        # parts archived with it, or re-parented in the same edit: nothing
        self.assertFalse([r for r in L.check("", _entry(1) + after, old=led, today=TODAY) if r["kind"] == "archive-open-parts"])
        moved = _entry(2, "Low", "**Part of:** TD-004") + _entry(3) + _entry(4)
        self.assertFalse([r for r in L.check(moved, _entry(1), old=led + _entry(4), today=TODAY) if r["kind"] == "archive-open-parts"])
        self.assertFalse([r for r in L.check(after, _entry(1), today=TODAY) if r["kind"] == "archive-open-parts"])
        # deleted outright, or renumbered with its parts left pointing at the old id: the same error
        for arc, extra in (("", ""), ("", _entry(9))):
            with self.subTest(renumbered=bool(extra)):
                got = [r["id"] for r in L.check(after + extra, arc, old=led, today=TODAY) if r["kind"] == "archive-open-parts"]
                self.assertEqual(got, ["TD-001"])


class TheLog(unittest.TestCase):
    """The Log (v2.4): its shapes, its place, the writers' lines, the lifted Status notes, a gate's age."""

    ENTRY = "## TD-5: x\n\n**Priority:** Low\n**Added:** 2026-01-01\n**Status:** Open\n\n**Why:** w\n"

    def test_each_writer_shape_is_read(self):
        lines = {
            '- 2026-01-02: filed by Paul, session led-tds, while other/x#TD-3: "say "it""': ("filed", {"while": "other/x#TD-3", "words": 'say "it"'}),
            "- 2026-01-02: gate added: until 2026-03-01": ("gate-added", {"gate": "until 2026-03-01"}),
            '- 2026-01-02: gate lifted: decision (Paul) — by Paul; answer "Go"; no board item': ("gate-lifted", {"via": "answer", "suffix": "; no board item"}),
            "- 2026-01-02: gate lifted: decision (Paul) — by Kim; override: away a month": ("gate-lifted", {"via": "override", "by": "Kim"}),
            "- 2026-01-02: gate lifted: event (ac-v2-4) — by host1; pr-merged passed; ac#12": ("gate-lifted", {"via": "check", "evidence": "ac#12"}),
            "- 2026-01-02: gate lifted: until 2026-01-02 — by host1; date reached": ("gate-lifted", {"via": "date"}),
            "- 2026-01-02: gate lift skipped: TD-4 no longer carries decision (Paul)": ("gate-lift-skipped", {"id": "TD-4"}),
            '- 2026-01-02: kept waiting: decision (Paul) — by Paul; answer "Not yet"': ("kept-waiting", {"label": "Not yet"}),
            "- 2026-01-02: gate reassigned: decision (Paul) → decision (Kim) — by Paul; away": ("gate-reassigned", {"to": "decision (Kim)"}),
            "- 2026-01-02: archived: Dropped — nothing needs it": ("archived", {"word": "Dropped"}),
            "- 2026-01-02: reopened — it broke": ("reopened", {"why": "it broke"}),
            "- 2026-01-02: was: Built 2026-01-01: half": ("was", {"status": "Built 2026-01-01: half"}),
            "- 2026-01-02: reopened the thread": ("note", {}),
            "- 2026-01-02: gate lifted: by hand": ("malformed", {}),
        }
        for line, (kind, parts) in lines.items():
            with self.subTest(line):
                got = L.log_line(line)
                self.assertEqual(got["kind"], kind)
                self.assertEqual({k: got[k] for k in parts}, parts)
        self.assertIsNone(L.log_line("- 2026-1-2: x"))

    def test_a_note_never_imitates_a_writer_line(self):
        for words in ("gate added: decision (Paul)", "was: Open", "reopened — no"):
            with self.subTest(words), self.assertRaises(L.Refused):
                L.edit_entry(self.ENTRY, "note", today="2026-01-03", words=words)
        lifted = L.status_notes_to_log(self.ENTRY.replace("Open", "Open 2026-01-02: was: a slip"))
        self.assertIn("- 2026-01-02: note: was: a slip\n", lifted)

    def test_the_writers_refuse_a_log_that_is_not_last_and_insert_before_it(self):
        text = L.edit_entry(self.ENTRY, "note", today="2026-01-03", words="one")
        self.assertTrue(L.edit_entry(text, "edit", section="Done when", words="d").endswith("- 2026-01-03: one\n"))
        stray = text + "\n**After:** a section below the Log\n"
        self.assertEqual([k for k, _ in L.log_problems(stray)], ["log-not-last"])
        for action, args in (("note", {"words": "two"}), ("reopen", {"why": "w"}), ("archive", {"why": "w"})):
            with self.subTest(action), self.assertRaises(L.Refused):
                L.edit_entry(stray, action, today="2026-01-04", **args)
        with self.assertRaises(L.Refused):
            L.edit_entry(text, "edit", section="Log", words="- 2026-01-01: rewritten")

    def test_check_flags_a_log_out_of_place_or_shape_and_only_where_the_entry_changed(self):
        good = L.edit_entry(self.ENTRY, "note", today="2026-01-03", words="one")
        bad = good + "- 2026-01-04 no colon\n\n**After:** x\n"
        kinds = sorted(r["kind"] for r in L.check(bad, "", today=TODAY) if r["field"] == "log")
        self.assertEqual(kinds, ["log-line", "log-not-last"])
        self.assertTrue(all(r["standing"] for r in L.check(bad, "", old=bad, today=TODAY) if r["field"] == "log"))
        self.assertTrue(all(r["level"] == "error" for r in L.check(bad, "", old=good, today=TODAY) if r["field"] == "log"))
        self.assertFalse([r for r in L.check(good, "", today=TODAY) if r["field"] == "log"])

    def test_a_status_lifts_only_from_a_word_its_end_a_colon_or_its_date_follow(self):
        for status in ("In progress: x", "Open, held", "Open; held", "**Open** x", "Openly x", "Open x",
                       "Resolved 2026-01-05.", "Open 2026-01-01T10:00", "Open 2026-01-01 by TD-9. x"):
            with self.subTest(status):
                text = self.ENTRY.replace("**Status:** Open", f"**Status:** {status}")
                self.assertEqual(L.status_notes_to_log(text), text)
        text = "## TD-6: x\n\n**Status:** Resolved: built\n**Resolved:** 2026-01-07 (PR #3)\n\n**Why:** w\n"
        self.assertIn("- 2026-01-07: built\n", L.edit_entry(text, "reopen", today="2026-02-01", why="again"))

    def test_a_gates_age(self):
        text = self.ENTRY.replace("**Status:** Open", "**Status:** Open\n**Blocked by:** decision (Paul)")
        self.assertEqual(L.gate_age(text, "decision (Paul)"), date(2026, 1, 1))  # no Log: Added
        text = L.edit_entry(text, "note", today="2026-01-03", words="looked")
        self.assertEqual(L.gate_age(text, "decision (Paul)"), date(2026, 1, 3))  # the first Log line
        text = text.replace("- 2026-01-03: looked", "- 2026-01-03: looked\n- 2026-01-09: kept waiting: decision (paul) — by Paul; answer \"Later\"")
        self.assertEqual(L.gate_age(text, "decision (Paul)"), date(2026, 1, 9))
        self.assertEqual(L.gate_age(text, "until 2026-05-01"), date(2026, 1, 3))

    def test_gate_added_of_an_unreadable_log_is_none(self):  # v2.5: no day to count from, and check() goes on
        two = ("## TD-084: Two Logs\n\n**Priority:** Low\n**Blocked by:** event (x)\n\n**Why:** w\n\n"
               "**Event (x):** the next record.\ncheck: host-log s \"x\"\n\n**Log:**\n- 2026-01-02: gate added: event (x)"
               "\n\n**Log:**\n- 2026-01-03: a note\n")
        self.assertIsNone(L.gate_added(two, "event (x)"))
        kinds = [r["kind"] for r in L.check("# L\n\n" + two, "", today="2026-01-20")]
        self.assertIn("event-undated", kinds)
        self.assertIn("log-not-last", kinds)
        bad = two.replace("\n\n**Log:**\n- 2026-01-03: a note\n", "\n").replace("2026-01-02: gate", "2026-02-30: gate")
        self.assertIsNone(L.gate_added(bad, "event (x)"))  # no day, never a ValueError
        self.assertIn("event-undated", [r["kind"] for r in L.check("# L\n\n" + bad, "", old="", today="2026-01-20")])


class Retitle(unittest.TestCase):  # v2.8 (TD-068 B1): what the fixtures do not show on their own
    ENTRY = "## TD-7: Old\n\n**Priority:** Low\n**Status:** Open\n**Blocked by:** until 2026-03-01\n\n**Why:** w\n"

    def test_retitled_is_not_a_line_a_gate_ages_from(self):
        self.assertNotIn("retitled", L.LOG_AGE_KINDS)
        out = L.edit_entry(self.ENTRY, "set", title="New", today="2026-01-20")
        self.assertEqual(L.log_line(out.splitlines()[-1])["kind"], "retitled")
        self.assertEqual(L.gate_added(out, "until 2026-03-01"), None)

    def test_each_refusal_names_the_verb_to_use(self):
        stray = self.ENTRY + "\n**Status:** a stray\n"
        nohdr = self.ENTRY.replace("**Status:** Open\n", "") + "\n**Status:** Open\n"
        for call, verb in ((lambda: L.edit_entry(self.ENTRY, "edit", section="Title", words="x"), "set --title"),
                           (lambda: L.edit_entry(self.ENTRY, "edit", section="Type", words="x"), "use set"),
                           (lambda: L.edit_entry(self.ENTRY, "set", fields={"Title": "x"}), "set --title"),
                           (lambda: L.edit_entry(nohdr, "edit", section="Status", remove=True), "set Status first"),
                           (lambda: L.entry_text("TD-8", "t", {"Priority": "Low"}, [("Why", "w"), ("Title", "x")]),
                            "set --title")):
            with self.assertRaises(L.Refused) as e:
                call()
            self.assertIn(verb, str(e.exception))
        self.assertNotIn("**Status:** a stray", L.edit_entry(stray, "edit", section="Status", remove=True))

    def test_a_header_title_on_a_fields_ledger_is_misplaced_not_undeclared(self):
        led = "# Ledger\n\nFields: Owner = a | b\n\n" + self.ENTRY.replace("**Status:** Open\n", "**Status:** Open\n**Title:** x\n")
        kinds = [(r["kind"], r["field"]) for r in L.check(led, "", today=TODAY)]
        self.assertIn(("misplaced-name", "title"), kinds)
        self.assertNotIn(("undeclared-field", "title"), kinds)

    def test_declared_fields_is_edits_alone(self):
        for action, kw in (("set", {"fields": {"Priority": "High"}}), ("note", {"words": "w", "today": "2026-01-20"})):
            with self.assertRaises(L.Refused):
                L.edit_entry(self.ENTRY, action, declared_fields=["tracker"], **kw)


class NextId(unittest.TestCase):
    """v2.4: the counter's takes judged (SPEC *The next id*)."""

    def test_no_failure_or_warning_prints_a_nonce(self):
        spec = json.loads((ROOT / "fixtures" / "ids" / "cases.json").read_text(encoding="utf-8"))
        nonces = {t["take"] for c in spec["judge_takes"] for t in c["takes"]}
        for c in spec["judge_takes"]:
            for kind, text in sum(L.judge_takes(c["new"], c["takes"], c["entries"], c["branch"], "main",
                                                accept_taken_by=c["accept_taken_by"]), []):
                with self.subTest(case=c["name"], kind=kind):
                    self.assertFalse([n for n in nonces if n in text], text)

    def test_a_take_read_back_from_the_writers_shape(self):
        got = L.parse_take("TD-007..TD-009 [skip ci]", "by: kim\nbranch: td7\ntake: " + "ab" * 16 + "\n")
        self.assertEqual(got, {"ids": [7, 8, 9], "by": "kim", "branch": "td7", "take": "ab" * 16})


class GateSweep(unittest.TestCase):  # v2.4: odd inputs the fixtures do not carry (ledgerboard TD-031)
    LEDGER = ("# Ledger\n\nLedgerboard: 2\n\n## TD-301: An event\n\n**Priority:** Low\n**Added:** 2026-08-01\n"
              "**Status:** Open\n**Blocked by:** event (x-ready), decision (pat)\n\n**Ask:** Go ahead?\n")
    BOARDS = [("git@example.com:Acme/Own.git", "own", "People: kim\n\n", ""),
              ("git@example.com:acme/other.git", "other", "People: pat\n\n", "")]

    def run_sweep(self, results, today_local="2026-11-03"):
        return L.sweep([self.LEDGER], self.BOARDS, results, "2026-11-03", today_local, repo="acme/own")

    def test_an_empty_result_is_no_outcome(self):
        got = self.run_sweep({("TD-301", "x-ready"): ()})
        self.assertNotIn("example.com/acme/own", got["to_file"])
        self.assertEqual(got["lifts"], [])

    def test_today_local_may_be_a_datetime(self):
        a = self.run_sweep({}, datetime(2026, 11, 3, 23, 30, tzinfo=timezone(timedelta(hours=-7))))
        self.assertEqual(a, self.run_sweep({}))

    def test_a_ref_on_another_board_writes_the_repo_lowercased(self):
        got = L.sweep([self.LEDGER], self.BOARDS, {}, "2026-11-03", "2026-11-03", repo="Acme/Own")
        self.assertEqual([i["context"] for i in got["to_file"]["example.com/acme/other"]],
                         ["acme/own#TD-301 decision (pat)"])


class UnliftedAnswer(unittest.TestCase):  # v2.7 (TD-056): a lifting answer closed with no lift; odd inputs
    BOARD = "People: pat\n\n"
    ANSWER = ("- [x] decide 2026-10-02 (n/a) — Go? Context: TD-{n} {gate}. Due: 2026-11-10. Answers: Go | Not yet. "
              "Decided: Go (by pat) (2026-10-25). Closed: 2026-10-25 — lifted.\n")

    def entry(self, n, gate="decision (pat)", log=""):
        return (f"## TD-{n}: An entry\n\n**Priority:** Low\n**Added:** 2026-09-01\n**Status:** Open\n"
                f"**Blocked by:** {gate}\n" + (f"\n**Log:**\n{log}" if log else ""))

    def run_sweep(self, ledger, board):
        got = L.sweep(["# Ledger\n\nLedgerboard: 2\n\n" + ledger], [("git@example.com:acme/own.git", "own", board, "")],
                      {}, "2026-11-03", "2026-11-03", repo="acme/own")
        return [(i["kind"], i["context"]) for i in got["to_file"].get("example.com/acme/own", [])], got["to_close"]

    def test_a_log_date_that_is_no_day_is_not_counted(self):
        log = "- 2026-02-30: gate lifted: decision (pat) — by pat; answer \"Go\"\n"
        filed, _ = self.run_sweep(self.entry(1, log=log), self.BOARD + self.ANSWER.format(n=1, gate="decision (pat)"))
        self.assertEqual(filed, [("act", "TD-1 decision (pat) lift")])

    def test_the_gate_in_another_case_is_one_question(self):
        filed, _ = self.run_sweep(self.entry(1, gate="decision (PAT)"),
                                  self.BOARD + self.ANSWER.format(n=1, gate="decision (pat)"))
        self.assertEqual(filed, [("act", "TD-1 decision (pat) lift")])

    def test_an_act_whose_head_has_no_date_never_blocks_a_filing(self):
        act = ("- [x] act (n/a) — decision (pat) on TD-1 was answered with a lift on 2026-10-25 but still stands on "
               "TD-1: lift it. Context: TD-1 decision (pat) lift. Due: 2026-11-10. Closed: 2026-10-27 — left.\n")
        filed, _ = self.run_sweep(self.entry(1), self.BOARD + self.ANSWER.format(n=1, gate="decision (pat)") + act)
        self.assertEqual(filed, [("act", "TD-1 decision (pat) lift")])

    def test_an_answer_for_an_unknown_entry_owes_nothing(self):
        filed, _ = self.run_sweep(self.entry(1), self.BOARD + self.ANSWER.format(n=9, gate="decision (pat)"))
        self.assertEqual(filed, [("decide", "TD-1 decision (pat)")])

    def test_the_act_carries_its_detail(self):
        got = L.sweep(["# Ledger\n\nLedgerboard: 2\n\n" + self.entry(1)],
                      [("git@example.com:acme/own.git", "own", self.BOARD + self.ANSWER.format(n=1, gate="decision (pat)"),
                        "")], {}, "2026-11-03", "2026-11-03", repo="acme/own")
        act = got["to_file"]["example.com/acme/own"][0]
        self.assertEqual(act["text"], "decision (pat) on TD-1 was answered with a lift on 2026-10-25 but still stands "
                                      "on TD-1: lift it.")
        self.assertEqual(act["detail"]["question"], "Lift the gate by hand, or ask the question again?")
        line = L.item_line(act["text"], "2026-11-10", "2026-11-03", "sweep", None, act["context"], kind="act",
                           detail=act["detail"])
        self.assertEqual(L._sweep_head(line), "unlifted")


class MergeGateVerdicts(unittest.TestCase):  # v2.4: what the fixtures do not carry (ledgerboard TD-032)
    D = Path(__file__).resolve().parent.parent / "fixtures" / "verdict"

    def trees(self, name):
        read = lambda d: {str(p.relative_to(d)): p.read_text(encoding="utf-8")  # noqa: E731
                          for p in sorted(d.rglob("*")) if p.is_file()} if d.is_dir() else {}
        base = {**read(self.D / "base"), **read(self.D / "cases" / name / "base")}
        return base, {**base, **read(self.D / "cases" / name / "head")}

    def test_the_tripwire_reads_the_base_as_well_as_the_head(self):
        base, head = self.trees("no board item, but the base had one (read the head alone and it passes)")
        self.assertEqual([k for k, _ in L.tripwire(base, head, "ledger: set TD-150 (session w-1)", "acme/widgets")],
                         ["tripwire-no-board-item"])
        # the same diff with the base's board read as the head's: nothing covers at either, so it passes
        alone = {**base, L.BOARD_PATH: head[L.BOARD_PATH]}
        self.assertEqual(L.tripwire(alone, head, "ledger: set TD-150 (session w-1)", "acme/widgets"), [])

    def test_a_shared_lift_whose_item_gains_a_decided_is_flagged(self):  # v2.7 (TD-067 D3)
        subj = "ledger: set TD-111 (session w-1)"
        base, head = self.trees("set by= on one part of a shared item, decided")
        self.assertEqual([k for k, _ in L.tripwire(base, head, subj, "acme/widgets")], ["tripwire-shared-decided"])
        base, head = self.trees("set by= on one part of a shared item, left open")
        self.assertEqual(L.tripwire(base, head, subj, "acme/widgets"), [])

    def test_aware_datetimes_are_their_utc_dates(self):
        base, head = self.trees("a lift, closed in the same write")
        files = sorted(set(head) - set(base) | {p for p in head if base.get(p) != head[p]})
        subject = L.subject("board", "decide", "decide 2026-01-06 (session `w-1`) — Warm the cache nightly?",
                            answer="Go", session="w-1")
        late = datetime(2026, 1, 15, 23, 30, tzinfo=timezone(timedelta(hours=-7)))  # 2026-01-16 in UTC
        got = L.lift_pr_verdict(base, head, files, subject, 1, late, late, "acme/widgets")
        self.assertTrue(got["carve_out"], got)
        with self.assertRaises(L.Refused):
            L.lift_pr_verdict(base, head, files, subject, 1, datetime(2026, 1, 15, 12), None, "acme/widgets")  # noqa: DTZ001
        with self.assertRaises(L.Refused):
            L.lift_pr_verdict(base, head, files, subject, 1, "2026-01-15", "2026-01-14", "acme/widgets")
        with self.assertRaises(L.Refused):
            L.lift_pr_verdict(base, head, files, subject, True, "2026-01-15", None, "acme/widgets")

    def test_a_repo_outside_the_grammar_is_refused(self):
        base, head = self.trees("a decide lift")
        for call in (lambda: L.tripwire(base, head, "", "acme widgets"),
                     lambda: L.uncovered_decisions(base, head, [], "acme widgets")):
            with self.assertRaises(L.Refused):
                call()

    def test_the_migrate_subject(self):
        s = L.migrate_subject("2.4", 12)
        self.assertEqual(s, "ledger: migrate v2.4 (12 entries)")
        self.assertEqual(L.subject_kind(s), "migrate")
        self.assertIsNone(L.edit_action(s))
        for bad in (("2.x", 3), ("2.4", -1), ("2.4", True)):
            with self.assertRaises(L.Refused):
                L.migrate_subject(*bad)

    def test_a_line_break_that_split_misses_numbers_as_parse_board_does(self):
        base, head = self.trees("a decide lift")
        for b in ("\x0c", " "):  # str.splitlines() breaks on these, as parse_board() numbers lines
            with self.subTest(brk=repr(b)):
                odd = lambda t: t.replace("\n\n", "\n" + b + "\n", 1)  # noqa: E731
                bt, ht = {**base, L.BOARD_PATH: odd(base[L.BOARD_PATH])}, {**head, L.BOARD_PATH: odd(head[L.BOARD_PATH])}
                self.assertEqual(L.tripwire(bt, ht, "", "acme/widgets"), [])
                new = ht[L.BOARD_PATH] + "- [ ] decide 2026-01-06 (n/a) — Which store? Context: TD-100 decision (pat). " \
                    "Due: 2026-01-20. Answers: Files | Db.\n"
                got = L.uncovered_decisions(bt, {**ht, L.BOARD_PATH: new}, [], "acme/widgets")[0]
                self.assertEqual([k for k, _ in got], ["decision-no-lift"])


class UnknownStatus(unittest.TestCase):
    """v2.4, TD-039: an archived blocker's Status word this reader does not know keeps the block."""
    LEDGER = "# Ledger\n\nLedgerboard: 2\n\n## TD-001: Waits\n\n**Priority:** Medium\n**Blocked by:** {b}\n"

    def _picked(self, status, *, cross=False):
        if cross:
            got = L.pickable(self.LEDGER.format(b="acme/tools#TD-9"), "",
                             lambda item: {"state": "archived", "why": "", "status": status}, today=TODAY)
        else:
            arc = f"# Archive\n\n## TD-002: Archived\n\n**Status:** {status}\n"
            got = L.pickable(self.LEDGER.format(b="TD-002"), arc, today=TODAY)
        return [e["id"] for e in got["pickable"]] == ["TD-001"]

    def test_status_words_are_the_reader_s_known_words(self):
        # A word added to STATUS_WORDS is a word pickable() reads: as closed and done unless it joins
        # Superseded's or Dropped's rules. One outside it holds the block.
        for word in L.STATUS_WORDS:
            for cross in (False, True):
                with self.subTest(word=word, cross=cross):
                    self.assertEqual(self._picked(f"{word.capitalize()} 2026-01-05", cross=cross),
                                     word not in ("superseded", "dropped"))
        for cross in (False, True):
            with self.subTest(word="xyzzy", cross=cross):
                self.assertFalse(self._picked("Xyzzy 2026-01-05", cross=cross))

    def test_status_word_as_written(self):
        for status, want in (("**Withdrawn** 2026-01-05", "Withdrawn"), ("** Xyzzy", "**"), ("**Resolved**.", "Resolved**"),
                             ("Resolved) see", "Resolved)"), ("Done.", "Done"), (", ;", ""), ("", ""), (None, "")):
            with self.subTest(status=status):
                self.assertEqual(L._status_word(status), want)

    def test_unknown_word_is_an_error_on_an_edited_entry(self):
        arc = "# Archive\n\n## TD-002: Archived\n\n**Status:** Xyzzy 2026-01-05\n"
        led = self.LEDGER.format(b="TD-002")
        for old, level in (("", "error"), (led, "info")):  # a new entry; a standing one
            with self.subTest(level=level):
                recs = [r for r in L.check(led, arc, old, today=TODAY) if r["kind"] == "blocker-unknown-status"]
                self.assertEqual([(r["id"], r["level"]) for r in recs], [("TD-001", level)])
                self.assertIn("(Xyzzy)", recs[0]["text"])
