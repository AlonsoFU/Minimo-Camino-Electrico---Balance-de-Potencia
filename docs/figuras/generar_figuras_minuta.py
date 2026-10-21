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
# PMGD at left, two STN substations at right (A near, B far)
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
node(ax, *pts["P"], "PMGD", ORANGE, 520, 8)
for k in ("n1","n2","n3"): node(ax, *pts[k], "", "#5FA6B9", 140)
node(ax, *pts["A"], "SE A", TEAL, 560, 8.5)
node(ax, *pts["B"], "SE B", TEAL, 560, 8.5)
ax.text(0.8, 0.75, "Punto de\ninyección", ha="center", va="top", fontsize=8.5, color=ORANGE)
ax.text(9.4, 3.0, "Subestación STN A", ha="center", va="bottom", fontsize=8.5, color=TEAL)
ax.text(9.4, -0.2, "Subestación STN B", ha="center", va="top", fontsize=8.5, color=TEAL)
ax.text(5.6, 3.25, "Distancia eléctrica a SE A = 12 + 9 + 7 = 28 Ω  →  más cercana", ha="center", va="bottom", fontsize=9, color=ORANGE, fontweight="bold")
ax.text(6.3, -0.45, "Distancia eléctrica a SE B = 20 + 15 = 35 Ω", ha="center", va="top", fontsize=9, color=GREY, fontweight="bold")
fig.savefig(OUT+"fig1_concepto.png", bbox_inches="tight", facecolor="white"); plt.close(fig)

# ---------- Figura 2: caso Taltal (datos ENT) ----------
fig, ax = plt.subplots(figsize=(7.2, 4.1), dpi=200)
ax.set_xlim(-0.8, 10.8); ax.set_ylim(-1.0, 4.9); ax.axis("off")
pts = {"TAL":(0.6,0.6), "LL":(2.6,0.6), "OX":(4.3,0.6), "JAV":(6.3,0.6), "DA110":(8.6,0.6),
       "DA220":(8.6,2.3), "SF":(6.0,3.5), "TT":(3.4,3.5), "PAP":(0.6,3.5)}
def edge(a,b,label,color,lw,ls="-",dx=0,dy=0.25,ha="center",va="bottom"):
    (x1,y1),(x2,y2)=pts[a],pts[b]
    ax.plot([x1,x2],[y1,y2], color=color, lw=lw, ls=ls, zorder=1)
    ax.text((x1+x2)/2+dx,(y1+y2)/2+dy,label,ha=ha,va=va,fontsize=8.2,color=DARK)
# camino 110 kV hacia D.Almagro (seleccionado)
edge("TAL","LL","15,39 Ω",ORANGE,3.4)
edge("LL","OX","4,37 Ω",ORANGE,3.4)
edge("OX","JAV","18,41 Ω",ORANGE,3.4)
edge("JAV","DA110","10,99 Ω",ORANGE,3.4)
edge("DA110","DA220","Trafo 220/110 kV\n9,02 Ω",ORANGE,3.4,dx=0.15,dy=-0.15,ha="left",va="center")
# extensión hacia Paposo (220 kV)
edge("DA220","SF","47,50 Ω",GREY,2.2,(0,(6,3)),dx=-0.3,dy=0.05,ha="right")
edge("SF","TT","21,61 Ω",GREY,2.2,(0,(6,3)))
edge("TT","PAP","8,00 Ω",GREY,2.2,(0,(6,3)))
# línea recta geográfica Taltal–Paposo (no existe eléctricamente)
ax.annotate("", xy=(0.6,3.2), xytext=(0.6,0.95), arrowprops=dict(arrowstyle="<->", color=TEAL, lw=1.2, ls=":"))
ax.text(0.45, 2.1, "≈ 44 km en línea recta\n(sin vínculo eléctrico\ndirecto en 110 kV)", ha="right", va="center", fontsize=7.8, color=TEAL, style="italic")
# nodos con etiqueta exterior
def lnode(k, label, color, size, dy, color_t=DARK):
    x,y=pts[k]; ax.scatter([x],[y], s=size, color=color, edgecolor="white", lw=1.5, zorder=3)
    ax.text(x, y+dy, label, ha="center", va="top" if dy<0 else "bottom", fontsize=8.2, color=color_t, fontweight="bold" if color_t!=DARK else "normal")
