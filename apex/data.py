# -*- coding: utf-8 -*-
"""Build the star-schema CSV tables from the raw f1db export.

Reads the unzipped f1db CSV files (F1DB_DIR) and the circuit GeoJSON, restricts
them to the YEAR_FROM..YEAR_TO era, and writes one CSV per dimension (D_*) and
fact (F_*) table into DATA_DIR. These CSV files are what the semantic model imports.
"""
import csv, json, math, os, collections
from apex.config import F1DB_DIR, DATA_DIR, CIRCUITS_GEOJSON, YEAR_FROM, YEAR_TO, ensure_dirs
ensure_dirs()
RAW=str(F1DB_DIR); OUT=str(DATA_DIR); GEO=str(CIRCUITS_GEOJSON)
Y0,Y1=YEAR_FROM,YEAR_TO

def rd(n): return list(csv.DictReader(open(os.path.join(RAW,'f1db-%s.csv'%n),encoding='utf-8')))
def num(v):
    if v in (None,''): return None
    try: return float(v)
    except: return None
def ii(v):
    f=num(v); return int(f) if f is not None else None
def yn(v): return 1 if str(v).lower()=='true' else 0
def w(name, rows, cols):
    with open(os.path.join(OUT,name+'.csv'),'w',newline='',encoding='utf-8-sig') as f:
        wr=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore',lineterminator='\n'); wr.writeheader()
        for r in rows: wr.writerow(r)
    print('%-26s %6d' % (name+'.csv', len(rows)))

C={c['id']:c for c in rd('countries')}
cname=lambda x: C.get(x,{}).get('name',x or '')
ccode=lambda x: C.get(x,{}).get('alpha2Code','')
cioc =lambda x: C.get(x,{}).get('iocCode','')
cdem =lambda x: C.get(x,{}).get('demonym',x or '')

circuits={c['id']:c for c in rd('circuits')}
gps={g['id']:g for g in rd('grands-prix')}
races=[r for r in rd('races') if Y0<=int(r['year'])<=Y1]
raceids={ii(r['id']) for r in races}

# =========================== D_Season ===========================
sds=[x for x in rd('seasons-driver-standings') if Y0<=int(x['year'])<=Y1]
scs=[x for x in rd('seasons-constructor-standings') if Y0<=int(x['year'])<=Y1]
drivers_raw={d['id']:d for d in rd('drivers')}
cons_raw={c['id']:c for c in rd('constructors')}
champD={x['year']:x for x in sds if x['positionDisplayOrder']=='1'}
champC={x['year']:x for x in scs if x['positionDisplayOrder']=='1'}
rr=[x for x in rd('races-race-results') if Y0<=int(x['year'])<=Y1]
run_rounds=collections.defaultdict(set)
for x in rr: run_rounds[int(x['year'])].add(int(x['round']))

ERA={ }
for y in range(Y0,Y1+1):
    if y<=2016: e='V6 Hybrid I · 2014-2016'
    elif y<=2021: e='V6 Hybrid II · 2017-2021'
    elif y<=2025: e='Ground Effect · 2022-2025'
    else: e='New Formula · 2026-'
    ERA[y]=e

season_rows=[]
for y in range(Y0,Y1+1):
    ry=[r for r in races if int(r['year'])==y]
    dc=champD.get(str(y)); cc=champC.get(str(y))
    run=len(run_rounds.get(y,set()))
    season_rows.append(dict(
        Year=y, SeasonLabel=str(y), Era=ERA[y], EraOrder={'V6 Hybrid I · 2014-2016':1,'V6 Hybrid II · 2017-2021':2,'Ground Effect · 2022-2025':3,'New Formula · 2026-':4}[ERA[y]],
        RoundsScheduled=len(ry), RoundsRun=run, SeasonComplete=1 if run==len(ry) and run>0 else 0,
        IsCurrentSeason=1 if y==Y1 else 0,
        DriversChampionId=(dc or {}).get('driverId',''),
        DriversChampion=drivers_raw.get((dc or {}).get('driverId',''),{}).get('name','n/a'),
        DriversChampionPoints=num((dc or {}).get('points')) or 0,
        ConstructorsChampionId=(cc or {}).get('constructorId',''),
        ConstructorsChampion=cons_raw.get((cc or {}).get('constructorId',''),{}).get('name','n/a'),
        ConstructorsChampionPoints=num((cc or {}).get('points')) or 0,
        SprintRaces=sum(1 for r in ry if r['sprintQualifyingFormat']),
    ))
