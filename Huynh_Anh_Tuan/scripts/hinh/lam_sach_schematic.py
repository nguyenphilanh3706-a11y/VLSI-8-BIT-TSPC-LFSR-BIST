# lam sach anh schematic/symbol xuat tu Virtuoso: nen den + luoi -> trang, mau sang -> mau dam, cat vua noi dung
# Dung: python3 scripts/hinh/lam_sach_schematic.py <anh_hiExportImage.png> <ra.png>
import sys
from PIL import Image
import numpy as np
src,dst=sys.argv[1],sys.argv[2]
im=np.array(Image.open(src).convert('RGB')).astype(int)
key=im[...,0]*65536+im[...,1]*256+im[...,2]
M={(0,0,0):None,(140,140,166):None,
   (255,0,0):(200,0,0),(0,204,102):(0,120,40),(57,191,255):(0,70,190),(255,255,255):None,(217,204,0):(140,100,0)}
out=np.full(im.shape,255,dtype=np.uint8); keep=np.zeros(key.shape,bool)
known=np.zeros(key.shape,bool)
for c,t in M.items():
    m=key==(c[0]*65536+c[1]*256+c[2]); known|=m
    if t: out[m]=t; keep|=m
oth=~known; out[oth]=(90,90,90)
ys,xs=np.where(keep); pad=30
y0,y1=max(ys.min()-pad,0),min(ys.max()+pad,im.shape[0]); x0,x1=max(xs.min()-pad,0),min(xs.max()+pad,im.shape[1])
Image.fromarray(out[y0:y1,x0:x1]).save(dst); print(dst,x1-x0,y1-y0)
