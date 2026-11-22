# ghep anh chup ViVA (cua so phong to 1440x900) + dai gia tri bus (hex) theo truc thoi gian
# Dung: python3 scripts/hinh/ghep_dang_song.py <anh_chup_viva.png> <file_mau.txt (vkSim)> Q|V <t0> <t1> <ra.png> "<chu thich>"
import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np
shot,mau,bus,t0,t1,dst,title=sys.argv[1],sys.argv[2],sys.argv[3],float(sys.argv[4]),float(sys.argv[5]),sys.argv[6],sys.argv[7]
X0,X1=494.9,1405.0          # vung ve cua do thi (pixel) ung voi t0..t1
CROP=(288,186,1432,850)
im=Image.open(shot).convert('RGB')
a=np.array(im).astype(int)
blue=(a[...,2]>150)&(a[...,0]<70)&(a[...,1]<70)
a[blue]=(90,150,255)
im=Image.fromarray(a.astype(np.uint8)).crop(CROP)
W,H=im.size
L=[l.split() for l in open(mau)]; hdr=L[0]
idx=[hdr.index('%s%d'%(bus,i)) for i in range(8)]
val={}
for r in L[1:]:
    k=int(r[0]); v=sum((1 if float(r[j])>0.6 else 0)<<i for i,j in enumerate(idx)); val[k]=v
T=2e-9
SH=46
out=Image.new('RGB',(W,H+SH+40),(0,0,0)); out.paste(im,(0,0))
d=ImageDraw.Draw(out)
try: f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',15); f2=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',15)
except: f=f2=ImageFont.load_default()
y0=H+6; y1=y0+SH-12
d.text((8,y0+8),'%s[7:0] (hex)'%bus,fill=(255,255,255),font=f2)
px=lambda t:(X0-CROP[0])+(t-t0)/(t1-t0)*(X1-X0)
for k,v in val.items():
    a_,b_=k*T,(k+1)*T
    if b_<=t0 or a_>=t1: continue
    xa,xb=px(max(a_,t0)),px(min(b_,t1))
    d.rectangle([xa,y0,xb,y1],outline=(90,150,255),fill=(10,25,50))
    if xb-xa>22: d.text(((xa+xb)/2,(y0+y1)/2),'%02X'%v,fill=(255,255,255),font=f,anchor='mm')
d.text((8,H+SH+8),title,fill=(200,200,200),font=f2)
out.save(dst); print(dst,out.size)
