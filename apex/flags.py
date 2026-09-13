# -*- coding: utf-8 -*-
"""Hand-drawn SVG national flags returned as data URIs.

flag_uri(country) yields a rounded 60x60 badge for the FlagSvg image columns
written by svg_columns.py; nothing is written to disk by this module.
"""
W,H=60,40
def rect(x,y,w,h,c): return '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>'%(x,y,w,h,c)
def hband(cs):
    n=len(cs); h=H/n
    return ''.join(rect(0,round(i*h,2),W,round(h,2),c) for i,c in enumerate(cs))
def vband(cs):
    n=len(cs); w=W/n
    return ''.join(rect(round(i*w,2),0,round(w,2),H,c) for i,c in enumerate(cs))
def circ(cx,cy,r,c): return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>'%(cx,cy,r,c)
def star(cx,cy,r,c,rot=0):
    import math
    p=[]
    for i in range(10):
        rr=r if i%2==0 else r*0.382
        a=math.radians(-90+rot+i*36)
        p.append('%.2f,%.2f'%(cx+rr*math.cos(a),cy+rr*math.sin(a)))
    return '<polygon points="%s" fill="%s"/>'%(' '.join(p),c)
def crescent(cx,cy,r,c,bg):
    return circ(cx,cy,r,c)+circ(cx+r*0.35,cy,r*0.80,bg)
def nordic(bg,cross,off=None):
    ox = off if off else W*0.30
    return rect(0,0,W,H,bg)+rect(ox-3,0,6,H,cross)+rect(0,H/2-3,W,6,cross)

UK = (rect(0,0,W,H,'#012169')
 +'<path d="M0,0 60,40 M60,0 0,40" stroke="%23FFF" stroke-width="8"/>'
 +'<path d="M0,0 60,40" stroke="%23C8102E" stroke-width="3.2"/>'
 +'<path d="M60,0 0,40" stroke="%23C8102E" stroke-width="3.2"/>'
 +rect(0,14,W,12,'#FFF')+rect(24,0,12,H,'#FFF')
 +rect(0,16.4,W,7.2,'#C8102E')+rect(26.4,0,7.2,H,'#C8102E'))

def canton_uk(s=0.5):
    return '<g transform="scale(%s)">%s</g>'%(s,UK)

