# -*- coding: utf-8 -*-
"""Builds the DAX measure catalogue and writes definition/tables/Metrics.tmdl for the semantic model."""
import os, uuid
from apex.config import MODEL_DIR
TBL=str(MODEL_DIR/'definition'/'tables')
import itertools as _it
_seq=_it.count()
G=lambda: str(uuid.uuid5(uuid.NAMESPACE_URL,'apex-f1/lineage/%s/%d'%(__name__,next(_seq))))
GREY='%237A8496'
M=[]
def m(name,dax,fmt=None,folder=None,cat=None,desc=None):
    M.append((name,' '.join(dax.split()),fmt,folder,cat,desc))

F1='01 Race record'; F2='02 Rates & averages'; F3='03 Championship'; F4='04 Circuit'
F5='05 Season pulse'; F6='06 Dynamic'; F7='07 Visual helpers'; F8='08 Qualifying & pit lane'

# ---------------- 01 Race record ----------------
m('Entries','COUNTROWS ( F_Result )','#,0',F1,None,'Number of driver race entries in context')
m('Grands Prix','DISTINCTCOUNT ( F_Result[RaceKey] )','#,0',F1)
m('Wins','CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsWin] = 1 )','#,0',F1)
m('Podiums','CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsPodium] = 1 )','#,0',F1)
m('Points','SUM ( F_Result[Points] )','#,0',F1)
m('Poles','CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsPole] = 1 )','#,0',F1)
m('Fastest Laps','CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsFastestLap] = 1 )','#,0',F1)
m('DNFs','CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsDNF] = 1 )','#,0',F1)
m('Points Finishes','CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsPoints] = 1 )','#,0',F1)
m('Grand Slams','CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsGrandSlam] = 1 )','#,0',F1)
m('Driver of the Day','CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsDriverOfTheDay] = 1 )','#,0',F1)
m('Laps Completed','SUM ( F_Result[LapsCompleted] )','#,0',F1)
m('Race Distance (km)','SUMX ( VALUES ( D_Race[RaceKey] ), CALCULATE ( MAX ( D_Race[DistanceKm] ) ) )','#,0',F1)
m('Sprint Wins','CALCULATE ( COUNTROWS ( F_Sprint ), F_Sprint[IsSprintWin] = 1 )','#,0',F1)
m('Sprint Points','SUM ( F_Sprint[SprintPoints] )','#,0.##',F1)
m('Places Gained','CALCULATE ( SUM ( F_Result[PositionsGained] ), F_Result[PositionsGained] > 0 )','#,0',F1)

# ---------------- 02 Rates ----------------
m('Win Rate','DIVIDE ( [Wins], [Entries] )','0.0%',F2)
m('Podium Rate','DIVIDE ( [Podiums], [Entries] )','0.0%',F2)
m('Points Rate','DIVIDE ( [Points Finishes], [Entries] )','0.0%',F2)
m('DNF Rate','DIVIDE ( [DNFs], [Entries] )','0.0%',F2)
m('Finish Rate','DIVIDE ( [Entries] - [DNFs], [Entries] )','0.0%',F2)
m('Avg Finish','AVERAGE ( F_Result[Position] )','0.0',F2)
m('Avg Grid','AVERAGE ( F_Result[GridPosition] )','0.0',F2)
m('Avg Places Gained','AVERAGE ( F_Result[PositionsGained] )','+0.0;-0.0;0.0',F2)
m('Points per Race','DIVIDE ( [Points], [Entries] )','0.0',F2)
m('Best Finish','MIN ( F_Result[Position] )','0',F2)
m('Pole to Win %','DIVIDE ( CALCULATE ( COUNTROWS ( F_Result ), F_Result[WinFromPole] = 1 ), CALCULATE ( COUNTROWS ( F_Result ), F_Result[StartedFromPole] = 1 ) )','0.0%',F2)
m('Points Share %','DIVIDE ( [Points], CALCULATE ( [Points], ALLSELECTED ( D_Driver ), ALLSELECTED ( D_Constructor ) ) )','0.0%',F2)

