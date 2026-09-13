# -*- coding: utf-8 -*-
"""Helpers for writing the PBIR report layer (schemas taken from CFO Cockpit)."""
import json, os
SCH_VIS="https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json"
SCH_PAGE="https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
SCH_PAGES="https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json"
SCH_REPORT="https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json"
SCH_VER="https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json"
SCH_PBIR="https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json"

# ---- palette ----
# v32 "Grand Prix": bright coral, lighter and larger text, translucent panels
INK='#F4F6FA'; MUTED='#C4CBD8'; DIM='#8F99AB'; LINE='#2C3446'
PANEL='#12161F'; PANEL2='#0D1017'; KPIBG='#171C2A'; KPILINE='#3A4358'; RED='#F0503C'; CYAN='#22D3EE'; AMBER='#F5B942'
GREEN='#3BD07A'; VIOLET='#A78BFA'; HDR='#F0503C'; GRIDC='#C9463A'
RAIL_W=120; CONTENT_X0=144; CONTENT_K=(1576-CONTENT_X0)/1480.0
PANEL_ALPHA=14   # panel transparency: the circuit background shows through
def fz(s,k=1.3): return int(round(float(s)*k))   # v40: INTEGER required, Power BI ignores a decimal axis size (13.7 -> falls back to 9 pt)
# v37: full CSS font stacks, as Power BI writes them itself. A bare name ("DIN",
# "Segoe UI Bold") is not resolved by the engine and falls back to serif; Power BI's
# web fonts are named wf_standard-font (DIN) and wf_segoe-ui_*.
FT="'Segoe UI', wf_segoe-ui_normal, helvetica, arial, sans-serif"
FTS="'Segoe UI Semibold', wf_segoe-ui_semibold, helvetica, arial, sans-serif"
FTB="'Segoe UI Bold', wf_segoe-ui_bold, helvetica, arial, sans-serif"
FD="'DIN', wf_standard-font, helvetica, arial, sans-serif"; FM="Consolas, 'Courier New', monospace"

def L(v):    return {"expr":{"Literal":{"Value":v}}}
def S(s):    return L("'%s'"%str(s).replace("'","''"))
def N(x):    return L("%sD"%x)
def B(b):    return L("true" if b else "false")
def C(hexv): return {"solid":{"color":S(hexv)}}
def Cm(meas,entity='Metrics'): return {"solid":{"color":{"expr":{"Measure":{"Expression":{"SourceRef":{"Entity":entity}},"Property":meas}}}}}
def P(**kw):  return [{"properties":kw}]

def mfield(name,entity='Metrics'):
    return {"Measure":{"Expression":{"SourceRef":{"Entity":entity}},"Property":name}}
def cfield(entity,prop):
    return {"Column":{"Expression":{"SourceRef":{"Entity":entity}},"Property":prop}}
def pm(name,entity='Metrics'):
    return {"field":mfield(name,entity),"queryRef":"%s.%s"%(entity,name),"nativeQueryRef":name}
def pc(entity,prop,active=None):
    d={"field":cfield(entity,prop),"queryRef":"%s.%s"%(entity,prop),"nativeQueryRef":prop}
    if active is not None: d["active"]=active
    return d

TOOLTIP_PAGE=None   # name of the empty tooltip page, set by gen_report

VC_OFF={"background":P(show=B(False)),"border":P(show=B(False)),"dropShadow":P(show=B(False)),
        "visualHeader":P(show=B(False)),"title":P(show=B(False)),"subTitle":P(show=B(False))}

def vc_panel(title=None,radius=14,bg=PANEL,alpha=None,border=LINE,tcolor=INK,tsize=16,tfont=FTS,sub=None):
    if alpha is None: alpha=PANEL_ALPHA
    o={"background":P(show=B(True),color=C(bg),transparency=N(alpha)),
       "border":P(show=B(True),color=C(border),radius=N(radius)),
       "dropShadow":P(show=B(False)),
       "visualHeader":P(show=B(False)),
       "subTitle":P(show=B(False))}
    if title:
        o["title"]=[{"properties":{"show":B(True),"text":S(title),"fontColor":C(tcolor),
                     "fontSize":N(tsize),"fontFamily":S(tfont),"alignment":S("left"),
                     "titleWrap":B(False)}}]
    else:
        o["title"]=P(show=B(False))
    if sub:
        o["subTitle"]=[{"properties":{"show":B(True),"text":S(sub),"fontColor":C(DIM),
                        "fontSize":N(12),"fontFamily":S(FT),"alignment":S("left")}}]
    return o

