"""The body's shape (v3.3, SPEC *The entry*, *The body's shape*, *The ledger writer*'s ``migrate-body``): what the
fixtures do not show — the ordinal's spelling, the Ask's one reading shared by ``check()`` and the sweep's item
text, the counting rule's prefix property, and ``migrate_body()``'s idempotence and its guard."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import ledgerboard as L  # noqa: E402
from ledgerboard import Refused  # noqa: E402

HEAD = "## TD-001: An invented entry\n\n**Priority:** Low\n**Added:** 2026-01-02\n**Status:** Open\n\n"


def entry(body: str) -> str:
    return HEAD + body + "\n"


def kinds(text: str) -> list[tuple[str, str]]:
    return [(k, key) for k, key, _ in L.body_problems(text)]


class EntryContext(unittest.TestCase):
    def test_read_and_fallbacks(self):
        self.assertEqual(L._entry_context(entry("**Why:** a.\n\n**Ask:** Go?\n\n**Context:** one\ntwo.")), "one two.")
        self.assertEqual(L._entry_context(entry("**Why:** a.\n\n**Ask:** Go?\n\n**Context**: because.")), "because.")
        self.assertEqual(L._entry_context(entry("**Why:** a.\n\n**Ask:** Go?")), "")
        self.assertEqual(L._entry_context("## TD-001: X\n\nnot a field\n"), "")


class Ordinal(unittest.TestCase):
    def test_spelling(self):
        self.assertEqual([L._ordinal(n) for n in (1, 2, 3, 4, 11, 12, 13, 21, 22, 101, 111)],
                         ["1st", "2nd", "3rd", "4th", "11th", "12th", "13th", "21st", "22nd", "101st", "111th"])


class Leads(unittest.TestCase):
    def test_strict_lead(self):
        for line, name in (("**Why:** x", "Why"), ("**Why :** x", "Why"), ("**Fix (to design):** x", "Fix (to design)"),
                           ("**a:b:** x", "a:b")):
            self.assertEqual(L.STRICT_LEAD_RE.match(line).group("name"), name)
        for line in ("**:** x", "** Why:** x", "**Why** x", "**Why**: x"):
            self.assertIsNone(L.STRICT_LEAD_RE.match(line), line)

    def test_each_non_strict_form_is_lead_form(self):
        for lead, key in (("**Done when** x", "done when"), ("**Done when**: x", "done when"), ("**:** x", ""),
                          ("** Why:** x", "why")):
            self.assertEqual(kinds(entry(f"**Why:** a.\n\n{lead}")), [("lead-form", key)], lead)

    def test_a_refused_entry_is_not_read(self):
        self.assertIsNone(L.body_problems("no heading\n"))


class TheAsk(unittest.TestCase):
    def test_comment_spans_over_the_raw_body(self):
        text = entry("**Why:** a.\n\n**Ask:** Go? <!-- a\n\n**Context:** x -->")
        self.assertEqual(L.body_problems(text), [])
        self.assertEqual(L._entry_ask(text, "the title"), "Go?")

    def test_an_empty_ask_reads_the_title(self):
        text = entry("**Why:** a.\n\n**Ask:** <!-- c -->")
        self.assertEqual(kinds(text), [("field-lines", "ask")])
        self.assertEqual(L._entry_ask(text, "the title"), "the title")

    def test_until_v4_the_whole_section_is_read(self):
        text = entry("**Why:** a.\n\n**Ask:** Go?\n\nThe review is done.")
        self.assertEqual(L._entry_ask(text, "t"), "Go? The review is done.")

    def test_a_tab_indented_ask_is_not_flagged(self):
        self.assertEqual(kinds(entry("**Why:** a.\n\n\t**Ask:** Go?")), [])

    def test_a_lowercase_quoted_ask_is_flagged(self):
        self.assertEqual(kinds(entry("**Why:** a.\n\n> **ask:** Go?")), [("glued-lead", "ask")])


class Counting(unittest.TestCase):
    LEDGER = "# Ledger\n\nLedgerboard: 2\n\n"

    def flags(self, new: str, old: str | None) -> list[tuple[str, str]]:
        return [(r["level"], r["text"].split(":", 1)[1].split("`")[0].strip())
                for r in L._body_records(self.LEDGER + new, None if old is None else self.LEDGER + old)]

    def test_a_lower_count_makes_no_new_text(self):
        two = entry("**Why:** a.\n\n**Done when** one.\n\n**Done when** two.")
        one = entry("**Why:** a.\n\n**Done when** one.")
        self.assertEqual(self.flags(one, two), [("info", "the 1st")])
        self.assertEqual(self.flags(two, one), [("info", "the 1st"), ("error", "the 2nd")])

    def test_respelling_keeps_the_text(self):
        a = L.body_problems(entry("**Why:** a.\n\n**Done when** x"))
        b = L.body_problems(entry("**Why:** a.\n\n**done when** x"))
        self.assertEqual(a, b)

    def test_old_none_is_info_and_not_standing(self):
        recs = L._body_records(self.LEDGER + entry("**Why** a."), None)
        self.assertEqual([(r["level"], r["standing"]) for r in recs], [("info", False)])


class Migrate(unittest.TestCase):
    def test_idempotent(self):
        text = entry("**Why** a.\n**Fix:** b.\n\n**Done when**: c.")
        once = L.migrate_body(text)
        self.assertNotEqual(once, text)
        self.assertEqual(L.migrate_body(once), once)
        self.assertEqual(L.body_problems(once), [])

    def test_a_clean_non_canonical_entry_is_left_as_it_is(self):
        text = "## TD-001: X\n\n**Status:** Open\n**Priority:** Low\n\n**Why:** a.\n\n\n"
        self.assertEqual(L.migrate_body(text), text)

    def test_an_entry_parts_refuses_is_refused(self):
        with self.assertRaises(Refused):
            L.migrate_body("## TD-001: X\n\nnot a field\n")

    def test_a_declared_name_is_refused(self):
        text = entry("**Why:** a.\n\n**Owner.** b.")
        with self.assertRaises(Refused):
            L.migrate_body(text, ("Owner",))
        with self.assertRaises(Refused):
            L.migrate_body(entry("**Why:** a.\n\n**Team.** b."), ("Team",))
        self.assertIn("**Note:** b.", L.migrate_body(entry("**Why:** a.\n\n**Note.** b.")))

    def test_a_comment_in_a_label_is_refused(self):
        with self.assertRaises(Refused):
            L.migrate_body(entry("**Why:** a.\n\n**Done <!-- c --> when** b."))

    def test_a_hard_break_in_a_wrapped_ask_is_refused(self):
        with self.assertRaises(Refused):
            L.migrate_body(entry("**Why:** a.\n\n**Ask:** Go  \nahead?"))

    def test_a_heading_or_rule_in_a_wrapped_ask_is_refused(self):
        for line in ("# A heading", "---", "===", "***"):
            with self.assertRaises(Refused, msg=line):
                L.migrate_body(entry(f"**Why:** a.\n\n**Ask:** Go?\nmore\n{line}"))

    def test_the_event_names_are_refused(self):
        with self.assertRaises(Refused):
            L.migrate_body(entry("**Why:** a.\n\n**Event (live).** b."))


if __name__ == "__main__":
    unittest.main()