# ---------------- 03 Championship ----------------
m('Championship Points','SUMX ( VALUES ( F_DriverStanding[Year] ), VAR r = CALCULATE ( MAX ( F_DriverStanding[Round] ) ) RETURN CALCULATE ( SUM ( F_DriverStanding[StandingPoints] ), F_DriverStanding[Round] = r ) )','#,0.##',F3)
m('Championship Position','MINX ( VALUES ( F_DriverStanding[Year] ), VAR r = CALCULATE ( MAX ( F_DriverStanding[Round] ) ) RETURN CALCULATE ( MIN ( F_DriverStanding[StandingPosition] ), F_DriverStanding[Round] = r ) )','0',F3)
m('Team Championship Points','SUMX ( VALUES ( F_ConstructorStanding[Year] ), VAR r = CALCULATE ( MAX ( F_ConstructorStanding[Round] ) ) RETURN CALCULATE ( SUM ( F_ConstructorStanding[StandingPoints] ), F_ConstructorStanding[Round] = r ) )','#,0.##',F3)
m('Team Championship Position','MINX ( VALUES ( F_ConstructorStanding[Year] ), VAR r = CALCULATE ( MAX ( F_ConstructorStanding[Round] ) ) RETURN CALCULATE ( MIN ( F_ConstructorStanding[StandingPosition] ), F_ConstructorStanding[Round] = r ) )','0',F3)
m('Drivers Titles','CALCULATE ( COUNTROWS ( F_DriverStanding ), F_DriverStanding[ChampionshipWon] = 1, F_DriverStanding[IsLatestRound] = 1 )','0',F3)
m('Constructors Titles','CALCULATE ( COUNTROWS ( F_ConstructorStanding ), F_ConstructorStanding[ChampionshipWon] = 1, F_ConstructorStanding[IsLatestRound] = 1 )','0',F3)
m('Running Points','SUM ( F_DriverStanding[StandingPoints] )','#,0.##',F3)
m('Team Running Points','SUM ( F_ConstructorStanding[StandingPoints] )','#,0.##',F3)

# ---------------- 04 Circuit ----------------
m('Circuit Length (km)','MAX ( D_Circuit[LengthKm] )','0.000',F4)
m('Circuit Turns','MAX ( D_Circuit[Turns] )','0',F4)
m('Grands Prix Held','CALCULATE ( DISTINCTCOUNT ( D_Race[RaceKey] ), D_Race[IsRun] = 1 )','#,0',F4)
m('First Grand Prix','MIN ( D_Circuit[FirstGrandPrix] )','0',F4)
m('Different Winners','CALCULATE ( DISTINCTCOUNT ( F_Result[DriverId] ), F_Result[IsWin] = 1 )','0',F4)
m('Different Winning Teams','CALCULATE ( DISTINCTCOUNT ( F_Result[ConstructorId] ), F_Result[IsWin] = 1 )','0',F4)
m('Lap Record ms','MIN ( F_FastestLap[LapTimeMs] )','#,0',F4)
m('Lap Record','VAR ms = [Lap Record ms] RETURN IF ( ISBLANK ( ms ), "n/a", FORMAT ( INT ( ms / 60000 ), "0" ) & ":" & FORMAT ( INT ( MOD ( ms, 60000 ) / 1000 ), "00" ) & "." & FORMAT ( MOD ( ms, 1000 ), "000" ) )',None,F4)
m('Lap Record Holder','VAR ms = [Lap Record ms] RETURN CALCULATE ( CONCATENATEX ( SUMMARIZE ( F_FastestLap, D_Driver[Driver] ), D_Driver[Driver], ", " ), F_FastestLap[LapTimeMs] = ms )',None,F4)
m('Lap Record Year','VAR ms = [Lap Record ms] RETURN CALCULATE ( MAX ( F_FastestLap[Year] ), F_FastestLap[LapTimeMs] = ms )','0',F4)
m('Track Master','VAR t = ADDCOLUMNS ( SUMMARIZE ( F_Result, D_Driver[Driver] ), "@w", CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsWin] = 1 ) ) VAR bestrow = TOPN ( 1, FILTER ( t, [@w] > 0 ), [@w], DESC, [Driver], ASC ) RETURN IF ( ISEMPTY ( bestrow ), "n/a", MAXX ( bestrow, [Driver] ) & "  ·  " & FORMAT ( MAXX ( bestrow, [@w] ), "0" ) & " wins" )',None,F4)
m('Track Master Team','VAR t = ADDCOLUMNS ( SUMMARIZE ( F_Result, D_Constructor[Team] ), "@w", CALCULATE ( COUNTROWS ( F_Result ), F_Result[IsWin] = 1 ) ) VAR bestrow = TOPN ( 1, FILTER ( t, [@w] > 0 ), [@w], DESC, [Team], ASC ) RETURN IF ( ISEMPTY ( bestrow ), "n/a", MAXX ( bestrow, [Team] ) & "  ·  " & FORMAT ( MAXX ( bestrow, [@w] ), "0" ) & " wins" )',None,F4)
m('Circuit Profile','VAR l = [Circuit Length (km)] VAR t = [Circuit Turns] VAR ty = SELECTEDVALUE ( D_Circuit[CircuitType] ) VAR d = SELECTEDVALUE ( D_Circuit[Direction] ) RETURN IF ( ISBLANK ( l ), "n/a", FORMAT ( l, "0.000" ) & " km  ·  " & FORMAT ( t, "0" ) & " turns  ·  " & ty & "  ·  " & d )',None,F4)