class Page:
    def __init__(self,name,display,bgimage=True,tooltip=False,size=(1600,900)):
        self.name=name; self.display=display; self.v=[]; self.z=1000; self.bgimage=bgimage
        self.tooltip=tooltip; self.size=size
    def add(self,visual_type,x,y,w,h,objects=None,query=None,vc=None,tag='v',extra=None,z=None,tooltip=True,filterConfig=None):
        # v33: the rail grows from 72 to 120 px; the content area (x>=84, formerly 96..1576)
        # is compressed horizontally by CONTENT_K so that it starts at CONTENT_X0.
        if tag!='bg' and x>=84:
            x=int(round(CONTENT_X0+(x-96)*CONTENT_K)); w=int(round(w*CONTENT_K))
            if objects and 'columnWidth' in objects:
                for cw in objects['columnWidth']:
                    v=cw['properties']['value']['expr']['Literal']['Value']
                    cw['properties']['value']=N(int(round(float(v.rstrip('D'))*CONTENT_K)))
        self.z+=1000
        idx=len(self.v)
        nm="%s_%03d_%s"%(self.name,idx,tag)
        vis={"visualType":visual_type}
        if query: vis["query"]=query
        if objects is not None: vis["objects"]=objects
        _vc = dict(vc) if vc is not None else dict(VC_OFF)
        # No tooltip on data visuals: on image columns, Power BI used to show the raw
        # SVG code on hover. The rail buttons keep their tooltip, which carries the
        # page name.
        # v57: tooltips enabled everywhere, except on tables that carry an image column
        # (Power BI would show the image's "data:image" code on hover there)
        if visual_type != 'actionButton':
            _vc["visualTooltip"]=P(show=B(bool(tooltip)))
        vis["visualContainerObjects"]=_vc
        if extra: vis.update(extra)
        if visual_type not in ('textbox','image','actionButton','shape'):
            vis["drillFilterOtherVisuals"]=True
        d={"$schema":SCH_VIS,"name":nm,
           "position":{"x":x,"y":y,"z":(z if z is not None else self.z),"width":w,"height":h,"tabOrder":idx*1000},
           "visual":vis}
        if filterConfig: d["filterConfig"]=filterConfig
        self.v.append(d); return nm
    # ---------- primitives ----------
    def text(self,x,y,w,h,runs,align='left',valign='middle',tag='tx',bg=None,radius=None,border=None):
        if isinstance(runs,str): runs=[dict(t=runs)]
        tr=[]
        for r in runs:
            st={"fontFamily":r.get('font',FT),"fontSize":"%spt"%r.get('size',11),"color":r.get('color',INK)}
            if r.get('bold'): st["fontWeight"]="bold"
            if r.get('italic'): st["fontStyle"]="italic"
            tr.append({"value":r['t'],"textStyle":st})
        para={"textRuns":tr,"horizontalTextAlignment":align}
        objs={"general":P(paragraphs=[para])}
        vc=dict(VC_OFF)
        if bg:
            vc=dict(vc); vc["background"]=P(show=B(True),color=C(bg),transparency=N(0))
            if border: vc["border"]=P(show=B(True),color=C(border),radius=N(radius or 12))
            elif radius: vc["border"]=P(show=B(True),color=C(bg),radius=N(radius))
        return self.add('textbox',x,y,w,h,objects=objs,vc=vc,tag=tag)
    def panel(self,x,y,w,h,bg=PANEL,radius=14,border=LINE,alpha=None,tag='pn'):
        if alpha is None: alpha=PANEL_ALPHA
        vc={"background":P(show=B(True),color=C(bg),transparency=N(alpha)),
            "border":P(show=B(True),color=C(border),radius=N(radius)),
            "dropShadow":P(show=B(False)),"visualHeader":P(show=B(False)),
            "title":P(show=B(False)),"subTitle":P(show=B(False))}
        objs={"general":P(paragraphs=[{"textRuns":[{"value":" ","textStyle":{"fontFamily":FT,"fontSize":"8pt","color":INK}}]}])}
        return self.add('textbox',x,y,w,h,objects=objs,vc=vc,tag=tag)
    def image(self,x,y,w,h,resource,scaling='Fit',tag='im'):
        objs={"general":P(imageUrl={"expr":{"ResourcePackageItem":{"PackageName":"RegisteredResources","PackageType":1,"ItemName":resource}}}),
              "imageScaling":P(imageScalingType=S(scaling))}
        return self.add('image',x,y,w,h,objects=objs,tag=tag)
    def navbtn(self,x,y,w,h,target,tip,tag='nv'):
        off=P(show=B(False))
        st=lambda: [{"properties":{"show":B(False)}}]+[{"properties":{"show":B(False)},"selector":{"id":i}} for i in ('default','hover','selected','disabled')]
        fill=[{"properties":{"show":B(True),"transparency":N(100),"fillColor":C('#FFFFFF')}}]+[
              {"properties":{"show":B(True),"transparency":N(100 if i!='hover' else 88),"fillColor":C('#FFFFFF' if i!='hover' else RED)},"selector":{"id":i}} for i in ('default','hover','selected','disabled')]
        objs={"text":st(),"icon":st(),"outline":st(),"glow":st(),"shadow":st(),"fill":fill}
        vc={"title":P(show=B(False)),"background":P(show=B(False)),"border":P(show=B(False)),
            "dropShadow":P(show=B(False)),
            "visualLink":P(show=B(True),type=S('PageNavigation'),navigationSection=S(target),tooltip=S(tip))}
        return self.add('actionButton',x,y,w,h,objects=objs,vc=vc,tag=tag,extra={"drillFilterOtherVisuals":True})
    def card(self,x,y,w,h,measure,size=34,color=INK,font=FD,units=None,prec=None,align=None,wrap=False,tag='kv',entity='Metrics'):
        lp={"color":C(color),"fontSize":N(int(round(size))),"fontFamily":S(font)}
        if units is not None: lp["labelDisplayUnits"]=N(units)
        if prec is not None: lp["labelPrecision"]=N(prec)
        if align: lp["alignment"]=S(align)
        objs={"labels":[{"properties":lp}],"categoryLabels":P(show=B(False)),"wordWrap":P(show=B(wrap))}
        q={"queryState":{"Values":{"projections":[pm(measure,entity)]}}}
        return self.add('card',x,y,w,h,objects=objs,query=q,tag=tag)
    def to_json(self):
        objs={}
        objs["background"]=P(color=C('#0A0C10'),transparency=N(0))
        objs["outspace"]=P(color=C('#05070B'),transparency=N(0))
        w,h=self.size
        d={"$schema":SCH_PAGE,"name":self.name,"displayName":self.display,
           "displayOption":"FitToPage","height":h,"width":w,"objects":objs}
        return d

