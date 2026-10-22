import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
TEAL="#30849B"; ORANGE="#E8752A"; GREY="#8C8C8C"; DARK="#404040"
OUT="./"

# ---------- Figura 1: concepto (camino directo con trafo de alta X vs rodeo) ----------
fig, ax = plt.subplots(figsize=(7.2, 3.0), dpi=200)
ax.set_xlim(-0.6, 10.6); ax.set_ylim(-0.9, 3.6); ax.axis("off")
pts={"P":(1.2,0.5),"A":(1.2,2.9),"n1":(4.2,0.5),"n2":(7.2,0.5),"B":(9.6,0.5),"B2":(9.6,2.9)}
def edge(a,b,label,color,lw,ls="-",dx=0,dy=0.22,ha="center",va="bottom",fs=8.5):
    (x1,y1),(x2,y2)=pts[a],pts[b]
    ax.plot([x1,x2],[y1,y2],color=color,lw=lw,ls=ls,zorder=1)
    ax.text((x1+x2)/2+dx,(y1+y2)/2+dy,label,ha=ha,va=va,fontsize=fs,color=DARK)
edge("P","A","Transformador\n0 km · X = 250 Ω",GREY,2.2,(0,(6,3)),dx=0.2,dy=0,ha="left",va="center")
edge("P","n1","Línea · 20 km · X = 8 Ω",ORANGE,3.2)
edge("n1","n2","Línea · 20 km · X = 8 Ω",ORANGE,3.2)
edge("n2","B","Línea · 15 km · X = 6 Ω",ORANGE,3.2)
edge("B","B2","Transformador\n0 km · X = 30 Ω",ORANGE,3.2,dx=-0.2,dy=0,ha="right",va="center")
for k,c,s in [("P",ORANGE,420),("A",TEAL,420),("n1","#5FA6B9",150),("n2","#5FA6B9",150),("B","#5FA6B9",150),("B2",TEAL,420)]:
    ax.scatter([pts[k][0]],[pts[k][1]],s=s,color=c,edgecolor="white",lw=1.5,zorder=3)
ax.text(1.2,0.5,"PMGD",ha="center",va="center",fontsize=7.5,color="white",fontweight="bold",zorder=4)
ax.text(1.2,2.9,"SE A",ha="center",va="center",fontsize=8,color="white",fontweight="bold",zorder=4)
ax.text(9.6,2.9,"SE B",ha="center",va="center",fontsize=8,color="white",fontweight="bold",zorder=4)
ax.text(1.2,-0.05,"Barra de inyección\n(barra de baja tensión de la SE A)",ha="center",va="top",fontsize=8.2,color=ORANGE)
ax.text(1.2,3.25,"Subestación A\n(misma ubicación)",ha="center",va="bottom",fontsize=8.2,color=TEAL)
ax.text(9.6,3.25,"Subestación B",ha="center",va="bottom",fontsize=8.2,color=TEAL)
ax.text(5.4,3.3,"Camino directo a SE A: 0 km, pero X = 250 Ω  →  descartado",ha="center",va="center",fontsize=9,color=GREY,fontweight="bold")
ax.text(5.4,2.75,"Camino a SE B: 55 km, X = 8 + 8 + 6 + 30 = 52 Ω  →  SE más cercana",ha="center",va="center",fontsize=9,color=ORANGE,fontweight="bold")
fig.savefig(OUT+"fig1_concepto.png",bbox_inches="tight",facecolor="white"); plt.close(fig)

# ---------- Figura 2: caso La Palma 13 kV ----------
fig, ax = plt.subplots(figsize=(8.2, 4.9), dpi=200)
ax.set_xlim(-2.3, 16.4); ax.set_ylim(-2.6, 5.0); ax.axis("off")
pts={"LP13":(0.6,-0.9),"LP66":(0.6,0.6),"IT66":(5.4,0.6),"IT154":(5.4,2.2),"IT220":(5.4,3.8),"AN220":(0.6,3.8),
     "SF66":(10.2,0.6),"SF154":(10.2,2.2),"TG220":(10.2,3.8),"CA220":(13.4,3.8)}
def edge(a,b,label,color,lw,ls="-",dx=0,dy=0.2,ha="center",va="bottom",fs=7.6,tc=DARK):
    (x1,y1),(x2,y2)=pts[a],pts[b]
    ax.plot([x1,x2],[y1,y2],color=color,lw=lw,ls=ls,zorder=1)
    ax.text((x1+x2)/2+dx,(y1+y2)/2+dy,label,ha=ha,va=va,fontsize=fs,color=tc,linespacing=1.15)