# ---------------- 05 Season pulse ----------------
m('Rounds Scheduled','DISTINCTCOUNT ( D_Race[RaceKey] )','0',F5)
m('Rounds Run','CALCULATE ( DISTINCTCOUNT ( D_Race[RaceKey] ), D_Race[IsRun] = 1 )','0',F5)
m('Rounds Remaining','[Rounds Scheduled] - [Rounds Run]','0',F5)
m('Season Progress','DIVIDE ( [Rounds Run], [Rounds Scheduled] )','0%',F5)
m('Championship Leader','VAR t = ADDCOLUMNS ( VALUES ( D_Driver[Driver] ), "@p", [Championship Points] ) VAR bestrow = TOPN ( 1, FILTER ( t, [@p] > 0 ), [@p], DESC ) RETURN IF ( ISEMPTY ( bestrow ), "n/a", MAXX ( bestrow, [Driver] ) )',None,F5)
m('Leader Points','MAXX ( ADDCOLUMNS ( VALUES ( D_Driver[Driver] ), "@p", [Championship Points] ), [@p] )','#,0',F5)
m('Gap to Second','VAR t = ADDCOLUMNS ( VALUES ( D_Driver[Driver] ), "@p", [Championship Points] ) VAR pair = TOPN ( 2, FILTER ( t, [@p] > 0 ), [@p], DESC ) RETURN MAXX ( pair, [@p] ) - MINX ( pair, [@p] )','#,0',F5)
m('Leading Team','VAR t = ADDCOLUMNS ( VALUES ( D_Constructor[Team] ), "@p", [Team Championship Points] ) VAR bestrow = TOPN ( 1, FILTER ( t, [@p] > 0 ), [@p], DESC ) RETURN IF ( ISEMPTY ( bestrow ), "n/a", MAXX ( bestrow, [Team] ) )',None,F5)
m('Leading Team Points','MAXX ( ADDCOLUMNS ( VALUES ( D_Constructor[Team] ), "@p", [Team Championship Points] ), [@p] )','#,0',F5)
m('Last Race','VAR k = CALCULATE ( MAX ( D_Race[SortKey] ), D_Race[IsRun] = 1 ) RETURN CALCULATE ( SELECTEDVALUE ( D_Race[GrandPrix] ), D_Race[SortKey] = k )',None,F5)
m('Last Race Winner','VAR k = CALCULATE ( MAX ( D_Race[SortKey] ), D_Race[IsRun] = 1 ) RETURN CALCULATE ( CONCATENATEX ( SUMMARIZE ( F_Result, D_Driver[Driver] ), D_Driver[Driver], ", " ), D_Race[SortKey] = k, F_Result[IsWin] = 1 )',None,F5)
m('Last Race Date','VAR k = CALCULATE ( MAX ( D_Race[SortKey] ), D_Race[IsRun] = 1 ) RETURN CALCULATE ( SELECTEDVALUE ( D_Race[RaceDate] ), D_Race[SortKey] = k )','yyyy-mm-dd',F5)
m('Next Race','VAR k = CALCULATE ( MIN ( D_Race[SortKey] ), D_Race[IsRun] = 0 ) RETURN IF ( ISBLANK ( k ), "Season complete", CALCULATE ( SELECTEDVALUE ( D_Race[GrandPrix] ), D_Race[SortKey] = k ) )',None,F5)
m('Next Race Circuit','VAR k = CALCULATE ( MIN ( D_Race[SortKey] ), D_Race[IsRun] = 0 ) RETURN CALCULATE ( SELECTEDVALUE ( D_Race[Circuit] ), D_Race[SortKey] = k )',None,F5)
m('Next Race Date','VAR k = CALCULATE ( MIN ( D_Race[SortKey] ), D_Race[IsRun] = 0 ) RETURN CALCULATE ( SELECTEDVALUE ( D_Race[RaceDate] ), D_Race[SortKey] = k )','yyyy-mm-dd',F5)
m('Season Headline','VAR l = [Championship Leader] VAR p = [Leader Points] VAR g = [Gap to Second] VAR r = [Rounds Remaining] RETURN IF ( ISBLANK ( p ), "n/a", l & " leads on " & FORMAT ( p, "#,0" ) & " points, " & FORMAT ( g, "#,0" ) & " clear, with " & FORMAT ( r, "0" ) & " rounds to run." )',None,F5)

# ---------------- 06 Dynamic ----------------
m('Selected Metric','SWITCH ( SELECTEDVALUE ( D_Metric[Metric], "Points" ), "Points", [Points], "Wins", [Wins], "Podiums", [Podiums], "Poles", [Poles], "Fastest laps", [Fastest Laps], "Avg finish", [Avg Finish], "DNFs", [DNFs] )',None,F6)
m('Selected Metric Label','SELECTEDVALUE ( D_Metric[Metric], "Points" )',None,F6)
m('Selected Metric Format','SWITCH ( SELECTEDVALUE ( D_Metric[Metric], "Points" ), "Avg finish", "0.0", "#,0.##" )',None,F6)
m('Scope Filter','IF ( SELECTEDVALUE ( D_Scope[Scope], "All circuits" ) = "Classic eleven", CALCULATE ( [Selected Metric], D_Race[IsClassicCircuit] = 1 ), [Selected Metric] )',None,F6)
m('Scope Label','SELECTEDVALUE ( D_Scope[ScopeDesc], "Every Grand Prix in the era" )',None,F6)

