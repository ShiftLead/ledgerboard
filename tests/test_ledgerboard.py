"""Unit tests for ledgerboard.py: the properties the fixtures do not show on their own."""

import ast
import hashlib
import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import ledgerboard as L  # noqa: E402

LEDGER = """# Ledger

## TD-001: One

**Priority:** High
**Blocked by:** far#TD-009

## TD-002: Two

**Priority:** Low
"""


class Purity(unittest.TestCase):
    def test_imports_nothing_that_reaches_outside_the_text(self):
        tree = ast.parse((ROOT / "ledgerboard.py").read_text(encoding="utf-8"))
        names = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        names |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        self.assertLessEqual(names, {"__future__", "logging", "re", "collections", "dataclasses", "datetime", "typing"})

    def test_stdlib_only_and_no_shebang(self):
        first = (ROOT / "ledgerboard.py").read_text(encoding="utf-8").splitlines()[:3]
        self.assertTrue(first[0].startswith("# ledgerboard "))
        self.assertIn("SYNCED FILE — canonical copy: ShiftLead/ledgerboard ledgerboard.py", first[1])
        self.assertFalse(first[0].startswith("#!"))
        self.assertNotIn("SYNCED FILE", L.__doc__)


class Resolver(unittest.TestCase):
    def test_no_resolver_keeps_the_block(self):
        r = L.pickable(LEDGER, "")
        self.assertEqual([e["id"] for e in r["blocked"]], ["TD-001"])
        self.assertIn("no resolver", r["entries"][0]["cross_repo"][0]["why"])

    def test_a_tuple_resolver(self):
        r = L.pickable(LEDGER, "", lambda item: ("archived", ""))
        self.assertEqual([e["id"] for e in r["pickable"]], ["TD-001", "TD-002"])

    def test_a_mapping_resolver_keeps_its_extra_keys(self):
        r = L.pickable(LEDGER, "", lambda item: {"state": "open", "why": "", "root": "/x", "source": "origin/main"})
        x = r["entries"][0]["cross_repo"][0]
        self.assertEqual((x["item"], x["state"], x["root"], x["source"]), ("far#TD-009", "open", "/x", "origin/main"))

    def test_an_unknown_state_is_unresolved(self):
        r = L.pickable(LEDGER, "", lambda item: ("maybe", ""))
        self.assertEqual(r["entries"][0]["cross_repo"][0]["state"], "unresolved")
        self.assertFalse(r["entries"][0]["pickable"])


class OddResolvers(unittest.TestCase):
    def test_odd_output_is_unresolved_never_an_error(self):
        for got in (None, ("open",), ("a", "b", "c"), {"state": "open"}, {"why": None}, {"state": "archived", "why": None}):
            x = L.pickable(LEDGER, "", lambda item, got=got: got)["entries"][0]["cross_repo"][0]
            self.assertIn(x["state"], ("open", "archived", "unresolved"), got)
            self.assertIsInstance(x["why"], str, got)


class Check(unittest.TestCase):
    def test_a_standing_flag_is_information(self):
        bad = LEDGER.replace("**Priority:** Low", "**Priority:** Low\n**Type:** chore")
        recs = L.check(bad, "", old=bad)
        self.assertTrue(all(r["level"] == "info" and r["standing"] for r in recs if r["kind"] == "type"))
        recs = L.check(bad, "", old=LEDGER)
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
    return [e["id"] for e in L.pickable(ledger, "", rank_text=rank_text, **kw)["entries"]]


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
        r = L.pickable(led, "", rank_text="TD-004: 3z\n")
        keys = {e["id"]: (e["key"], e["card_key"]) for e in r["entries"]}
        self.assertEqual(keys["TD-005"], ("1|0|000005", "3z"))
        self.assertEqual([e["id"] for e in r["entries"]][-2:], ["TD-004", "TD-005"])

    def test_the_repo_is_the_implicit_keys_last_component(self):
        r = L.pickable(RANKED, "", repo="far")
        self.assertEqual(r["entries"][0]["key"], "1|0|000001|far")

    def test_rank_flags_reach_check(self):
        recs = L.check(RANKED, "", old=RANKED, rank_text="TD-1 0h\n")
        self.assertEqual([(r["kind"], r["level"], r["standing"]) for r in recs], [("rank", "error", False)])

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


class Header(unittest.TestCase):
    def test_check_header(self):
        run = [sys.executable, str(ROOT / "fixtures" / "run.py"), "--check-header", "--module"]
        body = b"# SYNCED FILE\n\"\"\"doc\"\"\"\n"
        ok = f"# ledgerboard v1.0 sha256:{hashlib.sha256(body).hexdigest()}\n".encode() + body
        tmp = ROOT / "tests" / "_header_tmp.py"
        try:
            tmp.write_bytes(ok)
            self.assertEqual(subprocess.run([*run, str(tmp)], capture_output=True, check=False).returncode, 0)
            tmp.write_bytes(ok + b"# edited\n")
            self.assertEqual(subprocess.run([*run, str(tmp)], capture_output=True, check=False).returncode, 1)
        finally:
            tmp.unlink(missing_ok=True)


class Fixtures(unittest.TestCase):
    def test_fixtures_pass(self):
        r = subprocess.run([sys.executable, str(ROOT / "fixtures" / "run.py")], capture_output=True, text=True, check=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
