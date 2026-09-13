# -*- coding: utf-8 -*-
"""Generate the Power BI semantic model (TMDL) for the APEX project.

Writes one <table>.tmdl per CSV in DATA_DIR plus relationships, expressions,
database and model files under DIST_DIR/<NAME>.SemanticModel/definition, and the
.pbip / .platform / definition.pbism project files next to it.
"""
import csv, os, uuid, json, shutil
from apex.config import DIST_DIR, NAME, DATA_DIR, DEFAULT_DATA_FOLDER, ensure_dirs
ensure_dirs()
ROOT=str(DIST_DIR)
SM=os.path.join(ROOT,NAME+'.SemanticModel')
DEF=os.path.join(SM,'definition'); TBL=os.path.join(DEF,'tables')
DATA=str(DATA_DIR)
for p in (TBL,): os.makedirs(p,exist_ok=True)
import itertools as _it
_seq=_it.count()
G=lambda: str(uuid.uuid5(uuid.NAMESPACE_URL,'apex-f1/lineage/%s/%d'%(__name__,next(_seq))))

INT='int64'; DBL='double'; STR='string'; DT='dateTime'; BOOL='int64'
# type, summarizeBy, hidden, formatString, dataCategory, displayFolder, description
S={
'D_Season':[('Year',INT,'none',0,'0'),('SeasonLabel',STR,'none',0,None),('Era',STR,'none',0,None),
  ('EraOrder',INT,'none',1,'0'),('RoundsScheduled',INT,'none',0,'0'),('RoundsRun',INT,'none',0,'0'),
  ('SeasonComplete',INT,'none',1,'0'),('IsCurrentSeason',INT,'none',1,'0'),('DriversChampionId',STR,'none',1,None),
  ('DriversChampion',STR,'none',0,None),('DriversChampionPoints',DBL,'none',0,'#,0'),
  ('ConstructorsChampionId',STR,'none',1,None),('ConstructorsChampion',STR,'none',0,None),
  ('ConstructorsChampionPoints',DBL,'none',0,'#,0'),('SprintRaces',INT,'none',0,'0')],
'D_Race':[('RaceKey',INT,'none',1,'0'),('Year',INT,'none',0,'0'),('Round',INT,'none',0,'0'),
  ('RaceDate',DT,'none',0,None),('GrandPrix',STR,'none',0,None),('GrandPrixShort',STR,'none',0,None),
  ('GrandPrixAbbr',STR,'none',1,None),('OfficialName',STR,'none',0,None),('CircuitId',STR,'none',1,None),
  ('Circuit',STR,'none',0,None),('CircuitFullName',STR,'none',0,None),('CountryId',STR,'none',1,None),
  ('Country',STR,'none',0,None),('CountryCode',STR,'none',1,None),('Laps',INT,'none',0,'0'),
  ('DistanceKm',DBL,'none',0,'#,0.0'),('CourseLengthKm',DBL,'none',0,'0.000'),('Turns',INT,'none',0,'0'),
  ('CircuitType',STR,'none',0,None),('Direction',STR,'none',0,None),('HasSprint',INT,'none',0,'0'),
  ('IsRun',INT,'none',0,'0'),('IsClassicCircuit',INT,'none',0,'0'),('RaceLabel',STR,'none',0,None),
  ('RoundLabel',STR,'none',0,None),('SortKey',INT,'none',1,'0'),('TitleDecider',INT,'none',0,'0')],
'D_Circuit':[('CircuitId',STR,'none',1,None),('Circuit',STR,'none',0,None),('CircuitFullName',STR,'none',0,None),
  ('Place',STR,'none',0,None,'City'),('CountryId',STR,'none',1,None),('Country',STR,'none',0,None,'Country'),
  ('CountryCode',STR,'none',1,None),('IOC',STR,'none',1,None),('Latitude',DBL,'none',0,'0.0000','Latitude'),
  ('Longitude',DBL,'none',0,'0.0000','Longitude'),('LengthKm',DBL,'none',0,'0.000'),('Turns',INT,'none',0,'0'),
  ('CircuitType',STR,'none',0,None),('Direction',STR,'none',0,None),('RacesHeldAllTime',INT,'none',0,'0'),
  ('RacesInEra',INT,'none',0,'0'),('FirstGrandPrix',INT,'none',0,'0'),('IsClassic',INT,'none',0,'0'),
  ('ClassicRank',INT,'none',1,'0'),('Nickname',STR,'none',0,None),('SignatureCorner',STR,'none',0,None),
  ('TrackSvg',STR,'none',0,None,'ImageUrl'),('TrackSvgLarge',STR,'none',0,None,'ImageUrl'),
  ('FlagSvg',STR,'none',0,None,'ImageUrl'),('CircuitDisplay',STR,'none',0,None)],
'D_Driver':[('DriverId',STR,'none',1,None),('Driver',STR,'none',0,None),('FirstName',STR,'none',1,None),
  ('LastName',STR,'none',0,None),('Abbr',STR,'none',0,None),('Number',INT,'none',0,'0'),
  ('NationalityId',STR,'none',1,None),('Nationality',STR,'none',0,None),('NationCountry',STR,'none',0,None),
  ('NationCode',STR,'none',1,None),('DateOfBirth',DT,'none',0,None),('CareerWins',INT,'sum',0,'#,0'),
  ('CareerPodiums',INT,'sum',0,'#,0'),('CareerPoles',INT,'sum',0,'#,0'),('CareerTitles',INT,'sum',0,'0'),
  ('CareerStarts',INT,'sum',0,'#,0'),('FlagSvg',STR,'none',0,None,'ImageUrl'),
  ('HelmetSvg',STR,'none',0,None,'ImageUrl')],
'D_Constructor':[('ConstructorId',STR,'none',1,None),('Team',STR,'none',0,None),('TeamFullName',STR,'none',0,None),
  ('CountryId',STR,'none',1,None),('Country',STR,'none',0,None),('CountryCode',STR,'none',1,None),
  ('TeamColour',STR,'none',0,None),('FirstYearInEra',INT,'none',0,'0'),('LastYearInEra',INT,'none',0,'0'),
  ('SeasonsInEra',INT,'none',0,'0'),('StillRacing',INT,'none',0,'0'),('CareerWins',INT,'sum',0,'#,0'),
  ('CareerTitles',INT,'sum',0,'0'),('CareerPodiums',INT,'sum',0,'#,0'),('CareerPoles',INT,'sum',0,'#,0'),
  ('TeamBadge',STR,'none',0,None,'ImageUrl'),('FlagSvg',STR,'none',0,None,'ImageUrl'),
  ('CarSvg',STR,'none',0,None,'ImageUrl')],
'D_Engine':[('EngineId',STR,'none',1,None),('Engine',STR,'none',0,None),('EngineCountry',STR,'none',0,None)],
'D_Metric':[('Metric',STR,'none',0,None),('MetricDesc',STR,'none',0,None),('MetricOrder',INT,'none',1,'0')],
'D_Scope':[('Scope',STR,'none',0,None),('ScopeDesc',STR,'none',0,None),('ScopeOrder',INT,'none',1,'0')],
'F_Result':[('RaceKey',INT,'none',1,'0'),('Year',INT,'none',1,'0'),('Round',INT,'none',1,'0'),
  ('DriverId',STR,'none',1,None),('ConstructorId',STR,'none',1,None),('EngineId',STR,'none',1,None),
  ('Position',INT,'none',0,'0'),('PositionText',STR,'none',0,None),('Points',DBL,'sum',0,'#,0.##'),
  ('GridPosition',INT,'none',0,'0'),('QualiPosition',INT,'none',0,'0'),('LapsCompleted',INT,'sum',0,'#,0'),
  ('PositionsGained',INT,'none',0,'+0;-0;0'),('IsWin',INT,'none',1,'0'),('IsPodium',INT,'none',1,'0'),
  ('IsPoints',INT,'none',1,'0'),('IsFinished',INT,'none',1,'0'),('IsPole',INT,'none',1,'0'),
  ('IsFastestLap',INT,'none',1,'0'),('IsGrandSlam',INT,'none',1,'0'),('IsDriverOfTheDay',INT,'none',1,'0'),
  ('IsDNF',INT,'none',1,'0'),('RetirementReason',STR,'none',0,None),('RaceTimeMillis',DBL,'none',1,'0'),
  ('GapMillis',DBL,'none',1,'0'),('PitStops',INT,'sum',0,'0'),('BestPitStopMs',DBL,'none',1,'0'),
  ('TotalPitMs',DBL,'none',1,'0'),('StartedFromPole',INT,'none',1,'0'),('WinFromPole',INT,'none',1,'0')],
'F_Qualifying':[('RaceKey',INT,'none',1,'0'),('Year',INT,'none',1,'0'),('DriverId',STR,'none',1,None),
  ('ConstructorId',STR,'none',1,None),('QualiPosition',INT,'none',0,'0'),('BestQualiMs',DBL,'none',1,'0'),
  ('Q1Ms',DBL,'none',1,'0'),('Q2Ms',DBL,'none',1,'0'),('Q3Ms',DBL,'none',1,'0'),
  ('GapToPoleMs',DBL,'none',1,'0'),('ReachedQ3',INT,'none',1,'0')],
'F_FastestLap':[('RaceKey',INT,'none',1,'0'),('Year',INT,'none',1,'0'),('DriverId',STR,'none',1,None),
  ('ConstructorId',STR,'none',1,None),('FLRank',INT,'none',0,'0'),('LapNumber',INT,'none',0,'0'),
  ('LapTimeMs',DBL,'none',1,'0'),('LapTime',STR,'none',0,None)],
'F_DriverStanding':[('RaceKey',INT,'none',1,'0'),('Year',INT,'none',1,'0'),('Round',INT,'none',1,'0'),
  ('DriverId',STR,'none',1,None),('StandingPoints',DBL,'none',0,'#,0.##'),('StandingPosition',INT,'none',0,'0'),
  ('ChampionshipWon',INT,'none',1,'0'),('IsLatestRound',INT,'none',1,'0')],
'F_ConstructorStanding':[('RaceKey',INT,'none',1,'0'),('Year',INT,'none',1,'0'),('Round',INT,'none',1,'0'),
  ('ConstructorId',STR,'none',1,None),('StandingPoints',DBL,'none',0,'#,0.##'),('StandingPosition',INT,'none',0,'0'),
  ('ChampionshipWon',INT,'none',1,'0'),('IsLatestRound',INT,'none',1,'0')],
'F_Sprint':[('RaceKey',INT,'none',1,'0'),('Year',INT,'none',1,'0'),('DriverId',STR,'none',1,None),
  ('ConstructorId',STR,'none',1,None),('SprintPosition',INT,'none',0,'0'),('SprintPoints',DBL,'sum',0,'#,0.##'),
  ('SprintGrid',INT,'none',0,'0'),('IsSprintWin',INT,'none',1,'0'),('IsSprintPodium',INT,'none',1,'0')],
'F_TrackPoint':[('CircuitId',STR,'none',1,None),('PointOrder',INT,'none',0,'0'),('X',DBL,'none',0,'0.0'),
  ('Y',DBL,'none',0,'0.0'),('Longitude',DBL,'none',0,'0.0000'),('Latitude',DBL,'none',0,'0.0000')],
}
MTYPE={INT:'Int64.Type',DBL:'type number',STR:'type text',DT:'type date'}