# camino seleccionado (naranja)
edge("LP13","LP66","Trafo La Palma\n66/13 kV\n0 km · 60,80 Ω",ORANGE,3.2,dx=-0.2,dy=0,ha="right",va="center")
edge("LP66","IT66","5 líneas 66 kV\nLa Palma – El Ruil –\nTalca – Panguilemo –\nSan Rafael – Itahue\n58,8 km · 10,65 Ω",ORANGE,3.2,dy=-0.28,va="top")
edge("IT66","SF66","7 líneas 66 kV\nItahue – Molina – Curicó –\nRauquén – Teno – Quinta –\nChimbarongo – S. Fernando\n70,6 km · 29,70 Ω",ORANGE,3.2,dy=-0.28,va="top")
edge("SF66","SF154","Trafo San Fernando 154/66 kV\n(3 unidades en paralelo)\n0 km · 18,63 Ω",ORANGE,3.2,dx=0.18,dy=0,ha="left",va="center")
edge("SF154","TG220","Línea S. Fernando – Tinguiririca 154 kV\n3,3 km · 0,71 Ω\n+ trafo Tinguiririca 220/154 kV · 13,95 Ω",ORANGE,3.2,dx=0.18,dy=0,ha="left",va="center")
edge("TG220","CA220","Líneas 220 kV Tinguiririca –\nPuente Negro – Candelaria (2 circuitos)\n91,3 km · 16,20 Ω",ORANGE,3.2,dy=0.18)
# camino directo (gris segmentado)
edge("IT66","IT154","Trafo Itahue 154/66 kV\n(2 unidades de 171,4 Ω en paralelo)\n0 km · 85,70 Ω",GREY,2.4,(0,(6,3)),dx=0.18,dy=0,ha="left",va="center",tc=GREY)
edge("IT154","IT220","Trafo Itahue 220/154 kV\n0 km · 48,85 Ω",GREY,2.4,(0,(6,3)),dx=0.18,dy=0,ha="left",va="center",tc=GREY)
edge("IT220","AN220","Línea Itahue – Ancoa 220 kV\n60,3 km · 15,97 Ω",GREY,2.4,(0,(6,3)),dy=0.18,tc=GREY)
def lnode(k,label,color,size,dx,dy,ha="center",va="center",tc=DARK,bold=False):
    x,y=pts[k]; ax.scatter([x],[y],s=size,color=color,edgecolor="white",lw=1.5,zorder=3)
    ax.text(x+dx,y+dy,label,ha=ha,va=va,fontsize=8,color=tc,fontweight="bold" if bold else "normal",linespacing=1.15)
lnode("LP13","La Palma 13 kV\n(barra de inyección)",ORANGE,300,0,-0.3,va="top",tc=ORANGE,bold=True)
lnode("LP66","La Palma 66",'#5FA6B9',170,-0.2,0.28,ha="right",va="bottom")
lnode("IT66","Itahue 66",'#5FA6B9',170,-0.2,0.28,ha="right",va="bottom")
lnode("IT154","Itahue 154 kV",'#9DBFC9',170,-0.3,0,ha="right",tc=GREY,bold=True)
lnode("IT220","Itahue 220 kV",TEAL,300,0.3,0,ha="left",tc=TEAL,bold=True)
lnode("AN220","Ancoa 220 kV\nmás cercana en distancia\n(≈ 32 km en línea recta)",TEAL,300,0,-0.3,va="top",tc=TEAL,bold=True)
lnode("SF66","San Fernando 66",'#5FA6B9',170,-0.2,0.28,ha="right",va="bottom")
lnode("SF154","San Fernando 154",'#5FA6B9',170,-0.22,0,ha="right")
lnode("TG220","Tinguiririca 220",'#5FA6B9',170,-0.22,0,ha="right")
lnode("CA220","Candelaria 220 kV\nBARRA ASIGNADA\n223,9 km · 150,7 Ω",TEAL,300,0.28,0,ha="left",tc=ORANGE,bold=True)
ax.text(2.6,-2.0,"Barra del transformador de alta reactancia: Itahue 154 kV (trafo 154/66 kV, 85,7 Ω equivalente)",ha="left",va="top",fontsize=8.3,color=GREY,fontweight="bold")
ax.text(2.6,-2.35,"Camino directo (segmentado): a Itahue 220 kV 58,8 km · 206,0 Ω;  a Ancoa 220 kV 119,1 km · 222,0 Ω  →  descartado",ha="left",va="top",fontsize=8.3,color=GREY)
fig.savefig(OUT+"fig2_caso_lapalma.png",bbox_inches="tight",facecolor="white"); plt.close(fig)

# ---------- Figura 3: km vs ohm ----------
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), dpi=200)
labels=["Directo a\nItahue 220 kV\n(trafos Itahue)","Directo a\nAncoa 220 kV\n(trafos Itahue + línea)","Rodeo a\nCandelaria 220 kV\n(por San Fernando)"]
km=[58.8,119.1,223.9]; xo=[206.0,222.0,150.7]
for ax,vals,title,unit,win,wcol in [(axes[0],km,"Longitud del camino","km",0,TEAL),(axes[1],xo,"Distancia eléctrica (suma de X)","Ω",2,ORANGE)]:
    colors=[GREY]*3; colors[win]=wcol
    bars=ax.bar(labels,vals,color=colors,width=0.55)
    for b,v in zip(bars,vals):
        ax.text(b.get_x()+b.get_width()/2,b.get_height()+max(vals)*0.02,f"{v:.1f} {unit}".replace(".",","),ha="center",va="bottom",fontsize=9,color=DARK)
    ax.set_title(title,fontsize=10.5,color=DARK,fontweight="bold"); ax.set_ylim(0,max(vals)*1.22); ax.set_yticks([])
    for s in ["top","right","left"]: ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GREY); ax.tick_params(axis="x",labelsize=7.8)
axes[0].text(0.5,-0.45,"Más corto en distancia: Itahue y luego Ancoa",transform=axes[0].transAxes,ha="center",fontsize=9,color=TEAL,fontweight="bold")
axes[1].text(0.5,-0.45,"Más corto eléctricamente: Candelaria → barra asignada",transform=axes[1].transAxes,ha="center",fontsize=9,color=ORANGE,fontweight="bold")
fig.tight_layout(w_pad=3)
fig.savefig(OUT+"fig3_comparacion_lapalma.png",bbox_inches="tight",facecolor="white"); plt.close(fig)
print("ok")
