# Architecture

APEX is a Power BI project that is **generated, not authored**. Nothing in `dist/` was
produced by clicking in Power BI Desktop: the semantic model (TMDL), the report (PBIR JSON),
the data files and every image are written by the Python package `apex/` from two committed
inputs. This page explains the shape of the system and the reasons behind each decision.

```
data/raw/f1db-csv.zip ─┐                       ┌─ dist/data/*.csv            (15 tables)
data/raw/f1-circuits ──┤  apex.data            │
assets/logos/*.png ────┤  apex.svg_columns  ───┼─ dist/APEX.SemanticModel/   (TMDL, 243 measures)
                       │  apex.model + measures│
                       │  apex.logo/background │
                       └─ apex.report ─────────┴─ dist/APEX.Report/          (9 pages, 597 visuals)
                                 │
                          apex.validate  ─── fails the build on any defect
```

## 1. Why generate a Power BI report from code

A report with nine pages and six hundred visuals cannot be kept consistent by hand. Every
page shares the same navigation rail, KPI strip, typography, colours, panel radii and
spacing. When one of those changes, it has to change everywhere, and a human editing JSON
files or dragging visuals will miss some. Generation makes the design system a set of
Python constants and the layout a set of functions (`kpi`, `table`, `bar`, `scatter`, ...):
a change is one edit, a rebuild and a diff.

Code generation also gives three properties a hand-built `.pbix` can never have:

* **Reviewable history.** The PBIR format is one JSON file per visual, so every change is a
  readable diff. Because all identifiers are derived deterministically (see below), two
  builds of the same source produce the same bytes; a diff shows only intended changes.
* **Automated quality gates.** `apex.validate` checks 600 visuals against rules learned the
  hard way (integer font sizes, header widths, resource registration, DAX references). A
  reviewer cannot do that by eye.
* **Reproducibility.** Anyone can clone the repository and rebuild the project on a clean
  machine, offline, and get the same output as the CI run.

## 2. The pipeline

| Step | Module | Input | Output | Purpose |
|------|--------|-------|--------|---------|
| 1 | `build.py` | `data/raw/f1db-csv.zip` | `build/f1db/*.csv` | verify the SHA-256 of the archive, extract 47 f1db tables |
| 2 | `apex.data` | f1db CSV, `f1-circuits.geojson` | `dist/data/*.csv` | shape the star schema for the 2014 to 2026 era |
| 3 | `apex.logo` | SVG drawn in code | `build/assets/mark.png`, `ic_*.png` | brand mark and 18 navigation icons (on/off states) |
| 4 | `apex.background` | procedural drawing | `build/assets/bg.png`, `accent_*.png` | the page background and accent strips |
| 5 | `apex.svg_columns` | `dist/data`, `assets/logos` | `dist/data` (image columns added) | flags, circuit outlines, team badges as SVG data URIs |
| 6 | `apex.model` | column specifications in code | `dist/APEX.SemanticModel/` | TMDL tables, relationships, parameter, project files |
| 7 | `apex.measures` | DAX in code | `.../tables/Metrics.tmdl` | 243 measures with display folders and descriptions |
| 8 | `apex.report` | layout in code, `build/assets` | `dist/APEX.Report/` | 9 pages, theme, registered resources |
| 9 | `apex.validate` | `dist/` | exit code | structural checks, fails the build |

Each step is an independent `python -m apex.<step>` process. `build.py` runs them in order
with `PYTHONHASHSEED=0` so that no dictionary or set ordering can leak into the output.

## 3. Data layer: a star schema fed by CSV

f1db ships 47 normalised tables. The report needs a handful of questions answered fast:
who won, who led, how a circuit behaves, how a team's season went. `apex.data` therefore
builds a classic **star schema**:

* **Dimensions** `D_Season`, `D_Race`, `D_Circuit`, `D_Driver`, `D_Constructor`, `D_Engine`
  carry descriptive attributes, pre-computed career totals and the image columns.