w('D_Season',season_rows,list(season_rows[0].keys()))

# =========================== D_Race =============================
NICK={'monza':'The Temple of Speed','silverstone':'The Home of Motor Racing','spa-francorchamps':'The Ardennes Rollercoaster',
 'paul-ricard':'The Blue Stripes','suzuka':'The Figure of Eight','monaco':'The Jewel in the Crown',
 'interlagos':'The Amphitheatre','melbourne':'The Park in the City','catalunya':'The Ultimate Benchmark',
 'montreal':'The Wall of Champions','hungaroring':'Monaco Without the Walls'}
SIGN={'monza':'Parabolica','silverstone':'Maggotts, Becketts, Chapel','spa-francorchamps':'Eau Rouge, Raidillon',
 'paul-ricard':'Signes','suzuka':'130R & the Esses','monaco':'Grand Hotel Hairpin','interlagos':'Senna S',
 'melbourne':'Turns 9 and 10 flat-out','catalunya':'Campsa','montreal':'Wall of Champions','hungaroring':'Turn 4 downhill'}
CLASSIC_ORDER=['monza','silverstone','spa-francorchamps','paul-ricard','suzuka','monaco','interlagos','melbourne','catalunya','montreal','hungaroring']

race_rows=[]
for r in races:
    y=int(r['year']); rnd=int(r['round']); cid=r['circuitId']; c=circuits.get(cid,{})
    gp=gps.get(r['grandPrixId'],{})
    isrun=1 if rnd in run_rounds.get(y,set()) else 0
    race_rows.append(dict(
        RaceKey=ii(r['id']), Year=y, Round=rnd, RaceDate=r['date'],
        GrandPrix=gp.get('name',r['grandPrixId']), GrandPrixShort=gp.get('shortName',''), GrandPrixAbbr=gp.get('abbreviation',''),
        OfficialName=r['officialName'], CircuitId=cid, Circuit=c.get('name',cid), CircuitFullName=c.get('fullName',''),
        CountryId=c.get('countryId',''), Country=cname(c.get('countryId','')), CountryCode=ccode(c.get('countryId','')),
        Laps=ii(r['laps']), DistanceKm=num(r['distance']), CourseLengthKm=num(r['courseLength']), Turns=ii(r['turns']),
        CircuitType=(c.get('type') or '').replace('_',' ').title(), Direction=(r['direction'] or '').title(),
        HasSprint=1 if r['sprintQualifyingFormat'] else 0, IsRun=isrun,
        IsClassicCircuit=1 if cid in CLASSIC_ORDER else 0,
        RaceLabel='%s · %s'%(y, gp.get('shortName') or gp.get('name')),
        RoundLabel='R%02d'%rnd, SortKey=y*100+rnd,
        TitleDecider=yn(r['driversChampionshipDecider']),
    ))
w('D_Race',race_rows,list(race_rows[0].keys()))
RACE={r['RaceKey']:r for r in race_rows}

# =========================== D_Circuit ==========================
era_cids=sorted(set(r['CircuitId'] for r in race_rows))
held=collections.Counter(r['CircuitId'] for r in race_rows if r['IsRun'])
firstgp={}
for r in sorted(rd('races'),key=lambda x:(int(x['year']),int(x['round']))):
    firstgp.setdefault(r['circuitId'], int(r['year']))
circ_rows=[]
for cid in sorted(era_cids):
    c=circuits[cid]
    circ_rows.append(dict(
        CircuitId=cid, Circuit=c['name'], CircuitFullName=c['fullName'], Place=c['placeName'],
        CountryId=c['countryId'], Country=cname(c['countryId']), CountryCode=ccode(c['countryId']), IOC=cioc(c['countryId']),
        Latitude=num(c['latitude']), Longitude=num(c['longitude']),
        LengthKm=num(c['length']), Turns=ii(c['turns']),
        CircuitType=(c['type'] or '').replace('_',' ').title(), Direction=(c['direction'] or '').title(),
        RacesHeldAllTime=ii(c['totalRacesHeld']), RacesInEra=held.get(cid,0),
        FirstGrandPrix=firstgp.get(cid),
        IsClassic=1 if cid in CLASSIC_ORDER else 0,
        ClassicRank=(CLASSIC_ORDER.index(cid)+1) if cid in CLASSIC_ORDER else 99,
        Nickname=NICK.get(cid,''), SignatureCorner=SIGN.get(cid,''),
    ))
