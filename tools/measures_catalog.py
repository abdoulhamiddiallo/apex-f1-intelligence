#!/usr/bin/env python3
"""Generate docs/measures.md from the DAX measures of the semantic model.

The catalog is committed so that it is readable on GitHub; the CI job regenerates
it and fails if it is out of date.
"""
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TMDL = ROOT / "dist" / "APEX.SemanticModel" / "definition" / "tables" / "Metrics.tmdl"
OUT = ROOT / "docs" / "measures.md"

MEASURE = re.compile(r"^\tmeasure (?:'((?:[^']|'')+)'|([A-Za-z0-9_]+)) =(.*)$")


def parse(txt):
    """Yield (name, dax, folder, format, description) for every measure of a TMDL table."""
    desc = ""
    cur = None
    for line in txt.splitlines():
        m = MEASURE.match(line)
        if m:
            if cur:
                yield cur
            cur = {"name": (m.group(1) or m.group(2)).replace("''", "'"), "dax": [m.group(3)],
                   "folder": "", "fmt": "", "desc": desc}
            desc = ""
            continue
        if line.startswith("\t/// "):
            desc = line[5:].strip()
            continue
        if cur is None:
            continue
        if line.startswith("\t\t") and not line.startswith("\t\t\t"):
            key, _, val = line.strip().partition(":")
            if key == "displayFolder":
                cur["folder"] = val.strip()
            elif key == "formatString":
                cur["fmt"] = val.strip()
            elif key in ("lineageTag", "isHidden", "annotation") or not _:
                pass
            continue
        if line.startswith("\t\t\t"):
            cur["dax"].append(line.strip())
            continue
        if line.startswith("\tcolumn") or line.startswith("\tpartition"):
            yield cur
            cur = None
    if cur:
        yield cur


def main():
    txt = TMDL.read_text(encoding="utf-8")
    folders = OrderedDict()
    n = 0
    for m in parse(txt):
        dax = " ".join(" ".join(m["dax"]).split())
        folders.setdefault(m["folder"] or "(no folder)", []).append((m["name"], dax, m["fmt"], m["desc"]))
        n += 1

    L = ["# Measure catalog", "",
         "Generated from `dist/APEX.SemanticModel/definition/tables/Metrics.tmdl` by "
         "`tools/measures_catalog.py`. %d measures in %d display folders. "
         "Do not edit by hand: the CI job regenerates this file and fails if it differs." % (n, len(folders)), ""]
    L += ["## Contents", ""]
    for f in folders:
        L.append("* [%s](#%s) (%d)" % (f, re.sub(r"[^a-z0-9]+", "-", f.lower()).strip("-"), len(folders[f])))
    L.append("")
    for f, items in folders.items():
        L += ["## %s" % f, ""]
        for name, dax, fmt, desc in items:
            L.append("### %s" % name)
            L.append("")
            if desc:
                L.append(desc)
                L.append("")
            if fmt:
                L.append("Format: `%s`" % fmt)
                L.append("")
            L.append("```dax")
            L.append(dax)
            L.append("```")
            L.append("")
    OUT.write_text("\n".join(L), encoding="utf-8")
    print("docs/measures.md: %d measures" % n)
    return 0 if n else 1


if __name__ == "__main__":
    sys.exit(main())
