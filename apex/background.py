# -*- coding: utf-8 -*-
"""APEX v32 "Grand Prix" page background: night-time circuit, speed streaks,
coral glow and an original single-seater silhouette as a watermark.
Writes bg.png and the accent_*.png strips into ASSET_DIR."""
import base64, io, math, random, os
from PIL import Image, ImageDraw, ImageFilter
from apex.config import ASSET_DIR, ensure_dirs
ensure_dirs(); OUT=str(ASSET_DIR)
W,H=1600,900
RAIL_W=120   # v33: wider navigation rail (72 -> 120)
INK=(233,237,245); RED=(240,80,60); BG=(9,10,14)

def car_sideview(scale=1.0):
    """Original silhouette of a single-seater in side view (nose to the right)."""
    w,h=1440,420
    m=Image.new('L',(w,h),0); d=ImageDraw.Draw(m)
    gy=380   # ground line
    # rear wing: endplate + planes
    d.polygon([(70,gy-345),(225,gy-345),(225,gy-165),(130,gy-150)],fill=255)
    d.rounded_rectangle([50,gy-345,240,gy-312],radius=6,fill=255)
    # body: floor, engine cover, airbox, nose
    d.polygon([(150,gy-70),(150,gy-140),(300,gy-160),(430,gy-236),(556,gy-270),
               (596,gy-330),(662,gy-330),(704,gy-268),(760,gy-205),(900,gy-165),
               (1100,gy-140),(1380,gy-108),(1400,gy-82),(1150,gy-72)],fill=255)
    # halo
    d.arc([712,gy-300,944,gy-150],190,352,fill=255,width=15)
    d.line([(828,gy-298),(806,gy-212)],fill=255,width=12)
    # front wing
    d.rounded_rectangle([1060,gy-46,1410,gy-20],radius=8,fill=255)
    d.polygon([(1380,gy-100),(1410,gy-100),(1410,gy-20),(1380,gy-20)],fill=255)
    # wheels (drawn over the body)
    for cx in (340,1160):
        d.ellipse([cx-120,gy-240,cx+120,gy],fill=255)
        d.ellipse([cx-58,gy-178,cx+58,gy-62],fill=0)
        d.ellipse([cx-18,gy-138,cx+18,gy-102],fill=255)
    if scale!=1.0: m=m.resize((int(w*scale),int(h*scale)),Image.LANCZOS)
    return m

def grandprix_bg(w=W,h=H):
    im=Image.new('RGB',(w,h),BG)
    d=ImageDraw.Draw(im)
    # vertical gradient: midnight blue at the top, black at the bottom
    for y in range(h):
        t=y/h
        c=(int(14+8*(1-t)), int(16+10*(1-t)), int(24+14*(1-t)))
        d.line([(0,y),(w,y)],fill=c)
    # subtle carbon-fibre weave
    tex=Image.new('L',(w,h),0); td=ImageDraw.Draw(tex)
    for i in range(-h,w,6):
        td.line([(i,0),(i+h,h)],fill=16,width=1)
        td.line([(i+h,0),(i,h)],fill=10,width=1)
    im=Image.composite(Image.new('RGB',(w,h),(30,34,44)),im,tex.point(lambda v:min(v*4,60)))
    # single-seater silhouette as a watermark, tilted, on the right
    car=car_sideview(1.0).rotate(4,expand=True,resample=Image.BICUBIC)
    car=car.filter(ImageFilter.GaussianBlur(2.0))
    lay=Image.new('L',(w,h),0)
    lay.paste(car,(w-car.width+40, h-car.height+30))
    im=Image.composite(Image.new('RGB',(w,h),(62,70,92)),im,lay.point(lambda v:int(v*0.34)))
    # speed streaks (long, blurred lines heading right)
    st=Image.new('L',(w,h),0); sd=ImageDraw.Draw(st)
    random.seed(7)
    for i in range(22):
        y0=random.randint(int(h*0.18),int(h*0.98)); ln=random.randint(260,900)
        x0=random.randint(-200,w); th=random.choice([1,1,2,3])
        sd.line([(x0,y0),(x0+ln,y0-ln*0.16)],fill=random.randint(40,120),width=th)
    st=st.filter(ImageFilter.GaussianBlur(1.6))
    im=Image.composite(Image.new('RGB',(w,h),(210,120,110)),im,st.point(lambda v:int(v*0.38)))
    # coral glow top right, cold blue glow top left
    gl=Image.new('L',(w,h),0); ImageDraw.Draw(gl).ellipse([1000,-560,2200,420],fill=70)
    im=Image.composite(Image.new('RGB',(w,h),(120,36,30)),im,gl.filter(ImageFilter.GaussianBlur(210)))
    gl2=Image.new('L',(w,h),0); ImageDraw.Draw(gl2).ellipse([-500,-620,900,380],fill=48)
    im=Image.composite(Image.new('RGB',(w,h),(26,44,72)),im,gl2.filter(ImageFilter.GaussianBlur(190)))
    gl3=Image.new('L',(w,h),0); ImageDraw.Draw(gl3).ellipse([300,700,1400,1300],fill=40)
    im=Image.composite(Image.new('RGB',(w,h),(90,24,26)),im,gl3.filter(ImageFilter.GaussianBlur(200)))
    # thin coral speed line under the title band
    d=ImageDraw.Draw(im,'RGBA')
    # left rail
    d.rectangle([0,0,RAIL_W,h],fill=(8,9,13,255))
    d.line([(RAIL_W,0),(RAIL_W,h)],fill=(255,255,255,30))
    d.rectangle([0,0,4,h],fill=RED+(255,))
    return im

def png_b64(im,opt=True):
    b=io.BytesIO(); im.save(b,'PNG',optimize=opt); return base64.b64encode(b.getvalue()).decode()

ACCENTS={'red':(240,80,60),'cyan':(34,211,238),'amber':(245,185,66),'line':(44,52,70)}

def accent_strips():
    # Solid 64x8 strips stretched by the report (KPI top bar, rail marker, section rule).
    # A text box that small would show a scrollbar; an image never does.
    for n,c in ACCENTS.items():
        Image.new('RGB',(64,8),c).save(OUT+'/accent_%s.png'%n)

if __name__=='__main__':
    bg=grandprix_bg()
    bg.save(OUT+'/bg.png')
    accent_strips()
    print('bg png', os.path.getsize(OUT+'/bg.png')//1024,'KB')
