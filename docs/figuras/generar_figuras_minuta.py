import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib import font_manager
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
TEAL="#30849B"; ORANGE="#E8752A"; GREY="#8C8C8C"; DARK="#404040"; LIGHT="#E9EEF1"
OUT="./"

def node(ax, x, y, label, color=TEAL, size=300, fs=8.5, textcolor="white"):
    ax.scatter([x],[y], s=size, color=color, edgecolor="white", lw=1.5, zorder=3)
    ax.text(x, y, label, ha="center", va="center", fontsize=fs, color=textcolor, fontweight="bold", zorder=4)

# ---------- Figura 1: concepto de la metodología ----------
fig, ax = plt.subplots(figsize=(7.2, 3.0), dpi=200)
ax.set_xlim(-0.5, 10.5); ax.set_ylim(-0.6, 3.4); ax.axis("off")
# barra analizada a la izquierda, dos barras troncales a la derecha
pts = {"P": (0.8, 1.4), "n1": (3.2, 2.4), "n2": (5.6, 2.4), "A": (9.4, 2.4), "n3": (3.2, 0.4), "B": (9.4, 0.4)}
def edge(a, b, label, color=GREY, lw=2.0, ls="-", off=0.28):
    (x1,y1),(x2,y2)=pts[a],pts[b]
    ax.plot([x1,x2],[y1,y2], color=color, lw=lw, ls=ls, zorder=1)
    ax.text((x1+x2)/2, (y1+y2)/2+off, label, ha="center", va="bottom", fontsize=8.5, color=DARK)
edge("P","n1","X₁ = 12 Ω", ORANGE, 3.2, off=0.22)
edge("n1","n2","X₂ = 9 Ω", ORANGE, 3.2)
edge("n2","A","X₃ = 7 Ω", ORANGE, 3.2)
edge("P","n3","X₄ = 20 Ω", GREY, 2.0, (0,(6,3)), off=-0.55)
edge("n3","B","X₅ = 15 Ω", GREY, 2.0, (0,(6,3)), off=-0.55)
node(ax, *pts["P"], "Barra", ORANGE, 520, 8)
for k in ("n1","n2","n3"): node(ax, *pts[k], "", "#5FA6B9", 140)
node(ax, *pts["A"], "A", TEAL, 560, 8.5)
node(ax, *pts["B"], "B", TEAL, 560, 8.5)
ax.text(0.8, 0.75, "Barra\nanalizada", ha="center", va="top", fontsize=8.5, color=ORANGE)
ax.text(9.4, 3.0, "Barra troncal A", ha="center", va="bottom", fontsize=8.5, color=TEAL)
ax.text(9.4, -0.2, "Barra troncal B", ha="center", va="top", fontsize=8.5, color=TEAL)
ax.text(5.6, 3.25, "Distancia eléctrica a A = 12 + 9 + 7 = 28 Ω  →  más cercana", ha="center", va="bottom", fontsize=9, color=ORANGE, fontweight="bold")
ax.text(6.3, -0.45, "Distancia eléctrica a B = 20 + 15 = 35 Ω", ha="center", va="top", fontsize=9, color=GREY, fontweight="bold")
fig.savefig(OUT+"fig1_concepto.png", bbox_inches="tight", facecolor="white"); plt.close(fig)

# ---------- Figura 2: caso La Palma 13 kV ----------
fig, ax = plt.subplots(figsize=(8.6, 5.0), dpi=200)
ax.set_xlim(-4.6, 17.2); ax.set_ylim(-2.7, 5.0); ax.axis("off")
pts={"LP13":(1.0,-0.9),"LP66":(1.0,0.6),"IT66":(5.6,0.6),"IT154":(5.6,2.2),"IT220":(5.6,3.8),"AN220":(1.0,3.8),
     "LIN66":(-3.0,0.6),"LIN154":(-3.0,2.2),"MAU220":(-3.0,3.8),
     "SF66":(10.4,0.6),"SF154":(10.4,2.2),"TG220":(10.4,3.8),"CA220":(13.6,3.8)}