* **Facts** `F_Result`, `F_Qualifying`, `F_FastestLap`, `F_Sprint`, `F_DriverStanding`,
  `F_ConstructorStanding`, `F_TrackPoint` are one row per driver per event (or per point
  of a circuit outline), with integer flags (`IsWin`, `IsPodium`, `IsPole`, `IsDNF`, ...)
  so that measures are simple `CALCULATE ( COUNTROWS ( ... ), flag = 1 )` expressions that
  compress well and evaluate quickly in VertiPaq.
* **Disconnected tables** `D_Metric` and `D_Scope` drive the report's interactivity: a
  slicer on `D_Metric[Metric]` lets a `SWITCH ( SELECTEDVALUE ( ... ) )` measure re-rank the
  Drivers page by points, wins, podiums, poles, fastest laps, average finish or DNFs without
  duplicating visuals.

The era is a hard filter (`YEAR_FROM = 2014`, `YEAR_TO = 2026`): the report is about the
turbo-hybrid era and everything after it, and keeping 13 seasons instead of 76 keeps the
model at a few megabytes.

Why CSV files rather than a database or a direct connection to f1db? Because the project
has to rebuild on any machine with nothing but Python and Power BI Desktop installed. The
`DataFolder` parameter in the model is the single place that knows where the CSV files
live; `tools/set_data_folder.py` rewrites it for a new clone.

### Circuit geometry

The Classic Eleven and Circuit Lab pages draw each track. Power BI has no vector layer for
that, so `apex.data` projects each circuit's GeoJSON ring onto a square plane (equirectangular
projection with a cosine correction at the circuit's latitude, then scaled to a 180-unit box),
stores the points in `F_TrackPoint`, and `apex.svg_columns` renders them as an inline SVG
path stored in `D_Circuit[TrackSvg]` (data category *ImageUrl*). The same points feed the
scatter-based "blueprint" of the Circuit Lab page, where the outline is an actual chart and
can therefore react to filters.

### Image columns

Flags, circuit outlines, helmets, car silhouettes and team badges are **SVG data URIs stored
in the model**. An `ImageUrl` column with `data:image/svg+xml;utf8,...` renders in tables
and cards without any external file, so the report has no dependency on a web server or a
network. The 24 team logos in `assets/logos` are embedded the same way as base64 PNG; when a
logo is missing the generator draws a crest with the team's colour and abbreviation instead.

## 4. Semantic model: TMDL written by hand, on purpose

The model is emitted as TMDL text rather than through an API because TMDL is what Power BI
Desktop itself writes in PBIP developer mode: the generated folder opens directly, and the
format is stable and diff-friendly.

Design rules applied throughout:

* **Measures live in one table** (`Metrics`, hidden placeholder column) sorted into
  numbered display folders (`01 Race record` ... `19 Countries`); a `///` description above
  a measure becomes the tooltip Power BI shows in the field list.
* **Columns are typed, formatted and summarised explicitly.** Every key is hidden, every
  numeric flag has `summarizeBy: none`, so implicit measures cannot produce misleading sums.
  `discourageImplicitMeasures` is set on the model.
* **Sort-by columns** give eras, metrics and race labels a meaningful order.
* **Lineage tags and relationship names are UUID v5** values derived from a fixed namespace
  and the object's position in the generator. Power BI needs them to be unique; the project
  needs them to be stable so that a rebuild does not touch 700 files.

### Measure patterns worth stealing

`docs/measures.md` lists all 243. A few patterns recur:

* *Zero-filled counts*: `IF ( NOT ISBLANK ( [Grands Prix] ), [Wins] + 0 )` shows `0` for a
  driver who started but never won, while a driver with no start in the context stays blank
  and therefore never appears as a phantom row.
* *Split leaderboards*: `Record Rank = RANKX ( ALLSELECTED ( D_Constructor[Team] ), [Points],, DESC )`
  plus a visual-level filter `Record Rank <= 12` on one table and `> 12` on its neighbour
  splits a ranking across two side-by-side tables (rows 1 to 12, rows 13 to 24) with no
  manual maintenance.
