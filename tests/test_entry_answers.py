"""Unit tests for an entry's own answers (v3.3, SPEC *An entry's own answers*): ``entry_answers()``'s refusals by
reason, and the gate sweep never raising on an entry's answers."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import ledgerboard as L  # noqa: E402

HEAD = ("## TD-5: An invented entry\n\n**Priority:** Medium\n**Status:** Open\n**Blocked by:** decision (pat)\n\n"
        "**Ask:** Does the widget work?\n\n")
BOARD = "# Needs the user\n\nLedgerboard: 3\nPeople: pat\n"
URL = "git@example.com:acme/widgets.git"


def refusal(body: str, text: str | None = None) -> str:
    try:
        L.entry_answers(text if text is not None else HEAD + body)
    except L.Refused as e:
        return str(e)
    raise AssertionError("not refused")


class EntryAnswersRefusals(unittest.TestCase):
    """Each refusal names its own reason, the first fault in the reader's order."""

    def test_reasons(self):
        cases = {
            "starts no section": "**Answers:** Go | Not yet\n**Lifts:** Go\n",
            "two **Answers:** sections": "**Answers:** Go | No\n\n**Answers:** Go | No\n",
            "runs past its line": "**Answers:** Go | Not\nyet\n",
            "a **Lifts:** with no **Answers:**": "**Lifts:** Go\n",
            "no answers": "**Answers:**\n",
            "no lifts": "**Answers:** Go | No\n\n**Lifts:** |\n",
            "a field inside the line": "**Answers:** A — x ** | B — y **Lifts:** A\n",
            "two answers marked": "**Answers:** Go (default) | No (default)\n",
            "as a decide's answers they are refused": "**Answers:** Go\n",
            "two answers with one label": "**Answers:** Go | go\n",
            "no answer lifts (labels read: **Go**, **Not yet**)": "**Answers:** **Go** — build it | **Not yet**\n",
        }
        for want, body in cases.items():
            with self.subTest(want=want):
                self.assertIn(want, refusal(body))

    def test_the_first_fault_is_named(self):
        # A field running past its line comes before the Lifts with no Answers.
        self.assertIn("runs past its line", refusal("**Lifts:** Go\nmore\n"))

    def test_an_entry_the_parts_refuse_gives_their_reason(self):
        text = "## TD-5: An invented entry\n\n**Priority:** Medium\nnot a field\n\n**Answers:** Go | No\n"
        self.assertIn("header block", refusal("", text))

    def test_only_refused_is_raised(self):
        for body in ("**Answers:** \\| | \\|\n", "**Answers:** — | —\n", "**Answers:** Go —\n\n**Lifts:** —\n",
                     "**Answers:** Go | Hold: <note>\n\n**Lifts:** Hold:\n", "**Answers:** <x>: | Go\n"):
            with self.subTest(body=body):
                try:
                    L.entry_answers(HEAD + body)
                except L.Refused:
                    pass


class SweepNeverRaises(unittest.TestCase):
    """The sweep offers Go | Not yet where an entry's answers are refused, and never raises for them."""

    def sweep(self, body: str) -> dict:
        board = L.load_board("b", lambda p: ["README.md"] if p == "b" else None, {"b/README.md": BOARD}.get)
        ledger = "# Ledger\n\nLedgerboard: 2\n\n" + HEAD + body
        got = L.sweep([ledger, ""], [(URL, "widgets", board)], {}, "2026-11-03", "2026-11-03", repo="acme/widgets")
        (item,) = got["to_file"]["example.com/acme/widgets"]
        return item

    def test_refused_answers_give_go_not_yet(self):
        for body in ("**Answers:** Go\n", "**Answers:** Go | Not yet\n**Lifts:** Go\n", "**Lifts:** Go\n",
                     "**Answers:** Go | Not\nyet\n", "```\n\n**Answers:** Go | No\n"):
            with self.subTest(body=body):
                item = self.sweep(body)
                self.assertEqual(item["answers"], ["Go", "Not yet"])
                self.assertIsNone(item["lifts"])
                self.assertTrue(item["detail"]["context"].endswith(
                    "; its own answers could not be offered (the ledger check names why)"))

    def test_usable_answers_are_offered(self):
        item = self.sweep("**Answers:** Works — I'll archive it | Not yet — nobody looks until you say\n\n"
                          "**Lifts:** Works\n")
        self.assertEqual(item["answers"], ["Works — I'll archive it", "Not yet — nobody looks until you say"])
        self.assertEqual(item["lifts"], ["Works"])
        self.assertEqual(item["detail"]["recommended"],
                         "Only pat can say: Works lifts the gate, and Not yet keeps it waiting, asked again in 30 days")

    def test_the_filed_item_is_one_item_file_takes(self):
        item = self.sweep("**Answers:** Go (default) — the grinders build it | Hold: <note> — a session revises it\n")
        L.item_file(item["text"], "2026-11-10", "2026-11-03", "sweep", None, item["context"], kind=item["kind"],
                    answers=item["answers"], default=item["default"], detail=item["detail"], lifts=item["lifts"])


if __name__ == "__main__":
    unittest.main()
