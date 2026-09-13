# -*- coding: utf-8 -*-
"""Builds the nine report pages and writes the PBIR report folder (pages, visuals, theme, resources) into dist."""
import json, os, shutil, sys, uuid
from apex.pbir import *
from apex.config import DIST_DIR, NAME, ASSET_DIR, ensure_dirs
ensure_dirs()
ROOT=str(DIST_DIR)
RP=os.path.join(ROOT,NAME+'.Report'); DEFN=os.path.join(RP,'definition'); PGS=os.path.join(DEFN,'pages')
RES=os.path.join(RP,'StaticResources','RegisteredResources')
# Mandatory cleanup: without it, renumbering the visuals leaves the files from the
# previous generation behind and Power BI shows everything twice
if os.path.isdir(PGS): shutil.rmtree(PGS)
for p in (PGS,RES): os.makedirs(p,exist_ok=True)
guid5=lambda s: str(uuid.uuid5(uuid.NAMESPACE_URL,'apex-f1/'+s))

# ---------------- chrome ----------------
# The rail is organised in three sections of three pages, each with its own colour.
NAVGROUPS = [
 ('SEASON',   RED,   [('p1','pulse','PULSE',   'Season Pulse'),
                      ('p8','flag',  'RACES',   'Race Results'),
                      ('p7','garage','GRID',    'Teams')]),
 ('CIRCUITS', CYAN,  [('p9','globe', 'NATIONS', 'Countries'),
                      ('p2','circuit','ELEVEN', 'Classic Eleven'),
                      ('p3','lab',   'LAB',     'Circuit Lab')]),
 ('HISTORY',  AMBER, [('p4','driver','DRIVERS', 'Drivers'),
                      ('p5','team',  'TEAMS',   'Constructors'),
                      ('p6','era',   'ERA',     'Formula 1')]),
]
NAV=[(p,i,t) for _,_,items in NAVGROUPS for p,i,_,t in items]
GCOL_NAME={RED:'red',CYAN:'cyan',AMBER:'amber'}

def rail(pg):
    """Navigation rail v34 (120 px): 96 px logo, three sections separated by a thin rule,
       44 px icon + label in a 22 px box (at 9 pt, a 15 px box clipped the text)."""
    pg.image(12,10,96,96,'mark.png',tag='lg')
    y=118; k=0
    for gi,(gname,gcol,items) in enumerate(NAVGROUPS):
        pg.text(0,y,RAIL_W,22,[dict(t=gname,size=10,color=gcol,font=FTB)],align='center',tag='gh%d'%gi)
        y+=24
        for pid,ic,lab,tip in items:
            on = (pid==pg.name)
            pg.image(38,y+2,44,44,'ic_%s_%s.png'%(ic,'on' if on else 'off'),tag='ni%d'%k)
            pg.text(0,y+46,RAIL_W,22,[dict(t=lab,size=10,color=(INK if on else MUTED),font=FTS)],
                    align='center',tag='nl%d'%k)
            if on:
                pg.image(0,y-3,5,72,'accent_%s.png'%GCOL_NAME[gcol],scaling='Fill',tag='nb%d'%k)
                pg.panel(10,y-3,102,72,bg='#161C29',radius=12,border='#2C3446',alpha=0,tag='nz%d'%k)
                # v[-1]=nz, v[-2]=nb, v[-3]=nl, v[-4]=ni: the background must sit UNDER the icon
                pg.v[-1]['position']['z']=pg.v[-4]['position']['z']-1
            pg.navbtn(6,y-3,108,72,pid,tip,tag='na%d'%k)
            y+=72; k+=1
        if gi<len(NAVGROUPS)-1:
            pg.image(28,y+6,64,2,'accent_line.png',scaling='Fill',tag='gs%d'%gi)
            y+=16
    pg.text(0,870,RAIL_W,22,[dict(t='APEX',size=9.5,color=RED,font=FTB)],align='center',tag='rl')

def season_caption(pg,x=560,w=1016):
    pass   # v38: the slicer moves up to y=10, the years no longer need a caption

def chrome(pg, active, eyebrow, title, subtitle_measure=None, subtitle_text=None, titlew=760, subw=776):
    pg.image(0,0,1600,900,'bg.png',scaling='Fill',tag='bg')
    pg.v[-1]['position']['z']=0
    rail(pg)
    grp = next((g for g,_,items in NAVGROUPS if any(p==pg.name for p,_,_,_ in items)), None)
    gcol= next((c for g,c,items in NAVGROUPS if any(p==pg.name for p,_,_,_ in items)), RED)
    if grp:
        pg.text(100,2,100,18,[dict(t=grp,size=11,color=gcol,font=FTB)],tag='eb')
        pg.text(200,2,340,18,[dict(t=eyebrow,size=11,color=RED,font=FTS)],tag='eb2')
    else:
        pg.text(100,2,560,18,[dict(t=eyebrow,size=11,color=RED,font=FTS)],tag='eb')
    pg.text(98,18,titlew,40,[dict(t=title,size=30,color=INK,font=FD)],tag='ti')
    if subtitle_measure: pg.card(98,56,subw,56,subtitle_measure,size=13,color=MUTED,font=FT,align='left',tag='st')   # a 40 px card clipped the text
    elif subtitle_text:  pg.text(100,70,subw,32,[dict(t=subtitle_text,size=13,color=MUTED)],tag='st')
    pg.text(96,868,1200,24,[dict(t='Source · f1db open dataset (results, qualifying, standings, pit stops) · circuit geometry from the f1-circuits dataset · seasons 2014-2026',size=11,color=MUTED)],tag='fo')

def kpi(pg,x,y,w,h,label,measure,sub_measure=None,sub_text=None,accent=INK,vsize=24,tag='k'):
    """KPI tile v37: opaque background, coral strip on top, everything centred (the card
       visual always centres its value, so the rest is aligned to it)."""
    pg.panel(x,y,w,h,bg=KPIBG,border=KPILINE,alpha=0,tag=tag+'p')
    pg.image(x+16,y,w-32,4,'accent_red.png',scaling='Fill',tag=tag+'a')
    pg.text(x+12,y+10,w-24,24,[dict(t=label.upper(),size=13,color=RED,font=FTS)],align='center',tag=tag+'l')
    pg.card(x+12,y+34,w-24,h-34-50,measure,size=vsize,color=INK,font=FD,wrap=True,units=1,tag=tag+'v')
    if sub_measure: pg.card(x+10,y+h-50,w-20,48,sub_measure,size=13,color=MUTED,font=FT,units=1,wrap=True,tag=tag+'s')
    elif sub_text:  pg.text(x+12,y+h-34,w-24,28,[dict(t=sub_text,size=12.5,color=MUTED)],align='center',tag=tag+'s')

