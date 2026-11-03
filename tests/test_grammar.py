"""SPEC's grammar appendix against the grammar fixtures (target design §7.4, *Grammar*): every fixture in
``fixtures/grammar/cases.json`` is matched against the appendix's EBNF, and the EBNF's verdict must be the
module's, as ``fixtures/grammar/expected.json`` records it (the fixtures are the authority, the EBNF is
informative). Each production has at least one fixture the module accepts and one it refuses.

The EBNF is read from SPEC.md's ```ebnf blocks and translated to a regular expression: the W3C notation
(``::=``, ``|``, ``?``, ``*``, ``+``, ``"…"``, ``[…]`` with ``^`` and ``#xN``, ``(…)``), with no recursion; its one
exclusion is a whole production ``x ::= y* - ( y* z y* )``, the runs of ``y`` that hold no ``z``.
This matcher is the test's own and never ships in the package."""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TOKEN_RE = re.compile(r'\s*(?:(?P<lit>"[^"]*"|\'[^\']*\')|(?P<cls>\[(?:[^\]\\]|\\.)*\])|(?P<hex>#x[0-9A-Fa-f]+)'
                      r'|(?P<name>[A-Za-z][\w-]*)|(?P<op>[|?*+()]))')

EXCLUDE_RE = re.compile(r"^(?P<x>[A-Za-z][\w-]*)\* - \( (?P=x)\* (?P<b>[A-Za-z][\w-]*) (?P=x)\* \)$")


def _cp(m: re.Match) -> str:
    return re.escape(chr(int(m.group(0)[2:], 16)))


def _cls(body: str) -> str:
    """A W3C character class as a Python one: `#xN` a code point, every other character itself."""
    neg = body.startswith("^")
    out, i = [], 1 if neg else 0
    while i < len(body):
        m = re.match(r"#x[0-9A-Fa-f]+", body[i:])
        if m:
            out.append(_cp(m))
            i += m.end()
        elif body[i] == "-" and 0 < i < len(body) - 1 and out:
            out.append("-")
            i += 1
        else:
            out.append(re.escape(body[i]))
            i += 1
    return "[" + ("^" if neg else "") + "".join(out) + "]"


def ebnf(spec: str) -> dict[str, str]:
    """Every production of SPEC's ```ebnf blocks: {name: its right-hand side}."""
    prods: dict[str, str] = {}
    for block in re.findall(r"^```ebnf\n(.*?)^```", spec, re.M | re.S):
        name = None
        for line in block.splitlines():
            m = re.match(r"^([A-Za-z][\w-]*)\s*::=\s*(.*)$", line)
            if m:
                name = m.group(1)
                assert name not in prods, f"{name} is defined twice"
                prods[name] = m.group(2)
            elif line.strip():
                prods[name] += " " + line.strip()
    return prods


def regex(prods: dict[str, str], start: str) -> str:
    """The production `start` as one Python regular expression, every name it uses inlined."""
    done: dict[str, str] = {}

    def rhs(name: str, stack: tuple[str, ...]) -> str:
        if name in stack:
            raise ValueError(f"{name} is recursive: {' > '.join(stack + (name,))}")
        if name not in done:
            ex = EXCLUDE_RE.match(prods[name].strip())
            if ex:  # `x* - ( x* b x* )`: runs of x holding no b
                b = rhs(ex.group("b"), stack + (name,))
                done[name] = f"(?:(?!{b})(?:{rhs(ex.group('x'), stack + (name,))}))*"
                return done[name]
            toks = [m for m in TOKEN_RE.finditer(prods[name])]
            assert "".join(m.group(0) for m in toks).strip() == prods[name].strip(), f"{name}: cannot read it"
            out = []
            for m in toks:
                if m.group("lit"):
                    out.append("(?:" + re.escape(m.group("lit")[1:-1]) + ")")
                elif m.group("cls"):
                    out.append(_cls(m.group("cls")[1:-1]))
                elif m.group("hex"):
                    out.append(_cp(re.match(r"#x[0-9A-Fa-f]+", m.group("hex"))))
                elif m.group("name"):
                    assert m.group("name") in prods, f"{name} uses {m.group('name')}, which is not defined"
                    out.append("(?:" + rhs(m.group("name"), stack + (name,)) + ")")
                else:
                    out.append(m.group("op"))
            done[name] = "".join(out)
        return done[name]

    return rhs(start, ())


def names_used(prods: dict[str, str], start: str) -> set[str]:
    seen, todo = set(), [start]
    while todo:
        n = todo.pop()
        if n not in seen:
            seen.add(n)
            todo += [m.group("name") for m in TOKEN_RE.finditer(prods[n]) if m.group("name")]
    return seen


class Grammar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prods = ebnf((ROOT / "SPEC.md").read_text(encoding="utf-8"))
        cls.cases = json.loads((ROOT / "fixtures/grammar/cases.json").read_text(encoding="utf-8"))
        cls.expected = json.loads((ROOT / "fixtures/grammar/expected.json").read_text(encoding="utf-8"))

    def test_every_fixture_matches_as_the_module_reads_it(self):
        for start, groups in self.cases.items():
            r = re.compile(regex(self.prods, start), re.S)
            for prod, g in groups.items():
                strings = g["accept"] + g["refuse"]
                self.assertEqual(len(strings), len(self.expected[start][prod]), f"{start} / {prod}: run fixtures/run.py")
                for s, got in zip(strings, self.expected[start][prod]):
                    with self.subTest(start=start, production=prod, fixture=s):
                        self.assertEqual(bool(r.fullmatch(s)), got["accepted"], got)

    def test_every_production_has_a_fixture_each_way(self):
        for start, groups in self.cases.items():
            self.assertEqual(set(groups), names_used(self.prods, start), f"{start}: the fixtures' productions")
            for prod in groups:
                n = len(groups[prod]["accept"])
                verdicts = [v["accepted"] for v in self.expected[start][prod]]
                self.assertTrue(n and len(verdicts) > n, f"{start} / {prod}: one fixture each way")
                self.assertEqual(verdicts, [True] * n + [False] * (len(verdicts) - n),
                                 f"{start} / {prod}: the module's verdict is what the fixture says")

    def test_every_start_has_fixtures(self):
        starts = {n for n in self.prods if not any(n in names_used(self.prods, o) for o in self.prods if o != n)}
        self.assertEqual(starts, set(self.cases))


if __name__ == "__main__":
    unittest.main()
