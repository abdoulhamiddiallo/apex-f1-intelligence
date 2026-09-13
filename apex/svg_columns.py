# -*- coding: utf-8 -*-
"""Add inline SVG image columns to the dimension CSVs in DATA_DIR.

Enriches D_Circuit (track outline, flag), D_Driver (flag, helmet) and D_Constructor
(team badge, car, flag) with data-URI columns and rewrites the CSV files in place.
"""
import csv, os, collections
from apex.flags import flag_uri
from apex.cars import car, helmet, crest
from apex.livery import livery, helmet_style, country_bars
from apex.config import DATA_DIR, LOGO_DIR
D=str(DATA_DIR)
def rd(n): return list(csv.DictReader(open(os.path.join(D,n+'.csv'),encoding='utf-8-sig')))
def wr(n,rows,cols):
    with open(os.path.join(D,n+'.csv'),'w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore',lineterminator='\n'); w.writeheader()
        for r in rows: w.writerow(r)
    print('%-24s %5d  (%d col.)'%(n+'.csv',len(rows),len(cols)))


# ---------- user-supplied logos ----------
# If an image file exists in the Logos folder, it REPLACES the drawn crest.
# Expected name: <ConstructorId>.png / .jpg / .svg  (e.g. ferrari.png, red-bull.png)
import base64, glob as _glob
LOGOS = str(LOGO_DIR)
_MIME = {'.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg',
         '.gif':'image/gif','.webp':'image/webp','.svg':'image/svg+xml'}
def user_logo(cid):
    for p in sorted(_glob.glob(os.path.join(LOGOS, cid + '.*'))):
        ext = os.path.splitext(p)[1].lower()
        if ext not in _MIME: continue
        b = open(p,'rb').read()
        if len(b) > 220000:      # beyond this, Power BI gets sluggish on an image column
            print('  ! %s skipped (%d KB, limit 220 KB)'%(os.path.basename(p), len(b)//1024)); continue
        return 'data:%s;base64,%s'%(_MIME[ext], base64.b64encode(b).decode())
    return None

INK='%23E9EDF5'; RED='%23E8323C'; DIM='%23394050'

# ---------- track outlines ----------
pts=collections.defaultdict(list)
for r in rd('F_TrackPoint'):
    pts[r['CircuitId']].append((int(r['PointOrder']),float(r['X']),float(r['Y'])))
def track_svg(cid,stroke=INK,accent=RED,w=190,h=190,sw=9,box=210):
    p=sorted(pts[cid])
    d='M'+' L'.join('%.1f %.1f'%(x,-y) for _,x,y in p)+' Z'
    x0,y0=p[0][1],-p[0][2]; x1,y1=p[1][1],-p[1][2]
    import math
    ang=math.degrees(math.atan2(y1-y0,x1-x0))
    half=box/2
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='%d %d %d %d' width='%d' height='%d'>"
            "<path d='%s' fill='none' stroke='%s' stroke-width='%.1f' stroke-linejoin='round' stroke-linecap='round' opacity='0.30'/>"
            "<path d='%s' fill='none' stroke='%s' stroke-width='%.1f' stroke-linejoin='round' stroke-linecap='round'/>"
            "<g transform='translate(%.1f %.1f) rotate(%.1f)'><rect x='-1.6' y='-11' width='3.2' height='22' fill='%s'/></g>"
            "</svg>")%(-half,-half,box,box,w,h,d,DIM,sw*2.1,d,stroke,sw,x0,y0,ang,accent)
def uri(s): return 'data:image/svg+xml;utf8,'+s

# ---------- team badges ----------
ABBR={'mercedes':'MER','red-bull':'RBR','ferrari':'FER','mclaren':'MCL','alpine':'ALP','aston-martin':'AMR',
 'williams':'WIL','racing-bulls':'RB','rb':'RB','alphatauri':'AT','toro-rosso':'STR','kick-sauber':'SAU',
 'sauber':'SAU','alfa-romeo':'ALF','haas':'HAA','racing-point':'RP','force-india':'FI','renault':'REN',
 'lotus-f1':'LOT','manor':'MNR','marussia':'MRU','caterham':'CAT','audi':'AUD','cadillac':'CAD'}

# ---------- D_Circuit ----------
cir=rd('D_Circuit')
for r in cir:
    r['TrackSvg']=uri(track_svg(r['CircuitId']))
    r['TrackSvgLarge']=uri(track_svg(r['CircuitId'],w=420,h=420,sw=7,box=215))
    r['FlagSvg']=flag_uri(r['Country'])
    r['CircuitDisplay']='%s · %s'%(r['Circuit'],r['Country'])
wr('D_Circuit',cir,list(cir[0].keys()))

# ---------- D_Driver ----------
drv=rd('D_Driver')
import collections as _c, csv as _csv, os as _os
_res=list(_csv.DictReader(open(_os.path.join(D,'F_Result.csv'),encoding='utf-8-sig')))
_col={c['ConstructorId']:c['TeamColour'] for c in rd('D_Constructor')}
_dt=_c.defaultdict(_c.Counter)
for x in _res: _dt[x['DriverId']][x['ConstructorId']]+=1
for r in drv:
    r['FlagSvg']=flag_uri(r['NationCountry'])
    _team=_dt[r['DriverId']].most_common(1)[0][0] if _dt[r['DriverId']] else None
    _p,_a,_pat=livery(_team) if _team else ('#8A8F98','#F2F5FA','edge')
    _hpat,_nat,_hv=helmet_style(r['DriverId'], r['NationCountry'], _p)
    r['HelmetSvg']=helmet(_p, number=(r['Number'] or None), accent=_nat,
                          pattern=_hpat, abbr=ABBR.get(_team,'') or None, variant=_hv)
wr('D_Driver',drv,list(drv[0].keys()))

# ---------- D_Constructor ----------
con=rd('D_Constructor')
for r in con:
    _ab=ABBR.get(r['ConstructorId'],r['Team'][:3].upper())
    _p,_a,_pat=livery(r['ConstructorId'], r['TeamColour'])
    _logo=user_logo(r['ConstructorId'])
    r['TeamBadge']=_logo if _logo else crest(_p, accent=_a, pattern=_pat,
                                             bars=country_bars(r['Country']))
    r['CarSvg']=car(_p, _ab, accent=_a, pattern=_pat)
    r['FlagSvg']=flag_uri(r['Country'])
wr('D_Constructor',con,list(con[0].keys()))

print('max len TrackSvgLarge:',max(len(r['TrackSvgLarge']) for r in cir))
print('max len TrackSvg     :',max(len(r['TrackSvg']) for r in cir))

_n=sum(1 for r in con if r['TeamBadge'].startswith('data:image/') and ';base64,' in r['TeamBadge'])
print('user-supplied logos in use: %d / %d'%(_n,len(con)))
