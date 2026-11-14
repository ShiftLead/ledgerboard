"""The item gate's property for the item file (v3.0, SPEC *Edits*; v2.x held it of the line writers v3.0
removed): every file item_file() or decided_file() writes passes item_file_problem(), as does each after any
edit_item() it does not refuse; canonical_item_file() returns each of them unchanged."""

import json
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import ledgerboard as L  # noqa: E402

FILE_EDITS = (("snooze", {"to": date(2026, 12, 1)}), ("due", {"to": date(2026, 12, 2)}),
              ("decide", {"answer": "Context: x, Decided: y"}), ("decide", {"answer": "Go (by Friday)", "by": "pat.lee"}),
              ("decide", {"answer": "Hold: after the freeze"}), ("decide", {"answer": "Go", "close": True}),
              ("decide", {"answer": "Not yet", "close": True}), ("reply", {"reply": "see Due: 2026-05-01", "by": "w-2"}),
              ("reply", {"reply": "ok", "by": "sam lee"}), ("done", {}), ("done", {"why": "fixed it"}))


def written_files() -> list[str]:
    """Every file a compose case of the item fixtures writes (v3.0), each item_file() case also with a hide."""
    spec = json.loads((ROOT / "fixtures/item/cases.json").read_text(encoding="utf-8"))
    out = []
    for c in spec["compose"]:
        kw = {k: c[k] for k in ("kind", "answers", "default", "detail", "hide_until", "lifts", "parts", "doer") if k in c}
        for extra in ({}, {"hide_until": "2026-11-30"}) if c["fn"] == "item_file" else ({},):
            try:
                if c["fn"] == "item_file":
                    out.append(L.item_file(c["text"], c["due"], spec["today"], c["session"], c["host"], c["context"],
                                           **{**kw, **extra}))
                else:
                    out.append(L.decided_file(c["title"], c["ref"], c["answers"], c["default"], c["words"],
                                              spec["today"], **({"by": c["by"]} if "by" in c else {})))
            except L.Refused:
                continue
    return out


def edited_files(text: str) -> list[str]:
    """`text` after each edit, and after each edit that follows a reply, where not refused."""
    out = []
    replied = L.edit_item(text, "reply", reply="hm", by="w-3", today=date(2026, 11, 16))
    for base in (text, replied):
        for action, kw in FILE_EDITS:
            try:
                out.append(L.edit_item(base, action, today=date(2026, 11, 17), **kw))
            except L.Refused:
                pass
    return [replied, *out]


class WritersPassTheFileGate(unittest.TestCase):
    def test_every_written_and_edited_file_passes(self):
        files = written_files()
        self.assertGreater(len(files), 10)
        n = 0
        for text in files:
            for v in (text, *edited_files(text)):
                n += 1
                with self.subTest(file=v):
                    self.assertIsNone(L.item_file_problem(v))
                    self.assertEqual(L.canonical_item_file(v), v)
        self.assertGreater(n, 5 * len(files))  # most edits are made, not refused


if __name__ == "__main__":
    unittest.main()
