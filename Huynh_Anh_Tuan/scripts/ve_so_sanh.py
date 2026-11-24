# ve_so_sanh.py - ve docs/images/so_sanh_MS_TSPC.png (truoc layout) va so_sanh_hau_layout.png (sau layout) tu so lieu trong results/.
#   python3 scripts/ve_so_sanh.py   (chay tu thu muc goc; can matplotlib)
import sys, matplotlib; matplotlib.use("Agg")
import matplotlib.ticker, matplotlib.pyplot as plt
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10})
SURF="#fcfcfb"; T1="#0b0b0b"; T2="#52514e"; GRID="#e4e3df"
COL=["#2a78d6","#eb6834"]
def chart(panels,title,out,names):
    C=dict(zip(names,COL))
    fig,axs=plt.subplots(1,len(panels),figsize=(3.5*len(panels),3.6),facecolor=SURF)
    for ax,(t,v,fmt) in zip(axs,panels):
        ax.set_facecolor(SURF); ys=[1,0]
        for y,n,val in zip(ys,names,v):
            ax.barh(y,val,height=0.55,color=C[n],edgecolor=SURF,linewidth=2)
            ax.text(val*1.02,y,fmt.format(val).replace(".", ","),va="center",ha="left",color=T1,fontsize=10)
        ax.set_yticks(ys); ax.set_yticklabels(["MS","TSPC"],color=T2)
        ax.set_xlim(0,max(v)*1.28); ax.set_title(t,fontsize=10,color=T1,loc="left")
        for s in ["top","right","left"]: ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color(GRID); ax.tick_params(colors=T2,length=0)
        ax.xaxis.grid(True,color=GRID,linewidth=0.8); ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x,p: ("%g"%x).replace(".",","))); ax.set_axisbelow(True)
    fig.legend(handles=[plt.Rectangle((0,0),1,1,color=C[n]) for n in names],labels=names,loc="lower center",ncol=2,frameon=False,fontsize=10,labelcolor=T1,bbox_to_anchor=(0.5,-0.02))
    fig.suptitle(title,x=0.01,ha="left",fontsize=12,color=T1,y=1.02)
    fig.tight_layout(rect=(0,0.08,1,1))
    fig.savefig(out,dpi=150,bbox_inches="tight",facecolor=SURF)
chart([("Số transistor (khối LFSR)\nthấp hơn là tốt",[234,144],"{:.0f}"),
       ("Trễ CLK→Q lớn nhất (ps)\nNN, 500 MHz – thấp hơn là tốt",[139.2,143.1],"{:.1f}"),
       ("Công suất logic P_DUT (µW)*\nNN, 500 MHz – thấp hơn là tốt",[62.0,42.0],"{:.1f}"),
       ("Công suất mạng clock (µW)*\nNN, 500 MHz – thấp hơn là tốt",[19.0,24.0],"{:.1f}"),
       ("Tổng P_DUT + P_clock (µW)\nNN, 500 MHz – thấp hơn là tốt",[81.1,66.0],"{:.1f}"),
       ("Tần số tối đa f_max (GHz)\nNN, 301/301 trạng thái đúng – cao hơn là tốt",[3.33,4.17],"{:.2f}")],
      "Trước layout: MS (cell TV1) và TSPC (cell TV2), LFSR 8 bit, gpdk090, cả hai có as/ad (24/11/2026). *MS: inverter tạo CLKB tính vào mạng clock",
      "docs/images/so_sanh_MS_TSPC.png",
      ["MS_LFSR_8bit (MS_DFF_SetReset TV1 26T, 2 pha clock)","TSPC_LFSR_8bit (TSPC_DFF TV2 15T, 1 pha clock)"])
chart([("Diện tích layout (µm²)\nmột hàng cao 2,76 µm – thấp hơn là tốt",[235.48,218.10],"{:.1f}"),
       ("Trễ CLK→Q lớn nhất (ps)\nNN, 500 MHz – thấp hơn là tốt",[381.6,238.8],"{:.1f}"),
       ("P_DUT + P_clock (µW)\nNN, 500 MHz – thấp hơn là tốt",[160.6,102.3],"{:.1f}"),
       ("Tần số tối đa f_max (GHz)\nNN, 301/301 trạng thái đúng – cao hơn là tốt",[1.33,2.63],"{:.2f}")],
      "Sau layout (trích RC): MS (flip-flop tạm, 21/11) và TSPC (layout flip-flop TV2, 22/11/2026), LFSR 8 bit, gpdk090","docs/images/so_sanh_hau_layout.png",
      ["MS_LFSR_8bit (flip-flop tạm 24T, 2 pha clock)","TSPC_LFSR_8bit (layout flip-flop TV2 15T, 1 pha clock)"])

# PVT: tre CLK->Q lon nhat o 500 MHz (27 diem / ban, tat ca PASS 301/301)
import re
def pvt(f):
    d={}
    for l in open(f):
        m=re.match(r"(NN|SS|FF) ([0-9.]+)V (-?[0-9]+)C .* (PASS|FAIL) .*tre_ps=([0-9.]+)",l)
        if m: d[(m.group(1),float(m.group(2)),int(m.group(3)))]=float(m.group(5))
    return d
S=[("MS_LFSR_8bit (TV1), trước layout","results/pvt/tb_MS_LFSR.txt","#2a78d6","-"),
   ("TSPC_LFSR_8bit (TV2), trước layout","results/pvt/tb_TSPC_LFSR_asad.txt","#eb6834","-"),
   ("TSPC_LFSR_8bit, sau layout (RCX)","results/pvt/tb_TSPC_LFSR_post.txt","#eb6834","--")]
fig,axs=plt.subplots(1,3,figsize=(13,3.8),facecolor=SURF,sharey=True)
for ax,c in zip(axs,["NN","SS","FF"]):
    ax.set_facecolor(SURF)
    for n,f,col,ls in S:
        d=pvt(f)
        for T,mk in [(125,"o"),(27,"s"),(0,"^")]:
            xs=[0.8,1.0,1.2]; ys=[d[(c,v,T)] for v in xs]
            ax.plot(xs,ys,color=col,ls=ls,marker=mk,ms=4,lw=1.6 if T==125 else 0.9,alpha=1 if T==125 else 0.55,label=n if (T==125 and c=="NN") else None)
    ax.set_title("Corner "+c,loc="left",fontsize=10,color=T1); ax.set_xticks([0.8,1.0,1.2]); ax.set_xlabel("VDD (V)",color=T2)
    for s_ in ["top","right"]: ax.spines[s_].set_visible(False)
    ax.yaxis.grid(True,color=GRID,linewidth=0.8); ax.set_axisbelow(True); ax.tick_params(colors=T2)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x,p: ("%g"%x).replace(".",",")))
axs[0].set_ylabel("Trễ CLK→Q lớn nhất (ps)",color=T2)
fig.legend(loc="lower center",ncol=3,frameon=False,fontsize=9,bbox_to_anchor=(0.5,-0.08))
fig.suptitle("PVT ở 500 MHz: 3 corner × VDD 0,8/1,0/1,2 V × 0/27/125 °C – cả 81 điểm PASS 301/301 (đậm: 125 °C, nhạt: 27 °C ■ và 0 °C ▲)",x=0.01,ha="left",fontsize=11,color=T1,y=1.02)
fig.tight_layout(rect=(0,0.07,1,1)); fig.savefig("docs/images/pvt_tre.png",dpi=150,bbox_inches="tight",facecolor=SURF)