# ---------------- 07 Visual helpers ----------------
m('Team Colour','COALESCE ( SELECTEDVALUE ( D_Constructor[TeamColour] ), "'+GREY.replace('%23','#')+'" )',None,F7)
m('Driver Team Colour','VAR t = ADDCOLUMNS ( SUMMARIZE ( F_Result, D_Constructor[TeamColour] ), "@n", CALCULATE ( COUNTROWS ( F_Result ) ) ) RETURN COALESCE ( MAXX ( TOPN ( 1, t, [@n], DESC ), [TeamColour] ), "'+GREY.replace('%23','#')+'" )',None,F7)
m('Track Blueprint','VAR ok = HASONEVALUE ( D_Circuit[CircuitId] ) VAR pts = CONCATENATEX ( F_TrackPoint, FORMAT ( F_TrackPoint[X], "0.0" ) & " " & FORMAT ( - F_TrackPoint[Y], "0.0" ), " L ", F_TrackPoint[PointOrder], ASC ) RETURN IF ( NOT ok || ISBLANK ( pts ), BLANK (), "data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'-112 -112 224 224\' width=\'620\' height=\'620\'><path d=\'M " & pts & " Z\' fill=\'none\' stroke=\'%2320252F\' stroke-width=\'21\' stroke-linejoin=\'round\' stroke-linecap=\'round\'/><path d=\'M " & pts & " Z\' fill=\'none\' stroke=\'%23E9EDF5\' stroke-width=\'10\' stroke-linejoin=\'round\' stroke-linecap=\'round\'/><path d=\'M " & pts & " Z\' fill=\'none\' stroke=\'%23E8323C\' stroke-width=\'1.6\' stroke-dasharray=\'3 8\' stroke-linecap=\'round\'/></svg>" )',None,F7,'ImageUrl')
m('Selected Circuit','COALESCE ( SELECTEDVALUE ( D_Circuit[Circuit] ), "All circuits" )',None,F7)
m('Selected Circuit Nickname','COALESCE ( SELECTEDVALUE ( D_Circuit[Nickname] ), "" )',None,F7)
m('Signature Corner','COALESCE ( SELECTEDVALUE ( D_Circuit[SignatureCorner] ), "n/a" )',None,F7)
m('Selected Season','COALESCE ( SELECTEDVALUE ( D_Season[SeasonLabel] ), "2014 to 2026" )',None,F7)

# ---------------- 08 Qualifying & pit lane ----------------
m('Pole Time ms','MIN ( F_Qualifying[BestQualiMs] )','#,0',F8)
m('Pole Time','VAR ms = [Pole Time ms] RETURN IF ( ISBLANK ( ms ), "n/a", FORMAT ( INT ( ms / 60000 ), "0" ) & ":" & FORMAT ( INT ( MOD ( ms, 60000 ) / 1000 ), "00" ) & "." & FORMAT ( MOD ( ms, 1000 ), "000" ) )',None,F8)
m('Q3 Appearances','CALCULATE ( COUNTROWS ( F_Qualifying ), F_Qualifying[ReachedQ3] = 1 )','#,0',F8)
m('Q3 Rate','DIVIDE ( [Q3 Appearances], COUNTROWS ( F_Qualifying ) )','0.0%',F8)
m('Avg Quali Gap (s)','AVERAGEX ( F_Qualifying, DIVIDE ( F_Qualifying[GapToPoleMs], 1000 ) )','0.000',F8)
m('Avg Quali Position','AVERAGE ( F_Qualifying[QualiPosition] )','0.0',F8)
m('Pit Stops','SUM ( F_Result[PitStops] )','#,0',F8)
m('Avg Pit Stops','AVERAGE ( F_Result[PitStops] )','0.00',F8)
m('Fastest Pit Stop (s)','DIVIDE ( MIN ( F_Result[BestPitStopMs] ), 1000 )','0.00',F8)


