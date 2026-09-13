# -*- coding: utf-8 -*-
"""Render the APEX brand mark and navigation icons to PNG.

Writes mark.png and ic_<name>_on.png / ic_<name>_off.png into ASSET_DIR
for the report to embed; the wordmark SVG is exposed for other modules.
"""
import cairosvg, os
from apex.config import ASSET_DIR, ensure_dirs
ensure_dirs(); OUT=str(ASSET_DIR)
RED='#F0503C'; INK='#F2F5FA'; DIM='#8892A4'; CY='#22D3EE'; ORA='#FF7A45'

# ---- APEX mark v11: full-frame apex chevron, dark badge with red border ----
MARK = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="{w}" height="{h}">
 <defs>
  <linearGradient id="ap" x1="0" y1="1" x2="1" y2="0">
    <stop offset="0" stop-color="{red}"/><stop offset="1" stop-color="{ora}"/></linearGradient>
  <linearGradient id="bd" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#1B2230"/><stop offset="1" stop-color="#0C1017"/></linearGradient>
 </defs>
 <rect x="3" y="3" width="94" height="94" rx="24" fill="url(#bd)"/>
 <rect x="3" y="3" width="94" height="94" rx="24" fill="none" stroke="{red}" stroke-width="3.4"/>
 <rect x="9" y="9" width="82" height="82" rx="19" fill="none" stroke="#FFFFFF" stroke-opacity="0.10" stroke-width="1.6"/>
 <path d="M14 78 H30 L44 44 H56 L70 78 H86 L62 22 H38 Z" fill="url(#ap)"/>
 <path d="M38 22 H62 L57.5 32 H42.5 Z" fill="#FFFFFF" fill-opacity="0.95"/>
 <rect x="21" y="63" width="20" height="4.6" rx="2.3" fill="{cy}" fill-opacity="0.85"/>
 <rect x="27" y="53" width="14" height="4.2" rx="2.1" fill="{cy}" fill-opacity="0.55"/>
 <rect x="59" y="63" width="20" height="4.6" rx="2.3" fill="#FFFFFF" fill-opacity="0.32"/>
</svg>"""

def mark(w=100,h=100):
    return MARK.format(w=w,h=h,red=RED,ora=ORA,cy=CY)

def wordmark(w=620,h=132):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 132" width="{w}" height="{h}">
 <g transform="translate(0,10)">{mark(112,112)}</g>
 <text x="132" y="72" font-family="Bahnschrift SemiBold Condensed,Bahnschrift,Segoe UI,Arial" font-size="70" font-weight="700" fill="{INK}" letter-spacing="12">APEX</text>
 <rect x="134" y="82" width="30" height="5" fill="{RED}"/>
 <rect x="170" y="82" width="12" height="5" fill="{CY}"/>
 <text x="194" y="93" font-family="Segoe UI,Arial" font-size="16" font-weight="600" fill="{DIM}" letter-spacing="4.8">FORMULA ONE INTELLIGENCE</text>
</svg>"""

ICONS={
 'pulse':'<path d="M4 18 H12 L15 8 L20 28 L24 18 H32" fill="none" stroke="{c}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>',
 'circuit':'<path d="M9 26 C4 20 8 11 16 10 C25 9 27 16 22 19 C17 22 15 25 20 27 C24 28.6 29 26 29 21" fill="none" stroke="{c}" stroke-width="2.6" stroke-linecap="round"/>',
 'lab':'<circle cx="18" cy="18" r="11" fill="none" stroke="{c}" stroke-width="2.4"/><path d="M18 7 V29 M7 18 H29" stroke="{c}" stroke-width="1.6" opacity="0.55"/><circle cx="18" cy="18" r="3.2" fill="{c}"/>',
 'driver':'<path d="M6 20 C6 12 12 7 19 7 C26 7 30 12 30 18 L30 21 L15 21 C10 21 6 22 6 20 Z" fill="none" stroke="{c}" stroke-width="2.4" stroke-linejoin="round"/><path d="M12 14 C15 11 22 11 26 13" stroke="{c}" stroke-width="2" fill="none"/><path d="M8 25 H28" stroke="{c}" stroke-width="2.4" stroke-linecap="round"/>',
 'team':'<rect x="5" y="12" width="26" height="13" rx="3" fill="none" stroke="{c}" stroke-width="2.4"/><path d="M10 12 L13 7 H23 L26 12" fill="none" stroke="{c}" stroke-width="2.2" stroke-linejoin="round"/><circle cx="11.5" cy="25.5" r="3" fill="{c}"/><circle cx="24.5" cy="25.5" r="3" fill="{c}"/>',
 'globe':'<circle cx="18" cy="18" r="12" fill="none" stroke="{c}" stroke-width="2.4"/><ellipse cx="18" cy="18" rx="5" ry="12" fill="none" stroke="{c}" stroke-width="1.8"/><path d="M6.6 14 H29.4 M6.6 22 H29.4" stroke="{c}" stroke-width="1.8"/>',
 'flag':'<path d="M9 6 V30" stroke="{c}" stroke-width="2.6" stroke-linecap="round"/><path d="M12 8 H30 V20 H12 Z" fill="none" stroke="{c}" stroke-width="2"/><path d="M12 8 H18 V14 H12 Z M24 8 H30 V14 H24 Z M18 14 H24 V20 H18 Z" fill="{c}"/>',
 'garage':'<path d="M5 22 H31 L29 26 H7 Z" fill="none" stroke="{c}" stroke-width="2.2" stroke-linejoin="round"/><path d="M9 22 C12 15 16 13 21 13 C25 13 28 16 29 22" fill="none" stroke="{c}" stroke-width="2.2"/><circle cx="12" cy="26" r="3" fill="{c}"/><circle cx="25" cy="26" r="3" fill="{c}"/>',
 'era':'<path d="M11 6 H25 V13 C25 19 22 22 18 22 C14 22 11 19 11 13 Z" fill="none" stroke="{c}" stroke-width="2.4" stroke-linejoin="round"/><path d="M11 9 H7 C7 14 9 15 11 15 M25 9 H29 C29 14 27 15 25 15" fill="none" stroke="{c}" stroke-width="2"/><path d="M18 22 V27 M13 30 H23" stroke="{c}" stroke-width="2.4" stroke-linecap="round"/>',
}
def icon(name,c,size=40):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36" width="%d" height="%d">%s</svg>'%(size,size,ICONS[name].format(c=c)))

def png(svg,path,w,h):
    cairosvg.svg2png(bytestring=svg.encode(),write_to=path,output_width=w,output_height=h)

png(mark(), OUT+'/mark.png',384,384)
for n in ICONS:
    png(icon(n,INK),OUT+'/ic_%s_on.png'%n,128,128)
    png(icon(n,'#8E99AD'),OUT+'/ic_%s_off.png'%n,128,128)
print('logo ok')
