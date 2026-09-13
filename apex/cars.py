# -*- coding: utf-8 -*-
"""Square SVG thumbnails (v12) returned as data URIs for image columns in the model.
   Power BI fits every image into a square of side imageHeight, so all drawings are square.
   Each team gets its own livery (colour + pattern), each driver his own helmet.
   Original artwork: no brand logo or photograph is reproduced."""
def uri(s): return 'data:image/svg+xml;utf8,'+s
def hx(c): return c.replace('#','%23')
W_='%23FFFFFF'; K_='%230A0D12'; D_='%23080B12'; G_='%23596276'

# ============================== CAR ==================================
def car(colour, abbr='', accent='#F2F5FA', pattern='edge', w=128, h=128):
    """Single-seater seen head-on, with the team's own livery."""
    c=hx(colour); a=hx(accent)
    BODY="M24 92 C24 74 40 62 64 62 C88 62 104 74 104 92 Z"
    P=[]
    P.append("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 128 128' width='%d' height='%d'>"%(w,h))
    P.append("<defs>"
      "<linearGradient id='g' x1='0' y1='0' x2='0' y2='1'>"
      "<stop offset='0' stop-color='"+c+"' stop-opacity='0.46'/>"
      "<stop offset='1' stop-color='"+c+"' stop-opacity='0.07'/></linearGradient>"
      "<linearGradient id='b' x1='0' y1='0' x2='1' y2='1'>"
      "<stop offset='0' stop-color='"+c+"'/><stop offset='1' stop-color='"+c+"' stop-opacity='0.74'/></linearGradient>"
      "<clipPath id='cb'><path d='"+BODY+"'/></clipPath></defs>")
    # background
    P.append("<rect x='1.5' y='1.5' width='125' height='125' rx='16' fill='url(%23g)'/>")
    P.append("<rect x='1.5' y='1.5' width='125' height='125' rx='16' fill='none' stroke='"+c+"' stroke-width='3'/>")
    P.append("<path d='M96 4 L126 4 L126 22 Z' fill='"+W_+"' fill-opacity='0.10'/>")
    P.append("<path d='M4 118 L4 100 L34 124 L10 124 Z' fill='"+W_+"' fill-opacity='0.08'/>")
    # rear wheels
    for x in (6,101):
        P.append("<rect x='%d' y='50' width='21' height='46' rx='7' fill='%s'/>"%(x,K_))
        P.append("<rect x='%d' y='50' width='21' height='46' rx='7' fill='none' stroke='%s' stroke-opacity='0.35' stroke-width='2'/>"%(x,W_))
    # rear wing
    rw_main = a if pattern in ('split','edge') else c
    P.append("<rect x='31' y='20' width='66' height='11' rx='2' fill='"+hx(rw_main)+"'/>")
    P.append("<rect x='32' y='21.5' width='64' height='3' fill='"+W_+"' fill-opacity='0.7'/>")
    if pattern=='stripe':
        P.append("<rect x='58' y='20' width='12' height='11' fill='"+a+"'/>")
    for x in (27,95):
        P.append("<rect x='%d' y='19' width='6' height='24' rx='2' fill='%s'/>"%(x, a if pattern in ('chevron','edge') else c))
    # airbox
    P.append("<path d='M56 32 H72 L76 54 H52 Z' fill='"+(a if pattern in ('split','stripe') else "url(%23b)")+"'/>")
    P.append("<rect x='60' y='33' width='8' height='18' rx='4' fill='"+D_+"'/>")
    # body
    P.append("<path d='"+BODY+"' fill='url(%23b)'/>")
    P.append("<g clip-path='url(%23cb)'>")
    if pattern=='stripe':
        P.append("<rect x='57' y='58' width='14' height='40' fill='"+a+"'/>")
    elif pattern=='split':
        P.append("<path d='M24 92 C24 74 40 62 64 62 C88 62 104 74 104 92 L104 78 C96 68 82 62 64 62 C46 62 32 68 24 78 Z' fill='"+a+"'/>")
    elif pattern=='flash':
        P.append("<path d='M28 96 L54 58 L72 58 L46 96 Z' fill='"+a+"' fill-opacity='0.95'/>")
    elif pattern=='chevron':
        P.append("<path d='M30 96 L64 72 L98 96 L98 88 L64 64 L30 88 Z' fill='"+a+"'/>")
    elif pattern=='band':
        P.append("<rect x='20' y='80' width='90' height='9' fill='"+a+"'/>")
    elif pattern=='edge':
        P.append("<path d='"+BODY+"' fill='none' stroke='"+a+"' stroke-width='6'/>")
    P.append("</g>")
    P.append("<path d='"+BODY+"' fill='none' stroke='"+W_+"' stroke-opacity='0.30' stroke-width='2'/>")
    P.append("<path d='M34 78 C44 70 56 67 64 67 C72 67 84 70 94 78' fill='none' stroke='"+W_+"' stroke-opacity='0.42' stroke-width='2.4'/>")
    # front wheels
    for x in (17,87):
        P.append("<rect x='%d' y='60' width='24' height='42' rx='8' fill='%s'/>"%(x,K_))
        P.append("<rect x='%d' y='60' width='24' height='42' rx='8' fill='none' stroke='%s' stroke-opacity='0.5' stroke-width='2.2'/>"%(x,W_))
        P.append("<rect x='%d' y='76' width='14' height='11' rx='3' fill='%s'/>"%(x+5,G_))
    # cockpit + halo + helmet
    P.append("<path d='M50 64 C50 55 78 55 78 64 L78 74 H50 Z' fill='"+D_+"'/>")
    P.append("<circle cx='64' cy='63' r='7.5' fill='"+(a if pattern in ('flash','band','chevron') else W_)+"' fill-opacity='0.95'/>")
    P.append("<path d='M46 66 C46 50 82 50 82 66' fill='none' stroke='"+(a if pattern=='edge' else W_)+"' stroke-width='4.6' stroke-linecap='round'/>")
    P.append("<rect x='62' y='50' width='4' height='11' rx='2' fill='"+W_+"'/>")
    # nose
    P.append("<path d='M57 74 H71 L75 96 H53 Z' fill='"+(a if pattern=='stripe' else "url(%23b)")+"'/>")
    if pattern=='chevron':
        P.append("<path d='M54 92 L64 85 L74 92 L74 87 L64 80 L54 87 Z' fill='"+a+"'/>")
    # front wing
    fw = a if pattern in ('band','edge') else c
    P.append("<rect x='7' y='94' width='114' height='8' rx='3' fill='"+hx(fw)+"'/>")
    P.append("<rect x='8' y='95.5' width='112' height='2.6' fill='"+W_+"' fill-opacity='0.8'/>")
    P.append("<rect x='11' y='103' width='106' height='5' rx='2.5' fill='"+(a if pattern=='flash' else c)+"' fill-opacity='0.9'/>")
    for x in (7,115):
        P.append("<path d='M%d 92 L%d 92 L%d 108 L%d 108 Z' fill='%s'/>"%(x,x+6,x+6,x, a if pattern in ('split','chevron') else c))
    if abbr:
        P.append("<text x='64' y='123' font-family='Segoe UI,Arial' font-size='16' font-weight='700' fill='"+W_+"' fill-opacity='0.95' text-anchor='middle' letter-spacing='2.5'>"+abbr+"</text>")
    P.append("</svg>")
    return uri(''.join(P))

