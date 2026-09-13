# -*- coding: utf-8 -*-
"""Structural validation of the generated project. Any defect fails the build.

Run after the other steps (``python -m apex.validate``) or through ``build.py``.
The checks encode every Power BI rendering pitfall met while building APEX:

* every JSON file parses and every page/visual carries its schema and position
* no visual leaves the 1600 x 900 canvas, no two data visuals overlap
* every font size is an integer (Power BI silently falls back to 9 pt otherwise)
* every text box is tall enough for its font size (below that Power BI shows scrollbars)
* every card is tall enough for its font size
* table column widths fit inside the visual (no horizontal scrollbar) and every
  column header fits on one line (no truncated label)
* every measure and column referenced by a visual exists in the semantic model
* every DAX reference inside a measure resolves to a measure, a column or a table
* every image resource used by a visual is present and registered, and vice versa
* every table of the model has its CSV file, with every source column present
* every navigation button targets an existing page
* no em dash or en dash in any displayed text, DAX string or label
* no machine-specific path inside the generated files
"""
import csv
import json
import os
import re
import sys
from pathlib import Path

from apex.config import DIST_DIR, NAME, REPORT_DIR, MODEL_DIR, DATA_DIR, DEFAULT_DATA_FOLDER

CANVAS_W, CANVAS_H = 1600, 900
MIN_TEXTBOX_H = 16           # absolute floor for a text box
LINE_HEIGHT = 1.0            # a text box needs at least pt * 96/72 * LINE_HEIGHT px, otherwise Power BI shows a scrollbar
CARD_H_PER_PT = 2.0          # a value-only card needs ~2 px of height per point of font size
TABLE_SCROLL_MARGIN = 45     # px reserved for the vertical scrollbar + grid borders
HEADER_PADDING = 10          # px of padding inside a table header cell
FORBIDDEN_TEXT = ("\u2014", "\u2013")   # em dash, en dash
FORBIDDEN_PATHS = (":\\Users\\", "/home/", "/Users/", "C:\\Users")

# Advance widths (em) of DejaVu Sans Bold scaled to approximate Segoe UI Bold, used to
# estimate header label widths without depending on the fonts installed on the machine.
_W = {'0': .696, '1': .696, '2': .696, '3': .696, '4': .696, '5': .696, '6': .696, '7': .696, '8': .696, '9': .696,
      'a': .675, 'b': .716, 'c': .593, 'd': .716, 'e': .678, 'f': .435, 'g': .716, 'h': .712, 'i': .343, 'j': .343,
      'k': .665, 'l': .343, 'm': 1.042, 'n': .712, 'o': .687, 'p': .716, 'q': .716, 'r': .493, 's': .595, 't': .478,
      'u': .712, 'v': .652, 'w': .924, 'x': .645, 'y': .652, 'z': .582, 'A': .774, 'B': .762, 'C': .734, 'D': .83,
      'E': .683, 'F': .683, 'G': .821, 'H': .837, 'I': .372, 'J': .372, 'K': .775, 'L': .637, 'M': .995, 'N': .837,
      'O': .85, 'P': .733, 'Q': .85, 'R': .77, 'S': .72, 'T': .682, 'U': .812, 'V': .774, 'W': 1.103, 'X': .771,
      'Y': .724, 'Z': .725, ' ': .348, '.': .38, ',': .38, '-': .415, '/': .365, '%': 1.002, '(': .457, ')': .457,
      '&': .872, ':': .4, "'": .306, '#': .838, '+': .838, '_': .5}
SEGOE_FACTOR = 0.83


def text_px(s, pt):
    em = sum(_W.get(c, .7) for c in s)
    return em * pt * 96 / 72 * SEGOE_FACTOR


class Report:
    def __init__(self):
        self.errors = []
        self.stats = {}

    def err(self, where, msg):
        self.errors.append("%s: %s" % (where, msg))


R = Report()


# --------------------------------------------------------------------------- helpers
def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        R.err(str(path), "invalid JSON (%s)" % e)
        return None