# ---------------- 05b Tile sub-lines ----------------
m('Leader Sub','VAR p = [Leader Points] VAR g = [Gap to Second] RETURN IF ( ISBLANK ( p ), "n/a", FORMAT ( p, "#,0" ) & " pts   ·   +" & FORMAT ( g, "#,0" ) & " on P2" )',None,F5)
m('Team Sub','VAR p = [Leading Team Points] RETURN IF ( ISBLANK ( p ), "n/a", FORMAT ( p, "#,0" ) & " pts" )',None,F5)
m('Round Line','"Round " & FORMAT ( [Rounds Run], "0" ) & " of " & FORMAT ( [Rounds Scheduled], "0" )',None,F5)
m('Winners Sub','FORMAT ( [Different Winners], "0" ) & " winners · " & FORMAT ( [Different Winning Teams], "0" ) & " winning teams"',None,F5)
m('Last GP Sub','VAR d = [Last Race Date] RETURN IF ( ISBLANK ( d ), "n/a", [Last Race] & "   ·   " & FORMAT ( d, "d mmm yyyy" ) )',None,F5)
m('Next GP Sub','VAR d = [Next Race Date] RETURN IF ( ISBLANK ( d ), "Season complete", [Next Race Circuit] & "   ·   " & FORMAT ( d, "d mmm yyyy" ) )',None,F5)
m('Era Footnote','"Source: f1db open dataset  ·  circuit geometry from the f1-circuits dataset  ·  2014-2026 hybrid era  ·  built with Power BI"',None,F7)
m('Lap Record Line','VAR t = [Lap Record] RETURN IF ( t = "n/a", "n/a", [Lap Record Holder] & "   ·   " & FORMAT ( [Lap Record Year], "0" ) )',None,F4)
m('Track Length Total','SUMX ( VALUES ( D_Circuit[CircuitId] ), CALCULATE ( MAX ( D_Circuit[LengthKm] ) ) )','#,0.0',F4)
m('Total Turns','SUMX ( VALUES ( D_Circuit[CircuitId] ), CALCULATE ( MAX ( D_Circuit[Turns] ) ) )','#,0',F4)
m('Circuits','DISTINCTCOUNT ( D_Circuit[CircuitId] )','0',F4)
m('Circuit Headline','VAR c = SELECTEDVALUE ( D_Circuit[Circuit] ) VAR n = SELECTEDVALUE ( D_Circuit[Nickname] ) RETURN IF ( ISBLANK ( c ), "Select a circuit", IF ( n = "", c, n ) )',None,F7)
m('Seasons Covered','DISTINCTCOUNT ( D_Race[Year] )','0',F1)


# ---------------- 09 Leaderboards (Top N without filters) ----------------
F9 = '09 Leaderboard'
m('Driver Rank','RANKX ( ALLSELECTED ( D_Driver[Driver] ), [Points],, DESC )','0',F9)
m('Team Rank','RANKX ( ALLSELECTED ( D_Constructor[Team] ), [Points],, DESC )','0',F9)
m('Top 15 Points','IF ( RANKX ( ALLSELECTED ( D_Driver[Driver] ), [Points],, DESC ) <= 15, [Points] )','#,0',F9)
m('Top 15 Metric','IF ( RANKX ( ALLSELECTED ( D_Driver[Driver] ), [Selected Metric],, DESC ) <= 15, [Selected Metric] )',None,F9)
m('Top 12 Wins','IF ( RANKX ( ALLSELECTED ( D_Driver[Driver] ), [Wins],, DESC ) <= 12 && [Wins] > 0, [Wins] )','#,0',F9)
m('Top 12 Poles','IF ( RANKX ( ALLSELECTED ( D_Driver[Driver] ), [Poles],, DESC ) <= 12 && [Poles] > 0, [Poles] )','#,0',F9)
m('Top 12 Podiums','IF ( RANKX ( ALLSELECTED ( D_Driver[Driver] ), [Podiums],, DESC ) <= 12 && [Podiums] > 0, [Podiums] )','#,0',F9)
m('Wins Here','IF ( [Wins] > 0, [Wins] )','#,0',F9)
m('Podiums Here','IF ( [Podiums] > 0, [Podiums] )','#,0',F9)
m('Driver Points (min 10 starts)','IF ( [Entries] >= 10, [Points] )','#,0',F9)
m('Avg Finish (min 60 starts)','IF ( [Entries] >= 60, [Avg Finish] )','0.0',F9)
m('Avg Grid (min 60 starts)','IF ( [Entries] >= 60, [Avg Grid] )','0.0',F9)


# ---------------- 10 Race cards & hall of fame ----------------
FA = '10 Race cards'
m('Race Winner','CALCULATE ( CONCATENATEX ( SUMMARIZE ( F_Result, D_Driver[Driver] ), D_Driver[Driver], ", " ), F_Result[IsWin] = 1 )',None,FA)
m('Winning Team','CALCULATE ( CONCATENATEX ( SUMMARIZE ( F_Result, D_Constructor[Team] ), D_Constructor[Team], ", " ), F_Result[IsWin] = 1 )',None,FA)
m('Pole Sitter','CALCULATE ( CONCATENATEX ( SUMMARIZE ( F_Result, D_Driver[Driver] ), D_Driver[Driver], ", " ), F_Result[IsPole] = 1 )',None,FA)
m('Fastest Lap By','CALCULATE ( CONCATENATEX ( SUMMARIZE ( F_Result, D_Driver[Driver] ), D_Driver[Driver], ", " ), F_Result[IsFastestLap] = 1 )',None,FA)
m('Winning Margin','VAR g = CALCULATE ( MIN ( F_Result[GapMillis] ), F_Result[Position] = 2 ) RETURN IF ( ISBLANK ( g ), "n/a", FORMAT ( g / 1000, "0.000" ) & " s" )',None,FA)
m('HoF Wins','IF ( RANKX ( ALLSELECTED ( D_Driver[Driver] ), [Wins],, DESC ) <= 10 && [Wins] > 0, [Wins] )','#,0',FA)
m('HoF Poles','IF ( NOT ISBLANK ( [HoF Wins] ), [Poles] + 0 )','#,0',FA)
m('HoF Podiums','IF ( NOT ISBLANK ( [HoF Wins] ), [Podiums] + 0 )','#,0',FA)
m('HoF Titles','IF ( NOT ISBLANK ( [HoF Wins] ), [Drivers Titles] )','0',FA)
m('HoF Points','IF ( NOT ISBLANK ( [HoF Wins] ), [Points] )','#,0',FA)
m('HoF Win Rate','IF ( NOT ISBLANK ( [HoF Wins] ), [Win Rate] )','0.0%',FA)
m('Busy Places Gained','IF ( RANKX ( ALLSELECTED ( D_Driver[Driver] ), [Entries],, DESC ) <= 15, [Avg Places Gained] )','+0.00;-0.00;0.00',FA)
m('Retirements per Race','DIVIDE ( [DNFs], [Grands Prix] )','0.00',F2)