def edge(a,b,label,color,lw,ls="-",dx=0,dy=0.2,ha="center",va="bottom",fs=7.4,tc=DARK):
    (x1,y1),(x2,y2)=pts[a],pts[b]
    ax.plot([x1,x2],[y1,y2],color=color,lw=lw,ls=ls,zorder=1)
    ax.text((x1+x2)/2+dx,(y1+y2)/2+dy,label,ha=ha,va=va,fontsize=fs,color=tc,linespacing=1.15)
# camino seleccionado (naranja)
edge("LP13","LP66","",ORANGE,3.2)
ax.text(1.35,-0.9,"Trafo La Palma 66/13 kV · 0 km · 60,80 Ω",ha="left",va="center",fontsize=7.4,color=DARK)
edge("LP66","IT66","5 líneas 66 kV\nLa Palma – El Ruil – Talca –\nPanguilemo – San Rafael – Itahue\nkm sin dato · 10,65 Ω",ORANGE,3.2,dy=-0.28,va="top")
edge("IT66","SF66","7 líneas 66 kV\nItahue – Molina – Curicó – Rauquén –\nTeno – Quinta – Chimbarongo – S. Fernando\n70,6 km · 29,70 Ω",ORANGE,3.2,dy=-0.28,va="top")
edge("SF66","SF154","Trafo San Fernando 154/66 kV\n(3 unidades en paralelo)\n0 km · 18,63 Ω",ORANGE,3.2,dx=0.18,dy=0,ha="left",va="center")
edge("SF154","TG220","Línea S. Fernando – Tinguiririca 154 kV\n3,3 km · 0,71 Ω\n+ trafo Tinguiririca 220/154 kV · 13,95 Ω",ORANGE,3.2,dx=0.18,dy=0,ha="left",va="center")
edge("TG220","CA220","Líneas 220 kV Tinguiririca –\nPuente Negro – Candelaria (2 circuitos)\n91,3 km · 16,20 Ω",ORANGE,3.2,dy=0.18)
# camino directo a Itahue (gris segmentado)
edge("IT66","IT154","Trafo Itahue 154/66 kV\n(2 unidades de 171,4 Ω en paralelo)\n0 km · 85,70 Ω",GREY,2.4,(0,(6,3)),dx=0.18,dy=0,ha="left",va="center",tc=GREY)
edge("IT154","IT220","Trafo Itahue 220/154 kV\n0 km · 48,85 Ω",GREY,2.4,(0,(6,3)),dx=0.18,dy=0,ha="left",va="center",tc=GREY)
edge("IT220","AN220","Línea Itahue – Ancoa 220 kV\n60,3 km · 15,97 Ω",GREY,2.4,(0,(6,3)),dy=0.18,tc=GREY)
# camino más corto en km a Ancoa, por Linares (gris segmentado)
edge("LP66","LIN66","3 líneas 66 kV\nLa Palma – San Javier –\nVilla Alegre – Linares\n30,6 km · 12,67 Ω",GREY,2.4,(0,(6,3)),dy=-0.28,va="top",tc=GREY)
edge("LIN66","LIN154","Trafo Linares 154/66 kV\n0 km · 164,22 Ω",GREY,2.4,(0,(6,3)),dx=-0.18,dy=0,ha="right",va="center",tc=GREY)
edge("LIN154","MAU220","Líneas 154 kV Linares –\nY. Buenas – Maule\n39,4 km · 16,50 Ω\n+ trafo Maule 220/154 kV\n15,57 Ω",GREY,2.4,(0,(6,3)),dx=-0.18,dy=0,ha="right",va="center",tc=GREY)
edge("MAU220","AN220","Líneas 220 kV Maule –\nSta. Isabel – Ancoa\n39,1 km · 18,10 Ω",GREY,2.4,(0,(6,3)),dy=0.18,tc=GREY)
def lnode(k,label,color,size,dx,dy,ha="center",va="center",tc=DARK,bold=False):
    x,y=pts[k]; ax.scatter([x],[y],s=size,color=color,edgecolor="white",lw=1.5,zorder=3)
    ax.text(x+dx,y+dy,label,ha=ha,va=va,fontsize=8,color=tc,fontweight="bold" if bold else "normal",linespacing=1.15)
