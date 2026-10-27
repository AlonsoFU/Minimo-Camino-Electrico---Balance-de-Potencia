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
OUT="fig/"

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

# ---------- Figura 2: caso Temuco ----------
fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)
ax.set_xlim(-0.9, 10.9); ax.set_ylim(-1.1, 4.9); ax.axis("off")
pts={"T66":(9.6,0.6),"PIL":(7.4,0.6),"LLA":(5.6,0.6),"LAU":(3.8,0.6),"VIC":(2.3,0.6),"LP66":(0.6,0.6),
     "LP220":(0.6,3.1),"T220":(9.6,3.1)}
def edge(a,b,label,color,lw,ls="-",dx=0,dy=0.22,ha="center",va="bottom",fs=8):
    (x1,y1),(x2,y2)=pts[a],pts[b]
    ax.plot([x1,x2],[y1,y2],color=color,lw=lw,ls=ls,zorder=1)
    ax.text((x1+x2)/2+dx,(y1+y2)/2+dy,label,ha=ha,va=va,fontsize=fs,color=DARK)
edge("T66","T220","Transformador\nTemuco 220/66 kV\n0 km · 265,4 Ω",GREY,2.4,(0,(6,3)),dx=0.2,dy=0,ha="left",va="center")
edge("T66","PIL","12,4 km\n4,39 Ω",ORANGE,3.4)
edge("PIL","LLA","2,4 km\n0,94 Ω",ORANGE,3.4)
edge("LLA","LAU","9,9 km\n3,84 Ω",ORANGE,3.4)
edge("LAU","VIC","36,8 km\n14,62 Ω",ORANGE,3.4)
edge("VIC","LP66","0,1 km\n1,29 Ω",ORANGE,3.4)
edge("LP66","LP220","Transformador\nLos Peumos 220/66 kV\n0 km · 28,61 Ω",ORANGE,3.4,dx=0.2,dy=0,ha="left",va="center")
edge("LP220","T220","Línea Los Peumos – Temuco 220 kV · 59,8 km · 22,89 Ω",TEAL,2.0,(0,(4,3)),dy=0.18)
def lnode(k,label,color,size,dy,ct=DARK,bold=False):
    x,y=pts[k]; ax.scatter([x],[y],s=size,color=color,edgecolor="white",lw=1.5,zorder=3)
    ax.text(x,y+dy,label,ha="center",va="top" if dy<0 else "bottom",fontsize=8,color=ct,fontweight="bold" if bold else "normal")
lnode("T66","Temuco 66 kV",ORANGE,280,-0.3,ORANGE,True)
lnode("PIL","Pillanlelbún 66",'#5FA6B9',170,-0.3)
lnode("LLA","Llaima 66",'#5FA6B9',170,-0.3)
lnode("LAU","Lautaro 66",'#5FA6B9',170,-0.3)
lnode("VIC","Victoria 66",'#5FA6B9',170,-0.3)
lnode("LP66","Los Peumos 66",'#5FA6B9',170,-0.3)
lnode("LP220","Los Peumos 220 kV",TEAL,320,0.3,TEAL,True)
lnode("T220","Temuco 220 kV",TEAL,320,0.3,TEAL,True)
ax.text(9.6,-0.6,"PMGD conectado en la barra Temuco 66 kV",ha="center",va="top",fontsize=8.5,color=ORANGE,fontweight="bold")
ax.text(0.6,3.75,"BARRA ASIGNADA\nΣX = 53,7 Ω · 61,5 km",ha="center",va="bottom",fontsize=8.5,color=ORANGE,fontweight="bold")
ax.text(9.6,3.75,"Barra del transformador de alta reactancia\n(no asignada)\nvía trafo: 265,4 Ω · 0 km\nvía Los Peumos: 76,6 Ω · 121,3 km",ha="center",va="bottom",fontsize=8.5,color=GREY,fontweight="bold")
ax.text(5.0,-0.95,"Red de 66 kV: camino de mínima distancia eléctrica (seleccionado)",ha="center",fontsize=8.5,color=ORANGE)
fig.savefig(OUT+"fig2_caso_temuco.png",bbox_inches="tight",facecolor="white"); plt.close(fig)

# ---------- Figura 3: km vs ohm ----------
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), dpi=200)
labels=["Directo a\nTemuco 220 kV\n(transformador)","Rodeo a\nLos Peumos 220 kV","Rodeo a\nTemuco 220 kV"]
km=[0,61.5,121.3]; xo=[265.4,53.7,76.6]
for ax,vals,title,unit,win,wcol in [(axes[0],km,"Longitud del camino","km",0,TEAL),(axes[1],xo,"Distancia eléctrica (suma de X)","Ω",1,ORANGE)]:
    colors=[GREY]*3; colors[win]=wcol
    bars=ax.bar(labels,vals,color=colors,width=0.55)
    for b,v in zip(bars,vals):
        ax.text(b.get_x()+b.get_width()/2,b.get_height()+max(vals)*0.02,f"{v:.1f} {unit}".replace(".",","),ha="center",va="bottom",fontsize=9,color=DARK)
    ax.set_title(title,fontsize=10.5,color=DARK,fontweight="bold"); ax.set_ylim(0,max(vals)*1.22); ax.set_yticks([])
    for s in ["top","right","left"]: ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GREY); ax.tick_params(axis="x",labelsize=8)
axes[0].text(0.5,-0.42,"Más corto: el transformador (0 km)",transform=axes[0].transAxes,ha="center",fontsize=9,color=TEAL,fontweight="bold")
axes[1].text(0.5,-0.42,"Más corto: rodeo por Los Peumos → SE asignada",transform=axes[1].transAxes,ha="center",fontsize=9,color=ORANGE,fontweight="bold")
fig.tight_layout(w_pad=3)
fig.savefig(OUT+"fig3_comparacion_temuco.png",bbox_inches="tight",facecolor="white"); plt.close(fig)
print("ok")