def kpi_num(pg,x,y,w,h,label,measure,sub_text=None,accent=INK,vsize=44,units=1,prec=None,tag='k',subdy=32):
    pg.panel(x,y,w,h,bg=KPIBG,border=KPILINE,alpha=0,tag=tag+'p')
    pg.image(x+16,y,w-32,4,'accent_red.png',scaling='Fill',tag=tag+'a')
    pg.text(x+12,y+10,w-24,24,[dict(t=label.upper(),size=13,color=RED,font=FTS)],align='center',tag=tag+'l')
    pg.card(x+12,y+32,w-24,h-32-subdy,measure,size=vsize,color=INK,font=FD,units=units,prec=prec,tag=tag+'v')
    if sub_text: pg.text(x+12,y+h-subdy,w-24,subdy-2,[dict(t=sub_text,size=12.5,color=MUTED)],align='center',tag=tag+'s')

def bigcard(pg,x,y,w,label,measure,size=24,color=INK,font=FD,sub_measure=None,tag='bc'):
    ch=max(int(size*3.2),46)
    pg.text(x+16,y+8,w-30,24,[dict(t=label.upper(),size=11,color=RED,font=FTS)],tag=tag+'l')
    pg.card(x+14,y+30,w-28,ch,measure,size=size,color=color,font=font,units=1,tag=tag+'v')
    if sub_measure: pg.card(x+16,y+30+ch,w-30,48,sub_measure,size=12,color=MUTED,font=FT,units=1,tag=tag+'s')


LOGO_ORDER = ['mercedes','red-bull','ferrari','mclaren','williams','force-india',
              'alpine','aston-martin','renault','haas','toro-rosso','alphatauri',
              'racing-point','racing-bulls','alfa-romeo','sauber','lotus-f1','kick-sauber',
              'rb','audi','marussia','manor','cadillac','caterham']
LOGO_NAME  = {'mercedes':'Mercedes','red-bull':'Red Bull','ferrari':'Ferrari','mclaren':'McLaren',
  'williams':'Williams','force-india':'Force India','alpine':'Alpine','aston-martin':'Aston Martin',
  'renault':'Renault','haas':'Haas','toro-rosso':'Toro Rosso','alphatauri':'AlphaTauri',
  'racing-point':'Racing Point','racing-bulls':'Racing Bulls','alfa-romeo':'Alfa Romeo',
  'sauber':'Sauber','lotus-f1':'Lotus','kick-sauber':'Kick Sauber','rb':'RB','audi':'Audi',
  'marussia':'Marussia','manor':'Manor','cadillac':'Cadillac','caterham':'Caterham'}

def logo_wall(pg,x,y,w,h,cols=8,tag='lw'):
    """Logo wall made of static images: no data behind it, so no tooltip is
       possible. This replaces the image column of the table."""
    pg.panel(x,y,w,h,tag=tag+'p')
    pg.text(x+16,y+12,w-30,18,[dict(t='THE TWENTY-FOUR CONSTRUCTORS',size=13,color=INK,font=FTS)],tag=tag+'t')
    pg.text(x+16,y+32,w-30,14,[dict(t='Every team of the era, 2014 to 2026',size=9.5,color=DIM)],tag=tag+'s')
    rows=(len(LOGO_ORDER)+cols-1)//cols
    cw=(w-32)/cols; ch=(h-60)/rows
    side=int(min(cw-12, ch-18))
    for i,cid in enumerate(LOGO_ORDER):
        cx = x+16 + (i%cols)*cw
        cy = y+54 + (i//cols)*ch
        pg.image(int(cx+(cw-side)/2), int(cy), side, side, 'lg_%s.png'%cid, tag='%s%02d'%(tag,i))
        pg.text(int(cx), int(cy+side+2), int(cw), 13,
                [dict(t=LOGO_NAME[cid],size=7.5,color=MUTED,font=FTS)],align='center',tag='%sn%02d'%(tag,i))

# ---------------- filters ----------------
def cat_filter(fname,entity,prop,values,vtype='L'):
    exprs=[{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":prop}}]
    vals=[[{"Literal":{"Value":("%s%s"%(v,vtype)) if vtype=='L' else "'%s'"%v}}] for v in values]
    return {"name":fname,"field":cfield(entity,prop),"type":"Categorical",
            "filter":{"Version":2,"From":[{"Name":"e","Entity":entity,"Type":0}],
                      "Where":[{"Condition":{"In":{"Expressions":exprs,"Values":vals}}}]},
            "howCreated":"Auto","displayName":prop}
def topn_filter(fname,entity,prop,measure,n,direction='Descending'):
    return {"name":fname,"field":cfield(entity,prop),"type":"TopN",
            "filter":{"Version":2,
              "From":[{"Name":"e","Entity":entity,"Type":0},{"Name":"m","Entity":"Metrics","Type":0}],
              "Where":[{"Condition":{"Not":{"Expression":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"e"}},"Property":prop}}],
                        "Table":{"SourceRef":{"Source":"t"}}}}}}}]},
            "howCreated":"Auto","displayName":prop,
            "objects":{"general":[{"properties":{"itemCount":{"expr":{"Literal":{"Value":"%dD"%n}}}}}]}}

# ---------------- composite visuals ----------------
def bar(pg,x,y,w,h,title,cat_ent,cat_prop,meas,colour_meas=None,solid=None,units=1,prec=0,
        sort_desc=True,catsize=10,valsize=10,lab=True,sub=None,tag='bc',invert=False,barh=None):
    q={"queryState":{"Category":{"projections":[pc(cat_ent,cat_prop,True)]},
                     "Y":{"projections":[pm(meas)]}},
       "sortDefinition":sortdef(mfield(meas),'Descending' if sort_desc else 'Ascending')}
    o={"legend":legend(False),
       "categoryAxis":axis(True,MUTED,catsize,grid=False,concat=False),
       "valueAxis":axis(False,MUTED,valsize,grid=True,units=units),
       "labels":labels(lab,INK,valsize,units=units,prec=prec,font=FTS),
       "dataPoint":(fill_measure(colour_meas) if colour_meas else fill_solid(solid or RED))}
    if barh: o["layout"]=P(categoryWidth=N(barh))
    return pg.add('barChart',x,y,w,h,objects=o,query=q,vc=vc_panel(title,sub=sub),tag=tag)

def column(pg,x,y,w,h,title,cat_ent,cat_prop,meas,colour_meas=None,solid=None,units=1,prec=0,
           lab=True,sub=None,tag='cc',sort_desc=True,catsize=10):
    q={"queryState":{"Category":{"projections":[pc(cat_ent,cat_prop,True)]},
                     "Y":{"projections":[pm(meas)]}},
       "sortDefinition":sortdef(mfield(meas),'Descending' if sort_desc else 'Ascending')}
    o={"legend":legend(False),
       "categoryAxis":axis(True,MUTED,catsize,grid=False,concat=False),
       "valueAxis":axis(False,MUTED,10,grid=True,units=units),
       "labels":labels(lab,INK,10,units=units,prec=prec,font=FTS),
       "dataPoint":(fill_measure(colour_meas) if colour_meas else fill_solid(solid or RED))}
    return pg.add('columnChart',x,y,w,h,objects=o,query=q,vc=vc_panel(title,sub=sub),tag=tag)