FLAGS={
'Argentina': hband(['#74ACDF','#FFFFFF','#74ACDF'])+circ(30,20,4,'#F6B40E'),
'Australia': rect(0,0,W,H,'#012169')+canton_uk(0.5)+star(12,31,3.2,'#FFFFFF')
    +star(46,9,2.2,'#FFFFFF')+star(52,18,2,'#FFFFFF')+star(44,24,2,'#FFFFFF')+star(49,31,2.2,'#FFFFFF')+star(47.5,19,1.2,'#FFFFFF'),
'Austria': hband(['#ED2939','#FFFFFF','#ED2939']),
'Azerbaijan': hband(['#00B5E2','#EF3340','#00AF66'])+crescent(28,20,5,'#FFFFFF','#EF3340')+star(35,20,2.4,'#FFFFFF'),
'Bahrain': rect(0,0,W,H,'#CE1126')+'<polygon points="0,0 18,0 26,4 18,8 26,12 18,16 26,20 18,24 26,28 18,32 26,36 18,40 0,40" fill="%23FFFFFF"/>',
'Belgium': vband(['#000000','#FAE042','#ED2939']),
'Brazil': rect(0,0,W,H,'#009B3A')+'<polygon points="30,4 55,20 30,36 5,20" fill="%23FEDF00"/>'+circ(30,20,8,'#002776')
    +'<path d="M22.6,17.6 Q30,26 37.4,17.6" stroke="%23FFFFFF" stroke-width="2.6" fill="none"/>',
'Canada': rect(0,0,W,H,'#FF0000')+rect(15,0,30,H,'#FFFFFF')
    +'<path d="M30,6 L31.6,12.6 L35.4,10.9 L34.4,15.2 L38.6,14.3 L37.4,17.4 L43,17.9 L39.9,20.6 L41,22.4 L35.4,23.6 L36.4,27.6 L32.2,26.6 L31.6,29.2 L30,27.4 L28.4,29.2 L27.8,26.6 L23.6,27.6 L24.6,23.6 L19,22.4 L20.1,20.6 L17,17.9 L22.6,17.4 L21.4,14.3 L25.6,15.2 L24.6,10.9 L28.4,12.6 Z" fill="%23FF0000"/>'
    +rect(29.4,27,1.2,7,'#FF0000'),
'China': rect(0,0,W,H,'#DE2910')+star(12,11,5.5,'#FFDE00')+star(23,4.5,2,'#FFDE00')+star(27,9,2,'#FFDE00')+star(27,15,2,'#FFDE00')+star(23,19.5,2,'#FFDE00'),
'Denmark': nordic('#C60C30','#FFFFFF',18),
'Finland': nordic('#FFFFFF','#003580',18),
'France': vband(['#002395','#FFFFFF','#ED2939']),
'Germany': hband(['#000000','#DD0000','#FFCE00']),
'Hungary': hband(['#CE2939','#FFFFFF','#477050']),
'India': hband(['#FF9933','#FFFFFF','#138808'])+'<circle cx="30" cy="20" r="5" fill="none" stroke="%23000080" stroke-width="1.2"/>'+circ(30,20,1.1,'#000080'),
'Indonesia': hband(['#CE1126','#FFFFFF']),
'Italy': vband(['#008C45','#F4F5F0','#CD212A']),
'Japan': rect(0,0,W,H,'#FFFFFF')+circ(30,20,10,'#BC002D'),
'Malaysia': ''.join(rect(0,round(i*H/7,2),W,round(H/7,2),'#CC0001' if i%2==0 else '#FFFFFF') for i in range(7))
    +rect(0,0,26,round(H*4/7,2),'#010066')+crescent(10,10.5,4.6,'#FFCC00','#010066')+star(17.5,10.5,2.8,'#FFCC00'),
'Mexico': vband(['#006847','#FFFFFF','#CE1126'])+circ(30,20,4,'#8B5A2B'),
'Monaco': hband(['#CE1126','#FFFFFF']),
'Netherlands': hband(['#AE1C28','#FFFFFF','#21468B']),
'New Zealand': rect(0,0,W,H,'#012169')+canton_uk(0.5)+star(46,10,2.4,'#C8102E')+star(52,20,2.4,'#C8102E')+star(43,23,2.4,'#C8102E')+star(48,31,2.4,'#C8102E'),
'Poland': hband(['#FFFFFF','#DC143C']),
'Portugal': rect(0,0,W,H,'#DA291C')+rect(0,0,24,H,'#046A38')+circ(24,20,6,'#FFE900')+circ(24,20,4,'#DA291C'),
'Qatar': rect(0,0,W,H,'#8A1538')+'<polygon points="0,0 16,0 24,4 16,8 24,12 16,16 24,20 16,24 24,28 16,32 24,36 16,40 0,40" fill="%23FFFFFF"/>',
'Russia': hband(['#FFFFFF','#0039A6','#D52B1E']),
'Saudi Arabia': rect(0,0,W,H,'#165D31')+rect(12,25,36,2.4,'#FFFFFF')+'<path d="M13,15 Q30,10 47,15" stroke="%23FFFFFF" stroke-width="2.6" fill="none"/>',
'Singapore': hband(['#ED2939','#FFFFFF'])+crescent(14,10,6,'#FFFFFF','#ED2939')+star(24,6,1.7,'#FFFFFF')+star(28,10,1.7,'#FFFFFF')+star(24,14,1.7,'#FFFFFF')+star(20,12.5,1.7,'#FFFFFF')+star(20,7.5,1.7,'#FFFFFF'),
'Spain': rect(0,0,W,H,'#AA151B')+rect(0,10,W,20,'#F1BF00'),
'Sweden': nordic('#006AA7','#FECC00',18),
'Switzerland': rect(0,0,W,H,'#DA291C')+rect(26.5,10,7,20,'#FFFFFF')+rect(20,16.5,20,7,'#FFFFFF'),
'Thailand': rect(0,0,W,H,'#A51931')+rect(0,6.7,W,26.6,'#F4F5F8')+rect(0,13.3,W,13.4,'#2D2A4A'),
'Turkey': rect(0,0,W,H,'#E30A17')+crescent(22,20,7,'#FFFFFF','#E30A17')+star(34,20,3.2,'#FFFFFF'),
'United Arab Emirates': rect(0,0,W,H,'#00732F')+rect(15,13.3,45,13.4,'#FFFFFF')+rect(15,26.7,45,13.3,'#000000')+rect(0,0,15,H,'#FF0000'),
'United Kingdom': UK,
'United States of America': ''.join(rect(0,round(i*H/13,2),W,round(H/13,2),'#B22234' if i%2==0 else '#FFFFFF') for i in range(13))
    +rect(0,0,27,round(H*7/13,2),'#3C3B6E')
    +''.join(star(round(3.4+5.0*(k%5),2),round(3.4+4.6*(k//5),2),2.15,'#FFFFFF') for k in range(20)),
'Venezuela': hband(['#FFCC00','#00247D','#CF142B'])
    +''.join(star(round(30+9*__import__('math').cos(__import__('math').radians(200+20*k)),2),
                  round(24+9*__import__('math').sin(__import__('math').radians(200+20*k)),2),1.3,'#FFFFFF') for k in range(8)),
}

def flag_uri(country):
    body=FLAGS.get(country)
    if not body: return ''
    svg=('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 60" width="60" height="60">'
         '<clipPath id="c"><rect x="0" y="3" width="60" height="54" rx="5"/></clipPath>'
         '<rect x="0" y="3" width="60" height="54" rx="5" fill="#0E1219"/>'
         '<g clip-path="url(%23c)"><g transform="translate(0,3) scale(1,1.35)">'+body+'</g></g>'
         '<rect x="1.4" y="4.4" width="57.2" height="51.2" rx="4" fill="none" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="2.8"/>'
         '<rect x="0.2" y="3.2" width="59.6" height="53.6" rx="5" fill="none" stroke="#000000" stroke-opacity="0.55" stroke-width="1.4"/></svg>')
    return 'data:image/svg+xml;utf8,'+svg.replace('#','%23').replace('"',"'").replace('\n','')
if __name__=='__main__':
    for k in FLAGS: 
        u=flag_uri(k); assert '#' not in u, k
    print(len(FLAGS),'flags, max length', max(len(flag_uri(k)) for k in FLAGS))