lnode("LP13","La Palma 13 kV\n(barra analizada)",ORANGE,300,0,-0.32,va="top",tc=ORANGE,bold=True)
lnode("LP66","La Palma 66",'#5FA6B9',170,0,0.28,va="bottom")
lnode("IT66","Itahue 66",'#5FA6B9',170,-0.2,0.28,ha="right",va="bottom")
lnode("IT154","Itahue 154 kV",'#9DBFC9',170,-0.3,0,ha="right",tc=GREY,bold=True)
lnode("IT220","Itahue 220 kV",TEAL,300,0.3,0,ha="left",tc=TEAL,bold=True)
lnode("AN220","Ancoa 220 kV\nmás cercana en distancia\n(≈ 32 km en línea recta)",TEAL,300,0,-0.3,va="top",tc=TEAL,bold=True)
lnode("LIN66","Linares 66",'#5FA6B9',170,0,0.28,va="bottom")
lnode("LIN154","Linares 154 kV",'#9DBFC9',170,0.3,0,ha="left",tc=GREY,bold=True)
lnode("MAU220","Maule 220",'#9DBFC9',170,-0.3,0,ha="right")
lnode("SF66","San Fernando 66",'#5FA6B9',170,-0.2,0.28,ha="right",va="bottom")
lnode("SF154","San Fernando 154",'#5FA6B9',170,-0.22,0,ha="right")
lnode("TG220","Tinguiririca 220",'#5FA6B9',170,-0.22,0,ha="right")
lnode("CA220","Candelaria 220 kV\nBARRA ASIGNADA\n150,7 Ω · ≈ 199 km en línea recta",TEAL,300,0.28,0,ha="left",tc=ORANGE,bold=True)
ax.text(3.0,-2.0,"Transformadores de alta reactancia rodeados: Linares 154/66 kV (164,2 Ω) e Itahue 154/66 kV (85,7 Ω equivalente)",ha="left",va="top",fontsize=8.3,color=GREY,fontweight="bold")
ax.text(3.0,-2.35,"Caminos descartados (segmentados): a Ancoa 220 kV por Linares 109,0 km · 287,9 Ω;  a Itahue 220 kV por sus trafos 206,0 Ω (km sin dato)",ha="left",va="top",fontsize=8.3,color=GREY)
fig.savefig(OUT+"fig2_caso_lapalma.png",bbox_inches="tight",facecolor="white"); plt.close(fig)

# ---------- Figura 3: km vs ohm ----------
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), dpi=200)
labels=["Ancoa 220 kV\n(por Linares)","Itahue 220 kV\n(por trafos Itahue)","Candelaria 220 kV\n(por San Fernando)"]
km=[32.0,58.1,199.1]; xo=[287.9,206.0,150.7]
for ax,vals,title,unit,win,wcol in [(axes[0],km,"Distancia en línea recta a la barra troncal","km",0,TEAL),(axes[1],xo,"Distancia eléctrica (suma de X)","Ω",2,ORANGE)]:
    colors=[GREY]*3; colors[win]=wcol
    bars=ax.bar(labels,vals,color=colors,width=0.55)
    for b,v in zip(bars,vals):
        ax.text(b.get_x()+b.get_width()/2,b.get_height()+max(vals)*0.02,(f"≈ {v:.0f} {unit}" if unit=="km" else f"{v:.1f} {unit}".replace(".",",")),ha="center",va="bottom",fontsize=9,color=DARK)
    ax.set_title(title,fontsize=10.5,color=DARK,fontweight="bold"); ax.set_ylim(0,max(vals)*1.22); ax.set_yticks([])
    for s in ["top","right","left"]: ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GREY); ax.tick_params(axis="x",labelsize=7.8)
axes[0].text(0.5,-0.45,"Más cercana en distancia: Ancoa",transform=axes[0].transAxes,ha="center",fontsize=9,color=TEAL,fontweight="bold")
axes[1].text(0.5,-0.45,"Más corto eléctricamente: Candelaria → barra asignada",transform=axes[1].transAxes,ha="center",fontsize=9,color=ORANGE,fontweight="bold")
fig.tight_layout(w_pad=3)
fig.savefig(OUT+"fig3_comparacion_lapalma.png",bbox_inches="tight",facecolor="white"); plt.close(fig)
print("ok")
