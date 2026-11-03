"""The item gate's property (v2.3, SPEC *The form the writers write*): every line item_line() or
decided_line() writes passes item_problem(), and so does each after any snooze, decide or reply
edit_line() does not refuse; canonical_item() returns each of them unchanged."""

import json
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import ledgerboard as L  # noqa: E402

EDITS = (("snooze", {"to": date(2026, 3, 1)}), ("due", {"to": date(2026, 3, 2)}), ("decide", {"answer": "Context: x"}),
         ("decide", {"answer": "b (default)"}), ("decide", {"answer": "b", "by": "pat.lee"}), ("reply", {"reply": "see Due: 2026-05-01", "by": "w-2"}),
         ("reply", {"reply": "ok", "by": "w-2"}))


def written() -> list[str]:
    """Every compose case's line that a writer writes, from the edit fixtures."""
    spec = json.loads((ROOT / "fixtures/edit/cases.json").read_text(encoding="utf-8"))
    out = []
    for c in spec["compose"]:
        kw = {k: c[k] for k in ("kind", "answers", "default", "detail", "hide_until") if k in c}
        # each item_line case also with a hide (v2.3), so the gate's Hide until rule meets every kind
        for extra in ({}, {"hide_until": "2026-02-01"}) if c["fn"] == "item_line" else ({},):
            try:
                if c["fn"] == "item_line":
                    made = L.item_line(c["text"], c["due"], c.get("today", spec["today"]), c["session"],
                                       c["host"], c["context"], **{**kw, **extra})
                else:
                    made = L.decided_line(c["title"], c["ref"], c["answers"], c["default"], c["words"],
                                          spec["today"])
            except L.Refused:
                continue
            out.append(made.splitlines()[0])
    return out


def edited(line: str) -> list[str]:
    """`line` after each edit, and after each edit that follows a reply, where not refused."""
    out = []
    replied = L.edit_line(line, "reply", reply="hm", by="w-3", today=date(2026, 1, 16))
    for base in (line, replied):
        for action, kw in EDITS:
            try:
                out.append(L.edit_line(base, action, today=date(2026, 1, 17), **kw))
            except L.Refused:
                pass
    return [replied, *out]


class WritersPassTheGate(unittest.TestCase):
    def test_every_written_and_edited_line_passes(self):
        lines = written()
        self.assertGreater(len(lines), 10)
        for line in lines:
            for v in (line, *edited(line)):
                with self.subTest(line=v):
                    self.assertIsNone(L.item_problem(v))
                    self.assertEqual(L.canonical_item(v + "\n"), v + "\n")

    def test_a_new_board_of_written_lines_has_no_problems(self):
        board = "".join(f"{ln}\n" for ln in written())
        self.assertEqual([p for p in L.board_problems(board) if not p[1].startswith("ℹ")], [])  # a note is no fault
        self.assertEqual(L.board_problems("People: w-1\n\n" + board), [])  # v2.3: with its People: line, none


if __name__ == "__main__":
    unittest.main()