# ============================== HELMET ==============================
SHELL="M6 54 C6 24 24 7 48 7 C72 7 90 24 90 50 L90 68 C90 79 82 85 71 85 L23 85 C13 85 6 77 6 65 Z"
def helmet(colour, number=None, accent='#E9EDF5', pattern='crown', abbr=None, variant=0, w=96, h=96):
    """Helmet in profile: team colour, driver-specific pattern, team badge, race number."""
    c=hx(colour); a=hx(accent)
    P=["<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 96 96' width='%d' height='%d'>"%(w,h)]
    P.append("<defs><clipPath id='s'><path d='"+SHELL+"'/></clipPath>"
             "<linearGradient id='f' x1='0' y1='0' x2='1' y2='0'>"
             "<stop offset='0' stop-color='"+a+"'/><stop offset='1' stop-color='"+a+"' stop-opacity='0'/></linearGradient></defs>")
    P.append("<path d='"+SHELL+"' fill='"+c+"'/>")
    P.append("<g clip-path='url(%23s)'>")
    if pattern=='crown':
        P.append("<path d='M2 44 C6 20 24 2 48 2 C72 2 92 20 94 42 L94 28 C88 12 70 -4 48 -4 C26 -4 8 12 2 28 Z' fill='"+a+"'/>")
        P.append("<path d='M0 30 C8 12 26 0 48 0 C70 0 88 12 96 30 L96 22 C88 6 70 -6 48 -6 C26 -6 8 6 0 22 Z' fill='"+a+"'/>")
        P.append("<rect x='0' y='8' width='96' height='16' fill='"+a+"'/>")
    elif pattern=='chevron':
        P.append("<path d='M10 8 L52 34 L10 60 L10 44 L28 34 L10 24 Z' fill='"+a+"'/>")
    elif pattern=='split':
        P.append("<rect x='50' y='0' width='46' height='96' fill='"+a+"'/>")
    elif pattern=='stripes':
        for yy in (10,24,38):
            P.append("<path d='M0 %d C20 %d 60 %d 96 %d L96 %d C60 %d 20 %d 0 %d Z' fill='%s'/>"
                     %(yy,yy-4,yy-8,yy-10,yy-3,yy-1,yy+3,yy+7,a))
    elif pattern=='halo':
        P.append("<path d='M14 42 C28 28 60 26 88 34 L88 62 C60 66 28 66 14 60 Z' fill='"+a+"'/>")
    elif pattern=='star':
        P.append("<rect x='0' y='0' width='96' height='30' fill='"+a+"' fill-opacity='0.85'/>")
        P.append("<polygon points='34,60 38,72 51,72 41,79 45,91 34,84 23,91 27,79 17,72 30,72' fill='"+a+"'/>")
    elif pattern=='wedge':
        P.append("<path d='M0 0 L52 0 L20 96 L0 96 Z' fill='"+a+"'/>")
        P.append("<path d='M58 0 L72 0 L40 96 L26 96 Z' fill='"+a+"' fill-opacity='0.55'/>")
    elif pattern=='checker':
        for i in range(8):
            for j in range(2):
                if (i+j)%2==0:
                    P.append("<rect x='%d' y='%d' width='12' height='11' fill='%s'/>"%(i*12, 4+j*11, a))
    P.append("</g>")
    # highlight, visor, vent strip
    P.append("<path d='M6 54 C6 24 24 7 48 7 C61 7 72 11 80 20 L24 38 Z' fill='"+W_+"' fill-opacity='0.20'/>")
    P.append("<path d='M19 45 C31 33 59 31 83 38 L83 58 C59 61 31 61 19 57 Z' fill='"+D_+"'/>")
    P.append("<path d='M21 44 C33 34 59 33 82 39 L82 44 C59 37 34 39 23 47 Z' fill='%237FD4FF' fill-opacity='0.42'/>")
    P.append("<rect x='6' y='66' width='84' height='6' fill='"+(a if variant in (1,3) else W_)+"' fill-opacity='0.62'/>")
    if variant >= 2:
        P.append("<g clip-path='url(%23s)'><rect x='0' y='76' width='96' height='5' fill='"+a+"' fill-opacity='0.9'/></g>")
    P.append("<path d='"+SHELL+"' fill='none' stroke='"+W_+"' stroke-opacity='0.40' stroke-width='2.6'/>")
    # team badge on the back of the helmet
    if abbr:
        P.append("<path d='M9 18 H41 L41 34 C41 41 32 45 25 48 C18 45 9 41 9 34 Z' fill='"+K_+"' fill-opacity='0.88'/>")
        P.append("<path d='M9 18 H41 L41 34 C41 41 32 45 25 48 C18 45 9 41 9 34 Z' fill='none' stroke='"+W_+"' stroke-opacity='0.8' stroke-width='2'/>")
        P.append("<text x='25' y='34' font-family='Segoe UI,Arial' font-size='13' font-weight='700' fill='"+W_+"' text-anchor='middle' letter-spacing='0.5'>"+abbr+"</text>")
    if number:
        P.append("<rect x='54' y='68' width='36' height='24' rx='6' fill='"+K_+"' fill-opacity='0.85'/>")
        P.append("<text x='72' y='87' font-family='Segoe UI,Arial' font-size='20' font-weight='700' fill='"+W_+"' text-anchor='middle'>"+str(number)+"</text>")
    P.append("</svg>")
    return uri(''.join(P))

