# -*- coding: utf-8 -*-
"""Visual identity per team: primary colour, accent colour and livery pattern.
   Pure data module used by cars.py and svg_columns.py; it writes nothing itself.
   The colour combinations and geometric patterns are original: no brand logo is reproduced."""

# constructorId -> (primary, accent, pattern)
LIVERY = {
 'ferrari':      ('#E8002D','#111318','stripe'),
 'mercedes':     ('#00D2BE','#0B0E14','split'),
 'red-bull':     ('#3671C6','#E8002D','chevron'),
 'mclaren':      ('#FF8000','#1B4A8C','flash'),
 'alpine':       ('#0093CC','#FF87BC','band'),
 'aston-martin': ('#229971','#CEDC00','edge'),
 'williams':     ('#1868DB','#F2F5FA','stripe'),
 'haas':         ('#B6BABD','#E8002D','flash'),
 'kick-sauber':  ('#52E252','#0B0E14','split'),
 'racing-bulls': ('#6C98FF','#F2F5FA','chevron'),
 'rb':           ('#6C98FF','#12233F','band'),
 'alphatauri':   ('#4E7C9B','#F2F5FA','split'),
 'toro-rosso':   ('#2B4562','#E8002D','flash'),
 'alfa-romeo':   ('#C92D4B','#F2F5FA','edge'),
 'sauber':       ('#9B0000','#F2F5FA','band'),
 'audi':         ('#BB0A30','#0B0E14','split'),
 'cadillac':     ('#C9B037','#0B1A2E','stripe'),
 'renault':      ('#FFF500','#111318','flash'),
 'lotus-f1':     ('#E6C229','#111318','edge'),
 'force-india':  ('#F596C8','#FF8000','band'),
 'racing-point': ('#F596C8','#12233F','chevron'),
 'manor':        ('#D40000','#F2F5FA','stripe'),
 'marussia':     ('#B0000A','#F2F5FA','flash'),
 'caterham':     ('#0B572E','#FFF500','band'),
}
def livery(cid, fallback='#8A8F98'):
    return LIVERY.get(cid, (fallback,'#F2F5FA','edge'))

# national accent colour for helmets (dominant hue of the flag)
NAT = {
 'United Kingdom':'#C8102E','Germany':'#FFCE00','Netherlands':'#AE1C28','Spain':'#F1BF00',
 'France':'#002395','Italy':'#008C45','Finland':'#003580','Mexico':'#006847','Australia':'#012169',
 'Monaco':'#CE1126','Brazil':'#FEDF00','Japan':'#BC002D','Canada':'#FF0000','Denmark':'#C60C30',
 'Belgium':'#FAE042','Russia':'#0039A6','Sweden':'#FECC00','Thailand':'#2D2A4A','China':'#FFDE00',
 'United States of America':'#3C3B6E','Poland':'#DC143C','Argentina':'#74ACDF','New Zealand':'#012169',
 'Venezuela':'#FFCC00','Indonesia':'#CE1126','Switzerland':'#DA291C','Austria':'#ED2939',
 'India':'#FF9933','Malaysia':'#FFCC00','Colombia':'#FCD116','Ireland':'#169B62','Hungary':'#CE2939',
 'Portugal':'#046A38','South Africa':'#007A4D','Estonia':'#0072CE','Czechia':'#11457E',
}
PATTERNS = ('crown','chevron','split','stripes','halo','star','wedge','checker')

def _rgb(c):
    c=c.lstrip('#'); return int(c[0:2],16),int(c[2:4],16),int(c[4:6],16)
def _lum(c):
    r,g,b=_rgb(c); return (0.2126*r+0.7152*g+0.0722*b)/255
def _dist(a,b):
    ra,ga,ba=_rgb(a); rb,gb,bb=_rgb(b)
    return ((ra-rb)**2*0.30+(ga-gb)**2*0.59+(ba-bb)**2*0.11)**0.5

def contrast_accent(base, wanted, mini=78):
    """Make sure the accent stands out from the team colour.
       If the national hue is too close, fall back to white or charcoal."""
    if _dist(base, wanted) >= mini: return wanted
    return '#0B0E14' if _lum(base) > 0.55 else '#F2F5FA'

def helmet_style(driver_id, nation, team_colour=None):
    """Deterministic, stable pattern per driver, with an accent taken from his nationality."""
    h = 0
    for ch in driver_id: h = (h*131 + ord(ch)) & 0xFFFFFFFF
    acc = NAT.get(nation, '#E9EDF5')
    if team_colour: acc = contrast_accent(team_colour, acc)
    return PATTERNS[h % len(PATTERNS)], acc, (h >> 5) % 4

# national colour bars for teams (country the constructor is registered in)
COUNTRY_BARS = {
 'Austria':                  ('#ED2939','#FFFFFF','#ED2939'),
 'France':                   ('#002395','#FFFFFF','#ED2939'),
 'Germany':                  ('#000000','#DD0000','#FFCE00'),
 'India':                    ('#FF9933','#FFFFFF','#138808'),
 'Italy':                    ('#008C45','#F4F5F0','#CD212A'),
 'Malaysia':                 ('#CC0001','#FFFFFF','#010066'),
 'Switzerland':              ('#DA291C','#FFFFFF','#DA291C'),
 'United Kingdom':           ('#012169','#FFFFFF','#C8102E'),
 'United States of America': ('#B22234','#FFFFFF','#3C3B6E'),
}
def country_bars(country):
    return COUNTRY_BARS.get(country, ('#5A6479','#9AA5B8','#5A6479'))