RENAME={'D_Season':{'DriversChampion':'Champion','ConstructorsChampion':'Constructor champion'}}
def q(n): return "'%s'"%n if (' ' in n or '(' in n) else n
def table_tmdl(t, spec, sort_by=None, hide_table=False, extra_measures=''):
    L=[]
    L.append('table %s'%t)
    L.append('\tlineageTag: %s'%G())
    if hide_table: L.append('\tisHidden')
    L.append('')
    if extra_measures: L.append(extra_measures)
    for c in spec:
        name,typ,summ,hidden,fmt = c[0],c[1],c[2],c[3],c[4]
        cat = c[5] if len(c)>5 else None
        disp=RENAME.get(t,{}).get(name,name)
        L.append('\tcolumn %s'%q(disp))
        L.append('\t\tdataType: %s'%typ)
        if typ==DT: L.append('\t\tformatString: yyyy-mm-dd')
        elif fmt: L.append('\t\tformatString: %s'%fmt)
        if hidden: L.append('\t\tisHidden')
        L.append('\t\tlineageTag: %s'%G())
        if cat: L.append('\t\tdataCategory: %s'%cat)
        L.append('\t\tsummarizeBy: %s'%summ)
        L.append('\t\tsourceColumn: %s'%name)
        if sort_by and name in sort_by: L.append('\t\tsortByColumn: %s'%q(RENAME.get(t,{}).get(sort_by[name],sort_by[name])))
        L.append('')
        L.append('\t\tannotation SummarizationSetBy = Automatic')
        L.append('')
    types=', '.join('{"%s", %s}'%(c[0],MTYPE[c[1]]) for c in spec)
    L.append('\tpartition %s = m'%t)
    L.append('\t\tmode: import')
    L.append('\t\tsource =')
    L.append('\t\t\t\tlet')
    L.append('\t\t\t\t    Source = Csv.Document(File.Contents(DataFolder & "\\%s.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),'%t)
    L.append('\t\t\t\t    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),')
    L.append('\t\t\t\t    Types = Table.TransformColumnTypes(Headers, {%s}, "en-US")'%types)
    L.append('\t\t\t\tin')
    L.append('\t\t\t\t    Types')
    L.append('')
    L.append('\tannotation PBI_ResultType = Table')
    L.append('')
    return '\n'.join(L)