w('D_Circuit',circ_rows,list(circ_rows[0].keys()))

# =========================== D_Driver ===========================
did_era=set(x['driverId'] for x in rr)
drv_rows=[]
for did in sorted(did_era):
    d=drivers_raw[did]
    nat=d['nationalityCountryId']
    drv_rows.append(dict(
        DriverId=did, Driver=d['name'], FirstName=d['firstName'], LastName=d['lastName'],
        Abbr=d['abbreviation'] or (d['lastName'][:3].upper()),
        Number=ii(d['permanentNumber']),
        NationalityId=nat, Nationality=cdem(nat), NationCountry=cname(nat), NationCode=ccode(nat),
        DateOfBirth=d['dateOfBirth'],
        CareerWins=ii(d['totalRaceWins']) or 0, CareerPodiums=ii(d['totalPodiums']) or 0,
        CareerPoles=ii(d['totalPolePositions']) or 0, CareerTitles=ii(d['totalChampionshipWins']) or 0,
        CareerStarts=ii(d['totalRaceStarts']) or 0,
    ))
w('D_Driver',drv_rows,list(drv_rows[0].keys()))

# ======================= D_Constructor ==========================
TEAMCOL={'mercedes':'#00D2BE','red-bull':'#3671C6','ferrari':'#E8002D','mclaren':'#FF8000','alpine':'#0093CC',
 'aston-martin':'#229971','williams':'#1868DB','racing-bulls':'#6C98FF','rb':'#6C98FF','alphatauri':'#4E7C9B',
 'toro-rosso':'#2B4562','kick-sauber':'#52E252','sauber':'#9B0000','alfa-romeo':'#C92D4B','haas':'#B6BABD',
 'racing-point':'#F596C8','force-india':'#F596C8','renault':'#FFF500','lotus-f1':'#E6C229','manor':'#D40000',
 'marussia':'#B0000A','caterham':'#0B572E','audi':'#BB0A30','cadillac':'#C9B037'}
cid_era=set(x['constructorId'] for x in rr)
con_rows=[]
for cid in sorted(cid_era):
    c=cons_raw[cid]
    yrs=sorted(set(int(x['year']) for x in rr if x['constructorId']==cid))
    con_rows.append(dict(
        ConstructorId=cid, Team=c['name'], TeamFullName=c['fullName'],
        CountryId=c['countryId'], Country=cname(c['countryId']), CountryCode=ccode(c['countryId']),
        TeamColour=TEAMCOL.get(cid,'#8A8F98'),
        FirstYearInEra=yrs[0], LastYearInEra=yrs[-1], SeasonsInEra=len(yrs),
        StillRacing=1 if yrs[-1]==Y1 else 0,
        CareerWins=ii(c['totalRaceWins']) or 0, CareerTitles=ii(c['totalChampionshipWins']) or 0,
        CareerPodiums=ii(c['totalPodiums']) or 0, CareerPoles=ii(c['totalPolePositions']) or 0,
    ))
w('D_Constructor',con_rows,list(con_rows[0].keys()))

# ========================= D_Engine =============================
eng={e['id']:e for e in rd('engine-manufacturers')} if os.path.exists(os.path.join(RAW,'f1db-engine-manufacturers.csv')) else {}
eid_era=sorted(set(x['engineManufacturerId'] for x in rr))
eng_rows=[dict(EngineId=e, Engine=eng.get(e,{}).get('name',e.replace('-',' ').title()),
               EngineCountry=cname(eng.get(e,{}).get('countryId',''))) for e in eid_era]
w('D_Engine',eng_rows,list(eng_rows[0].keys()))

# ========================== F_Result ============================
pits=collections.defaultdict(list)
for p in rd('races-pit-stops'):
    k=ii(p['raceId'])
    if k in raceids: pits[(k,p['driverId'])].append(num(p['timeMillis']) or 0)