# ============================== TEAM CREST ==============================
CREST = "M48 3 L89 17 L89 51 C89 74 70 89 48 93 C26 89 7 74 7 51 L7 17 Z"

def _device(pattern, a):
    """Central device of the crest, matched to the team's livery pattern."""
    if pattern=='stripe':
        return ("<rect x='39' y='16' width='18' height='54' rx='3' fill='"+a+"'/>"
                "<rect x='27' y='24' width='7' height='38' rx='3' fill='"+a+"' fill-opacity='0.6'/>"
                "<rect x='62' y='24' width='7' height='38' rx='3' fill='"+a+"' fill-opacity='0.6'/>")
    if pattern=='split':
        return ("<path d='M48 17 A26 26 0 0 1 48 69 Z' fill='"+a+"' fill-opacity='0.55'/>"
                "<path d='M48 17 A26 26 0 0 0 48 69 Z' fill='"+a+"'/>"
                "<rect x='20' y='40' width='56' height='6' fill='"+W_+"' fill-opacity='0.85'/>")
    if pattern=='flash':
        return ("<path d='M58 14 L30 46 L45 46 L38 72 L67 39 L51 39 Z' fill='"+a+"'/>"
                "<path d='M58 14 L30 46 L45 46 L38 72 L67 39 L51 39 Z' fill='none' stroke='"+W_+"' stroke-opacity='0.55' stroke-width='2'/>")
    if pattern=='chevron':
        return ("<path d='M48 15 L76 41 L76 54 L48 28 L20 54 L20 41 Z' fill='"+a+"'/>"
                "<path d='M48 43 L76 69 L64 69 L48 54 L32 69 L20 69 Z' fill='"+a+"' fill-opacity='0.62'/>")
    if pattern=='band':
        return ("<rect x='18' y='22' width='60' height='10' rx='5' fill='"+a+"'/>"
                "<rect x='24' y='39' width='48' height='10' rx='5' fill='"+a+"' fill-opacity='0.78'/>"
                "<rect x='30' y='56' width='36' height='10' rx='5' fill='"+a+"' fill-opacity='0.56'/>")
    # edge
    return ("<circle cx='48' cy='43' r='25' fill='none' stroke='"+a+"' stroke-width='11'/>"
            "<rect x='42' y='8' width='12' height='24' fill='"+K_+"'/>"
            "<rect x='43' y='39' width='10' height='9' rx='3' fill='"+a+"'/>")