def line(pg,x,y,w,h,title,cat_ent,cat_prop,meas,legend_ent=None,legend_prop=None,colour_meas=None,
         sub=None,tag='ln',stroke=2.4,marker=False,showleg=True,units=None,catsize=10,categorical=False):
    qs={"Category":{"projections":[pc(cat_ent,cat_prop,True)]},"Y":{"projections":[pm(meas)]}}
    if legend_ent: qs["Series"]={"projections":[pc(legend_ent,legend_prop)]}
    o={"legend":legend(showleg and bool(legend_ent),'TopCenter',9.5),
       "categoryAxis":axis(True,MUTED,catsize,grid=False,concat=False),
       "valueAxis":axis(True,MUTED,9.5,grid=True,units=units),
       "labels":labels(False),
       "lineStyles":P(strokeWidth=N(stroke),showMarker=B(marker),lineStyle=S('solid'))}
    if categorical: o["categoryAxis"][0]["properties"]["axisType"]=S('Categorical')
    if colour_meas: o["dataPoint"]=fill_measure(colour_meas)
    return pg.add('lineChart',x,y,w,h,objects=o,query={"queryState":qs},vc=vc_panel(title,sub=sub),tag=tag)

def area(pg,x,y,w,h,title,cat_ent,cat_prop,meas,legend_ent,legend_prop,colour_meas=None,sub=None,tag='ar',showleg=True,stacked=False):
    qs={"Category":{"projections":[pc(cat_ent,cat_prop,True)]},"Y":{"projections":[pm(meas)]},
        "Series":{"projections":[pc(legend_ent,legend_prop)]}}
    o={"legend":legend(showleg,'TopCenter',9.5),
       "categoryAxis":axis(True,MUTED,9.5,grid=False,concat=False),
       "valueAxis":axis(True,MUTED,9.5,grid=True),
       "labels":labels(False)}
    if colour_meas: o["dataPoint"]=fill_measure(colour_meas)
    o["categoryAxis"][0]["properties"]["axisType"]=S('Categorical')
    return pg.add('stackedAreaChart' if stacked else 'areaChart',x,y,w,h,objects=o,query={"queryState":qs},vc=vc_panel(title,sub=sub),tag=tag)

def donut(pg,x,y,w,h,title,cat_ent,cat_prop,meas,colour_meas=None,sub=None,tag='dn'):
    q={"queryState":{"Category":{"projections":[pc(cat_ent,cat_prop,True)]},"Y":{"projections":[pm(meas)]}},
       "sortDefinition":sortdef(mfield(meas))}
    o={"legend":legend(False),
       "labels":labels(True,INK,9.5,font=FTS,prec=0),
       "slices":P(innerRadiusRatio=N(0.58))}
    o["labels"][0]["properties"]["labelStyle"]=S('Category, percent of total')
    if colour_meas: o["dataPoint"]=fill_measure(colour_meas)
    return pg.add('donutChart',x,y,w,h,objects=o,query=q,vc=vc_panel(title,sub=sub),tag=tag)

def scatter(pg,x,y,w,h,title,det_ent,det_prop,xm,ym,sizem=None,colour_meas=None,sub=None,tag='sc',
            xtitle=None,ytitle=None,invert_y=False):
    qs={"Category":{"projections":[pc(det_ent,det_prop,True)]},
        "X":{"projections":[pm(xm)]},"Y":{"projections":[pm(ym)]}}
    if sizem: qs["Size"]={"projections":[pm(sizem)]}
    o={"legend":legend(False),
       "categoryAxis":[{"properties":{"show":B(True),"labelColor":C(MUTED),"fontSize":N(12),"fontFamily":S(FT),
                        "showAxisTitle":B(bool(xtitle)),"axisTitle":S(xtitle or ''),"titleText":S(xtitle or ''),"titleFontSize":N(12),
                        "titleColor":C(DIM),"gridlineShow":B(True),"gridlineColor":C(LINE)}}],
       "valueAxis":[{"properties":{"show":B(True),"labelColor":C(MUTED),"fontSize":N(12),"fontFamily":S(FT),
                        "showAxisTitle":B(bool(ytitle)),"axisTitle":S(ytitle or ''),"titleText":S(ytitle or ''),"titleFontSize":N(12),
                        "titleColor":C(DIM),"gridlineShow":B(True),"gridlineColor":C(LINE),
                        "invertAxis":B(invert_y)}}],
       "categoryLabels":P(show=B(True),color=C(MUTED),fontSize=N(11),fontFamily=S(FT)),
       "bubbles":P(bubbleSize=N(-20))}
    if colour_meas: o["dataPoint"]=fill_measure(colour_meas)
    return pg.add('scatterChart',x,y,w,h,objects=o,query={"queryState":qs},vc=vc_panel(title,sub=sub),tag=tag)

IMAGE_MEASURES={'Nat','Nation flag','Track','Flag','Lab Blueprint','Nation','Helmet','Car','Badge','Helmet chip'}
def table(pg,x,y,w,h,title,cols,widths=None,sort=None,sort_dir='Descending',rowpad=6,textsize=11,
          imageh=None,sub=None,tag='tb',hdrsize=10,vfilter=None):
    projections=[]
    for c in cols:
        if c[0]=='m': projections.append(pm(c[1]))
        else: projections.append(pc(c[1],c[2]))
    q={"queryState":{"Values":{"projections":projections}}}
    if sort:
        f = mfield(sort[1]) if sort[0]=='m' else cfield(sort[1],sort[2])
        q["sortDefinition"]=sortdef(f,sort_dir)
    textsize=fz(textsize,1.2); hdrsize=fz(hdrsize,1.3)
    grid={"gridVertical":B(True),"gridVerticalColor":C(GRIDC),"gridVerticalWeight":N(1),
          "gridHorizontal":B(True),"gridHorizontalColor":C(GRIDC),"gridHorizontalWeight":N(1),
          "rowPadding":N(rowpad+1),"outlineColor":C(RED),"outlineWeight":N(2),"textSize":N(textsize)}
    if imageh: grid["imageHeight"]=N(imageh)
    o={"grid":[{"properties":grid}],
       "columnHeaders":[{"properties":{"fontColor":C('#FFFFFF'),"backColor":C(RED),"fontSize":N(hdrsize),
                          "fontFamily":S(FTB),"alignment":S('Center'),"wordWrap":B(False),"autoSizeColumnWidth":B(False),
                          "outline":S('Frame')}}],
       "values":[{"properties":{"fontColorPrimary":C(INK),"backColorPrimary":C('#0B0E15'),
                   "fontColorSecondary":C(INK),"backColorSecondary":C('#151A25'),
                   "fontSize":N(textsize),"fontFamily":S(FT),"wordWrap":B(False)}}],
       "total":[{"properties":{"totals":B(False)}}]}
    if widths:
        cw=[]
        for c,wd in zip(cols,widths):
            meta = "Metrics.%s"%c[1] if c[0]=='m' else "%s.%s"%(c[1],c[2])
            cw.append({"properties":{"value":N(wd)},"selector":{"metadata":meta}})
        o["columnWidth"]=cw
    has_img=any(c[0]=='m' and c[1] in IMAGE_MEASURES for c in cols)
    fc=measure_filter(guid5('vf/%s/%s'%(pg.name,tag)),*vfilter) if vfilter else None
    return pg.add('tableEx',x,y,w,h,objects=o,query=q,vc=vc_panel(title,sub=sub),tag=tag,tooltip=not has_img,filterConfig=fc)