SORTBY={'D_Season':{'Era':'EraOrder'},'D_Metric':{'Metric':'MetricOrder'},'D_Scope':{'Scope':'ScopeOrder'},
        'D_Race':{'RaceLabel':'SortKey'},'D_Circuit':{}}
for t,spec in S.items():
    open(os.path.join(TBL,t+'.tmdl'),'w',encoding='utf-8').write(table_tmdl(t,spec,SORTBY.get(t)))
print('tables:',len(S))

# ================= model-level files =================
import uuid as _u
def guid5(s):
    return str(_u.uuid5(_u.NAMESPACE_URL,'apex-f1/'+s))

TABLES=['D_Season','D_Race','D_Circuit','D_Driver','D_Constructor','D_Engine','D_Metric','D_Scope',
        'F_Result','F_Qualifying','F_FastestLap','F_DriverStanding','F_ConstructorStanding','F_Sprint',
        'F_TrackPoint','Metrics']
REL=[('F_Result','RaceKey','D_Race','RaceKey'),
     ('F_Result','DriverId','D_Driver','DriverId'),
     ('F_Result','ConstructorId','D_Constructor','ConstructorId'),
     ('F_Result','EngineId','D_Engine','EngineId'),
     ('F_Qualifying','RaceKey','D_Race','RaceKey'),
     ('F_Qualifying','DriverId','D_Driver','DriverId'),
     ('F_Qualifying','ConstructorId','D_Constructor','ConstructorId'),
     ('F_FastestLap','RaceKey','D_Race','RaceKey'),
     ('F_FastestLap','DriverId','D_Driver','DriverId'),
     ('F_FastestLap','ConstructorId','D_Constructor','ConstructorId'),
     ('F_DriverStanding','RaceKey','D_Race','RaceKey'),
     ('F_DriverStanding','DriverId','D_Driver','DriverId'),
     ('F_ConstructorStanding','RaceKey','D_Race','RaceKey'),
     ('F_ConstructorStanding','ConstructorId','D_Constructor','ConstructorId'),
     ('F_Sprint','RaceKey','D_Race','RaceKey'),
     ('F_Sprint','DriverId','D_Driver','DriverId'),
     ('F_Sprint','ConstructorId','D_Constructor','ConstructorId'),
     ('D_Race','CircuitId','D_Circuit','CircuitId'),
     ('D_Race','Year','D_Season','Year'),
     ('F_TrackPoint','CircuitId','D_Circuit','CircuitId')]
