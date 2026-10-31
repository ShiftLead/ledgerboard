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
        self.assertEqual([e["id"] for e in L.pickable(led, arc)["pickable"]], ["TD-002", "TD-10"])

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
        return [(r["id"], r["kind"], r["level"]) for r in L.check(led, arc, old=old)]

    def test_a_parent_with_open_parts_is_not_pickable_and_keeps_its_blockers_apart(self):
        r = L.pickable(self.DESIGN, self.ARCHIVE)
        rec = {e["id"]: e for e in r["entries"]}
        self.assertFalse(rec["TD-001"]["pickable"])
        self.assertEqual(rec["TD-001"]["parts_open"], ["TD-002", "TD-003"])
        self.assertEqual(rec["TD-001"]["blocked_by"], [])  # parts are not blockers
        self.assertEqual(rec["TD-002"]["part_of"], "TD-001")
        self.assertEqual(rec["TD-003"]["part_of"], "TD-1")  # as written; matched by number
        self.assertEqual([e["id"] for e in r["pickable"]], ["TD-002"])

    def test_a_parent_whose_parts_are_all_archived_is_pickable(self):
        led = _entry(1, "Medium", "**Blocked by:** TD-009") + _entry(2, "Low", "**Part of:** TD-001")
        text = [f for f in L.pickable(led, _entry(9))["flags"] if "every blocker is archived" in f]
        self.assertIn("still waits on its open parts", text[0])  # review of #22: not "pickable"
        r = L.pickable(_entry(1), self.ARCHIVE)
        self.assertEqual([e["id"] for e in r["pickable"]], ["TD-001"])
        self.assertEqual(r["entries"][0]["parts_open"], [])

    def test_a_parent_is_ordered_after_its_parts_whatever_its_key(self):
        led = _entry(1, "High") + _entry(2, "Low", "**Part of:** TD-001") + _entry(3, "Medium", "**Part of:** TD-001")
        self.assertEqual(_order(led), ["TD-003", "TD-002", "TD-001"])
        self.assertEqual(_order(led, "TD-001: 0a\nTD-002: 0z\n"), ["TD-002", "TD-003", "TD-001"])  # the parent's line moves the card, not it
        self.assertEqual(_order(self.DESIGN), ["TD-002", "TD-003", "TD-001"])  # TD-003 waits on TD-002

    def test_parts_do_not_inherit_their_parents_blockers(self):
        led = _entry(1, "Medium", "**Blocked by:** TD-009") + _entry(2, "Low", "**Part of:** TD-001") + _entry(9)
        self.assertCountEqual([e["id"] for e in L.pickable(led, "")["pickable"]], ["TD-002", "TD-009"])

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
        self.assertEqual(L.pickable(led, "")["pickable"], [])

    def test_a_blocked_by_cycle_alone_is_flagged_too(self):
        led = _entry(1, "Medium", "**Blocked by:** TD-002") + _entry(2, "Medium", "**Blocked by:** TD-001")
        self.assertEqual([t for t, k, _ in self.kinds(led) if k == "cycle"], ["TD-001", "TD-002"])

    def test_the_legacy_edge_is_carried_by_the_parent(self):
        led = (_entry(1, "Medium", "**Blocked by:** TD-002, TD-003, TD-009") + _entry(2, "Medium", "**Part of:** TD-001")
               + _entry(3, "Medium", "**Part of:** TD-002") + _entry(9))
        legacy = [r for r in L.check(led, "") if r["kind"] == "legacy-part"]
        self.assertEqual([(r["id"], r["level"]) for r in legacy], [("TD-001", "info")])
        self.assertIn("TD-002, TD-003", legacy[0]["text"])  # a part and a part's part; TD-009 is a real blocker
        self.assertNotIn("cycle", [k for _, k, _ in self.kinds(led)])  # a parallel edge, no cycle
        # standing: information; the parent changed: an error; only the part changed: the parent's flag stands
        self.assertIn(("TD-001", "legacy-part", "info"), self.kinds(led, old=led))
        self.assertIn(("TD-001", "legacy-part", "error"),
                      self.kinds(led, old=led.replace(", TD-003, TD-009", ", TD-009")))
        self.assertIn(("TD-001", "legacy-part", "info"),
                      self.kinds(led, old=led.replace("**Part of:** TD-002", "**Status:** Open")))

    def test_what_a_part_of_line_cannot_name(self):
        led = (_entry(1, "Low", "**Part of:** far#TD-005") + _entry(2, "Low", "**Part of:** TD-099")
               + _entry(3, "Low", "**Part of:** TD-008") + _entry(4, "Low", "**Part of:** TD-005, TD-006")
               + _entry(5) + _entry(6) + _entry(7, "Low", "**Part of:** soon"))
        self.assertEqual([(t, k, lv) for t, k, lv in self.kinds(led, _entry(8)) if t != "TD-005"],
                         [("TD-001", "part-of-item", "error"), ("TD-002", "part-of-unknown", "error"),
                          ("TD-003", "part-of-archived", "info"), ("TD-004", "part-of-item", "error"),
                          ("TD-007", "part-of-item", "error")])
        # an unreadable or cross-repo line makes no parent: TD-005 stays pickable
        self.assertIn("TD-005", [e["id"] for e in L.pickable(led, _entry(8))["pickable"]])

    def test_part_of_is_a_cadence_field(self):
        led = "Fields: Owner = a | b\n\n" + _entry(1) + _entry(2, "Low", "**Part of:** TD-001")
        self.assertNotIn("undeclared-field", [k for _, k, _ in self.kinds(led, old="")])
        self.assertIn("part of", L.CADENCE_FIELDS)

    def test_escaped_from_is_a_cadence_field(self):
        led = "Fields: Owner = a | b\n\n" + _entry(1) + _entry(2, "Low", "**Escaped from:** other#TD-009 — its review missed it")
        self.assertNotIn("undeclared-field", [k for _, k, _ in self.kinds(led, old="")])
        self.assertIn("escaped from", L.CADENCE_FIELDS)

    def test_a_ledger_with_no_part_of_reads_as_before(self):
        r = L.pickable(RANKED, "")
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
        self.assertNotIn("undeclared-field", [r["kind"] for r in L.check(led, "", old="")])
        self.assertIn("id take", L.CADENCE_FIELDS)

    def test_a_new_entry_reads_back_its_fields(self):
        out = L.entry_text("TD-7", "t", {"Kind": "build", "Priority": "High", "Waits": ""}, {"Why": "w"})
        e = L.entries(out)[0]
        self.assertEqual((e["id"], e["fields"]), ("TD-7", {"priority": "High", "kind": "build"}))
        self.assertEqual(L.canonical(out), out)