lnode("TAL","Taltal 110 kV",ORANGE,260,-0.28,ORANGE)
lnode("LL","Las Luces 110",'#5FA6B9',180,-0.28)
lnode("OX","Óxidos 110",'#5FA6B9',180,-0.28)
lnode("JAV","Javiera 110",'#5FA6B9',180,-0.28)
lnode("DA110","D. Almagro 110",'#5FA6B9',180,-0.28)
lnode("DA220","D. Almagro 220 kV",TEAL,300,-0.3,TEAL)
lnode("SF","San Francisco 220",'#9DBFC9',180,0.26)
lnode("TT","Tap Taltal 1 220",'#9DBFC9',180,0.26)
lnode("PAP","Paposo 220 kV",TEAL,300,0.26,TEAL)
ax.text(0.6, -0.05, "PMGD\n(punto de inyección)", ha="center", va="top", fontsize=8.5, color=ORANGE, fontweight="bold")
ax.text(9.15, 2.35, "SE STN más cercana\neléctricamente\nΣX = 58,2 Ω", ha="left", va="center", fontsize=8.5, color=ORANGE, fontweight="bold")
ax.text(0.6, 4.05, "SE STN más cercana en distancia\nΣX = 135,3 Ω", ha="center", va="bottom", fontsize=8.5, color=GREY, fontweight="bold")
ax.text(5.0, -0.75, "Red de 110 kV (camino seleccionado)", ha="center", fontsize=8.5, color=ORANGE)
ax.text(5.0, 4.15, "Red de 220 kV (tramo adicional para llegar a Paposo)", ha="center", fontsize=8.5, color=GREY)
fig.savefig(OUT+"fig2_caso_taltal.png", bbox_inches="tight", facecolor="white"); plt.close(fig)

# ---------- Figura 3: comparación km vs ohm ----------
fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), dpi=200)
labels = ["SE Paposo 220 kV", "SE Diego de Almagro 220 kV"]
km = [44, 118]; xo = [135.3, 58.2]
for ax, vals, title, fmt, win, wcol in [(axes[0], km, "Distancia geográfica (línea recta)", "≈ {:.0f} km", 0, TEAL),
                                         (axes[1], xo, "Distancia eléctrica (suma de X)", "{:.1f} Ω", 1, ORANGE)]:
    colors = [GREY, GREY]; colors[win] = wcol
    bars = ax.bar(labels, vals, color=colors, width=0.55)
    for b, v in zip(bars, vals):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()*1.02, fmt.format(v).replace(".",","), ha="center", va="bottom", fontsize=9, color=DARK)
    ax.set_title(title, fontsize=10.5, color=DARK, fontweight="bold")
    ax.set_ylim(0, max(vals)*1.25); ax.set_yticks([])
    for s in ["top","right","left"]: ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GREY); ax.tick_params(axis="x", labelsize=8.5)
axes[0].text(0.5, -0.3, "Más cercana: Paposo", transform=axes[0].transAxes, ha="center", fontsize=9, color=TEAL, fontweight="bold")
axes[1].text(0.5, -0.3, "Más cercana: Diego de Almagro → la que asigna la metodología", transform=axes[1].transAxes, ha="center", fontsize=9, color=ORANGE, fontweight="bold")
fig.tight_layout(w_pad=3)
fig.savefig(OUT+"fig3_comparacion_taltal.png", bbox_inches="tight", facecolor="white"); plt.close(fig)
print("ok")