def axis(show=True,color=MUTED,size=10,grid=False,gridcolor=LINE,title=False,units=None,font=FT,concat=None,invert=False,start=None,end=None):
    size=fz(size)
    p={"show":B(show),"labelColor":C(color),"fontSize":N(size),"fontFamily":S(font),
       "showAxisTitle":B(title),"gridlineShow":B(grid)}
    if grid: p["gridlineColor"]=C(gridcolor); p["gridlineThickness"]=N(1)
    if units is not None: p["labelDisplayUnits"]=N(units)
    if concat is not None: p["concatenateLabels"]=B(concat)
    if invert: p["invertAxis"]=B(True)
    if start is not None: p["start"]=N(start)
    if end is not None: p["end"]=N(end)
    return [{"properties":p}]
def legend(show=True,pos='TopCenter',size=10,color=MUTED):
    size=fz(size)
    return [{"properties":{"show":B(show),"position":S(pos),"labelColor":C(color),"fontSize":N(size),
             "fontFamily":S(FT),"showTitle":B(False)}}]
def labels(show=True,color=INK,size=10,units=None,prec=None,font=FT,pos=None):
    size=fz(size); font=FTS if font==FT else font
    p={"show":B(show),"color":C(color),"fontSize":N(size),"fontFamily":S(font)}
    if units is not None: p["labelDisplayUnits"]=N(units)
    if prec is not None: p["labelPrecision"]=N(prec)
    if pos: p["labelPosition"]=S(pos)
    return [{"properties":p}]
def fill_solid(hexv):
    return [{"properties":{"fill":C(hexv)}}]
def fill_measure(meas):
    return [{"properties":{"fill":Cm(meas)},"selector":{"data":[{"dataViewWildcard":{"matchingOption":0}}]}}]
def sortdef(field,direction='Descending',default=True):
    return {"sort":[{"field":field,"direction":direction}],"isDefaultSort":default}

def measure_filter(name,measure,kind,value):
    """Visual-level filter on a measure (syntax taken from WorldCup2026.Report, where it
       works). kind: 0 =, 1 >, 2 >=, 3 <, 4 <=."""
    return {"filters":[{"name":name,"field":mfield(measure),"type":"Advanced",
        "filter":{"Version":2,"From":[{"Name":"mp","Entity":"Metrics","Type":0}],
          "Where":[{"Condition":{"Comparison":{"ComparisonKind":kind,
            "Left":{"Measure":{"Expression":{"SourceRef":{"Source":"mp"}},"Property":measure}},
            "Right":{"Literal":{"Value":"%dL"%value}}}}}]}}]}