dotd={(ii(x['raceId']),x['driverId']) for x in rd('races-driver-of-the-day-results') if x['positionDisplayOrder']=='1'}
res_rows=[]
for x in rr:
    k=ii(x['raceId']); pos=ii(x['positionNumber']); grid=ii(x['gridPositionNumber'])
    st=pits.get((k,x['driverId']),[])
    fin = 1 if pos is not None else 0
    res_rows.append(dict(
        RaceKey=k, Year=int(x['year']), Round=int(x['round']), DriverId=x['driverId'],
        ConstructorId=x['constructorId'], EngineId=x['engineManufacturerId'],
        Position=pos, PositionText=x['positionText'], Points=num(x['points']) or 0,
        GridPosition=grid, QualiPosition=ii(x['qualificationPositionNumber']),
        LapsCompleted=ii(x['laps']) or 0, PositionsGained=ii(x['positionsGained']),
        IsWin=1 if pos==1 else 0, IsPodium=1 if pos and pos<=3 else 0,
        IsPoints=1 if (num(x['points']) or 0)>0 else 0, IsFinished=fin,
        IsPole=yn(x['polePosition']), IsFastestLap=yn(x['fastestLap']), IsGrandSlam=yn(x['grandSlam']),
        IsDriverOfTheDay=1 if (k,x['driverId']) in dotd else 0,
        IsDNF=0 if fin else 1, RetirementReason=x['reasonRetired'] or '',
        RaceTimeMillis=num(x['timeMillis']), GapMillis=num(x['gapMillis']),
        PitStops=len(st), BestPitStopMs=(min(st) if st else None), TotalPitMs=(sum(st) if st else None),
        StartedFromPole=1 if grid==1 else 0,
        WinFromPole=1 if (grid==1 and pos==1) else 0,
    ))
w('F_Result',res_rows,list(res_rows[0].keys()))

# ======================== F_Qualifying ==========================
q_rows=[]
for x in rd('races-qualifying-results'):
    k=ii(x['raceId'])
    if k not in raceids: continue
    best=num(x['timeMillis']) or num(x['q3Millis']) or num(x['q2Millis']) or num(x['q1Millis'])
    q_rows.append(dict(RaceKey=k, Year=int(x['year']), DriverId=x['driverId'], ConstructorId=x['constructorId'],
        QualiPosition=ii(x['positionNumber']), BestQualiMs=best,
        Q1Ms=num(x['q1Millis']), Q2Ms=num(x['q2Millis']), Q3Ms=num(x['q3Millis']),
        GapToPoleMs=num(x['gapMillis']), ReachedQ3=1 if num(x['q3Millis']) else 0))
w('F_Qualifying',q_rows,list(q_rows[0].keys()))

# ======================= F_FastestLap ===========================
fl_rows=[]
for x in rd('races-fastest-laps'):
    k=ii(x['raceId'])
    if k not in raceids: continue
    fl_rows.append(dict(RaceKey=k, Year=int(x['year']), DriverId=x['driverId'], ConstructorId=x['constructorId'],
        FLRank=ii(x['positionNumber']), LapNumber=ii(x['lap']), LapTimeMs=num(x['timeMillis']), LapTime=x['time']))
w('F_FastestLap',fl_rows,list(fl_rows[0].keys()))

# ===================== F_DriverStanding =========================
ds_rows=[]
for x in rd('races-driver-standings'):
    k=ii(x['raceId'])
    if k not in raceids: continue
    ds_rows.append(dict(RaceKey=k, Year=int(x['year']), Round=int(x['round']), DriverId=x['driverId'],
        StandingPoints=num(x['points']) or 0, StandingPosition=ii(x['positionNumber']),
        ChampionshipWon=yn(x['championshipWon'])))
w('F_DriverStanding',ds_rows,list(ds_rows[0].keys()))

cs_rows=[]
for x in rd('races-constructor-standings'):
    k=ii(x['raceId'])
    if k not in raceids: continue
    cs_rows.append(dict(RaceKey=k, Year=int(x['year']), Round=int(x['round']), ConstructorId=x['constructorId'],
        StandingPoints=num(x['points']) or 0, StandingPosition=ii(x['positionNumber']),
        ChampionshipWon=yn(x['championshipWon'])))
w('F_ConstructorStanding',cs_rows,list(cs_rows[0].keys()))


# ======================== F_Sprint ==============================
sp_rows=[]
for x in rd('races-sprint-race-results'):
    k=ii(x['raceId'])
    if k not in raceids: continue
    pos=ii(x['positionNumber'])
    sp_rows.append(dict(RaceKey=k, Year=int(x['year']), DriverId=x['driverId'], ConstructorId=x['constructorId'],
        SprintPosition=pos, SprintPoints=num(x['points']) or 0, SprintGrid=ii(x['gridPositionNumber']),
        IsSprintWin=1 if pos==1 else 0, IsSprintPodium=1 if pos and pos<=3 else 0))
