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
