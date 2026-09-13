# Data sources

Every number in the report can be traced to one of two files committed under `data/raw/`.
Both are verified by checksum before each build (`data/raw/SHA256SUMS`, checked by CI and by
`build.py`), so a rebuild can never silently pick up a different dataset.

| File | Origin | Version | Licence | Size |
|------|--------|---------|---------|------|
| `f1db-csv.zip` | [f1db/f1db](https://github.com/f1db/f1db) | release `v2026.13.0` | CC BY 4.0 | 4.3 MB, 47 CSV tables |
| `f1-circuits.geojson` | [bacinger/f1-circuits](https://github.com/bacinger/f1-circuits) | snapshot of September 2026 | MIT | 40 circuit rings |

## f1db

f1db is a community-maintained, openly licensed database of Formula 1 covering every World
Championship season since 1950: seasons, races, entrants, results, qualifying, sprints,
fastest laps, pit stops, standings, drivers, constructors, engines, circuits and countries.
The CSV distribution is downloaded from the GitHub release page:

```
https://github.com/f1db/f1db/releases/download/v2026.13.0/f1db-csv.zip
sha256  82a5102e1157a4096cd38bae72e581aaa52083d2ceca7942acfe7744e214c9a6
```

Tables used by `apex.data` (all prefixed `f1db-` inside the archive):

| f1db table | Feeds | Notes |
|------------|-------|-------|
| `seasons-driver-standings`, `seasons-constructor-standings` | `D_Season` | champions and their points |
| `races` | `D_Race`, `D_Season` | schedule, laps, distance, sprint format, circuit and country keys |
| `races-race-results` | `F_Result` | one row per classified or retired entry; flags derived here |
| `races-qualifying-results` | `F_Qualifying` | Q1 to Q3 times in milliseconds, gap to pole |
| `races-fastest-laps` | `F_FastestLap` | |
| `races-sprint-race-results` | `F_Sprint` | |
| `races-driver-standings`, `races-constructor-standings` | `F_DriverStanding`, `F_ConstructorStanding` | standings after every round |
| `races-pit-stops` | `F_Result` (`PitStops`, `BestPitStopMs`, `TotalPitMs`) | aggregated per entry |
| `races-driver-of-the-day-results` | `F_Result` (`IsDriverOfTheDay`) | |
| `grands-prix`, `drivers`, `constructors`, `engine-manufacturers`, `circuits`, `countries` | dimensions | names, nationalities, coordinates, career totals |

### Transformations applied

* **Era filter.** Only seasons 2014 to 2026 are kept (`apex/config.py`, `YEAR_FROM`, `YEAR_TO`).
  Career totals in `D_Driver` and `D_Constructor` are recomputed for that window so that
  "career" always means "in the era shown".
* **Race key.** f1db's integer race id becomes `RaceKey`, the single key that joins every fact
  table to `D_Race`; a separate `SortKey` orders races chronologically.
* **Result flags.** `IsWin`, `IsPodium`, `IsPoints`, `IsFinished`, `IsPole`, `IsFastestLap`,
  `IsGrandSlam`, `IsDriverOfTheDay`, `IsDNF`, `StartedFromPole`, `WinFromPole` are integers
  (0/1) computed once, so the DAX layer counts rows instead of re-deriving conditions.
* **Pit stops.** The per-stop table is aggregated to one row per entry: number of stops, best
  stop and total time in the pit lane.
* **Latest round.** `IsLatestRound` marks, in each season, the last round with results, which
  lets the Season Pulse page show the live standings without a date slicer.
* **Eras.** Seasons are grouped into four regulation eras (`V6 Hybrid I`, `V6 Hybrid II`,
  `Ground Effect`, `New Formula`) for the Formula 1 page.
* **Classic eleven.** Eleven heritage circuits (Monza, Silverstone, Spa-Francorchamps,
  Paul Ricard, Suzuka, Monaco, Interlagos, Melbourne, Catalunya, Montreal, Hungaroring)
  receive `IsClassic = 1`, a nickname and a signature corner. They drive the Classic Eleven
  page and the `D_Scope` slicer.
* **Team colours.** A curated `TeamColour` hex value per constructor, used by the colour
  measures so every chart wears the right livery.

No value is edited by hand. If a figure looks wrong, it is either in f1db (open an issue
there) or in `apex/data.py` (open an issue here).

## f1-circuits

`f1-circuits.geojson` (Tomislav Bacinger, MIT licence) contains the outline of every current
and many historical Formula 1 circuits as GeoJSON `LineString` features, with an `id` such as
`gb-1948` (country code and year of first race). `apex/data.py` maps each f1db circuit id
used in the era to one feature (`GEOMAP`); 33 of the 33 circuits raced between 2014 and 2026
have an outline.

The rings are projected as described in [architecture.md](architecture.md#circuit-geometry)
and stored in `F_TrackPoint` (4 168 points). The file is redistributed unmodified.

## Team logos

`assets/logos/` holds 24 PNG logos named after the f1db constructor id (`ferrari.png`,
`red-bull.png`, ...). They are embedded as base64 data URIs in `D_Constructor[TeamBadge]`.
The logos remain the property of the teams; see `NOTICE`. Deleting a file makes the build
fall back to a generated crest for that team, so the repository builds with or without them.

## Freshness

The report is a snapshot of f1db `v2026.13.0`. To move to a newer release:

1. download the new `f1db-csv.zip` into `data/raw/`;
2. update `F1DB_RELEASE` and `F1DB_ZIP_SHA256` in `apex/config.py` and regenerate
   `data/raw/SHA256SUMS` (`sha256sum f1db-csv.zip f1-circuits.geojson > SHA256SUMS`);
3. run `python build.py --check` and commit `dist/` together with the archive.

The CI job refuses an archive whose checksum does not match the configuration.