def slicer(pg,x,y,w,h,entity,prop,horizontal=True,single=True,tag='sl',size=10.5,bg=PANEL2,fg=MUTED,selbg=RED):
    size=fz(size,1.2)
    o={"general":P(orientation=N(1 if horizontal else 2),responsive=B(False),
                   outlineColor=C(LINE),outlineWeight=N(0)),
       "selection":P(singleSelect=B(single),strictSingleSelect=B(False),selectAllCheckboxEnabled=B(False)),
       "header":P(show=B(False)),
       "items":P(fontColor=C(fg),background=C(bg),fontSize=N(size),fontFamily=S(FTS),
                 outline=S('None'),padding=N(4)),
       "pips":P(show=B(False))}
    q={"queryState":{"Values":{"projections":[pc(entity,prop)]}}}
    vc={"background":P(show=B(False)),"border":P(show=B(False)),"dropShadow":P(show=B(False)),
        "visualHeader":P(show=B(False)),"title":P(show=B(False)),"subTitle":P(show=B(False))}
    return pg.add('slicer',x,y,w,h,objects=o,query=q,vc=vc,tag=tag)

def slicer_default(entity,prop,values,text=True):
    vals=[[{"Literal":{"Value":("'%s'"%v) if text else ("%sL"%v)}}] for v in values]
    return {"filters":[{"name":guid5('slf/%s/%s'%(entity,prop)),
        "field":cfield(entity,prop),"type":"Categorical",
        "filter":{"Version":2,"From":[{"Name":"s","Entity":entity,"Type":0}],
          "Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"s"}},"Property":prop}}],"Values":vals}}}]},
        "howCreated":"Slicer"}]}
def page_filter(entity,prop,values,text=False,name='pf'):
    vals=[[{"Literal":{"Value":("'%s'"%v) if text else ("%sL"%v)}}] for v in values]
    return {"filters":[{"name":guid5('pf/%s/%s/%s'%(entity,prop,name)),
        "field":cfield(entity,prop),"type":"Categorical",
        "filter":{"Version":2,"From":[{"Name":"p","Entity":entity,"Type":0}],
          "Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"p"}},"Property":prop}}],"Values":vals}}}]},
        "howCreated":"Auto","displayName":prop,"isLockedInView":False,"isHiddenInViewMode":True}]}


def stackcol(pg,x,y,w,h,title,cat_ent,cat_prop,meas,legend_ent,legend_prop,colour_meas=None,sub=None,tag='sk',lab=False,showleg=True,categorical=False):
    qs={"Category":{"projections":[pc(cat_ent,cat_prop,True)]},"Y":{"projections":[pm(meas)]},
        "Series":{"projections":[pc(legend_ent,legend_prop)]}}
    o={"legend":legend(showleg,'TopCenter',9.5),
       "categoryAxis":axis(True,MUTED,10,grid=False,concat=False),
       "valueAxis":axis(True,MUTED,9.5,grid=True,units=1),
       "labels":labels(lab,INK,9,font=FTS),
       "dataPoint":(fill_measure(colour_meas) if colour_meas else fill_solid(RED))}
    if categorical: o["categoryAxis"][0]["properties"]["axisType"]=S('Categorical')
    return pg.add('columnChart',x,y,w,h,objects=o,query={"queryState":qs},vc=vc_panel(title,sub=sub),tag=tag)

def line2(pg,x,y,w,h,title,cat_ent,cat_prop,measures,sub=None,tag='l2',marker=True):
    qs={"Category":{"projections":[pc(cat_ent,cat_prop,True)]},
        "Y":{"projections":[pm(mm) for mm in measures]}}
    o={"legend":legend(True,'TopCenter',9.5),
       "categoryAxis":axis(True,MUTED,10,grid=False,concat=False),
       "valueAxis":axis(True,MUTED,9.5,grid=True),
       "labels":labels(False),
       "lineStyles":P(strokeWidth=N(2.6),showMarker=B(marker),markerSize=N(5))}
    return pg.add('lineChart',x,y,w,h,objects=o,query={"queryState":qs},vc=vc_panel(title,sub=sub),tag=tag)

def mapviz(pg,x,y,w,h,title,cat_ent,cat_prop,lon,lat,size=None,sub=None,tag='mp',bubble=-20,labels_on=False):
    qs={"Category":{"projections":[pc(cat_ent,cat_prop,True)]},
        "X":{"projections":[pm(lon)]},"Y":{"projections":[pm(lat)]}}
    if size: qs["Size"]={"projections":[pm(size)]}
    o={"legend":legend(False),
       "bubbles":P(bubbleSize=N(bubble)),
       "dataPoint":fill_solid(RED),
       "categoryLabels":P(show=B(labels_on),color=C(MUTED),fontSize=N(11))}
    return pg.add('map',x,y,w,h,objects=o,query={"queryState":qs},vc=vc_panel(title,sub=sub),tag=tag)

def band(pg,x,y,w,text,tag='bd'):
    pg.text(x,y,w,24,[dict(t=text.upper(),size=11,color=RED,font=FTS)],tag=tag)

PAGES=[]
EYE='·  FORMULA 1  ·  2014-2026'
KY, KH = 112, 152          # KPI strip (v37: moved down 8 px to give the subtitle breathing room)
R2Y, R2H = 276, 372        # row 2
R3Y, R3H = 664, 200        # row 3
C3=[96,594,1092]; W3=[482,482,484]
TX5=[96,395,694,993,1292]; W5=283
TX4=[96,470,844,1218]; W4=358

# ================================ P1 - SEASON PULSE ================================
p1=Page('p1','Season Pulse')
chrome(p1,'p1',EYE,'Season Pulse',subtitle_measure='Live Headline',titlew=440,subw=600)
slicer(p1,560,10,1016,44,'D_Season','SeasonLabel',horizontal=True,size=10,tag='ss')
kpi(p1,TX5[0],KY,W5,KH,'Championship leader','Live Leader','Live Leader Sub',accent=INK,tag='k0')
kpi(p1,TX5[1],KY,W5,KH,'Leading team','Live Team','Live Team Sub',accent=CYAN,tag='k1')
kpi(p1,TX5[2],KY,W5,KH,'Latest winner','Live Last Winner','Live Last GP Sub',accent=INK,tag='k2')
kpi(p1,TX5[3],KY,W5,KH,'Next up','Live Next GP','Live Next GP Sub',accent=AMBER,tag='k3')
kpi(p1,TX5[4],KY,W5,KH,'Season','Live Round Line','Live Winners Sub',accent=INK,tag='k4')
# v35: the drivers standings (22 rows) fill the whole left column, without scrolling;
#      the points share (donut) duplicated the constructors standings.
bar(p1,C3[0],276,W3[0],588,"DRIVERS CHAMPIONSHIP",'D_Driver','Driver','Season points',
    colour_meas='Driver Team Colour',sub='Every driver, points after the latest round',tag='c1',catsize=9.5,valsize=9.5)
bar(p1,C3[1],276,W3[1],364,"CONSTRUCTORS CHAMPIONSHIP",'D_Constructor','Team','Team points',
    colour_meas='Team Colour',sub='Every team, points after the latest round',tag='c2',catsize=9,valsize=9.5)
line(p1,C3[2],276,W3[2],364,'THE TITLE RACE, ROUND BY ROUND','D_Race','Round','Running team points',
     'D_Constructor','Team',colour_meas='Team Colour',sub='Cumulative constructor points, one line per team in team colours',tag='c3',catsize=9,showleg=False,categorical=True)
column(p1,C3[1],652,W3[1],212,'RACE WINS','D_Driver','Driver','Season wins',colour_meas='Driver Team Colour',tag='c4',catsize=9)
column(p1,C3[2],652,W3[2],212,'POLE POSITIONS','D_Driver','Driver','Season poles',colour_meas='Driver Team Colour',tag='c5',catsize=9)
PAGES.append(p1)

# ================================ P2 - CLASSIC ELEVEN ================================
p2=Page('p2','Classic Eleven')
chrome(p2,'p2',EYE,'The Classic Eleven',subw=1000,
       subtitle_text='Eleven circuits that made the sport: real geometry, real records, 2014 to 2026.')
kpi_num(p2,TX4[0],KY,W4,KH,'Heritage circuits','Classic circuits',sub_text='on the 2014-2026 calendar',accent=INK,tag='k0')
kpi_num(p2,TX4[1],KY,W4,KH,'Grands Prix held','Classic GP',sub_text='races run at these eleven tracks',accent=CYAN,tag='k1')
kpi_num(p2,TX4[2],KY,W4,KH,'Different winners','Classic winners',sub_text='drivers who have won here',accent=AMBER,tag='k2')
kpi_num(p2,TX4[3],KY,W4,KH,'Combined lap length','Classic km',sub_text='kilometres of racing circuit',accent=INK,prec=1,tag='k3')
table(p2,96,276,1080,588,'THE ELEVEN',
      [('m','Track'),('c','D_Circuit','Circuit'),('m','Flag'),('m','Nickname'),
       ('m','Km'),('m','Corners'),('m','GP'),('m','Winners'),('m','Record')],
      widths=[60,192,58,264,78,92,58,96,118],sort=('c','D_Circuit','ClassicRank'),sort_dir='Ascending',
      rowpad=1,textsize=11,imageh=32,sub='Circuit outlines traced from real track geometry, all eleven on one screen',tag='tb')
bar(p2,1192,276,384,588,'GRANDS PRIX HELD, 2014-2026','D_Circuit','Circuit','GP',
    solid=RED,sub='Races run at each heritage circuit',tag='c1',catsize=10,valsize=10)
PAGES.append(p2)

# ================================ P3 - CIRCUIT LAB ================================
p3=Page('p3','Circuit Lab')
chrome(p3,'p3',EYE,'Circuit Lab',subtitle_measure='Lab Headline',subw=420)
p3.panel(96,110,230,754,bg=PANEL2,tag='sp')
band(p3,112,116,200,'circuit',tag='sl0')
p3.text(112,138,200,24,[dict(t='Click a circuit to load the page',size=9,color=DIM)],tag='sl1')
lo={"grid":[{"properties":{"gridVertical":B(False),"gridHorizontal":B(False),"rowPadding":N(3),
      "outlineWeight":N(0),"textSize":N(12)}}],
    "columnHeaders":[{"properties":{"fontColor":C(PANEL2),"backColor":C(PANEL2),"fontSize":N(8)}}],
    "values":[{"properties":{"fontColorPrimary":C(INK),"backColorPrimary":C(PANEL2),
      "fontColorSecondary":C(INK),"backColorSecondary":C(PANEL2),"fontSize":N(12),
      "fontFamily":S(FT),"wordWrap":B(False)}}],
    "total":[{"properties":{"totals":B(False)}}],
    "columnWidth":[{"properties":{"value":N(164)},"selector":{"metadata":"D_Circuit.Circuit"}}]}
p3.add('tableEx',104,160,214,700,objects=lo,
       query={"queryState":{"Values":{"projections":[pc('D_Circuit','Circuit')]}},
              "sortDefinition":sortdef(cfield('D_Circuit','Circuit'),'Ascending')},tag='sc',tooltip=False)
p3.panel(342,110,400,440,tag='bp')
band(p3,358,118,368,'track blueprint',tag='bl')
tbo={"grid":[{"properties":{"gridVertical":B(False),"gridHorizontal":B(False),"rowPadding":N(0),
       "outlineWeight":N(0),"textSize":N(8),"imageHeight":N(300)}}],
     "columnHeaders":[{"properties":{"fontColor":C(PANEL),"backColor":C(PANEL),"fontSize":N(8)}}],
     "values":[{"properties":{"backColorPrimary":C(PANEL),"backColorSecondary":C(PANEL),
       "fontColorPrimary":C(PANEL),"fontSize":N(8),"wordWrap":B(False)}}],
     "total":[{"properties":{"totals":B(False)}}],
     "columnWidth":[{"properties":{"value":N(300)},"selector":{"metadata":"Metrics.Lab Blueprint"}}]}
p3.add('tableEx',362,146,362,396,objects=tbo,query={"queryState":{"Values":{"projections":[pm('Lab Blueprint')]}}},tag='tk',tooltip=False)
p3.panel(342,566,400,298,tag='pf')
bigcard(p3,342,566,400,'circuit profile','Lab Profile',size=14,color=INK,font=FT,tag='b1')
bigcard(p3,342,632,400,'signature corner','Lab Corner',size=17,color=AMBER,font=FTS,tag='b2')
bigcard(p3,342,708,400,'lap record  ·  hybrid era','Lab Record',size=22,color=RED,font=FM,
        sub_measure='Lab Record Line',tag='b3')
KX=[758,965,1172,1379]
kpi_num(p3,KX[0],KY,195,KH,'Grands Prix','Lab GP',accent=INK,tag='q0')
kpi_num(p3,KX[1],KY,195,KH,'First GP','Lab First GP',accent=INK,vsize=34,tag='q1')
kpi_num(p3,KX[2],KY,195,KH,'Winners','Lab Winners',accent=CYAN,tag='q2')
kpi_num(p3,KX[3],KY,195,KH,'Winning teams','Lab Teams',accent=AMBER,tag='q3')
p3.panel(758,276,402,104,tag='t1')
bigcard(p3,758,278,402,'track master  ·  driver','Lab Master',size=19,color=INK,tag='b4')
p3.panel(1174,276,402,104,tag='t2')
bigcard(p3,1174,278,402,'track master  ·  team','Lab Master Team',size=19,color=INK,tag='b5')
table(p3,758,392,818,472,'EVERY GRAND PRIX RUN HERE',
      [('c','D_Race','Year'),('m','Race win by'),('m','Constructor'),('m','Pole'),('m','Margin'),('m','Fastest lap')],
      widths=[58,170,134,170,92,126],sort=('c','D_Race','Year'),sort_dir='Descending',
      rowpad=0,textsize=10,sub='Winner, pole and the fastest lap set that weekend, every season since 2014',tag='tb')
PAGES.append(p3)

# ================================ P4 - DRIVERS ================================
p4=Page('p4','Drivers')
chrome(p4,'p4',EYE,'Drivers',titlew=440,subw=1000,
       subtitle_text='Pick a metric, pick a season: the order changes.')
season_caption(p4)
slicer(p4,560,10,1016,44,'D_Season','SeasonLabel',horizontal=True,size=10,tag='ss')
p4.panel(96,112,1480,46,bg=PANEL2,radius=12,tag='mb')
slicer(p4,104,116,1464,38,'D_Metric','Metric',horizontal=True,size=10.5,bg=PANEL2,tag='sm')
bar(p4,96,176,804,380,'TOP 12 DRIVERS','D_Driver','Driver','Top 12 Metric',
    colour_meas='Driver Team Colour',sub='Ranked on the metric selected above',tag='c1',catsize=11,valsize=10.5)
table(p4,916,176,660,380,'HALL OF FAME',
      [('c','D_Driver','Driver'),('m','GP wins'),('m','GP poles'),('m','GP podiums')],
      widths=[220,120,120,150],sort=('m','GP wins'),rowpad=0,textsize=10,
      sub='Ten most successful drivers of the era: wins, poles, podiums',tag='tb')
scatter(p4,96,568,740,296,'START HERE, FINISH THERE','D_Driver','Driver',
        'Avg Grid (min 60 starts)','Avg Finish (min 60 starts)',sizem='Entries',
        colour_meas='Driver Team Colour',xtitle='Average grid slot  (1 = pole)',ytitle='Average finish  (1 = win)',
        invert_y=True,sub='The 28 drivers with 60+ starts · bubble = race entries · top-left = the best',tag='sc')
column(p4,852,568,724,296,'AVERAGE PLACES GAINED ON RACE DAY','D_Driver','Driver','Busy Places Gained',
       colour_meas='Driver Team Colour',prec=2,sub='Grid slot minus finishing position · 15 busiest drivers',
       tag='c2',catsize=9.5)
PAGES.append(p4)

# ================================ P5 - CONSTRUCTORS ================================
p5=Page('p5','Constructors')
chrome(p5,'p5',EYE,'Constructors',titlew=440,subw=1000,
       subtitle_text='Thirteen seasons of the hybrid era, seen from the pit wall.')
season_caption(p5)
slicer(p5,560,10,1016,44,'D_Season','SeasonLabel',horizontal=True,size=10,tag='ss')
kpi_num(p5,TX4[0],KY,W4,KH,'Seasons covered','Seasons Covered',sub_text='2014 to the live 2026 season',accent=INK,tag='k0')
kpi_num(p5,TX4[1],KY,W4,KH,'Grands Prix','Grands Prix',sub_text='races in the selection',accent=CYAN,tag='k1')
kpi_num(p5,TX4[2],KY,W4,KH,'Winning teams','Different Winning Teams',sub_text='constructors that have won',accent=AMBER,tag='k2')
kpi_num(p5,TX4[3],KY,W4,KH,'Championship points','Points',sub_text='scored across the selection',accent=INK,tag='k3')
# v50: the team slicer (FILTER BY TEAM) was removed at the user's request; the table takes its place.
# v59: the 24 teams on two side-by-side tables (rank 1-12 / 13-24), nothing scrolls any more.
#      The Race wins column of the table makes the RACE WINS chart redundant: removed.
P5COLS=[('c','D_Constructor','Team'),('m','Race wins'),('m','Podium finishes'),('m','Pole positions'),('m','Points')]
P5W=[130,76,114,108,88]
table(p5,96,276,564,588,'CONSTRUCTOR RECORD  ·  1 to 12',P5COLS,widths=P5W,sort=('m','Points'),rowpad=9,textsize=11,hdrsize=8,
      sub='Top twelve by points, click a row to filter the page',tag='ta',vfilter=('Record Rank',4,12))
table(p5,676,276,564,588,'CONSTRUCTOR RECORD  ·  13 to 24',P5COLS,widths=P5W,sort=('m','Points'),rowpad=9,textsize=11,hdrsize=8,
      sub='Thirteenth to twenty-fourth, every other team of the era',tag='tb',vfilter=('Record Rank',1,12))
area(p5,1256,276,320,284,'POINTS BY SEASON','D_Season','Year','Era points',
     'D_Constructor','Team',colour_meas='Team Colour',
     sub='Stacked in team colours',tag='c1',showleg=False,stacked=True)
bar(p5,1256,572,320,292,'WINS BY ENGINE','D_Engine','Engine','Wins',solid=RED,
    sub='Race wins per power unit',tag='c3',catsize=9.5,valsize=9.5)
PAGES.append(p5)

# ================================ P6 - FORMULA ONE ================================
p6=Page('p6','Formula 1')
chrome(p6,'p6',EYE,'Formula 1',
       subtitle_text='2014 to 2026 · thirteen seasons, thirty-three circuits, one long argument about who was fastest.')
kpi_num(p6,TX5[0],KY,W5,KH,'Seasons','Seasons Covered',sub_text='2014 → 2026',accent=INK,tag='k0')
kpi_num(p6,TX5[1],KY,W5,KH,'Grands Prix','Grands Prix',sub_text='races run',accent=CYAN,tag='k1')
kpi_num(p6,TX5[2],KY,W5,KH,'Circuits','Circuits',sub_text='tracks visited',accent=INK,tag='k2')
kpi_num(p6,TX5[3],KY,W5,KH,'Race winners','Different Winners',sub_text='drivers who won at least once',accent=AMBER,tag='k3')
kpi_num(p6,TX5[4],KY,W5,KH,'Laps completed','Laps Completed',sub_text='by every car on every grid',units=1,prec=0,accent=INK,tag='k4')
table(p6,96,276,560,588,'CHAMPIONS OF THE ERA',
      [('c','D_Season','Year'),('c','D_Season','Champion'),('c','D_Season','Constructor champion')],
      widths=[64,220,226],sort=('c','D_Season','Year'),sort_dir='Descending',rowpad=3,textsize=11,
      sub='Thirteen seasons, thirteen answers: drivers and constructors champions',tag='tb')
stackcol(p6,672,276,904,344,'WHO WON WHAT, SEASON BY SEASON','D_Season','Year','Era wins',
         'D_Constructor','Team',colour_meas='Team Colour',
         sub='Race wins per constructor, stacked by season: the shape of every era change',tag='c1')
line2(p6,672,632,904,232,'RELIABILITY, SEASON BY SEASON','D_Season','Year',
      ['Retirements per Race','Avg Pit Stops'],
      sub='Retirements per Grand Prix and average pit stops per car',tag='c2')
PAGES.append(p6)

# ================================ P7 - TEAMS ================================
p7=Page('p7','Teams')
chrome(p7,'p7',EYE,'Teams',titlew=440,subw=1000,
       subtitle_text='The grid, team by team: championship position, points, wins, podiums and driver line-up.')
season_caption(p7)
slicer(p7,560,10,1016,44,'D_Season','SeasonLabel',horizontal=True,size=10,tag='ss')
kpi_num(p7,TX4[0],KY,W4,KH,'Teams on the grid','Grid teams',sub_text='constructors entered',accent=INK,tag='k0')
kpi_num(p7,TX4[1],KY,W4,KH,'Drivers','Grid drivers',sub_text='who started a Grand Prix',accent=CYAN,tag='k1')
kpi_num(p7,TX4[2],KY,W4,KH,'Grands Prix','Grid races',sub_text='races in the selection',accent=AMBER,tag='k2')
kpi_num(p7,TX4[3],KY,W4,KH,'Championship points','Pts',sub_text='scored by the whole grid',accent=INK,tag='k3')
table(p7,96,276,812,588,'THE GRID',
      [('c','D_Constructor','Team'),('m','Pos'),('m','Pts'),
       ('m','Won'),('m','Top 3'),('m','Line-up')],
      widths=[130,46,66,52,60,411],sort=('m','Pts'),rowpad=10,textsize=12,
      sub='Every constructor of the season: position, points, wins, podiums and drivers',tag='tb')
bar(p7,924,276,652,588,'CHAMPIONSHIP POINTS','D_Constructor','Team','Pts',
    colour_meas='Team Colour',sub='Every team of the season; wins and podiums are in the table',tag='c1',catsize=11,valsize=11)
PAGES.append(p7)

# ================================ P8 - RACE RESULTS ================================
p8=Page('p8','Race Results')
chrome(p8,'p8',EYE,'Race Results',titlew=440,subw=1000,
       subtitle_text='Every Grand Prix of the season: country, date, winner, team and race time.')
season_caption(p8)
slicer(p8,560,10,1016,44,'D_Season','SeasonLabel',horizontal=True,size=10,tag='ss')
kpi_num(p8,TX4[0],KY,W4,KH,'Grands Prix','Grid races',sub_text='races run in the season',accent=INK,tag='k0')
kpi_num(p8,TX4[1],KY,W4,KH,'Different winners','Grid winners',sub_text='drivers who took a win',accent=CYAN,tag='k1')
kpi_num(p8,TX4[2],KY,W4,KH,'Winning teams','Grid teams won',sub_text='constructors who took a win',accent=AMBER,tag='k2')
kpi_num(p8,TX4[3],KY,W4,KH,'Drivers','Grid drivers',sub_text='who started a Grand Prix',accent=INK,tag='k3')
# v59: two tables (rounds 1-12 / 13-24): a 24-race season fits without scrolling.
#      RACE WINS (drivers) lives on Season Pulse, WINS BY TEAM on Teams: removed from here.
P8COLS=[('m','Rnd'),('m','Nat'),('c','D_Race','GrandPrix'),('m','Date'),('m','Winner'),('m','Team'),('m','Time')]
P8W=[44,44,170,74,130,112,100]
table(p8,96,276,740,588,'ROUNDS 1 to 12',P8COLS,widths=P8W,sort=('m','Rnd'),sort_dir='Ascending',
      rowpad=1,textsize=11,imageh=26,sub='Country, date, winner, team and winning time',tag='ta',vfilter=('Rnd',4,12))
table(p8,852,276,724,588,'ROUNDS 13 to 24',P8COLS,widths=P8W,sort=('m','Rnd'),sort_dir='Ascending',
      rowpad=1,textsize=11,imageh=26,sub='Second half of the season, empty until it has been raced',tag='tb',vfilter=('Rnd',1,12))
PAGES.append(p8)


# ================================ P9 - COUNTRIES ================================
p9=Page('p9','Countries')
chrome(p9,'p9',EYE,'Countries',titlew=520,subw=1000,
       subtitle_text='Every nation that has hosted a Grand Prix since 2014, Gulf states included.')
kpi_num(p9,TX4[0],KY,W4,KH,'Host countries','Countries',sub_text='nations on the calendar',accent=INK,tag='k0')
kpi_num(p9,TX4[1],KY,W4,KH,'Circuits','Circuits',sub_text='tracks used since 2014',accent=CYAN,tag='k1')
kpi_num(p9,TX4[2],KY,W4,KH,'Grands Prix','Grands Prix',sub_text='races run in those countries',accent=AMBER,tag='k2')
kpi_num(p9,TX4[3],KY,W4,KH,'Race winners','Different Winners',sub_text='drivers who won',accent=INK,tag='k3')
# v59: the 27 nations on two tables (rank 1-14 / 15-27); the per-country chart
#      repeated the Nation GP column: removed.
P9COLS=[('m','Nation flag'),('c','D_Circuit','Country'),('m','Tracks'),('m','Nation GP'),('m','Nation winners'),('m','First visit')]
P9W=[100,190,66,96,136,88]
table(p9,96,276,740,588,'HOST NATIONS  ·  1 to 14',P9COLS,widths=P9W,sort=('m','Nation GP'),rowpad=1,textsize=11,imageh=26,hdrsize=9,
      sub='Most Grands Prix hosted since 2014, Gulf states included',tag='ta',vfilter=('Nation Rank',4,14))
table(p9,852,276,724,588,'HOST NATIONS  ·  15 to 27',P9COLS,widths=P9W,sort=('m','Nation GP'),rowpad=1,textsize=11,imageh=26,hdrsize=9,
      sub='The rest of the calendar, newest hosts included',tag='tb',vfilter=('Nation Rank',1,14))
PAGES.append(p9)

# ============================ output ============================
THEME={
 "name":"APEX Grand Prix",
 "dataColors":["#F0503C","#22D3EE","#F5B942","#A78BFA","#3BD07A","#FF7A45","#5B8DEF","#E45C9A",
               "#C4CBD8","#00D2BE","#FF8000","#3671C6","#229971","#1868DB","#6C98FF","#B6BABD"],
 "background":"#0D1017","backgroundLight":"#12161F","backgroundNeutral":"#1A2030",
 "foreground":"#F4F6FA","foregroundNeutralSecondary":"#C4CBD8","foregroundNeutralTertiary":"#8F99AB",
 "tableAccent":"#F0503C","good":"#3BD07A","neutral":"#22D3EE","bad":"#F0503C",
 "maximum":"#F0503C","center":"#F5B942","minimum":"#1A2030","null":"#12161F",
 "hyperlink":"#22D3EE","visitedHyperlink":"#A78BFA",
 "textClasses":{
   "title":{"fontFace":"Segoe UI Semibold","fontSize":14,"color":"#F4F6FA"},
   "header":{"fontFace":"Segoe UI Semibold","fontSize":12,"color":"#F4F6FA"},
   "label":{"fontFace":"Segoe UI","fontSize":12,"color":"#C4CBD8"},
   "callout":{"fontFace":"Segoe UI Bold","fontSize":44,"color":"#F4F6FA"},
   "largeTitle":{"fontFace":"Segoe UI Bold","fontSize":31,"color":"#F4F6FA"}},
 "visualStyles":{
   "*":{"*":{
     "background":[{"show":True,"color":{"solid":{"color":"#12161F"}},"transparency":14}],
     "border":[{"show":True,"color":{"solid":{"color":"#2C3446"}},"radius":14}],
     "dropShadow":[{"show":False}],
     "visualHeader":[{"show":False}],
     "outspacePane":[{"backgroundColor":{"solid":{"color":"#0D1017"}},"foregroundColor":{"solid":{"color":"#F4F6FA"}},
                      "borderColor":{"solid":{"color":"#2C3446"}}}],
     "filterCard":[{"$id":"Applied","backgroundColor":{"solid":{"color":"#12161F"}},
                    "foregroundColor":{"solid":{"color":"#F4F6FA"}},"borderColor":{"solid":{"color":"#2C3446"}}},
                   {"$id":"Available","backgroundColor":{"solid":{"color":"#0D1017"}},
                    "foregroundColor":{"solid":{"color":"#C4CBD8"}},"borderColor":{"solid":{"color":"#2C3446"}}}]}},
   "page":{"*":{"background":[{"color":{"solid":{"color":"#0A0C10"}},"transparency":0}],
                "outspace":[{"color":{"solid":{"color":"#05070B"}},"transparency":0}]}},
   "slicer":{"*":{"background":[{"show":False}],"border":[{"show":False}],
                  "items":[{"fontColor":{"solid":{"color":"#C4CBD8"}},"background":{"solid":{"color":"#12161F"}},
                            "outline":"None","fontSize":12}]}},
   "tableEx":{"*":{"grid":[{"gridVertical":True,"gridHorizontal":True,
                            "gridVerticalColor":{"solid":{"color":"#C9463A"}},
                            "gridHorizontalColor":{"solid":{"color":"#C9463A"}},"outlineWeight":2}],
                   "columnHeaders":[{"backColor":{"solid":{"color":"#F0503C"}},
                                     "fontColor":{"solid":{"color":"#FFFFFF"}}}]}}}}

def write_report():
    for p in PAGES:
        d=os.path.join(PGS,p.name,'visuals'); os.makedirs(d,exist_ok=True)
        pj=p.to_json()
        if getattr(p,'filterConfig',None): pj['filterConfig']=p.filterConfig
        json.dump(pj,open(os.path.join(PGS,p.name,'page.json'),'w',encoding='utf-8'),indent=2,ensure_ascii=False)
        for v in p.v:
            vd=os.path.join(d,v['name']); os.makedirs(vd,exist_ok=True)
            json.dump(v,open(os.path.join(vd,'visual.json'),'w',encoding='utf-8'),indent=2,ensure_ascii=False)
    json.dump({"$schema":SCH_PAGES,"pageOrder":["p1","p8","p7","p9","p2","p3","p4","p5","p6"],"activePageName":"p1"},
              open(os.path.join(PGS,'pages.json'),'w',encoding='utf-8'),indent=2)
    json.dump({"$schema":SCH_VER,"version":"2.0.0"},
              open(os.path.join(DEFN,'version.json'),'w',encoding='utf-8'),indent=2)
    # resources
    A=str(ASSET_DIR)
    imgs=['bg.png','mark.png','accent_red.png','accent_cyan.png','accent_amber.png','accent_line.png']+['ic_%s_%s.png'%(n,s) for n in ['pulse','circuit','lab','driver','team','era','flag','garage','globe'] for s in ['on','off']]
    for f in imgs: shutil.copy(os.path.join(A,f),os.path.join(RES,f))
    json.dump(THEME,open(os.path.join(RES,'ThemeApex'),'w',encoding='utf-8'),indent=2,ensure_ascii=False)
    # EVERY image referenced by a visual must be declared here, otherwise Power BI
    # shows the "broken image" icon even when the file is present in the folder
    items=[{"name":f,"path":f,"type":"Image"} for f in imgs]
    items.append({"name":"ThemeApex","path":"ThemeApex","type":"CustomTheme"})
    rep={"$schema":SCH_REPORT,
      "themeCollection":{
        "baseTheme":{"name":"Fluent2-CY26SU08","reportVersionAtImport":{"visual":"2.12.0","report":"3.4.0","page":"2.3.1"},"type":"SharedResources"},
        "customTheme":{"name":"ThemeApex","reportVersionAtImport":{"visual":"2.12.0","report":"3.4.0","page":"2.3.1"},"type":"RegisteredResources"}},
      "objects":{"section":[{"properties":{"verticalAlignment":S('Top')}}],
                 "outspacePane":[{"properties":{"expanded":B(False)}}]},
      "resourcePackages":[
        {"name":"SharedResources","type":"SharedResources",
         "items":[{"name":"Fluent2-CY26SU08","path":"BaseThemes/Fluent2-CY26SU08.json","type":"BaseTheme"}]},
        {"name":"RegisteredResources","type":"RegisteredResources","items":items}],
      "settings":{"useStylableVisualContainerHeader":True,"exportDataMode":"AllowSummarized",
                  "defaultDrillFilterOtherVisuals":True,"allowChangeFilterTypes":True,
                  "useEnhancedTooltips":True,"useDefaultAggregateDisplayName":True}}
    json.dump(rep,open(os.path.join(DEFN,'report.json'),'w',encoding='utf-8'),indent=2,ensure_ascii=False)
    json.dump({"$schema":SCH_PBIR,"version":"4.0","datasetReference":{"byPath":{"path":"../%s.SemanticModel"%NAME}}},
              open(os.path.join(RP,'definition.pbir'),'w',encoding='utf-8'),indent=2)
    json.dump({"$schema":"https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
               "metadata":{"type":"Report","displayName":NAME},
               "config":{"version":"2.0","logicalId":guid5('platform/report')}},
              open(os.path.join(RP,'.platform'),'w',encoding='utf-8'),indent=2)
    n=sum(len(p.v) for p in PAGES)
    print('%d pages, %d visuals'%(len(PAGES),n))
    for p in PAGES: print('  %-3s %-18s %3d visuals'%(p.name,p.display,len(p.v)))

if __name__=='__main__':
    write_report()