def crest(colour, accent='#F2F5FA', pattern='edge', bars=('#5A6479','#9AA5B8','#5A6479'), w=96, h=96):
    """Team crest: shield, central device matched to the livery, national colour bar.
       Original drawing without lettering: no brand logo is reproduced."""
    c=hx(colour); a=hx(accent); b=[hx(x) for x in bars]
    P=["<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 96 96' width='%d' height='%d'>"%(w,h)]
    P.append("<defs><clipPath id='k'><path d='"+CREST+"'/></clipPath>"
             "<linearGradient id='e' x1='0' y1='0' x2='0.6' y2='1'>"
             "<stop offset='0' stop-color='"+c+"'/><stop offset='1' stop-color='"+c+"' stop-opacity='0.55'/>"
             "</linearGradient></defs>")
    P.append("<path d='"+CREST+"' fill='%230C1017'/>")
    P.append("<path d='"+CREST+"' fill='url(%23e)'/>")
    P.append("<g clip-path='url(%23k)'>")
    P.append("<path d='M7 17 H89 L89 30 C70 22 26 22 7 30 Z' fill='"+W_+"' fill-opacity='0.16'/>")
    P.append(_device(pattern, a))
    for i,col in enumerate(b):
        P.append("<rect x='%d' y='72' width='28' height='10' fill='%s'/>"%(6+i*28, col))
    P.append("<rect x='6' y='72' width='84' height='2' fill='"+K_+"' fill-opacity='0.45'/>")
    P.append("</g>")
    P.append("<path d='"+CREST+"' fill='none' stroke='"+W_+"' stroke-opacity='0.92' stroke-width='4'/>")
    P.append("<path d='"+CREST+"' fill='none' stroke='"+K_+"' stroke-opacity='0.5' stroke-width='1.6'/>")
    P.append("</svg>")
    return uri(''.join(P))

# ============================== BADGE ==============================
def badge(abbr, colour, w=96, h=96, accent=None):
    c=hx(colour); a=hx(accent) if accent else W_
    return uri(
 "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 96 96' width='"+str(w)+"' height='"+str(h)+"'>"
 "<defs><linearGradient id='b' x1='0' y1='0' x2='1' y2='1'>"
 "<stop offset='0' stop-color='"+c+"' stop-opacity='1'/><stop offset='1' stop-color='"+c+"' stop-opacity='0.6'/>"
 "</linearGradient></defs>"
 "<path d='M8 5 H88 L88 60 C88 76 70 86 48 93 C26 86 8 76 8 60 Z' fill='url(%23b)'/>"
 "<rect x='8' y='5' width='80' height='9' fill='"+a+"' fill-opacity='0.75'/>"
 "<path d='M8 5 H88 L88 60 C88 76 70 86 48 93 C26 86 8 76 8 60 Z' fill='none' stroke='"+W_+"' stroke-opacity='0.7' stroke-width='3.4'/>"
 "<text x='48' y='58' font-family='Segoe UI,Arial' font-size='33' font-weight='700' fill='"+W_+"' text-anchor='middle' letter-spacing='1'>"+abbr+"</text>"
 "</svg>")