def walk(obj, path=""):
    """Yield (path, key, value) for every key of a nested JSON object."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield path, k, v
            yield from walk(v, path + "/" + k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, path + "[%d]" % i)


def literal(v):
    """Return the literal value string of an {"expr":{"Literal":{"Value":...}}} node, or None."""
    try:
        return v["expr"]["Literal"]["Value"]
    except (KeyError, TypeError):
        return None


def num(lit):
    return float(lit.rstrip("DL"))


# --------------------------------------------------------------------------- model
TMDL_MEASURE = re.compile(r"^\tmeasure\s+(?:'((?:[^']|'')+)'|([A-Za-z0-9_]+))\s*=", re.M)
TMDL_COLUMN = re.compile(r"^\tcolumn\s+(?:'((?:[^']|'')+)'|([A-Za-z0-9_]+))\s*$", re.M)
TMDL_SOURCE = re.compile(r"^\t\tsourceColumn:\s*(.+?)\s*$", re.M)
TMDL_TABLE = re.compile(r"^table\s+(?:'((?:[^']|'')+)'|([A-Za-z0-9_]+))\s*$", re.M)


def read_model():
    tables, columns, measures, dax = {}, {}, {}, {}
    tdir = MODEL_DIR / "definition" / "tables"
    if not tdir.is_dir():
        R.err(str(tdir), "tables folder missing")
        return tables, columns, measures, dax
    for f in sorted(tdir.glob("*.tmdl")):
        txt = f.read_text(encoding="utf-8")
        m = TMDL_TABLE.search(txt)
        if not m:
            R.err(str(f), "no table declaration")
            continue
        tname = (m.group(1) or m.group(2)).replace("''", "'")
        cols = [(a or b).replace("''", "'") for a, b in TMDL_COLUMN.findall(txt)]
        tables[tname] = {"file": f, "columns": cols, "sources": TMDL_SOURCE.findall(txt), "text": txt}
        for c in cols:
            columns.setdefault(tname, set()).add(c)
        for a, b in TMDL_MEASURE.findall(txt):
            name = (a or b).replace("''", "'")
            if name in measures:
                R.err(str(f), "duplicate measure %r" % name)
            measures[name] = tname
        # capture the DAX body of every measure (up to the next indented property line)
        for mm in re.finditer(r"^\tmeasure\s+(?:'(?:[^']|'')+'|[A-Za-z0-9_]+)\s*=(.*?)(?=^\t\t[a-zA-Z]+:|^\tmeasure|^\t///|\Z)",
                              txt, re.M | re.S):
            head = txt[mm.start():mm.start() + 200]
            nm = TMDL_MEASURE.match(head)
            if nm:
                dax[(nm.group(1) or nm.group(2)).replace("''", "'")] = mm.group(1)
    R.stats["tables"] = len(tables)
    R.stats["measures"] = len(measures)
    return tables, columns, measures, dax


DAX_STRING = re.compile(r'"(?:[^"]|"")*"')
DAX_QUALIFIED = re.compile(r"(?:'((?:[^']|'')+)'|([A-Za-z_][A-Za-z0-9_]*))\s*\[([^\]]+)\]")
DAX_BARE = re.compile(r"(?<![A-Za-z0-9_'\]\)\s])\[([^\]]+)\]|(?<=[\s(,+\-*/=<>&|])\[([^\]]+)\]")
DAX_FUNCS = {"CALCULATE", "FILTER", "ALL", "VALUES", "SUMX", "MAXX", "MINX", "COUNTROWS", "SELECTEDVALUE",
             "RANKX", "TOPN", "ADDCOLUMNS", "SUMMARIZE", "DISTINCTCOUNT", "AVERAGEX", "ALLSELECTED",
             "KEEPFILTERS", "REMOVEFILTERS", "ISBLANK", "DIVIDE", "IF", "SWITCH", "TRUE", "FALSE",
             "CONCATENATEX", "FORMAT", "COALESCE", "MAX", "MIN", "SUM", "AVERAGE", "VAR", "RETURN",
             "CALCULATETABLE", "NOT", "AND", "OR", "BLANK", "HASONEVALUE", "SELECTEDMEASURE", "ROUND",
             "INT", "COUNT", "FIRSTNONBLANK", "LASTNONBLANK", "RELATED", "RELATEDTABLE", "EARLIER",
             "ALLEXCEPT", "UNICHAR", "REPT", "LEN", "LEFT", "RIGHT", "MID", "SUBSTITUTE", "UPPER", "LOWER",
             "TRIM", "ISINSCOPE", "DISTINCT", "COUNTX", "MAXA", "MINA", "IN", "GENERATE", "ROW", "CROSSJOIN",
             "NATURALINNERJOIN", "EXCEPT", "INTERSECT", "UNION", "SELECTCOLUMNS", "CONTAINS", "LOOKUPVALUE",
             "USERELATIONSHIP", "TREATAS", "ISEMPTY", "PERCENTILEX.INC", "MEDIANX", "GEOMEANX", "STDEVX.P",
             "ABS", "MOD", "ISNUMBER", "VALUE", "DATE", "YEAR", "MONTH", "DAY", "TODAY", "NOW", "DATEDIFF",
             "CONVERT", "TRUNC", "CEILING", "FLOOR", "EXP", "LN", "LOG", "SQRT", "POWER", "SIGN", "COUNTBLANK",
             "ISFILTERED", "ISCROSSFILTERED", "SELECTEDVALUE", "SAMPLE", "OFFSET", "WINDOW", "INDEX", "ORDERBY",
             "PARTITIONBY", "RANK", "ROWNUMBER", "ASC", "DESC", "PRODUCTX", "IFERROR", "ERROR", "CURRENCY",
             "COUNTA", "SUMMARIZECOLUMNS", "IGNORE", "NONVISUAL", "NAMEOF", "COMBINEVALUES", "EXACT", "FIND",
             "SEARCH", "REPLACE", "FIXED", "MROUND", "QUOTIENT", "RAND", "DATEVALUE", "TIME", "HOUR", "MINUTE",
             "SECOND", "WEEKDAY", "WEEKNUM", "EOMONTH", "EDATE", "DATESYTD", "TOTALYTD", "SAMEPERIODLASTYEAR",
             "DATEADD", "PREVIOUSYEAR", "NEXTYEAR", "PATH", "PATHITEM", "MAXX", "AVERAGEA", "ISONORAFTER",
             "SUBSTITUTEWITHINDEX", "GROUPBY", "CURRENTGROUP", "DETAILROWS", "EVALUATEANDLOG", "TOCSV", "TOJSON"}


def check_dax(measures, columns, dax):
    """Every 'Table'[Column], Table[Column] and bare [Measure] must resolve."""
    bad = 0
    all_columns = set().union(*columns.values()) if columns else set()
    for name, body in dax.items():
        # column aliases declared inside the measure ("@p" in ADDCOLUMNS, SELECTCOLUMNS, ...)
        aliases = {m.group(0)[1:-1] for m in DAX_STRING.finditer(body)}
        body_ns = DAX_STRING.sub('""', body)
        # variables declared in this measure may be used as bare identifiers; not bracketed, ignore
        for a, b, col in DAX_QUALIFIED.findall(body_ns):
            tbl = (a or b).replace("''", "'")
            if tbl.upper() in DAX_FUNCS:
                continue
            col = col.strip()
            if tbl not in columns:
                if tbl == "Metrics" and col in measures:
                    continue
                R.err("measure %r" % name, "unknown table %r in %r[%s]" % (tbl, tbl, col))
                bad += 1
            elif col not in columns[tbl] and not (col in measures and measures[col] == tbl):
                R.err("measure %r" % name, "unknown column %s[%s]" % (tbl, col))
                bad += 1
        # bare measure references: [X] not preceded by an identifier or quote
        stripped = DAX_QUALIFIED.sub(" X ", body_ns)
        for m in re.finditer(r"\[([^\]]+)\]", stripped):
            ref = m.group(1).strip()
            # a bare [X] is a measure, a column alias of this measure, or a column used in row context
            if ref not in measures and ref not in aliases and ref not in all_columns:
                R.err("measure %r" % name, "unknown reference [%s]" % ref)
                bad += 1
    R.stats["dax references checked"] = len(dax)
    return bad


def check_csv(tables):
    for tname, t in tables.items():
        if not t["sources"] or "partition %s = calculated" % tname in t["text"] or "= calculated\n" in t["text"]:
            continue  # calculated table or measure table
        f = DATA_DIR / (tname + ".csv")
        if not f.is_file():
            R.err(tname, "missing data file %s" % f.name)
            continue
        with open(f, encoding="utf-8-sig", newline="") as fh:
            rd = csv.reader(fh)
            header = next(rd, [])
            n = sum(1 for _ in rd)
        if n == 0:
            R.err(f.name, "no data rows")
        for s in t["sources"]:
            if s not in header:
                R.err(tname, "source column %r not in %s" % (s, f.name))
    R.stats["csv files"] = len(list(DATA_DIR.glob("*.csv")))


# --------------------------------------------------------------------------- report
def check_report(measures, columns):
    pages_dir = REPORT_DIR / "definition" / "pages"
    pages_meta = load_json(pages_dir / "pages.json") or {}
    page_order = pages_meta.get("pageOrder", [])
    report_json = load_json(REPORT_DIR / "definition" / "report.json") or {}
    registered = set()
    themes = set()
    for pkg in report_json.get("resourcePackages", []):
        if pkg.get("type") == "RegisteredResources":
            registered = {it["name"] for it in pkg.get("items", [])}
            themes = {it["name"] for it in pkg.get("items", []) if it.get("type") != "Image"}
    for t in report_json.get("themeCollection", {}).values():
        if t.get("type") == "RegisteredResources" and t.get("name") not in registered:
            R.err("report.json", "theme %r is not a registered resource" % t.get("name"))
    res_dir = REPORT_DIR / "StaticResources" / "RegisteredResources"
    on_disk = {p.name for p in res_dir.iterdir()} if res_dir.is_dir() else set()
    for r in registered - on_disk:
        R.err("report.json", "registered resource %r missing on disk" % r)
    for r in on_disk - registered:
        R.err("RegisteredResources", "file %r not registered in report.json" % r)
    used_resources = set()

    pages = {}
    nvis = 0
    for pdir in sorted(p for p in pages_dir.iterdir() if p.is_dir()):
        page = load_json(pdir / "page.json")
        if not page:
            continue
        pages[page["name"]] = page
        if page["name"] not in page_order:
            R.err(page["name"], "page not listed in pages.json")
        for k in ("$schema", "name", "displayName", "width", "height"):
            if k not in page:
                R.err(page["name"], "page.json lacks %r" % k)
        data_visuals = []
        for vf in sorted(pdir.glob("visuals/*/visual.json")):
            v = load_json(vf)
            if not v:
                continue
            nvis += 1
            where = "%s/%s" % (page["name"], v.get("name", vf.parent.name))
            if v.get("name") != vf.parent.name:
                R.err(where, "visual name does not match its folder")
            for k in ("$schema", "position", "visual"):
                if k not in v:
                    R.err(where, "visual.json lacks %r" % k)
            pos = v.get("position", {})
            x, y, w, h = (pos.get(k, 0) for k in ("x", "y", "width", "height"))
            vt = v.get("visual", {}).get("visualType", "?")
            if x < 0 or y < 0 or x + w > page.get("width", CANVAS_W) or y + h > page.get("height", CANVAS_H):
                R.err(where, "%s leaves the canvas (%d,%d,%d,%d)" % (vt, x, y, w, h))
            objects = v.get("visual", {}).get("objects", {}) or {}

            # --- font sizes must be integers
            for pth, key, val in walk(v):
                if key in ("fontSize", "textSize") and isinstance(val, dict):
                    lit = literal(val)
                    if lit is None:
                        continue
                    if not re.fullmatch(r"\d+D", lit):
                        R.err(where, "non-integer font size %s at %s" % (lit, pth))
                if key == "textStyle" and isinstance(val, dict) and "fontSize" in val:
                    # rich text accepts half points; anything finer is silently rounded
                    if not re.fullmatch(r"\d+(\.5)?pt", str(val["fontSize"])):
                        R.err(where, "invalid text box font size %r" % val["fontSize"])
                if key == "fontFamily" and isinstance(val, dict):
                    lit = literal(val) or ""
                    if "," not in lit:
                        R.err(where, "font family %s is not a full CSS stack" % lit)

            # --- text boxes
            is_panel = False
            if vt == "textbox":
                try:
                    runs = objects["general"][0]["properties"]["paragraphs"][0]["textRuns"]
                    is_panel = all(r["value"].strip() == "" for r in runs)
                except (KeyError, IndexError, TypeError):
                    runs = []
                pts = [float(str(r.get("textStyle", {}).get("fontSize", "0pt")).rstrip("pt") or 0) for r in runs]
                need = max([MIN_TEXTBOX_H] + [pt * 96 / 72 * LINE_HEIGHT for pt in pts])
                if h < need and not is_panel:
                    R.err(where, "text box %d px tall for %s pt text (needs %d, scrollbar otherwise)" % (h, max(pts), need))
                for r in runs:
                    for ch in FORBIDDEN_TEXT:
                        if ch in r.get("value", ""):
                            R.err(where, "forbidden dash in text %r" % r["value"])

            # --- cards
            if vt == "card":
                try:
                    size = num(literal(objects["labels"][0]["properties"]["fontSize"]))
                except (KeyError, TypeError):
                    size = 0
                if size and h < size * CARD_H_PER_PT:
                    R.err(where, "card %d px tall for a %d pt value (needs %d)" % (h, size, size * CARD_H_PER_PT))

            # --- tables
            if vt == "tableEx" and "columnWidth" in objects:
                widths = []
                for cw in objects["columnWidth"]:
                    widths.append((cw.get("selector", {}).get("metadata", "?"), num(literal(cw["properties"]["value"]))))
                total = sum(wd for _, wd in widths)
                if total > w - TABLE_SCROLL_MARGIN:
                    R.err(where, "column widths sum to %d px for a %d px table (max %d): horizontal scrollbar"
                          % (total, w, w - TABLE_SCROLL_MARGIN))
                try:
                    hdr_pt = num(literal(objects["columnHeaders"][0]["properties"]["fontSize"]))
                    wrap = literal(objects["columnHeaders"][0]["properties"].get("wordWrap", {})) == "true"
                except (KeyError, TypeError):
                    hdr_pt, wrap = 0, True
                if hdr_pt and not wrap:
                    for meta, wd in widths:
                        label = meta.split(".", 1)[-1]
                        need = text_px(label, hdr_pt) + HEADER_PADDING
                        if need > wd:
                            R.err(where, "header %r needs ~%d px at %d pt but the column is %d px: truncated label"
                                  % (label, need, hdr_pt, wd))

            # --- field references
            for pth, key, val in walk(v.get("visual", {})):
                if key == "Measure" and isinstance(val, dict) and "Property" in val:
                    if val["Property"] not in measures:
                        R.err(where, "unknown measure %r" % val["Property"])
                if key == "Column" and isinstance(val, dict) and "Property" in val:
                    ent = val.get("Expression", {}).get("SourceRef", {}).get("Entity")
                    if ent and val["Property"] not in columns.get(ent, set()):
                        R.err(where, "unknown column %s[%s]" % (ent, val["Property"]))
            for pth, key, val in walk(v.get("filterConfig", {})):
                if key == "Property" and isinstance(val, str) and "/Measure" in pth and val not in measures:
                    R.err(where, "filter on unknown measure %r" % val)

            # --- resources
            for pth, key, val in walk(v):
                if key == "ResourcePackageItem" and isinstance(val, dict):
                    used_resources.add(val.get("ItemName"))
                    if val.get("ItemName") not in registered:
                        R.err(where, "image resource %r not registered" % val.get("ItemName"))
                if key == "navigationSection" and isinstance(val, dict):
                    target = (literal(val) or "").strip("'")
                    if target and target not in page_order:
                        R.err(where, "navigation target %r is not a page" % target)

            # --- title / subtitle text
            for pth, key, val in walk(v.get("visual", {}).get("visualContainerObjects", {})):
                if key == "text" and isinstance(val, dict):
                    lit = literal(val) or ""
                    for ch in FORBIDDEN_TEXT:
                        if ch in lit:
                            R.err(where, "forbidden dash in title %s" % lit)

            if vt not in ("actionButton", "image", "shape") and not is_panel:
                data_visuals.append((v["name"], vt, x, y, w, h))

        # --- overlaps between data visuals of the same page
        for i in range(len(data_visuals)):
            for j in range(i + 1, len(data_visuals)):
                a, b = data_visuals[i], data_visuals[j]
                ox = min(a[2] + a[4], b[2] + b[4]) - max(a[2], b[2])
                oy = min(a[3] + a[5], b[3] + b[5]) - max(a[3], b[3])
                if ox > 2 and oy > 2:
                    R.err(page["name"], "%s(%s) overlaps %s(%s) by %dx%d px" % (a[0], a[1], b[0], b[1], ox, oy))

    for p in page_order:
        if p not in pages:
            R.err("pages.json", "page %r listed but missing" % p)
    for r in registered - used_resources - themes:
        R.err("report.json", "registered resource %r is never used" % r)
    R.stats["pages"] = len(pages)
    R.stats["visuals"] = nvis


def check_text_files():
    """Forbidden dashes in DAX strings, machine paths anywhere in dist."""
    for f in sorted(DIST_DIR.rglob("*")):
        if not f.is_file() or f.suffix.lower() not in (".json", ".tmdl", ".pbip", ".pbir", ".pbism", ".csv"):
            continue
        txt = f.read_text(encoding="utf-8", errors="replace")
        rel = str(f.relative_to(DIST_DIR))
        for ch in FORBIDDEN_TEXT:
            if ch in txt:
                line = next(i for i, l in enumerate(txt.splitlines(), 1) if ch in l)
                R.err(rel, "forbidden dash at line %d" % line)
        if f.suffix.lower() != ".csv":
            for bad in FORBIDDEN_PATHS:
                if bad in txt and not (bad == "C:\\Users" and False):
                    # the DataFolder parameter default is the only absolute path allowed
                    if bad in DEFAULT_DATA_FOLDER:
                        continue
                    R.err(rel, "machine-specific path %r" % bad)


def check_project_files():
    for rel in (NAME + ".pbip", NAME + ".Report/definition.pbir", NAME + ".SemanticModel/definition.pbism",
                NAME + ".SemanticModel/definition/model.tmdl", NAME + ".SemanticModel/definition/database.tmdl",
                NAME + ".Report/definition/version.json", NAME + ".Report/definition/pages/pages.json"):
        if not (DIST_DIR / rel).is_file():
            R.err(rel, "missing project file")
    pbir = load_json(REPORT_DIR / "definition.pbir") or {}
    path = pbir.get("datasetReference", {}).get("byPath", {}).get("path")
    if path != "../" + NAME + ".SemanticModel":
        R.err("definition.pbir", "dataset reference is %r" % path)


def main():
    tables, columns, measures, dax = read_model()
    check_dax(measures, columns, dax)
    check_csv(tables)
    check_report(measures, columns)
    check_text_files()
    check_project_files()
    for k, v in R.stats.items():
        print("  %-24s %6d" % (k, v))
    if R.errors:
        print("\nVALIDATION FAILED: %d problem(s)" % len(R.errors))
        for e in R.errors:
            print("  - " + e)
        sys.exit(1)
    print("validation passed: 0 problems")


if __name__ == "__main__":
    main()