# ============ 11 Default scopes, without JSON filters ============
FS = '11 Scope'
m('Default Season','IF ( ISFILTERED ( D_Season[SeasonLabel] ), BLANK ( ), CALCULATE ( MAX ( D_Season[Year] ), REMOVEFILTERS ( D_Season ), D_Season[IsCurrentSeason] = 1 ) )','0',FS)
m('Default Circuit','IF ( ISFILTERED ( D_Circuit[Circuit] ), BLANK ( ), "monza" )',None,FS)

def live(name, base, fmt=None, cat=None):
    m(name,'VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [%s], CALCULATE ( [%s], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )'%(base,base),fmt,'12 Live season',cat)
def lab(name, base, fmt=None, cat=None):
    m(name,'VAR c = [Default Circuit] RETURN IF ( ISBLANK ( c ), [%s], CALCULATE ( [%s], REMOVEFILTERS ( D_Circuit ), D_Circuit[CircuitId] = c ) )'%(base,base),fmt,'13 Circuit lab',cat)

# ---- Season Pulse page ----
live('Season points','Championship Points','#,0')
live('Team points','Team Championship Points','#,0')
live('Running team points','Team Running Points','#,0')
live('Season wins','Top 12 Wins','#,0')
live('Season poles','Top 12 Poles','#,0')
live('Live Leader','Championship Leader')
live('Live Leader Sub','Leader Sub')
live('Live Team','Leading Team')
live('Live Team Sub','Team Sub')
live('Live Last Winner','Last Race Winner')
live('Live Last GP Sub','Last GP Sub')
live('Live Next GP','Next Race')
live('Live Next GP Sub','Next GP Sub')
live('Live Round Line','Round Line')
live('Live Winners Sub','Winners Sub')
live('Live Headline','Season Headline')
live('Live Season','Selected Season')

# ---- Classic Eleven page: columns served by filtering measures ----
FC = '14 Classic eleven'
def classic(name, expr, fmt=None, cat=None):
    m(name,'IF ( SELECTEDVALUE ( D_Circuit[IsClassic] ) = 1, %s )'%expr,fmt,FC,cat)
classic('Track','SELECTEDVALUE ( D_Circuit[TrackSvg] )',None,'ImageUrl')
classic('Flag','SELECTEDVALUE ( D_Circuit[FlagSvg] )',None,'ImageUrl')
classic('Nickname','SELECTEDVALUE ( D_Circuit[Nickname] )')
classic('Classic country','SELECTEDVALUE ( D_Circuit[Country] )')
classic('Km','SELECTEDVALUE ( D_Circuit[LengthKm] )','0.000')
classic('Corners','SELECTEDVALUE ( D_Circuit[Turns] )','0')
classic('GP','[Grands Prix Held]','#,0')
classic('Record','[Lap Record]')
classic('Winners','[Different Winners]','0')
classic('Lat','AVERAGE ( D_Circuit[Latitude] )','0.0000')
classic('Lon','AVERAGE ( D_Circuit[Longitude] )','0.0000')

# ---- Circuit Lab page ----
lab('Lab Blueprint','Track Blueprint',None,'ImageUrl')
lab('Lab Profile','Circuit Profile')
lab('Lab Headline','Circuit Headline')
lab('Lab Corner','Signature Corner')
lab('Lab GP','Grands Prix Held','#,0')
lab('Lab First GP','First Grand Prix','0')
lab('Lab Winners','Different Winners','0')
lab('Lab Teams','Different Winning Teams','0')
lab('Lab Record','Lap Record')
lab('Lab Record Line','Lap Record Line')
lab('Lab Master','Track Master')
lab('Lab Master Team','Track Master Team')
lab('Lab Length','Circuit Length (km)','0.000')
lab('Lab Turns','Circuit Turns','0')
lab('Driver wins here','Wins Here','#,0')
lab('Team podiums here','Podiums Here','#,0')
lab('Race win by','Race Winner')
lab('Constructor','Winning Team')
lab('Pole','Pole Sitter')
lab('Margin','Winning Margin')
lab('Fastest lap','Lap Record')
lab('Lab Lat','Circuit Latitude','0.0000')
lab('Lab Lon','Circuit Longitude','0.0000')
m('Circuit Latitude','AVERAGE ( D_Circuit[Latitude] )','0.0000',FS)
m('Circuit Longitude','AVERAGE ( D_Circuit[Longitude] )','0.0000',FS)

