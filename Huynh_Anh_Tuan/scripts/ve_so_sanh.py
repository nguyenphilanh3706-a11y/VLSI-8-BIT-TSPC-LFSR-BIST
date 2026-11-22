# ve_so_sanh.py - ve docs/images/so_sanh_MS_TSPC.png (truoc layout) va so_sanh_hau_layout.png (sau layout) tu so lieu trong results/.
#   python3 scripts/ve_so_sanh.py   (chay tu thu muc goc; can matplotlib)
import sys, matplotlib; matplotlib.use("Agg")
import matplotlib.ticker, matplotlib.pyplot as plt
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10})
SURF="#fcfcfb"; T1="#0b0b0b"; T2="#52514e"; GRID="#e4e3df"
COL=["#2a78d6","#eb6834"]
def chart(panels,title,out,names):
    C=dict(zip(names,COL))
    fig,axs=plt.subplots(1,4,figsize=(14,3.6),facecolor=SURF)
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
chart([("Trễ CLK→Q lớn nhất (ps)\nNN, 500 MHz – thấp hơn là tốt",[240.1,186.6],"{:.1f}"),
       ("Công suất mạch P_DUT (µW)\nNN, 500 MHz – thấp hơn là tốt",[94.1,63.5],"{:.1f}"),
       ("P_DUT + P_clock (µW)\nNN, 500 MHz – thấp hơn là tốt",[115.5,87.5],"{:.1f}"),
       ("Tần số tối đa f_max (GHz)\nNN, 301/301 trạng thái đúng – cao hơn là tốt",[1.82,3.45],"{:.2f}")],
      "Trước layout: MS và TSPC, LFSR 8 bit, gpdk090 (22/11/2026)","docs/images/so_sanh_MS_TSPC.png",
      ["MS_LFSR_8bit (flip-flop tạm 24T, 2 pha clock)","TSPC_LFSR_8bit (flip-flop TV2 15T, 1 pha clock)"])
chart([("Diện tích layout (µm²)\nmột hàng cao 2,76 µm – thấp hơn là tốt",[235.48,159.47],"{:.1f}"),
       ("Trễ CLK→Q lớn nhất (ps)\nNN, 500 MHz – thấp hơn là tốt",[381.6,201.5],"{:.1f}"),
       ("P_DUT + P_clock (µW)\nNN, 500 MHz – thấp hơn là tốt",[160.6,89.8],"{:.1f}"),
       ("Tần số tối đa f_max (GHz)\nNN, 301/301 trạng thái đúng – cao hơn là tốt",[1.33,3.45],"{:.2f}")],
      "Sau layout (trích RC): MS và TSPC, LFSR 8 bit, gpdk090 (flip-flop tạm của TV4, 21/11/2026)","docs/images/so_sanh_hau_layout.png",
      ["MS_LFSR_8bit (flip-flop tạm 24T, 2 pha clock)","TSPC_LFSR_8bit (flip-flop tạm 17T, 1 pha clock)"])