w('F_Sprint',sp_rows,list(sp_rows[0].keys()))

# ---- flag the last round actually run in each season ----
import csv as _c
for tbl,key in (('F_DriverStanding','DriverId'),('F_ConstructorStanding','ConstructorId')):
    rows=list(_c.DictReader(open(os.path.join(OUT,tbl+'.csv'),encoding='utf-8-sig')))
    last={}
    for r in rows: last[r['Year']]=max(last.get(r['Year'],0),int(r['Round']))
    for r in rows: r['IsLatestRound']=1 if int(r['Round'])==last[r['Year']] else 0
    w(tbl,rows,list(rows[0].keys()))

# ======================== F_TrackPoint ==========================
geo=json.load(open(GEO,encoding='utf-8'))
GEOMAP={'melbourne':'au-1953','catalunya':'es-1991','monaco':'mc-1929','montreal':'ca-1978','paul-ricard':'fr-1969',
 'silverstone':'gb-1948','hungaroring':'hu-1986','spa-francorchamps':'be-1925','monza':'it-1922','suzuka':'jp-1962',
 'interlagos':'br-1940','bahrain':'bh-2002','shanghai':'cn-2004','spielberg':'at-1969','hockenheimring':'de-1932',
 'marina-bay':'sg-2008','sochi':'ru-2014','austin':'us-2012','mexico-city':'mx-1962','yas-marina':'ae-2009',
 'imola':'it-1953','nurburgring':'de-1927','portimao':'pt-2008','mugello':'it-1914','sepang':'my-1999',
 'istanbul':'tr-2005','zandvoort':'nl-1948','jeddah':'sa-2021','miami':'us-2022','lusail':'qa-2004',
 'madring':'es-2026','baku':'az-2016','las-vegas':'us-2023','indianapolis':'us-1909'}
feat={f['properties']['id']:f for f in geo['features']}
tp_rows=[]; got=[]
for cid in sorted(era_cids):
    gid=GEOMAP.get(cid)
    if not gid or gid not in feat: continue
    coords=feat[gid]['geometry']['coordinates']
    if coords and isinstance(coords[0][0],list): coords=coords[0]
    lat0=sum(c[1] for c in coords)/len(coords)
    k=math.cos(math.radians(lat0))
    xs=[c[0]*k for c in coords]; ys=[c[1] for c in coords]
    cx=(max(xs)+min(xs))/2; cy=(max(ys)+min(ys))/2
    span=max(max(xs)-min(xs), max(ys)-min(ys)) or 1e-9
    s=180.0/span
    for n,(x,y) in enumerate(zip(xs,ys)):
        tp_rows.append(dict(CircuitId=cid, PointOrder=n,
            X=round((x-cx)*s,3), Y=round((y-cy)*s,3),
            Longitude=round(coords[n][0],6), Latitude=round(coords[n][1],6)))
    # close the loop
    tp_rows.append(dict(CircuitId=cid, PointOrder=len(xs),
        X=round((xs[0]-cx)*s,3), Y=round((ys[0]-cy)*s,3),
        Longitude=round(coords[0][0],6), Latitude=round(coords[0][1],6)))
    got.append(cid)
w('F_TrackPoint',tp_rows,list(tp_rows[0].keys()))
print('track outlines:',len(got),'/',len(era_cids),'missing:',sorted(set(era_cids)-set(got)))

# ============ disconnected tables driving report interactivity ===============
metrics=[('Points','Championship points',1),('Wins','Race wins',2),('Podiums','Podium finishes',3),
 ('Poles','Pole positions',4),('Fastest laps','Fastest race laps',5),('Avg finish','Average finishing position',6),
 ('DNFs','Retirements',7)]
w('D_Metric',[dict(Metric=m,MetricDesc=d,MetricOrder=o) for m,d,o in metrics],['Metric','MetricDesc','MetricOrder'])
scopes=[('All circuits','Every Grand Prix in the era',1),('Classic eleven','Only the eleven heritage circuits',2)]
w('D_Scope',[dict(Scope=s,ScopeDesc=d,ScopeOrder=o) for s,d,o in scopes],['Scope','ScopeDesc','ScopeOrder'])