# ---- clean column headers for the tables ----
FH = '15 Table columns'
m('Nation','IF ( NOT ISBLANK ( [HoF Wins] ), SELECTEDVALUE ( D_Driver[FlagSvg] ) )',None,FH,'ImageUrl')
m('Helmet chip','IF ( NOT ISBLANK ( [HoF Wins] ), SELECTEDVALUE ( D_Driver[HelmetSvg] ) )',None,FH,'ImageUrl')
m('GP wins','[HoF Wins]','#,0',FH)
m('GP poles','[HoF Poles]','#,0',FH)
m('GP podiums','[HoF Podiums]','#,0',FH)
m('Badge','IF ( NOT ISBLANK ( [Grands Prix] ), SELECTEDVALUE ( D_Constructor[TeamBadge] ) )',None,FH,'ImageUrl')
m('Race wins','IF ( NOT ISBLANK ( [Grands Prix] ), [Wins] + 0 )','#,0',FH)
m('Podium finishes','IF ( NOT ISBLANK ( [Grands Prix] ), [Podiums] + 0 )','#,0',FH)
m('Pole positions','IF ( NOT ISBLANK ( [Grands Prix] ), [Poles] + 0 )','#,0',FH)
m('Record Rank','RANKX ( ALLSELECTED ( D_Constructor[Team] ), [Points],, DESC )','0',FH)
m('Nation Rank','RANKX ( ALLSELECTED ( D_Circuit[Country] ), [Nation GP],, DESC )','0',FH)


# ============ 16 Page totals (aggregates, no SELECTEDVALUE) ============
FT2 = '16 Page totals'
m('Classic circuits','CALCULATE ( DISTINCTCOUNT ( D_Circuit[CircuitId] ), D_Circuit[IsClassic] = 1 )','0',FT2)
m('Classic GP','CALCULATE ( [Grands Prix Held], D_Circuit[IsClassic] = 1 )','#,0',FT2)
m('Classic winners','CALCULATE ( [Different Winners], D_Circuit[IsClassic] = 1 )','0',FT2)
m('Classic km','CALCULATE ( SUMX ( VALUES ( D_Circuit[CircuitId] ), CALCULATE ( MAX ( D_Circuit[LengthKm] ) ) ), D_Circuit[IsClassic] = 1 )','0.0',FT2)
m('Classic corners','CALCULATE ( SUMX ( VALUES ( D_Circuit[CircuitId] ), CALCULATE ( MAX ( D_Circuit[Turns] ) ) ), D_Circuit[IsClassic] = 1 )','#,0',FT2)
m('Era points','[Points]','#,0',FT2)
m('Era wins','[Wins]','#,0',FT2)
m('Top 12 Metric','IF ( RANKX ( ALLSELECTED ( D_Driver[Driver] ), [Selected Metric],, DESC ) <= 12, [Selected Metric] )',None,FT2)


# ============ 17 Teams & Results pages (layout inspired by formula1.com) ============
FR = '17 Teams & results'
m('Car base','IF ( NOT ISBLANK ( [Grands Prix] ), SELECTEDVALUE ( D_Constructor[CarSvg] ) )',None,FR,'ImageUrl')
m('Line-up base','CALCULATE ( CONCATENATEX ( SUMMARIZE ( F_Result, D_Driver[Driver] ), D_Driver[Driver], "   ·   " ), F_Result[Position] <= 30 )',None,FR)
m('Pos base','VAR p = [Team Championship Position] RETURN IF ( ISBLANK ( p ), BLANK ( ), "P" & FORMAT ( p, "0" ) )',None,FR)
m('Points base','[Team Championship Points]','#,0',FR)
m('Grand Prix','SELECTEDVALUE ( D_Race[GrandPrix] )',None,FR)
m('Round base','IF ( ISBLANK ( [Winner base] ), BLANK ( ), SELECTEDVALUE ( D_Race[Round] ) )','0',FR)
m('Date base','VAR d = SELECTEDVALUE ( D_Race[RaceDate] ) RETURN IF ( ISBLANK ( d ) || ISBLANK ( [Winner base] ), BLANK ( ), FORMAT ( d, "dd mmm" ) )',None,FR)
m('Country','SELECTEDVALUE ( D_Race[Country] )',None,FR)
m('Flag base','IF ( ISBLANK ( [Winner base] ), BLANK ( ), LOOKUPVALUE ( D_Circuit[FlagSvg], D_Circuit[CircuitId], SELECTEDVALUE ( D_Race[CircuitId] ) ) )',None,FR,'ImageUrl')
m('Helmet base','VAR w = CALCULATETABLE ( SUMMARIZE ( F_Result, D_Driver[HelmetSvg] ), F_Result[IsWin] = 1 ) RETURN IF ( COUNTROWS ( w ) = 1, MAXX ( w, [HelmetSvg] ) )',None,FR,'ImageUrl')
m('Winner base','CALCULATE ( CONCATENATEX ( SUMMARIZE ( F_Result, D_Driver[Driver] ), D_Driver[Driver] ), F_Result[IsWin] = 1 )',None,FR)
m('Team base','CALCULATE ( CONCATENATEX ( SUMMARIZE ( F_Result, D_Constructor[Team] ), D_Constructor[Team] ), F_Result[IsWin] = 1 )',None,FR)
m('Laps base','CALCULATE ( MAX ( F_Result[LapsCompleted] ), F_Result[IsWin] = 1 )','0',FR)
m('Time base','VAR ms = CALCULATE ( MIN ( F_Result[RaceTimeMillis] ), F_Result[IsWin] = 1 ) RETURN IF ( ISBLANK ( ms ), BLANK ( ), FORMAT ( INT ( ms / 3600000 ), "0" ) & ":" & FORMAT ( INT ( MOD ( ms, 3600000 ) / 60000 ), "00" ) & ":" & FORMAT ( INT ( MOD ( ms, 60000 ) / 1000 ), "00" ) & "." & FORMAT ( MOD ( ms, 1000 ), "000" ) )',None,FR)
m('Wins base','IF ( NOT ISBLANK ( [Grands Prix] ), [Wins] + 0 )','#,0',FR)
m('Podiums base','IF ( NOT ISBLANK ( [Grands Prix] ), [Podiums] + 0 )','#,0',FR)
m('Team poles','IF ( NOT ISBLANK ( [Grands Prix] ), [Poles] )','#,0',FR)
m('Teams on the grid','DISTINCTCOUNT ( F_Result[ConstructorId] )','0',FR)
m('Drivers on the grid','DISTINCTCOUNT ( F_Result[DriverId] )','0',FR)


