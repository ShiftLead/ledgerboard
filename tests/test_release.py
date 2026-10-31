"""release.sh --tag: it tags from any checkout whose HEAD is origin/main, and from nowhere else (TD-009).

Each test builds a throwaway origin from this tree's release.sh, ledgerboard.py and fixtures/run.py,
clones it, and runs the clone's release.sh. git's identity comes from the environment, never config.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ("release.sh", "ledgerboard.py", "fixtures/run.py")
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
        self.version = (ROOT / "ledgerboard.py").read_text(encoding="utf-8").split()[2][1:]  # "# ledgerboard v2.2 …"
        seed = self.tmp / "seed"
        for f in FILES:
            (seed / f).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / f, seed / f)
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


if __name__ == "__main__":
    unittest.main()
