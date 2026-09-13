#!/usr/bin/env python3
"""Point the semantic model at the CSV files of this clone.

Power BI Desktop needs an absolute path for the DataFolder parameter. The committed
default is C:\\apex-f1-intelligence\\dist\\data; run this script once after cloning
somewhere else (or pass a path) and the parameter is rewritten in place:

    python tools/set_data_folder.py            # use <this clone>/dist/data
    python tools/set_data_folder.py D:\\data    # use an explicit folder

The same thing can be done inside Power BI Desktop: Home > Transform data >
Edit parameters > DataFolder. Note that this edits a generated file, so a later
``python build.py`` restores the default.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPR = ROOT / "dist" / "APEX.SemanticModel" / "definition" / "expressions.tmdl"


def main():
    folder = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else (ROOT / "dist" / "data").resolve()
    txt = EXPR.read_text(encoding="utf-8")
    new, n = re.subn(r'(expression DataFolder = ")[^"]*(")', lambda m: m.group(1) + str(folder).replace("\\", "\\\\") + m.group(2), txt)
    if n != 1:
        sys.exit("DataFolder parameter not found in %s" % EXPR)
    EXPR.write_text(new, encoding="utf-8")
    print("DataFolder ->", folder)


if __name__ == "__main__":
    main()
