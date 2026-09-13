# Measure catalog

Generated from `dist/APEX.SemanticModel/definition/tables/Metrics.tmdl` by `tools/measures_catalog.py`. 243 measures in 19 display folders. Do not edit by hand: the CI job regenerates this file and fails if it differs.

## Contents

* [01 Race record](#01-race-record) (17)
* [02 Rates & averages](#02-rates-averages) (13)
* [03 Championship](#03-championship) (8)
* [04 Circuit](#04-circuit) (17)
* [05 Season pulse](#05-season-pulse) (22)
* [06 Dynamic](#06-dynamic) (5)
* [07 Visual helpers](#07-visual-helpers) (9)
* [08 Qualifying & pit lane](#08-qualifying-pit-lane) (9)
* [09 Leaderboard](#09-leaderboard) (12)
* [10 Race cards](#10-race-cards) (12)
* [11 Scope](#11-scope) (4)
* [12 Live season](#12-live-season) (28)
* [14 Classic eleven](#14-classic-eleven) (11)
* [13 Circuit lab](#13-circuit-lab) (23)
* [15 Table columns](#15-table-columns) (11)
* [16 Page totals](#16-page-totals) (8)
* [17 Teams & results](#17-teams-results) (19)
* [18 Race row](#18-race-row) (8)
* [19 Countries](#19-countries) (7)

## 01 Race record

### Entries

Number of driver race entries in context

Format: `#,0`

```dax
COUNTROWS ( F_Result )
```

### Grands Prix

Format: `#,0`

```dax
DISTINCTCOUNT ( F_Result[RaceKey] )
```

### Wins

Format: `#,0`

```dax
CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsWin] = 1 )
```

### Podiums

Format: `#,0`

```dax
CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsPodium] = 1 )
```

### Points

Format: `#,0`

```dax
SUM ( F_Result[Points] )
```

### Poles

Format: `#,0`

```dax
CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsPole] = 1 )
```

### Fastest Laps

Format: `#,0`

```dax
CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsFastestLap] = 1 )
```

### DNFs

Format: `#,0`

```dax
CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsDNF] = 1 )
```

### Points Finishes

Format: `#,0`

```dax
CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsPoints] = 1 )
```

### Grand Slams

Format: `#,0`

```dax
CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsGrandSlam] = 1 )
```

### Driver of the Day

Format: `#,0`

```dax
CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsDriverOfTheDay] = 1 )
```

### Laps Completed

Format: `#,0`

```dax
SUM ( F_Result[LapsCompleted] )
```

### Race Distance (km)

Format: `#,0`

```dax
SUMX ( VALUES ( D_Race[RaceKey] ), CALCULATE ( MAX ( D_Race[DistanceKm] ) ) )
```

### Sprint Wins

Format: `#,0`

```dax
CALCULATE ( COUNTROWS ( F_Sprint ), F_Sprint[IsSprintWin] = 1 )
```

### Sprint Points

Format: `#,0.##`

```dax
SUM ( F_Sprint[SprintPoints] )
```

### Places Gained

Format: `#,0`

```dax
CALCULATE ( SUM ( F_Result[PositionsGained] ), F_Result[PositionsGained] > 0 )
```

### Seasons Covered

Format: `0`

```dax
DISTINCTCOUNT ( D_Race[Year] )
```

## 02 Rates & averages

### Win Rate

Format: `0.0%`

```dax
DIVIDE ( [Wins], [Entries] )
```

### Podium Rate

Format: `0.0%`

```dax
DIVIDE ( [Podiums], [Entries] )
```

### Points Rate

Format: `0.0%`

```dax
DIVIDE ( [Points Finishes], [Entries] )
```

### DNF Rate

Format: `0.0%`

```dax
DIVIDE ( [DNFs], [Entries] )
```

### Finish Rate

Format: `0.0%`

```dax
DIVIDE ( [Entries] - [DNFs], [Entries] )
```

### Avg Finish

Format: `0.0`

```dax
AVERAGE ( F_Result[Position] )
```

### Avg Grid

Format: `0.0`

```dax
AVERAGE ( F_Result[GridPosition] )
```

### Avg Places Gained

Format: `+0.0;-0.0;0.0`

```dax
AVERAGE ( F_Result[PositionsGained] )
```

### Points per Race

Format: `0.0`

```dax
DIVIDE ( [Points], [Entries] )
```

### Best Finish

Format: `0`

```dax
MIN ( F_Result[Position] )
```

### Pole to Win %

Format: `0.0%`

```dax
DIVIDE ( CALCULATE ( COUNTROWS ( F_Result ), F_Result[WinFromPole] = 1 ), CALCULATE ( COUNTROWS ( F_Result ), F_Result[StartedFromPole] = 1 ) )
```

### Points Share %

Format: `0.0%`

```dax
DIVIDE ( [Points], CALCULATE ( [Points], ALLSELECTED ( D_Driver ), ALLSELECTED ( D_Constructor ) ) )
```

### Retirements per Race

Format: `0.00`

```dax
DIVIDE ( [DNFs], [Grands Prix] )
```

## 03 Championship

### Championship Points

Format: `#,0.##`

```dax
SUMX ( VALUES ( F_DriverStanding[Year] ), VAR r = CALCULATE ( MAX ( F_DriverStanding[Round] ) ) RETURN CALCULATE ( SUM ( F_DriverStanding[StandingPoints] ), F_DriverStanding[Round] = r ) )
```

### Championship Position

Format: `0`

```dax
MINX ( VALUES ( F_DriverStanding[Year] ), VAR r = CALCULATE ( MAX ( F_DriverStanding[Round] ) ) RETURN CALCULATE ( MIN ( F_DriverStanding[StandingPosition] ), F_DriverStanding[Round] = r ) )
```

### Team Championship Points

Format: `#,0.##`

```dax
SUMX ( VALUES ( F_ConstructorStanding[Year] ), VAR r = CALCULATE ( MAX ( F_ConstructorStanding[Round] ) ) RETURN CALCULATE ( SUM ( F_ConstructorStanding[StandingPoints] ), F_ConstructorStanding[Round] = r ) )
```

### Team Championship Position

Format: `0`

```dax
MINX ( VALUES ( F_ConstructorStanding[Year] ), VAR r = CALCULATE ( MAX ( F_ConstructorStanding[Round] ) ) RETURN CALCULATE ( MIN ( F_ConstructorStanding[StandingPosition] ), F_ConstructorStanding[Round] = r ) )
```

### Drivers Titles

Format: `0`

```dax
CALCULATE ( COUNTROWS ( F_DriverStanding ), F_DriverStanding[ChampionshipWon] = 1, F_DriverStanding[IsLatestRound] = 1 )
```

### Constructors Titles

Format: `0`

```dax
CALCULATE ( COUNTROWS ( F_ConstructorStanding ), F_ConstructorStanding[ChampionshipWon] = 1, F_ConstructorStanding[IsLatestRound] = 1 )
```

### Running Points

Format: `#,0.##`

```dax
SUM ( F_DriverStanding[StandingPoints] )
```

### Team Running Points

Format: `#,0.##`

```dax
SUM ( F_ConstructorStanding[StandingPoints] )
```

## 04 Circuit

### Circuit Length (km)

Format: `0.000`

```dax
MAX ( D_Circuit[LengthKm] )
```

### Circuit Turns

Format: `0`

```dax
MAX ( D_Circuit[Turns] )
```

### Grands Prix Held

Format: `#,0`

```dax
CALCULATE ( DISTINCTCOUNT ( D_Race[RaceKey] ), D_Race[IsRun] = 1 )
```

### First Grand Prix

Format: `0`

```dax
MIN ( D_Circuit[FirstGrandPrix] )
```

### Different Winners

Format: `0`

```dax
CALCULATE ( DISTINCTCOUNT ( F_Result[DriverId] ), F_Result[IsWin] = 1 )
```

### Different Winning Teams

Format: `0`

```dax
CALCULATE ( DISTINCTCOUNT ( F_Result[ConstructorId] ), F_Result[IsWin] = 1 )
```

### Lap Record ms

Format: `#,0`

```dax
MIN ( F_FastestLap[LapTimeMs] )
```

### Lap Record

```dax
VAR ms = [Lap Record ms] RETURN IF ( ISBLANK ( ms ), "n/a", FORMAT ( INT ( ms / 60000 ), "0" ) & ":" & FORMAT ( INT ( MOD ( ms, 60000 ) / 1000 ), "00" ) & "." & FORMAT ( MOD ( ms, 1000 ), "000" ) )
```

### Lap Record Holder

```dax
VAR ms = [Lap Record ms] RETURN CALCULATE ( CONCATENATEX ( SUMMARIZE ( F_FastestLap, D_Driver[Driver] ), D_Driver[Driver], ", " ), F_FastestLap[LapTimeMs] = ms )
```

### Lap Record Year

Format: `0`

```dax
VAR ms = [Lap Record ms] RETURN CALCULATE ( MAX ( F_FastestLap[Year] ), F_FastestLap[LapTimeMs] = ms )
```

### Track Master

```dax
VAR t = ADDCOLUMNS ( SUMMARIZE ( F_Result, D_Driver[Driver] ), "@w", CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsWin] = 1 ) ) VAR bestrow = TOPN ( 1, FILTER ( t, [@w] > 0 ), [@w], DESC, [Driver], ASC ) RETURN IF ( ISEMPTY ( bestrow ), "n/a", MAXX ( bestrow, [Driver] ) & " · " & FORMAT ( MAXX ( bestrow, [@w] ), "0" ) & " wins" )
```

### Track Master Team

```dax
VAR t = ADDCOLUMNS ( SUMMARIZE ( F_Result, D_Constructor[Team] ), "@w", CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsWin] = 1 ) ) VAR bestrow = TOPN ( 1, FILTER ( t, [@w] > 0 ), [@w], DESC, [Team], ASC ) RETURN IF ( ISEMPTY ( bestrow ), "n/a", MAXX ( bestrow, [Team] ) & " · " & FORMAT ( MAXX ( bestrow, [@w] ), "0" ) & " wins" )
```

### Circuit Profile

```dax
VAR l = [Circuit Length (km)] VAR t = [Circuit Turns] VAR ty = SELECTEDVALUE ( D_Circuit[CircuitType] ) VAR d = SELECTEDVALUE ( D_Circuit[Direction] ) RETURN IF ( ISBLANK ( l ), "n/a", FORMAT ( l, "0.000" ) & " km · " & FORMAT ( t, "0" ) & " turns · " & ty & " · " & d )
```

### Lap Record Line

```dax
VAR t = [Lap Record] RETURN IF ( t = "n/a", "n/a", [Lap Record Holder] & " · " & FORMAT ( [Lap Record Year], "0" ) )
```

### Track Length Total

Format: `#,0.0`

```dax
SUMX ( VALUES ( D_Circuit[CircuitId] ), CALCULATE ( MAX ( D_Circuit[LengthKm] ) ) )
```

### Total Turns

Format: `#,0`

```dax
SUMX ( VALUES ( D_Circuit[CircuitId] ), CALCULATE ( MAX ( D_Circuit[Turns] ) ) )
```

### Circuits

Format: `0`

```dax
DISTINCTCOUNT ( D_Circuit[CircuitId] )
```

## 05 Season pulse

### Rounds Scheduled

Format: `0`

```dax
DISTINCTCOUNT ( D_Race[RaceKey] )
```

### Rounds Run

Format: `0`

```dax
CALCULATE ( DISTINCTCOUNT ( D_Race[RaceKey] ), D_Race[IsRun] = 1 )
```

### Rounds Remaining

Format: `0`

```dax
[Rounds Scheduled] - [Rounds Run]
```

### Season Progress

Format: `0%`

```dax
DIVIDE ( [Rounds Run], [Rounds Scheduled] )
```

### Championship Leader

```dax
VAR t = ADDCOLUMNS ( VALUES ( D_Driver[Driver] ), "@p", [Championship Points] ) VAR bestrow = TOPN ( 1, FILTER ( t, [@p] > 0 ), [@p], DESC ) RETURN IF ( ISEMPTY ( bestrow ), "n/a", MAXX ( bestrow, [Driver] ) )
```

### Leader Points

Format: `#,0`

```dax
MAXX ( ADDCOLUMNS ( VALUES ( D_Driver[Driver] ), "@p", [Championship Points] ), [@p] )
```

### Gap to Second

Format: `#,0`

```dax
VAR t = ADDCOLUMNS ( VALUES ( D_Driver[Driver] ), "@p", [Championship Points] ) VAR pair = TOPN ( 2, FILTER ( t, [@p] > 0 ), [@p], DESC ) RETURN MAXX ( pair, [@p] ) - MINX ( pair, [@p] )
```

### Leading Team

```dax
VAR t = ADDCOLUMNS ( VALUES ( D_Constructor[Team] ), "@p", [Team Championship Points] ) VAR bestrow = TOPN ( 1, FILTER ( t, [@p] > 0 ), [@p], DESC ) RETURN IF ( ISEMPTY ( bestrow ), "n/a", MAXX ( bestrow, [Team] ) )
```

### Leading Team Points

Format: `#,0`

```dax
MAXX ( ADDCOLUMNS ( VALUES ( D_Constructor[Team] ), "@p", [Team Championship Points] ), [@p] )
```

### Last Race

```dax
VAR k = CALCULATE ( MAX ( D_Race[SortKey] ), D_Race[IsRun] = 1 ) RETURN CALCULATE ( SELECTEDVALUE ( D_Race[GrandPrix] ), D_Race[SortKey] = k )
```

### Last Race Winner

```dax
VAR k = CALCULATE ( MAX ( D_Race[SortKey] ), D_Race[IsRun] = 1 ) RETURN CALCULATE ( CONCATENATEX ( SUMMARIZE ( F_Result, D_Driver[Driver] ), D_Driver[Driver], ", " ), D_Race[SortKey] = k, F_Result[IsWin] = 1 )
```

### Last Race Date

Format: `yyyy-mm-dd`

```dax
VAR k = CALCULATE ( MAX ( D_Race[SortKey] ), D_Race[IsRun] = 1 ) RETURN CALCULATE ( SELECTEDVALUE ( D_Race[RaceDate] ), D_Race[SortKey] = k )
```

### Next Race

```dax
VAR k = CALCULATE ( MIN ( D_Race[SortKey] ), D_Race[IsRun] = 0 ) RETURN IF ( ISBLANK ( k ), "Season complete", CALCULATE ( SELECTEDVALUE ( D_Race[GrandPrix] ), D_Race[SortKey] = k ) )
```

### Next Race Circuit

```dax
VAR k = CALCULATE ( MIN ( D_Race[SortKey] ), D_Race[IsRun] = 0 ) RETURN CALCULATE ( SELECTEDVALUE ( D_Race[Circuit] ), D_Race[SortKey] = k )
```

### Next Race Date

Format: `yyyy-mm-dd`

```dax
VAR k = CALCULATE ( MIN ( D_Race[SortKey] ), D_Race[IsRun] = 0 ) RETURN CALCULATE ( SELECTEDVALUE ( D_Race[RaceDate] ), D_Race[SortKey] = k )
```

### Season Headline

```dax
VAR l = [Championship Leader] VAR p = [Leader Points] VAR g = [Gap to Second] VAR r = [Rounds Remaining] RETURN IF ( ISBLANK ( p ), "n/a", l & " leads on " & FORMAT ( p, "#,0" ) & " points, " & FORMAT ( g, "#,0" ) & " clear, with " & FORMAT ( r, "0" ) & " rounds to run." )
```

### Leader Sub

```dax
VAR p = [Leader Points] VAR g = [Gap to Second] RETURN IF ( ISBLANK ( p ), "n/a", FORMAT ( p, "#,0" ) & " pts · +" & FORMAT ( g, "#,0" ) & " on P2" )
```

### Team Sub

```dax
VAR p = [Leading Team Points] RETURN IF ( ISBLANK ( p ), "n/a", FORMAT ( p, "#,0" ) & " pts" )
```

### Round Line

```dax
"Round " & FORMAT ( [Rounds Run], "0" ) & " of " & FORMAT ( [Rounds Scheduled], "0" )
```

### Winners Sub

```dax
FORMAT ( [Different Winners], "0" ) & " winners · " & FORMAT ( [Different Winning Teams], "0" ) & " winning teams"
```

### Last GP Sub

```dax
VAR d = [Last Race Date] RETURN IF ( ISBLANK ( d ), "n/a", [Last Race] & " · " & FORMAT ( d, "d mmm yyyy" ) )
```

### Next GP Sub

```dax
VAR d = [Next Race Date] RETURN IF ( ISBLANK ( d ), "Season complete", [Next Race Circuit] & " · " & FORMAT ( d, "d mmm yyyy" ) )
```

## 06 Dynamic

### Selected Metric

```dax
SWITCH ( SELECTEDVALUE ( D_Metric[Metric], "Points" ), "Points", [Points], "Wins", [Wins], "Podiums", [Podiums], "Poles", [Poles], "Fastest laps", [Fastest Laps], "Avg finish", [Avg Finish], "DNFs", [DNFs] )
```

### Selected Metric Label

```dax
SELECTEDVALUE ( D_Metric[Metric], "Points" )
```

### Selected Metric Format

```dax
SWITCH ( SELECTEDVALUE ( D_Metric[Metric], "Points" ), "Avg finish", "0.0", "#,0.##" )
```

### Scope Filter

```dax
IF ( SELECTEDVALUE ( D_Scope[Scope], "All circuits" ) = "Classic eleven", CALCULATE ( [Selected Metric], D_Race[IsClassicCircuit] = 1 ), [Selected Metric] )
```

### Scope Label

```dax
SELECTEDVALUE ( D_Scope[ScopeDesc], "Every Grand Prix in the era" )
```

## 07 Visual helpers

### Team Colour

```dax
COALESCE ( SELECTEDVALUE ( D_Constructor[TeamColour] ), "#7A8496" )
```

### Driver Team Colour

```dax
VAR t = ADDCOLUMNS ( SUMMARIZE ( F_Result, D_Constructor[TeamColour] ), "@n", CALCULATE ( COUNTROWS ( F_Result ) ) ) RETURN COALESCE ( MAXX ( TOPN ( 1, t, [@n], DESC ), [TeamColour] ), "#7A8496" )
```

### Track Blueprint

```dax
VAR ok = HASONEVALUE ( D_Circuit[CircuitId] ) VAR pts = CONCATENATEX ( F_TrackPoint, FORMAT ( F_TrackPoint[X], "0.0" ) & " " & FORMAT ( - F_TrackPoint[Y], "0.0" ), " L ", F_TrackPoint[PointOrder], ASC ) RETURN IF ( NOT ok || ISBLANK ( pts ), BLANK (), "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='-112 -112 224 224' width='620' height='620'><path d='M " & pts & " Z' fill='none' stroke='%2320252F' stroke-width='21' stroke-linejoin='round' stroke-linecap='round'/><path d='M " & pts & " Z' fill='none' stroke='%23E9EDF5' stroke-width='10' stroke-linejoin='round' stroke-linecap='round'/><path d='M " & pts & " Z' fill='none' stroke='%23E8323C' stroke-width='1.6' stroke-dasharray='3 8' stroke-linecap='round'/></svg>" )
```

### Selected Circuit

```dax
COALESCE ( SELECTEDVALUE ( D_Circuit[Circuit] ), "All circuits" )
```

### Selected Circuit Nickname

```dax
COALESCE ( SELECTEDVALUE ( D_Circuit[Nickname] ), "" )
```

### Signature Corner

```dax
COALESCE ( SELECTEDVALUE ( D_Circuit[SignatureCorner] ), "n/a" )
```

### Selected Season

```dax
COALESCE ( SELECTEDVALUE ( D_Season[SeasonLabel] ), "2014 to 2026" )
```

### Era Footnote

```dax
"Source: f1db open dataset · circuit geometry from the f1-circuits dataset · 2014-2026 hybrid era · built with Power BI"
```

### Circuit Headline

```dax
VAR c = SELECTEDVALUE ( D_Circuit[Circuit] ) VAR n = SELECTEDVALUE ( D_Circuit[Nickname] ) RETURN IF ( ISBLANK ( c ), "Select a circuit", IF ( n = "", c, n ) )
```

## 08 Qualifying & pit lane

### Pole Time ms

Format: `#,0`

```dax
MIN ( F_Qualifying[BestQualiMs] )
```

### Pole Time

```dax
VAR ms = [Pole Time ms] RETURN IF ( ISBLANK ( ms ), "n/a", FORMAT ( INT ( ms / 60000 ), "0" ) & ":" & FORMAT ( INT ( MOD ( ms, 60000 ) / 1000 ), "00" ) & "." & FORMAT ( MOD ( ms, 1000 ), "000" ) )
```

### Q3 Appearances

Format: `#,0`

```dax
CALCULATE ( COUNTROWS ( F_Qualifying ), F_Qualifying[ReachedQ3] = 1 )
```

### Q3 Rate

Format: `0.0%`

```dax
DIVIDE ( [Q3 Appearances], COUNTROWS ( F_Qualifying ) )
```

### Avg Quali Gap (s)

Format: `0.000`

```dax
AVERAGEX ( F_Qualifying, DIVIDE ( F_Qualifying[GapToPoleMs], 1000 ) )
```

### Avg Quali Position

Format: `0.0`

```dax
AVERAGE ( F_Qualifying[QualiPosition] )
```

### Pit Stops

Format: `#,0`

```dax
SUM ( F_Result[PitStops] )
```

### Avg Pit Stops

Format: `0.00`

```dax
AVERAGE ( F_Result[PitStops] )
```

### Fastest Pit Stop (s)

Format: `0.00`

```dax
DIVIDE ( MIN ( F_Result[BestPitStopMs] ), 1000 )
```

## 09 Leaderboard

### Driver Rank

Format: `0`

```dax
RANKX ( ALLSELECTED ( D_Driver[Driver] ), [Points],, DESC )
```

### Team Rank

Format: `0`

```dax
RANKX ( ALLSELECTED ( D_Constructor[Team] ), [Points],, DESC )
```

### Top 15 Points

Format: `#,0`

```dax
IF ( RANKX ( ALLSELECTED ( D_Driver[Driver] ), [Points],, DESC ) <= 15, [Points] )
```

### Top 15 Metric

```dax
IF ( RANKX ( ALLSELECTED ( D_Driver[Driver] ), [Selected Metric],, DESC ) <= 15, [Selected Metric] )
```

### Top 12 Wins

Format: `#,0`

```dax
IF ( RANKX ( ALLSELECTED ( D_Driver[Driver] ), [Wins],, DESC ) <= 12 && [Wins] > 0, [Wins] )
```

### Top 12 Poles

Format: `#,0`

```dax
IF ( RANKX ( ALLSELECTED ( D_Driver[Driver] ), [Poles],, DESC ) <= 12 && [Poles] > 0, [Poles] )
```

### Top 12 Podiums

Format: `#,0`

```dax
IF ( RANKX ( ALLSELECTED ( D_Driver[Driver] ), [Podiums],, DESC ) <= 12 && [Podiums] > 0, [Podiums] )
```

### Wins Here

Format: `#,0`

```dax
IF ( [Wins] > 0, [Wins] )
```

### Podiums Here

Format: `#,0`

```dax
IF ( [Podiums] > 0, [Podiums] )
```

### Driver Points (min 10 starts)

Format: `#,0`

```dax
IF ( [Entries] >= 10, [Points] )
```

### Avg Finish (min 60 starts)

Format: `0.0`

```dax
IF ( [Entries] >= 60, [Avg Finish] )
```

### Avg Grid (min 60 starts)

Format: `0.0`

```dax
IF ( [Entries] >= 60, [Avg Grid] )
```

## 10 Race cards

### Race Winner

```dax
CALCULATE ( CONCATENATEX ( SUMMARIZE ( F_Result, D_Driver[Driver] ), D_Driver[Driver], ", " ), F_Result[IsWin] = 1 )
```

### Winning Team

```dax
CALCULATE ( CONCATENATEX ( SUMMARIZE ( F_Result, D_Constructor[Team] ), D_Constructor[Team], ", " ), F_Result[IsWin] = 1 )
```

### Pole Sitter

```dax
CALCULATE ( CONCATENATEX ( SUMMARIZE ( F_Result, D_Driver[Driver] ), D_Driver[Driver], ", " ), F_Result[IsPole] = 1 )
```

### Fastest Lap By

```dax
CALCULATE ( CONCATENATEX ( SUMMARIZE ( F_Result, D_Driver[Driver] ), D_Driver[Driver], ", " ), F_Result[IsFastestLap] = 1 )
```

### Winning Margin

```dax
VAR g = CALCULATE ( MIN ( F_Result[GapMillis] ), F_Result[Position] = 2 ) RETURN IF ( ISBLANK ( g ), "n/a", FORMAT ( g / 1000, "0.000" ) & " s" )
```

### HoF Wins

Format: `#,0`

```dax
IF ( RANKX ( ALLSELECTED ( D_Driver[Driver] ), [Wins],, DESC ) <= 10 && [Wins] > 0, [Wins] )
```

### HoF Poles

Format: `#,0`

```dax
IF ( NOT ISBLANK ( [HoF Wins] ), [Poles] + 0 )
```

### HoF Podiums

Format: `#,0`

```dax
IF ( NOT ISBLANK ( [HoF Wins] ), [Podiums] + 0 )
```

### HoF Titles

Format: `0`

```dax
IF ( NOT ISBLANK ( [HoF Wins] ), [Drivers Titles] )
```

### HoF Points

Format: `#,0`

```dax
IF ( NOT ISBLANK ( [HoF Wins] ), [Points] )
```

### HoF Win Rate

Format: `0.0%`

```dax
IF ( NOT ISBLANK ( [HoF Wins] ), [Win Rate] )
```

### Busy Places Gained

Format: `+0.00;-0.00;0.00`

```dax
IF ( RANKX ( ALLSELECTED ( D_Driver[Driver] ), [Entries],, DESC ) <= 15, [Avg Places Gained] )
```

## 11 Scope

### Default Season

Format: `0`

```dax
IF ( ISFILTERED ( D_Season[SeasonLabel] ), BLANK ( ), CALCULATE ( MAX ( D_Season[Year] ), REMOVEFILTERS ( D_Season ), D_Season[IsCurrentSeason] = 1 ) )
```

### Default Circuit

```dax
IF ( ISFILTERED ( D_Circuit[Circuit] ), BLANK ( ), "monza" )
```

### Circuit Latitude

Format: `0.0000`

```dax
AVERAGE ( D_Circuit[Latitude] )
```

### Circuit Longitude

Format: `0.0000`

```dax
AVERAGE ( D_Circuit[Longitude] )
```

## 12 Live season

### Season points

Format: `#,0`

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Championship Points], CALCULATE ( [Championship Points], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Team points

Format: `#,0`

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Team Championship Points], CALCULATE ( [Team Championship Points], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Running team points

Format: `#,0`

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Team Running Points], CALCULATE ( [Team Running Points], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Season wins

Format: `#,0`

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Top 12 Wins], CALCULATE ( [Top 12 Wins], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Season poles

Format: `#,0`

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Top 12 Poles], CALCULATE ( [Top 12 Poles], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Live Leader

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Championship Leader], CALCULATE ( [Championship Leader], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Live Leader Sub

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Leader Sub], CALCULATE ( [Leader Sub], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Live Team

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Leading Team], CALCULATE ( [Leading Team], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Live Team Sub

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Team Sub], CALCULATE ( [Team Sub], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Live Last Winner

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Last Race Winner], CALCULATE ( [Last Race Winner], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Live Last GP Sub

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Last GP Sub], CALCULATE ( [Last GP Sub], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Live Next GP

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Next Race], CALCULATE ( [Next Race], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Live Next GP Sub

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Next GP Sub], CALCULATE ( [Next GP Sub], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Live Round Line

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Round Line], CALCULATE ( [Round Line], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Live Winners Sub

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Winners Sub], CALCULATE ( [Winners Sub], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Live Headline

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Season Headline], CALCULATE ( [Season Headline], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Live Season

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Selected Season], CALCULATE ( [Selected Season], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Car

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Car base], CALCULATE ( [Car base], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Line-up

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Line-up base], CALCULATE ( [Line-up base], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Pos

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Pos base], CALCULATE ( [Pos base], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Pts

Format: `#,0`

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Points base], CALCULATE ( [Points base], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Won

Format: `#,0`

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Wins base], CALCULATE ( [Wins base], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Top 3

Format: `#,0`

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Podiums base], CALCULATE ( [Podiums base], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Grid teams

Format: `0`

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Teams on the grid], CALCULATE ( [Teams on the grid], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Grid drivers

Format: `0`

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Drivers on the grid], CALCULATE ( [Drivers on the grid], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Grid races

Format: `#,0`

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Grands Prix], CALCULATE ( [Grands Prix], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Grid winners

Format: `0`

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Different Winners], CALCULATE ( [Different Winners], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Grid teams won

Format: `0`

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Different Winning Teams], CALCULATE ( [Different Winning Teams], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

## 14 Classic eleven

### Track

```dax
IF ( SELECTEDVALUE ( D_Circuit[IsClassic] ) = 1, SELECTEDVALUE ( D_Circuit[TrackSvg] ) )
```

### Flag

```dax
IF ( SELECTEDVALUE ( D_Circuit[IsClassic] ) = 1, SELECTEDVALUE ( D_Circuit[FlagSvg] ) )
```

### Nickname

```dax
IF ( SELECTEDVALUE ( D_Circuit[IsClassic] ) = 1, SELECTEDVALUE ( D_Circuit[Nickname] ) )
```

### Classic country

```dax
IF ( SELECTEDVALUE ( D_Circuit[IsClassic] ) = 1, SELECTEDVALUE ( D_Circuit[Country] ) )
```

### Km

Format: `0.000`

```dax
IF ( SELECTEDVALUE ( D_Circuit[IsClassic] ) = 1, SELECTEDVALUE ( D_Circuit[LengthKm] ) )
```

### Corners

Format: `0`

```dax
IF ( SELECTEDVALUE ( D_Circuit[IsClassic] ) = 1, SELECTEDVALUE ( D_Circuit[Turns] ) )
```

### GP

Format: `#,0`

```dax
IF ( SELECTEDVALUE ( D_Circuit[IsClassic] ) = 1, [Grands Prix Held] )
```

### Record

```dax
IF ( SELECTEDVALUE ( D_Circuit[IsClassic] ) = 1, [Lap Record] )
```

### Winners

Format: `0`

```dax
IF ( SELECTEDVALUE ( D_Circuit[IsClassic] ) = 1, [Different Winners] )
```

### Lat

Format: `0.0000`

```dax
IF ( SELECTEDVALUE ( D_Circuit[IsClassic] ) = 1, AVERAGE ( D_Circuit[Latitude] ) )
```

### Lon

Format: `0.0000`

```dax
IF ( SELECTEDVALUE ( D_Circuit[IsClassic] ) = 1, AVERAGE ( D_Circuit[Longitude] ) )
```

## 13 Circuit lab

### Lab Blueprint

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Track Blueprint], CALCULATE ( [Track Blueprint], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Lab Profile

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Circuit Profile], CALCULATE ( [Circuit Profile], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Lab Headline

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Circuit Headline], CALCULATE ( [Circuit Headline], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Lab Corner

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Signature Corner], CALCULATE ( [Signature Corner], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Lab GP

Format: `#,0`

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Grands Prix Held], CALCULATE ( [Grands Prix Held], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Lab First GP

Format: `0`

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [First Grand Prix], CALCULATE ( [First Grand Prix], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Lab Winners

Format: `0`

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Different Winners], CALCULATE ( [Different Winners], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Lab Teams

Format: `0`

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Different Winning Teams], CALCULATE ( [Different Winning Teams], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Lab Record

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Lap Record], CALCULATE ( [Lap Record], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Lab Record Line

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Lap Record Line], CALCULATE ( [Lap Record Line], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Lab Master

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Track Master], CALCULATE ( [Track Master], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Lab Master Team

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Track Master Team], CALCULATE ( [Track Master Team], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Lab Length

Format: `0.000`

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Circuit Length (km)], CALCULATE ( [Circuit Length (km)], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Lab Turns

Format: `0`

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Circuit Turns], CALCULATE ( [Circuit Turns], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Driver wins here

Format: `#,0`

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Wins Here], CALCULATE ( [Wins Here], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Team podiums here

Format: `#,0`

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Podiums Here], CALCULATE ( [Podiums Here], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Race win by

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Race Winner], CALCULATE ( [Race Winner], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Constructor

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Winning Team], CALCULATE ( [Winning Team], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Pole

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Pole Sitter], CALCULATE ( [Pole Sitter], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Margin

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Winning Margin], CALCULATE ( [Winning Margin], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Fastest lap

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Lap Record], CALCULATE ( [Lap Record], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Lab Lat

Format: `0.0000`

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Circuit Latitude], CALCULATE ( [Circuit Latitude], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

### Lab Lon

Format: `0.0000`

```dax
VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [Circuit Longitude], CALCULATE ( [Circuit Longitude], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )
```

## 15 Table columns

### Nation

```dax
IF ( NOT ISBLANK ( [HoF Wins] ), SELECTEDVALUE ( D_Driver[FlagSvg] ) )
```

### Helmet chip

```dax
IF ( NOT ISBLANK ( [HoF Wins] ), SELECTEDVALUE ( D_Driver[HelmetSvg] ) )
```

### GP wins

Format: `#,0`

```dax
[HoF Wins]
```

### GP poles

Format: `#,0`

```dax
[HoF Poles]
```

### GP podiums

Format: `#,0`

```dax
[HoF Podiums]
```

### Badge

```dax
IF ( NOT ISBLANK ( [Grands Prix] ), SELECTEDVALUE ( D_Constructor[TeamBadge] ) )
```

### Race wins

Format: `#,0`

```dax
IF ( NOT ISBLANK ( [Grands Prix] ), [Wins] + 0 )
```

### Podium finishes

Format: `#,0`

```dax
IF ( NOT ISBLANK ( [Grands Prix] ), [Podiums] + 0 )
```

### Pole positions

Format: `#,0`

```dax
IF ( NOT ISBLANK ( [Grands Prix] ), [Poles] + 0 )
```

### Record Rank

Format: `0`

```dax
RANKX ( ALLSELECTED ( D_Constructor[Team] ), [Points],, DESC )
```

### Nation Rank

Format: `0`

```dax
RANKX ( ALLSELECTED ( D_Circuit[Country] ), [Nation GP],, DESC )
```

## 16 Page totals

### Classic circuits

Format: `0`

```dax
CALCULATE ( DISTINCTCOUNT ( D_Circuit[CircuitId] ), D_Circuit[IsClassic] = 1 )
```

### Classic GP

Format: `#,0`

```dax
CALCULATE ( [Grands Prix Held], D_Circuit[IsClassic] = 1 )
```

### Classic winners

Format: `0`

```dax
CALCULATE ( [Different Winners], D_Circuit[IsClassic] = 1 )
```

### Classic km

Format: `0.0`

```dax
CALCULATE ( SUMX ( VALUES ( D_Circuit[CircuitId] ), CALCULATE ( MAX ( D_Circuit[LengthKm] ) ) ), D_Circuit[IsClassic] = 1 )
```

### Classic corners

Format: `#,0`

```dax
CALCULATE ( SUMX ( VALUES ( D_Circuit[CircuitId] ), CALCULATE ( MAX ( D_Circuit[Turns] ) ) ), D_Circuit[IsClassic] = 1 )
```

### Era points

Format: `#,0`

```dax
[Points]
```

### Era wins

Format: `#,0`

```dax
[Wins]
```

### Top 12 Metric

```dax
IF ( RANKX ( ALLSELECTED ( D_Driver[Driver] ), [Selected Metric],, DESC ) <= 12, [Selected Metric] )
```

## 17 Teams & results

### Car base

```dax
IF ( NOT ISBLANK ( [Grands Prix] ), SELECTEDVALUE ( D_Constructor[CarSvg] ) )
```

### Line-up base

```dax
CALCULATE ( CONCATENATEX ( SUMMARIZE ( F_Result, D_Driver[Driver] ), D_Driver[Driver], " · " ), F_Result[Position] <= 30 )
```

### Pos base

```dax
VAR p = [Team Championship Position] RETURN IF ( ISBLANK ( p ), BLANK ( ), "P" & FORMAT ( p, "0" ) )
```

### Points base

Format: `#,0`

```dax
[Team Championship Points]
```

### Grand Prix

```dax
SELECTEDVALUE ( D_Race[GrandPrix] )
```

### Round base

Format: `0`

```dax
IF ( ISBLANK ( [Winner base] ), BLANK ( ), SELECTEDVALUE ( D_Race[Round] ) )
```

### Date base

```dax
VAR d = SELECTEDVALUE ( D_Race[RaceDate] ) RETURN IF ( ISBLANK ( d ) || ISBLANK ( [Winner base] ), BLANK ( ), FORMAT ( d, "dd mmm" ) )
```

### Country

```dax
SELECTEDVALUE ( D_Race[Country] )
```

### Flag base

```dax
IF ( ISBLANK ( [Winner base] ), BLANK ( ), LOOKUPVALUE ( D_Circuit[FlagSvg], D_Circuit[CircuitId], SELECTEDVALUE ( D_Race[CircuitId] ) ) )
```

### Helmet base

```dax
VAR w = CALCULATETABLE ( SUMMARIZE ( F_Result, D_Driver[HelmetSvg] ), F_Result[IsWin] = 1 ) RETURN IF ( COUNTROWS ( w ) = 1, MAXX ( w, [HelmetSvg] ) )
```

### Winner base

```dax
CALCULATE ( CONCATENATEX ( SUMMARIZE ( F_Result, D_Driver[Driver] ), D_Driver[Driver] ), F_Result[IsWin] = 1 )
```

### Team base

```dax
CALCULATE ( CONCATENATEX ( SUMMARIZE ( F_Result, D_Constructor[Team] ), D_Constructor[Team] ), F_Result[IsWin] = 1 )
```

### Laps base

Format: `0`

```dax
CALCULATE ( MAX ( F_Result[LapsCompleted] ), F_Result[IsWin] = 1 )
```

### Time base

```dax
VAR ms = CALCULATE ( MIN ( F_Result[RaceTimeMillis] ), F_Result[IsWin] = 1 ) RETURN IF ( ISBLANK ( ms ), BLANK ( ), FORMAT ( INT ( ms / 3600000 ), "0" ) & ":" & FORMAT ( INT ( MOD ( ms, 3600000 ) / 60000 ), "00" ) & ":" & FORMAT ( INT ( MOD ( ms, 60000 ) / 1000 ), "00" ) & "." & FORMAT ( MOD ( ms, 1000 ), "000" ) )
```

### Wins base

Format: `#,0`

```dax
IF ( NOT ISBLANK ( [Grands Prix] ), [Wins] + 0 )
```

### Podiums base

Format: `#,0`

```dax
IF ( NOT ISBLANK ( [Grands Prix] ), [Podiums] + 0 )
```

### Team poles

Format: `#,0`

```dax
IF ( NOT ISBLANK ( [Grands Prix] ), [Poles] )
```

### Teams on the grid

Format: `0`

```dax
DISTINCTCOUNT ( F_Result[ConstructorId] )
```

### Drivers on the grid

Format: `0`

```dax
DISTINCTCOUNT ( F_Result[DriverId] )
```

## 18 Race row

### Nat

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Flag base], CALCULATE ( [Flag base], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Date

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Date base], CALCULATE ( [Date base], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Helmet

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Helmet base], CALCULATE ( [Helmet base], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Winner

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Winner base], CALCULATE ( [Winner base], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Team

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Team base], CALCULATE ( [Team base], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Laps

Format: `0`

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Laps base], CALCULATE ( [Laps base], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Time

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Time base], CALCULATE ( [Time base], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

### Rnd

Format: `0`

```dax
VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [Round base], CALCULATE ( [Round base], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )
```

## 19 Countries

### Nation flag

```dax
SELECTEDVALUE ( D_Circuit[FlagSvg] )
```

### Tracks

Format: `0`

```dax
DISTINCTCOUNT ( D_Circuit[CircuitId] )
```

### Nation GP

Format: `#,0`

```dax
[Grands Prix Held]
```

### Nation winners

Format: `0`

```dax
[Different Winners]
```

### First visit

Format: `0`

```dax
MIN ( D_Circuit[FirstGrandPrix] )
```

### Countries

Format: `0`

```dax
DISTINCTCOUNT ( D_Circuit[Country] )
```

### Continents

Format: `0`

```dax
DISTINCTCOUNT ( D_Circuit[CountryId] )
```