# ---- row measures for the Results page (guarded by the default season) ----
def rrow(name, base, fmt=None, cat=None):
    m(name,'VAR y = [Default Season] RETURN IF ( ISBLANK ( y ), [%s], CALCULATE ( [%s], REMOVEFILTERS ( D_Season ), D_Season[Year] = y ) )'%(base,base),fmt,'18 Race row',cat)
rrow('Nat','Flag base',None,'ImageUrl')
rrow('Date','Date base')
rrow('Helmet','Helmet base',None,'ImageUrl')
rrow('Winner','Winner base')
rrow('Team','Team base')
rrow('Laps','Laps base','0')
rrow('Time','Time base')
rrow('Rnd','Round base','0')
# ---- live measures for the Teams page ----
live('Car','Car base',None,'ImageUrl')
live('Line-up','Line-up base')
live('Pos','Pos base')
live('Pts','Points base','#,0')
live('Won','Wins base','#,0')
live('Top 3','Podiums base','#,0')
live('Grid teams','Teams on the grid','0')
live('Grid drivers','Drivers on the grid','0')
live('Grid races','Grands Prix','#,0')
live('Grid winners','Different Winners','0')
live('Grid teams won','Different Winning Teams','0')

import collections as _cc
_names=[x[0] for x in M]
_dup=[k for k,v in _cc.Counter(n.lower() for n in _names).items() if v>1]
assert not _dup, 'DUPLICATE MEASURES: %s'%_dup


# ============ 19 Countries page: every country visited ============
FN = '19 Countries'
m('Nation flag','SELECTEDVALUE ( D_Circuit[FlagSvg] )',None,FN,'ImageUrl')
m('Tracks','DISTINCTCOUNT ( D_Circuit[CircuitId] )','0',FN)
m('Nation GP','[Grands Prix Held]','#,0',FN)
m('Nation winners','[Different Winners]','0',FN)
m('First visit','MIN ( D_Circuit[FirstGrandPrix] )','0',FN)
m('Countries','DISTINCTCOUNT ( D_Circuit[Country] )','0',FN)
m('Continents','DISTINCTCOUNT ( D_Circuit[CountryId] )','0',FN)

L=['table Metrics','\tlineageTag: %s'%G(),'']
for name,dax,fmt,folder,cat,desc in M:
    if desc: L.append('\t/// %s'%desc)
    L.append("\tmeasure '%s' = %s"%(name,dax))
    if fmt: L.append('\t\tformatString: %s'%fmt)
    L.append('\t\tlineageTag: %s'%G())
    if folder: L.append('\t\tdisplayFolder: %s'%folder)
    if cat: L.append('\t\tdataCategory: %s'%cat)
    L.append('')
L+=['\tcolumn Placeholder','\t\tdataType: string','\t\tisHidden','\t\tlineageTag: %s'%G(),
    '\t\tsummarizeBy: none','\t\tsourceColumn: [Placeholder]','',
    '\t\tannotation SummarizationSetBy = Automatic','',
    '\tpartition Metrics = calculated','\t\tmode: import','\t\tsource = ROW ( "Placeholder", "" )','',
    '\tannotation PBI_Id = Metrics','']
open(os.path.join(TBL,'Metrics.tmdl'),'w',encoding='utf-8').write('\n'.join(L))
print('measures:',len(M))
