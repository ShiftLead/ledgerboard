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
        self.assertEqual(L.pickable(led, "", rank_text="TD-0007: 0h\n")["entries"][0]["key"], "0h")


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


if __name__ == "__main__":
    unittest.main()
