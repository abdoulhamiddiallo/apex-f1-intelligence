# Building and opening the project

## Requirements

* Python 3.11 (any 3.10+ works; CI pins 3.11 so that the output is byte-identical)
* the Cairo library for the SVG rasteriser: `sudo apt-get install libcairo2` on Debian and
  Ubuntu, `brew install cairo` on macOS, on Windows the wheels of `cairocffi` need the GTK
  runtime or `conda install cairo`
* Power BI Desktop (Windows) to open the result, with the **Power BI Project (.pbip)**
  preview feature enabled (File > Options > Preview features)

No network access is needed after `pip install`: the data travels in the repository.

## Build

```bash
git clone https://github.com/abdoulhamiddiallo/apex-f1-intelligence.git
cd apex-f1-intelligence
pip install -r requirements.txt
python build.py            # about 5 seconds
```

`build.py` verifies the checksum of the f1db archive, extracts it to `build/f1db/`, runs the
eight generation steps in order, then runs `apex.validate`. The result is `dist/`:

```
dist/
  APEX.pbip                      open this file in Power BI Desktop
  APEX.Report/                   PBIR report: 9 pages, 597 visuals, theme, images
  APEX.SemanticModel/            TMDL model: 16 tables, 20 relationships, 243 measures
  data/                          15 CSV files read by the model
```

Options:

| Command | Effect |
|---------|--------|
| `python build.py --clean` | delete `build/` and `dist/` first |
| `python build.py --check` | build, then build again from scratch and fail unless every file is identical |
| `python -m apex.validate` | re-run only the validation on the current `dist/` |
| `python -m apex.report` | re-run a single step (the report layer here) |
| `python tools/measures_catalog.py` | regenerate `docs/measures.md` |
| `python tools/repo_lint.py` | house rules: language, dashes, machine paths, pinned dependencies |

## Open in Power BI Desktop

1. Tell the model where the CSV files are. The committed default is
   `C:\apex-f1-intelligence\dist\data`. Either clone the repository to `C:\apex-f1-intelligence`,
   or run `python tools/set_data_folder.py` once (it rewrites the `DataFolder` parameter to
   this clone's `dist/data`), or change the parameter in Power BI Desktop afterwards
   (Home > Transform data > Edit parameters).
2. Open `dist/APEX.pbip`.
3. Click **Refresh**. The model loads about 30 000 fact rows in a few seconds.
4. Power BI Desktop writes a `.pbi/` cache folder and a `localSettings.json` next to the
   definition; both are ignored by git.

Power BI Desktop rewrites TMDL files with CRLF line endings when it saves. `.gitattributes`
normalises them back to LF, so a save without a change leaves the tree clean.

## Reproducibility, in detail

The promise is: two builds of the same commit give the same bytes, on any machine.
Everything that could break it has been pinned or removed:

* **Identifiers.** Every `lineageTag`, relationship name, filter name, `logicalId` and
  visual name is a UUID v5 or a positional name derived from the generator, never
  `uuid4()`.
* **Ordering.** The steps run with `PYTHONHASHSEED=0`; every collection that reaches the
  output is a list or a sorted view.
* **Randomness.** The background's speed streaks come from `random.seed(7)`.
* **Rasterisation.** PNG bytes depend on Pillow's zlib and on Cairo's anti-aliasing.
  `requirements.txt` pins Pillow (whose wheels bundle zlib) and CairoSVG; CI runs on
  Ubuntu 24.04 whose `libcairo2` is 1.18.
* **Timestamps.** Nothing writes a date. The "current season" is `YEAR_TO` from `apex/config.py`,
  not the clock.
* **Line endings.** All generated text is LF; `.gitattributes` enforces it on checkout.

`python build.py --check` proves the property locally; the CI job proves it on a clean
runner and additionally requires the committed `dist/` to match. If it ever fails, the
job output lists the files that differ.

## Making a change

1. Edit the generator (`apex/report.py` for layout, `apex/measures.py` for DAX,
   `apex/data.py` for the data shape, `apex/pbir.py` for the design system).
2. `python build.py --check`. Read the validator's output: it names the visual and the
   rule when something is wrong.
3. Open `dist/APEX.pbip` in Power BI Desktop and look at the pages you touched.
4. `python tools/measures_catalog.py` if you changed measures.
5. Commit the source **and** `dist/` together. CI rebuilds and compares.

Never edit files under `dist/` by hand: the next build overwrites them and CI would
reject a commit where `dist/` and the source disagree.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `f1db archive checksum mismatch` | `data/raw/f1db-csv.zip` is not the pinned release | restore the file or update `apex/config.py` and `SHA256SUMS` together |
| `OSError: no library called "cairo-2" was found` | Cairo runtime missing | install `libcairo2` (see Requirements) |
| Power BI shows an empty model | `DataFolder` points to a folder without the CSV files | run `python tools/set_data_folder.py` or edit the parameter |
| validation reports a truncated header | a column is narrower than its label at the header font size | widen the column in the `widths=` list of that `table(...)` call, keeping the sum under the visual width minus 45 |
| CI fails on `git diff -- dist` | source changed without a rebuild, or `dist/` was edited by hand | run `python build.py --check` and commit the result |