r=[]
for a,ac,b,bc in REL:
    r.append('relationship %s'%guid5('rel/%s.%s->%s.%s'%(a,ac,b,bc)))
    r.append('\tfromColumn: %s.%s'%(a,ac))
    r.append('\ttoColumn: %s.%s'%(b,bc))
    r.append('')
open(os.path.join(DEF,'relationships.tmdl'),'w',encoding='utf-8').write('\n'.join(r))

open(os.path.join(DEF,'database.tmdl'),'w',encoding='utf-8').write('database\n\tcompatibilityLevel: 1606\n\n')

DEFAULT_PATH=DEFAULT_DATA_FOLDER
expr=('/// Folder holding the CSV files that feed the model. Change this parameter if you move the project.\n'
 'expression DataFolder = "%s" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n'
 '\tlineageTag: %s\n\n\tannotation PBI_ResultType = Text\n\n')%(DEFAULT_PATH,guid5('expr/DataFolder'))
open(os.path.join(DEF,'expressions.tmdl'),'w',encoding='utf-8').write(expr)

order=json.dumps([t for t in TABLES if t!='Metrics']+['DataFolder'])
mdl=['model Model','\tculture: en-US','\tdefaultPowerBIDataSourceVersion: powerBI_V3',
     '\tdiscourageImplicitMeasures','\tsourceQueryCulture: en-US','\tdataAccessOptions',
     '\t\tlegacyRedirects','\t\treturnErrorValuesAsNull','',
     'annotation PBI_QueryOrder = %s'%order,'','annotation PBI_ProTooling = ["DevMode"]','']
for t in TABLES: mdl.append('ref table %s'%t)
mdl.append('')
open(os.path.join(DEF,'model.tmdl'),'w',encoding='utf-8').write('\n'.join(mdl))

json.dump({"$schema":"https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
           "version":"4.2","settings":{}}, open(os.path.join(SM,'definition.pbism'),'w',encoding='utf-8'), indent=2)
json.dump({"$schema":"https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
           "metadata":{"type":"SemanticModel","displayName":NAME},
           "config":{"version":"2.0","logicalId":guid5('platform/semanticmodel')}},
          open(os.path.join(SM,'.platform'),'w',encoding='utf-8'), indent=2)
json.dump({"$schema":"https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
           "version":"1.0","artifacts":[{"report":{"path":NAME+".Report"}}],
           "settings":{"enableAutoRecovery":True}},
          open(os.path.join(ROOT,NAME+'.pbip'),'w',encoding='utf-8'), indent=2)
print('model written:', ROOT)
