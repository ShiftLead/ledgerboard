"""release.sh --tag: it tags from any checkout whose HEAD is origin/main, and from nowhere else (TD-009).
And the fixture set's release, fixtures/MANIFEST (TD-040): fixtures/run.py's --stamp, --check-tracked and
--check-header over sets built in temporary directories, release.sh's stamp block run and pinned, and the tag.

Each ReleaseTag test builds a throwaway origin from this tree's release.sh, ledgerboard/ and fixtures/run.py,
clones it, and runs the clone's release.sh. git's identity comes from the environment, never config.
"""

import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ("release.sh", "ledgerboard/__init__.py", "fixtures/run.py")
ENV = {
    **{k: v for k, v in os.environ.items() if not k.startswith("GIT_")},  # no stray GIT_DIR from a hook
    "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@example.invalid",
    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
}


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, env=ENV, check=True, capture_output=True, text=True).stdout.strip()


@unittest.skipUnless(shutil.which("git") and shutil.which("bash"), "needs git and bash")
class ReleaseTag(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.version = (ROOT / "ledgerboard" / "__init__.py").read_text(encoding="utf-8").split()[2][1:]  # "# ledgerboard v2.2 …"
        seed = self.tmp / "seed"
        for f in FILES:
            (seed / f).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / f, seed / f)
        # A PR that changes the module leaves its header stale until the release stamps it (release.sh),
        # so the seed is stamped here as the release would be: the tag checks a released module.
        first, rest = (seed / "ledgerboard" / "__init__.py").read_bytes().split(b"\n", 1)
        (seed / "ledgerboard" / "__init__.py").write_bytes(
            f"# ledgerboard v{self.version} sha256:{hashlib.sha256(rest).hexdigest()}\n".encode() + rest)
        # The set is stamped too, as the release would: --check-header checks its MANIFEST (TD-040).
        subprocess.run([sys.executable, "fixtures/run.py", "--stamp", self.version], cwd=seed, env=ENV, check=True,
                       capture_output=True)
        git(seed, "init", "-q", "-b", "main")
        git(seed, "add", ".")
        git(seed, "commit", "-qm", "seed")
        git(self.tmp, "clone", "-q", "--bare", str(seed), "origin.git")
        git(self.tmp, "clone", "-q", "origin.git", "anchor")
        self.anchor = self.tmp / "anchor"

    def tag(self, cwd):
        return subprocess.run(["bash", "release.sh", "--tag", self.version], cwd=cwd, env=ENV, check=False,
                              capture_output=True, text=True)

    def test_a_worktree_at_a_detached_origin_main_tags(self):
        wt = self.tmp / "wt"
        git(self.anchor, "worktree", "add", "-q", "--detach", str(wt), "origin/main")
        r = self.tag(wt)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(git(wt, "rev-parse", f"v{self.version}^{{commit}}"), git(wt, "rev-parse", "origin/main"))

    def test_main_in_the_anchor_still_tags(self):
        r = self.tag(self.anchor)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_a_head_that_is_not_origin_main_is_refused(self):
        git(self.anchor, "commit", "-q", "--allow-empty", "-m", "ahead")
        r = self.tag(self.anchor)
        self.assertEqual(r.returncode, 2)
        self.assertIn("HEAD is not origin/main", r.stderr)
        self.assertEqual(git(self.anchor, "tag"), "")

    def test_a_fixture_edited_after_its_release_is_refused(self):
        with open(self.anchor / "fixtures" / "run.py", "a", encoding="utf-8") as f:
            f.write("# edited\n")
        git(self.anchor, "commit", "-qam", "edit a fixture")
        git(self.anchor, "push", "-q", "origin", "main")
        r = self.tag(self.anchor)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("fixtures: run.py: its sha256 does not match MANIFEST — edited after its release", r.stdout + r.stderr)
        self.assertEqual(git(self.anchor, "tag"), "")


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _load(run: Path):
    spec = importlib.util.spec_from_file_location(f"_run_{abs(hash(str(run)))}", run)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run(run: Path, *args, stdin: bytes | None = None):
    return subprocess.run([sys.executable, str(run), *args], input=stdin, capture_output=True, check=False)


def _symlinks_work(d: Path) -> bool:
    try:
        os.symlink("x", d / ".probe")
    except (OSError, NotImplementedError):
        return False
    os.unlink(d / ".probe")
    return True


