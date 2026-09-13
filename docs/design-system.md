# Design system

Every visual on the nine pages is produced by a handful of functions in `apex/pbir.py` and
`apex/report.py`, which is why the report looks like one object rather than nine dashboards.
This page records the constants and the rules, and the Power BI behaviour that shaped them.

## Canvas

* 1600 x 900 px, `FitToPage`, page background `#0A0C10`, outspace `#05070B`.
* A single generated background image (`bg.png`, 1600 x 900) sits behind every page: a night
  gradient, a faint carbon weave, an original single-seater silhouette in watermark, coral
  and cold-blue glows, speed streaks. It is drawn procedurally by `apex/background.py` with a
  fixed random seed.
* A 120 px navigation rail on the left (`RAIL_W`), coral edge line 4 px wide.
* Content area from x = 144 to x = 1576. Layout code still thinks in the original 96 to 1576
  coordinates; `Page.add` applies the rail transform (`K = 1432 / 1480`).

## Grid

| Region | y | height | purpose |
|--------|---|--------|---------|
| eyebrow + title + subtitle | 16 to 104 | | `·  FORMULA 1  ·  2014-2026`, page title at 30 pt, subtitle at 13 pt |
| KPI strip | 112 | 152 | four or five tiles (`kpi`, `kpi_num`, `bigcard`) |
| row 2 | 276 | 372 | main panels |
| row 3 | 664 | 200 | secondary panels |

Columns: three columns of 482 px at x = 96, 594, 1092; four of 358 px; five of 283 px.
Panels are 14 px radius, `#12161F` at 14 percent transparency over the background, border
`#2C3446`.

## Colour

| Token | Hex | Use |
|-------|-----|-----|
| `INK` | `#F4F6FA` | primary text, values |
| `MUTED` | `#C4CBD8` | axis labels, legends |
| `DIM` | `#8F99AB` | subtitles, captions |
| `LINE` | `#2C3446` | panel borders, gridlines |
| `PANEL` / `PANEL2` | `#12161F` / `#0D1017` | panel and slicer backgrounds |
| `RED` | `#F0503C` | brand coral: headers, active states, Season section |
| `CYAN` | `#22D3EE` | Circuits section |
| `AMBER` | `#F5B942` | History section |
| `GREEN`, `VIOLET` | `#3BD07A`, `#A78BFA` | secondary series |

Data series never use these tokens when a team is involved: bars, lines, scatter points and
areas take their colour from the `Team Colour` and `Driver Team Colour` measures (a curated
hex per constructor in `D_Constructor[TeamColour]`), applied as a conditional fill with a
`dataViewWildcard` selector. A Ferrari bar is always Ferrari red.

## Typography

Power BI resolves font names only when they are written the way Power BI Desktop itself
writes them, as a full CSS stack whose second entry is the web-font alias:

| Token | Stack | Use |
|-------|-------|-----|
| `FD` | `'DIN', wf_standard-font, helvetica, arial, sans-serif` | KPI values, titles |
| `FTS` | `'Segoe UI Semibold', wf_segoe-ui_semibold, helvetica, arial, sans-serif` | panel titles, labels |
| `FTB` | `'Segoe UI Bold', wf_segoe-ui_bold, helvetica, arial, sans-serif` | table headers |
| `FT` | `'Segoe UI', wf_segoe-ui_normal, helvetica, arial, sans-serif` | body text |
| `FM` | `Consolas, 'Courier New', monospace` | times and codes |

A bare `DIN` falls back to a serif face. Sizes: page title 30 pt, panel titles 16 pt, KPI
values 24 to 44 pt, table body 13 pt (11 x 1.2), table headers 12 to 13 pt, axes 12 to 13 pt.
Every size that reaches a visual property is an integer (`fz()` rounds), because Power BI
ignores `13.7D` and silently uses 9 pt.

## Components

| Function | Visual type | Notes |
|----------|-------------|-------|
| `rail`, `navbtn` | `image` + `actionButton` | icon on/off states as images, transparent button on top with `PageNavigation`; hover fill coral at 12 percent |
| `chrome` | `textbox`, `image`, `card` | eyebrow, title, subtitle (text or measure), accent strip image |
| `kpi`, `kpi_num`, `bigcard` | `card` + `textbox` | value card centred, label above, sub-line below; card height at least 2 px per point |
| `table` | `tableEx` | coral header band, white bold header text, zebra rows, explicit column widths, optional image column height, optional `vfilter` measure filter |
| `bar`, `column`, `stackcol` | `barChart`, `columnChart` | livery fills, integer axis sizes, no axis titles unless asked |
| `line`, `line2`, `area` | `lineChart`, `stackedAreaChart` | 2.4 to 2.6 px strokes, optional markers, categorical axis for years |
| `scatter` | `scatterChart` | bubble size by entries, inverted y axis where 1 is best |
| `donut`, `mapviz` | `donutChart`, `map` | available, used sparingly |
| `slicer` | `slicer` | horizontal chiclets, single select, coral selected state |
| `panel`, `band`, `text` | `textbox` | panels are empty text boxes with background and border |

## Rules learned from Power BI (all enforced by `apex.validate`)

1. **Integer font sizes.** A decimal `fontSize` literal is ignored.
2. **Full font stacks.** A bare family name renders in serif.
3. **Text box height at least the font size in pixels** (pt x 96 / 72), otherwise a scrollbar.
   Thin accent bars are therefore images, not text boxes.
4. **Card height at least 2 px per point.** Cards centre their value vertically and clip it.
5. **Table width budget.** Column widths must sum to at most the visual width minus 45 px, or
   Power BI adds a horizontal scrollbar.
6. **Header width.** A header label must fit its column at the header font size; the validator
   estimates the width from Segoe UI Bold metrics.
7. **Tooltips off on tables with image columns.** Hovering an `ImageUrl` cell otherwise shows
   the raw `data:image...` string.
8. **Every image registered.** `report.json` must list each file under `RegisteredResources`.
9. **No `pageBinding`.** Power BI Desktop crashes on open.
10. **Measure filters use `filterConfig`** with `ComparisonKind` 4 (<=) or 1 (>), the syntax
    Power BI Desktop writes, so the filter pane shows them normally.
11. **No em or en dash anywhere in displayed text.** Titles, subtitles, DAX strings and labels
    use commas, colons or the word "to".
