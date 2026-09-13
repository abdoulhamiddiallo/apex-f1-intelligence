#!/usr/bin/env python3
"""House rules for the repository, enforced by CI.

* English only: no accented Latin letters in source code (comments, docstrings, messages)
* no em dash or en dash in any text file of the repository (the report data excepted)
* no machine-specific path (home folders, user profiles)
* pinned dependencies only
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".py", ".md", ".yml", ".yaml", ".txt", ".json", ".tmdl", ".pbip", ".pbir", ".pbism", ".platform", ".csv", ""}
SKIP_DIRS = {".git", "build", "__pycache__", "data"}
DASHES = ("\u2014", "\u2013")
PATHS = re.compile(r"(?i)(?:[A-Z]:\\Users\\|/home/[a-z]|/Users/[a-z])")
ACCENTS = re.compile(r"[\u00C0-\u00FF]")
ALLOWED_PATH = "C:\\apex-f1-intelligence"


def files():
    for p in sorted(ROOT.rglob("*")):
        if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts):
            continue
        if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES and p.name != "LICENSE" or p.name in ("LICENSE", "NOTICE"):
            yield p


def main():
    problems = []
    for p in files():
        try:
            txt = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = p.relative_to(ROOT).as_posix()
        for i, line in enumerate(txt.splitlines(), 1):
            if any(d in line for d in DASHES):
                problems.append("%s:%d: em/en dash" % (rel, i))
            if PATHS.search(line.replace(ALLOWED_PATH, "")):
                problems.append("%s:%d: machine-specific path" % (rel, i))
            if p.suffix == ".py" and ACCENTS.search(line):
                problems.append("%s:%d: accented character in source code" % (rel, i))
    req = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    for line in req.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "==" not in line:
            problems.append("requirements.txt: %r is not pinned" % line)
    if problems:
        print("\n".join(problems))
        print("\nrepo lint FAILED: %d problem(s)" % len(problems))
        return 1
    print("repo lint passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