* *Season default*: `Default Season` returns the current season when no season is selected, so
  the Race Results and Teams pages are live the moment the report opens, and follow the
  slicer afterwards.
* *Text measures for cards*: `Season Headline` assembles a sentence
  ("X leads on N points, G clear, with R rounds to run") so the page narrative updates by itself.
* *Colour measures*: `Driver Team Colour` returns a hex string used as a conditional
  fill, so bars and scatter points always wear the constructor's livery colour.

## 5. Report layer: PBIR built from a layout DSL

`apex/pbir.py` wraps the PBIR JSON schemas (visual container 2.12, page 2.1, report 3.3) in
small functions: `L`, `S`, `N`, `B`, `C` build literals; `Page.add` writes a visual with a
name, z-order and tab order; `card`, `table`, `bar`, `line`, `area`, `scatter`, `slicer`,
`navbtn`, `image` produce complete visuals. `apex/report.py` is then a readable description
of nine pages.

Two mechanics are specific to this project:

* **The navigation rail is a coordinate transform.** Pages were first laid out on a
  1600 x 900 canvas with content from x = 96 to 1576. When the rail grew from 72 to
  120 px, `Page.add` started compressing every content x coordinate and width by
  `K = 1432 / 1480` and shifting it to start at x = 144, including table column widths.
  The layout code did not change; the transform did.
* **Visual-level measure filters** (`Record Rank <= 12`) use the `filterConfig` block
  with `ComparisonKind` 4 (less than or equal) or 1 (greater than). This is the syntax
  Power BI Desktop writes itself, so the filter pane shows it as a normal filter.

Power BI rendering rules encoded in the generator (and enforced by `apex.validate`):

| Rule | Symptom when broken |
|------|---------------------|
| font sizes are integers | Power BI ignores `13.7D` and falls back to 9 pt |
| font families are full CSS stacks (`'DIN', wf_standard-font, helvetica, arial, sans-serif`) | a bare `DIN` renders in serif |
| a text box is at least as tall as its font size in pixels | scrollbars appear inside the box |
| a value card is at least 2 px tall per point of font size | the number is clipped |
| table column widths sum to at most the visual width minus 45 px | a horizontal scrollbar appears |
| a header label fits its column at the header font size | the label is truncated with an ellipsis |
| tables with an image column have tooltips off | hovering shows the raw `data:image` text |
| every image used is listed in `report.json` under `RegisteredResources` | the image is blank |
| no `pageBinding` in a visual | Power BI Desktop crashes on open |

## 6. Validation and CI

`apex.validate` reads the generated model and report back and cross-checks them: every
`Measure` and `Column` referenced by a visual exists, every DAX reference inside a measure
resolves (qualified `Table[Column]`, bare `[Measure]`, or a column alias declared in the same
expression), every resource is registered and used, every navigation button targets a page,
no two data visuals overlap, no visual leaves the canvas, and no em or en dash appears in
displayed text. It exits non-zero on the first list of problems.

The GitHub Actions workflow (`.github/workflows/build.yml`) runs `python build.py --clean
--check` on a fresh Ubuntu runner: it rebuilds twice, requires both builds to be identical,
and requires the committed `dist/` to equal the rebuild. A pull request that changes a label
and forgets to rebuild fails; a change that truncates a header fails; a DAX typo fails.

## 7. Repository layout

```
apex/                the generator package (one module per step, config.py holds every path)
assets/logos/        24 team logos supplied as PNG (optional, see NOTICE)
build.py             orchestrator: unzip, run the steps, validate, prove determinism
data/raw/            the two bundled inputs and their SHA-256 checksums
dist/                the generated Power BI project (open dist/APEX.pbip)
docs/                this documentation, the measure catalog, screenshots
tools/               measures catalog generator, repository lint, data folder helper
.github/workflows/   the CI rebuild
```