class Manifest(unittest.TestCase):
    """fixtures/MANIFEST (TD-040, docs/plans/TD-040-fixture-release.md *The cases* 1–6b)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.root = self.tmp / "fixtures"
        self.root.mkdir()
        self.run_py = self.root / "run.py"
        shutil.copy2(ROOT / "fixtures" / "run.py", self.run_py)
        self.m = _load(self.run_py)
        (self.root / "a.md").write_bytes(b"a\n")

    def write(self, rel: str, data: bytes = b"x\n"):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def stamp(self, release: str = "2.4"):
        r = _run(self.run_py, "--stamp", release)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r

    def package(self, release: str = "2.4") -> Path:
        pkg = self.tmp / "ledgerboard"
        pkg.mkdir(exist_ok=True)
        body = b'"""doc"""\n'
        (pkg / "__init__.py").write_bytes(f"# ledgerboard v{release} sha256:{_sha(body)}\n".encode() + body)
        return pkg

    def problems(self):
        return self.m.manifest_problems(self.root)

    def manifest(self, text: bytes):
        (self.root / "MANIFEST").write_bytes(text)

    def lines(self, *paths: str) -> bytes:
        return b"".join(f"{_sha((self.root / p).read_bytes())}  {p}\n".encode() for p in paths)

    # 1
    def test_stamp_then_check(self):
        r = self.stamp()
        self.assertEqual(r.stdout.decode(), "stamped fixtures v2.4 (2 files)\n")
        self.assertEqual(self.problems(), [])
        r = _run(self.run_py, "--check-header", "--module", str(self.package()))
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn(b"fixtures: ok (v2.4, 2 files)\n", r.stdout)
        self.assertEqual(self.m.manifest_release(self.root), "2.4")

    # 2
    def test_the_text_byte_for_byte(self):
        root = self.tmp / "set"
        for rel, data in (("a/b.json", b"j\n"), ("a-b.md", b"m\n"), ("B.md", b"B\n"), ("crlf.md", b"x\r\n")):
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_bytes(data)
        want = ("# ledgerboard v2.4 fixtures\n"
                f"{_sha(b'B' + bytes([10]))}  B.md\n{_sha(b'm' + bytes([10]))}  a-b.md\n"
                f"{_sha(b'j' + bytes([10]))}  a/b.json\n{_sha(b'x' + bytes([13, 10]))}  crlf.md\n")
        self.assertEqual(self.m.manifest_text(root, "2.4"), want)

    # 3
    def test_pycache(self):
        self.write("__pycache__/run.cpython.pyc")
        self.write("d/__pycache__")  # a file so named is a member
        self.stamp()
        self.assertEqual([p for _, p in self.m.manifest_entries(self.root)], ["a.md", "d/__pycache__", "run.py"])
        self.write("__pycache__/other.pyc")
        self.assertEqual(self.problems(), [])
        if _symlinks_work(self.root):  # a link so named is a link: refused, never pruned
            (self.root / "e").mkdir()
            os.symlink("../a.md", self.root / "e" / "__pycache__")
            self.assertEqual(self.problems(), ["'e/__pycache__': not a regular file"])

    # 4
    def test_no_manifest(self):
        self.assertEqual(self.problems(), [self.m.NO_MANIFEST])
        self.assertEqual(self.m.manifest_release(self.root), None)
        self.assertEqual(self.m.manifest_entries(self.root), [])

    def test_a_bad_first_line(self):
        self.manifest(b"# ledgerboard v2 fixtures\n" + self.lines("a.md", "run.py"))
        self.assertEqual(self.problems(), ["MANIFEST's first line is not a release line: '# ledgerboard v2 fixtures'"])

    def test_a_non_ascii_digit_release_is_refused(self):
        self.manifest("# ledgerboard v2.\u0664 fixtures\n".encode() + self.lines("a.md", "run.py"))
        self.assertEqual(len(self.problems()), 1)
        self.assertIn("first line is not a release line", self.problems()[0])

    def test_a_malformed_line(self):
        self.manifest(b"# ledgerboard v2.4 fixtures\n" + self.lines("a.md") + b"zz  run.py\n")
        self.assertEqual(self.problems(), ["MANIFEST line 3 is not '<sha256>  <path>': 'zz  run.py'",
                                           "run.py: not in MANIFEST — added after its release"])

    def test_an_out_of_order_line(self):
        self.manifest(b"# ledgerboard v2.4 fixtures\n" + self.lines("run.py", "a.md"))
        self.assertEqual(self.problems(), ["MANIFEST line 3 is out of order"])

    def test_a_path_listed_twice(self):
        self.write("b.md")
        self.manifest(b"# ledgerboard v2.4 fixtures\n" + self.lines("a.md", "b.md", "a.md", "run.py"))
        self.assertEqual(self.problems(), ["MANIFEST lists a.md twice"])
        self.manifest(b"# ledgerboard v2.4 fixtures\n" + self.lines("a.md", "run.py", "run.py", "b.md"))
        self.assertEqual(self.problems(), ["MANIFEST lists run.py twice", "MANIFEST line 5 is out of order"])

    def test_not_lf_text(self):
        good = b"# ledgerboard v2.4 fixtures\n" + self.lines("a.md", "run.py")
        for bad in (good.replace(b"\n", b"\r\n"), good[:-1], b"", good + b"\n", b"\xff" + good):
            with self.subTest(bad=bad[:30]):
                self.manifest(bad)
                self.assertEqual(self.problems(), [self.m.NOT_LF_TEXT])

    def test_manifest_a_directory(self):
        (self.root / "MANIFEST").mkdir()
        (self.root / "MANIFEST" / "inside.md").write_bytes(b"x\n")
        self.assertEqual(self.problems(), [self.m.NOT_A_FILE])
        r = _run(self.run_py, "--stamp", "2.4")
        self.assertEqual((r.returncode, r.stderr.decode()), (1, "fixtures: MANIFEST is not a file\n"))

    def test_a_malformed_line_beside_an_edited_file(self):
        self.stamp()
        text = (self.root / "MANIFEST").read_bytes()
        self.manifest(text + b"nonsense\n")
        self.write("a.md", b"changed\n")
        self.assertEqual(self.problems(), ["MANIFEST line 4 is not '<sha256>  <path>': 'nonsense'",
                                           "a.md: its sha256 does not match MANIFEST — edited after its release"])

    def test_missing_added_and_edited(self):
        self.write("b.md")
        self.stamp()
        (self.root / "b.md").unlink()
        self.write("c.md")
        self.write("a.md", b"changed\n")
        self.assertEqual(self.problems(), ["a.md: its sha256 does not match MANIFEST — edited after its release",
                                           "b.md: in MANIFEST but missing", "c.md: not in MANIFEST — added after its release"])

    def test_links(self):
        if not _symlinks_work(self.root):
            self.skipTest("no symbolic links here")
        self.write("d/x.md")
        self.stamp()
        os.symlink("a.md", self.root / "link.md")
        os.symlink("d", self.root / "linkdir")
        self.assertEqual(self.problems(), ["'link.md': not a regular file", "'linkdir': not a regular file"])
        before = (self.root / "MANIFEST").read_bytes()
        r = _run(self.run_py, "--stamp", "2.5")
        self.assertEqual(r.returncode, 1)
        self.assertIn(b"fixtures: 'link.md': not a regular file", r.stderr)
        self.assertEqual((self.root / "MANIFEST").read_bytes(), before)

    def test_a_non_ascii_name(self):
        self.write("\u00e9.md")
        self.stamp()
        self.assertIn("\u00e9.md", [p for _, p in self.m.manifest_entries(self.root)])
        self.write("\u00e9.md", b"changed\n")
        self.assertEqual(self.problems(), ["\u00e9.md: its sha256 does not match MANIFEST — edited after its release"])

    def test_a_fifo(self):
        if not hasattr(os, "mkfifo"):
            self.skipTest("no os.mkfifo")
        self.stamp()
        os.mkfifo(self.root / "pipe")
        self.assertEqual(self.problems(), ["'pipe': not a regular file"])

    def test_odd_names(self):
        self.stamp()
        for name, want in ((b"bad\xff.md", "'bad\\udcff.md': a name that is not UTF-8"),
                           (b"a\nb.md", "'a\\nb.md': a path holding a newline, a carriage return or a backslash"),
                           (b"a\\b.md", "'a\\\\b.md': a path holding a newline, a carriage return or a backslash"),
                           (b"c\xff\\d.md", "'c\\udcff\\\\d.md': a name that is not UTF-8")):
            with self.subTest(name=name):
                try:
                    with open(os.path.join(os.fsencode(self.root), name), "wb") as f:
                        f.write(b"x\n")
                except OSError:
                    continue
                got = self.problems()
                self.assertEqual(got, [want])
                os.unlink(os.path.join(os.fsencode(self.root), name))

    def test_the_release_mismatch(self):
        self.stamp("2.4")
        r = _run(self.run_py, "--check-header", "--module", str(self.package("2.3")))
        self.assertEqual(r.returncode, 1)
        self.assertIn(b"fixtures: MANIFEST names v2.4, the package v2.3\n", r.stdout)

    # 5
    def test_no_mismatch_beside_another_problem(self):
        self.stamp("2.4")
        self.write("a.md", b"changed\n")
        r = _run(self.run_py, "--check-header", "--module", str(self.package("2.3")))
        self.assertEqual(r.returncode, 1)
        self.assertNotIn(b"MANIFEST names", r.stdout)
        self.write("a.md", b"a\n")
        pkg = self.package("2.3")
        with open(pkg / "__init__.py", "ab") as f:
            f.write(b"# edited\n")
        r = _run(self.run_py, "--check-header", "--module", str(pkg))
        self.assertEqual(r.returncode, 1)
        self.assertNotIn(b"MANIFEST names", r.stdout)
        self.assertIn(b"fixtures: ok (v2.4, 2 files)", r.stdout)

    # 6
    def test_the_command_line(self):
        for args, err in ((("--stamp", "2"), b"usage: --stamp <major.minor>\n"),
                          (("--stamp", "v2.4"), b"usage: --stamp <major.minor>\n"),
                          (("--stamp", "2.4", "--module", "x"), b"--module is not used with --stamp\n"),
                          (("--stamp", "2", "--module", "x"), b"--module is not used with --stamp\n"),
                          (("--check-tracked", "--module", "x"), b"--module is not used with --check-tracked\n")):
            with self.subTest(args=args):
                r = _run(self.run_py, *args)
                self.assertEqual((r.returncode, r.stderr), (2, err))
        for args in (("--check-header", "--write"), ("--stamp", "2.4", "--check-header"), ("--stamp", "2.4", "--write"),
                     ("--check-tracked", "--write")):
            with self.subTest(args=args):
                self.assertEqual(_run(self.run_py, *args).returncode, 2)
        self.assertFalse(os.path.lexists(self.root / "MANIFEST"))

    def test_a_stamp_leaves_no_temporary_file(self):
        self.stamp()
        names = sorted(p.name for p in self.root.iterdir() if p.name != "__pycache__")  # the import's, not the stamp's
        self.assertEqual(names, ["MANIFEST", "a.md", "run.py"])

    # 6a
    def tracked(self, *paths: bytes):
        return _run(self.run_py, "--check-tracked", stdin=b"".join(p + b"\0" for p in paths))

    def test_check_tracked(self):
        self.write("\u00e9.md")
        self.stamp()
        files = (b"MANIFEST", b"a.md", b"run.py", "\u00e9.md".encode(), b"__pycache__/x.pyc")
        r = self.tracked(*files)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, b"", b""))
        r = self.tracked(*files[:2], *files[3:])
        self.assertEqual((r.returncode, r.stderr), (1, b"fixtures/ differs from what git tracks: run.py\n"))
        r = self.tracked(*files, b"extra.md")
        self.assertEqual((r.returncode, r.stderr), (1, b"fixtures/ differs from what git tracks: extra.md\n"))
        r = self.tracked(*files, b"bad\xff.md", b"a\nb.md")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stderr.decode().splitlines(), ["fixtures/ differs from what git tracks: 'a\\nb.md'",
                                                          "fixtures/ differs from what git tracks: 'bad\\udcff.md'"])

    def test_check_tracked_with_no_manifest(self):
        r = self.tracked(b"a.md", b"run.py")
        self.assertEqual((r.returncode, r.stderr.decode()), (1, f"fixtures: {self.m.NO_MANIFEST}\n"))

    # 6b
    def test_paths_with_spaces(self):
        self.write("a b.md")
        self.write("a  b.md")
        self.stamp()
        self.assertEqual(self.problems(), [])
        self.assertIn("a  b.md", [p for _, p in self.m.manifest_entries(self.root)])
        self.manifest(b"# ledgerboard v2.4 fixtures\n" + f"{_sha(b'')}  \n".encode())
        self.assertIn("MANIFEST line 2 is not '<sha256>  <path>'", self.problems()[0])


class TheRealSet(unittest.TestCase):
    """Case 6c: the repo's own set stamps, and is what git tracks, in every precheck (writing nothing into it)."""

    def test_the_real_set(self):
        here = ROOT / "fixtures"
        m = _load(here / "run.py")
        m.manifest_text(here, "0.0")  # no file of the set is refused
        if not shutil.which("git"):
            self.skipTest("no git")
        inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=here, env=ENV, capture_output=True, check=False)
        listed = subprocess.run(["git", "ls-files", "-z"], cwd=here, env=ENV, capture_output=True, check=False)
        if inside.returncode != 0 or listed.returncode != 0:
            self.skipTest("not in a git work tree")
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        copy = tmp / "fixtures"
        shutil.copytree(here, copy, symlinks=True, ignore=shutil.ignore_patterns("__pycache__", "MANIFEST"))
        r = _run(copy / "run.py", "--stamp", "0.0")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = _run(copy / "run.py", "--check-tracked", stdin=listed.stdout)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, b"", b""), r.stderr.decode()[:2000])


