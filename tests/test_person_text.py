"""Text a person reads (v3.2, SPEC *Text a person reads*): what the fixtures do not show on their own — the eight
names the module exports, and that no writer of the package calls the check (TD-111 D3)."""

import ast
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import ledgerboard as L  # noqa: E402

NAMES = ("person_text_problems", "title_problems", "sentence_problems", "code_tokens", "PersonTextProblem",
         "SENTENCE_WORDS", "CODE_EXTS", "ACTOR_WORDS")
CHECKS = {"person_text_problems", "title_problems", "sentence_problems", "code_tokens"}


class TheExports(unittest.TestCase):
    def test_the_eight_names(self):
        for name in NAMES:
            self.assertTrue(hasattr(L, name), name)

    def test_a_problem_unpacks_as_a_tuple(self):
        (problem,) = L.title_problems("Fix TD-5")
        rule, refuse, line = problem
        self.assertEqual((rule, refuse), (3, True))
        self.assertEqual((problem.rule, problem.refuse, problem.line), (rule, refuse, line))

    def test_the_constants(self):
        self.assertEqual(L.SENTENCE_WORDS, 25)
        self.assertIsInstance(L.CODE_EXTS, tuple)
        self.assertIsInstance(L.ACTOR_WORDS, tuple)
        for form in ("I", "I'll", "I'm", "I've", "I'd", "i"):
            self.assertNotIn(form, L.ACTOR_WORDS)

    def test_rule_four_never_refuses(self):
        (problem,) = L.person_text_problems(None, (), "see foo.py", question=True)
        self.assertEqual((problem.rule, problem.refuse), (4, False))

    def test_person_text_uses_the_sentence_words(self):
        text = " ".join(["word"] * L.SENTENCE_WORDS) + "?"
        self.assertEqual(L.person_text_problems(text, question=True), [])
        self.assertEqual(L.sentence_problems(text, question=True, max_words=L.SENTENCE_WORDS), [])
        self.assertEqual(len(L.sentence_problems(text, question=True, max_words=L.SENTENCE_WORDS - 1)), 1)

    def test_pure(self):
        # Reads only its arguments: the same call twice gives the same answer, and the lists passed are not changed.
        actors, people = ["session"], ["Dana"]
        args = ("Should I merge it?", ["Go — a session merges it", "Wait — Dana waits"], "see foo.py")
        first = L.person_text_problems(*args, question=True, actors=actors, people=people)
        self.assertEqual(first, L.person_text_problems(*args, question=True, actors=actors, people=people))
        self.assertEqual((actors, people), (["session"], ["Dana"]))


class TheWritersDoNotCallIt(unittest.TestCase):
    def test_no_call_in_the_writers(self):
        for name in ("board.py", "ledger.py"):
            path = ROOT / "ledgerboard" / name
            if not path.exists():
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            called = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    f = node.func
                    called.add(f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None))
                elif isinstance(node, (ast.ImportFrom, ast.Import)):
                    called.update(a.name for a in node.names if a.name in CHECKS)
            self.assertFalse(called & CHECKS, f"{name} calls or imports {sorted(called & CHECKS)}")

    def test_no_call_in_the_module_writers(self):
        tree = ast.parse((ROOT / "ledgerboard" / "__init__.py").read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in {"plan_add", "plan_new", "plan_edit", "item_file",
                                                                   "edit_entry", "edit_item"}:
                calls = {getattr(n.func, "id", None) for n in ast.walk(node) if isinstance(n, ast.Call)}
                self.assertFalse(calls & CHECKS, node.name)


if __name__ == "__main__":
    unittest.main()