BLOCK_START = 'python3 fixtures/run.py --stamp "$v"'


def _block() -> list[str]:
    """Rule 2's nine-line block, as release.sh holds it (stripped, comment lines left out)."""
    lines = [ln.strip() for ln in (ROOT / "release.sh").read_text(encoding="utf-8").splitlines()
             if not ln.lstrip().startswith("#")]
    i = lines.index(BLOCK_START)
    return lines[i:lines.index("fi", lines.index("fi", i) + 1) + 1]


class StampStep(unittest.TestCase):
    """Cases 7a and 8: release.sh's stamp block, run in a throwaway repo, and pinned by text."""

    WANT = [BLOCK_START,
            "if ! (cd fixtures && git ls-files -z) | python3 fixtures/run.py --check-tracked; then",
            "if git ls-files --error-unmatch fixtures/MANIFEST >/dev/null 2>&1; then",
            "git checkout -q -- fixtures/MANIFEST", "else", "rm -f fixtures/MANIFEST", "fi", "exit 2", "fi"]

    def test_the_block_is_pinned(self):  # 8
        lines = [ln.strip() for ln in (ROOT / "release.sh").read_text(encoding="utf-8").splitlines()
                 if not ln.lstrip().startswith("#")]
        i = lines.index(BLOCK_START)
        self.assertEqual(lines[i:i + 9], self.WANT)
        stamp = next(n for n, ln in enumerate(lines) if "sha256:" in ln and "write_bytes" in ln)
        self.assertLess(stamp, i)
        check = lines.index("python3 fixtures/run.py --check-header", i)
        self.assertEqual(check, i + 9)
        commit = ['git add fixtures/MANIFEST', 'git commit -qm "Release v$v" -- ledgerboard fixtures/MANIFEST']
        j = lines.index(commit[0], check)
        self.assertEqual(lines[j:j + 2], commit)
        cut = lines.index('git checkout -q -b "release-v$v" origin/main')
        self.assertEqual([ln for ln in lines[cut:] if ln.startswith("git commit")], [commit[1]])

    @unittest.skipUnless(shutil.which("git") and shutil.which("bash"), "needs git and bash")
    def test_the_block_runs(self):  # 7a
        block = "\n".join(_block())

        def repo(tracked_exit: int, committed: bool) -> Path:
            d = Path(tempfile.mkdtemp())
            self.addCleanup(shutil.rmtree, d)
            (d / "fixtures").mkdir()
            (d / "fixtures" / "run.py").write_text(
                "import sys\n"
                "if sys.argv[1] == '--stamp':\n    open('fixtures/MANIFEST', 'w').write('new\\n')\n"
                f"else:\n    sys.stdin.buffer.read(); print('stub: differs', file=sys.stderr); sys.exit({tracked_exit})\n")
            if committed:
                (d / "fixtures" / "MANIFEST").write_text("old\n")
            git(d, "init", "-q", "-b", "main")
            git(d, "add", ".")
            git(d, "commit", "-qm", "seed")
            return d

        def run(d: Path):
            return subprocess.run(["bash", "-c", f"set -euo pipefail; v=9.9; {block}"], cwd=d, env=ENV,
                                  capture_output=True, text=True, check=False)
        d = repo(1, committed=False)
        r = run(d)
        self.assertEqual((r.returncode, r.stderr), (2, "stub: differs\n"))
        self.assertFalse((d / "fixtures" / "MANIFEST").exists())
        d = repo(1, committed=True)
        r = run(d)
        self.assertEqual(r.returncode, 2)
        self.assertEqual((d / "fixtures" / "MANIFEST").read_text(), "old\n")
        d = repo(0, committed=False)
        r = run(d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((d / "fixtures" / "MANIFEST").read_text(), "new\n")


if __name__ == "__main__":
    unittest.main()
