import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib import font_manager
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
TEAL="#30849B"; ORANGE="#E8752A"; GREEN="#6BAE3D"; GREY="#8C8C8C"; DARK="#404040"; LIGHT="#E9EEF1"
OUT="./"

# ---------- Figura 1: flujo del código ----------
fig, ax = plt.subplots(figsize=(7.2, 2.9), dpi=200)
ax.set_xlim(0, 10); ax.set_ylim(0, 4.5); ax.axis("off")
def box(x, y, w, h, text, fc=LIGHT, ec=TEAL, fs=9, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc=fc, ec=ec, lw=1.4))
    ax.text(x+w/2, y+h/2, text, ha="center", va="center", fontsize=fs, color=DARK, fontweight="bold" if bold else "normal", linespacing=1.25)
def arrow(x1,y1,x2,y2,color=TEAL):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2), arrowstyle="-|>", mutation_scale=12, color=color, lw=1.3))
# fuentes
box(0.2, 2.75, 2.2, 1.0, "Base ENT\n(Barra A, Barra B, V, R, X)")
box(0.2, 1.5, 2.2, 1.0, "CNE operación +\nmantenimiento (mes)")
box(0.2, 0.25, 2.2, 1.0, "Infotécnica\n(tramos y transformadores)")
# homologación
box(3.3, 1.35, 2.3, 1.3, "Homologación\npor barras, tensión\ny circuito", fc="#DCEBF0")
arrow(2.4, 3.25, 3.3, 2.3); arrow(2.4, 2.0, 3.3, 2.0); arrow(2.4, 0.75, 3.3, 1.7)
# validación
box(6.1, 1.35, 1.9, 1.3, "Validación X_ENT\n(umbral 15 %,\n50 Ω)", fc="#DCEBF0")
arrow(5.6, 2.0, 6.1, 2.0)
# grafo / camino
box(8.4, 1.35, 1.5, 1.3, "Grafo de\nimpedancias →\nmínimo camino", fc="#FBE3D3", ec=ORANGE, bold=True)
arrow(8.0, 2.0, 8.4, 2.0, color=ORANGE)
ax.text(5.0, 4.2, "Alcance del código del repositorio", ha="center", fontsize=9, color=TEAL, style="italic")
ax.plot([0.2, 8.1],[4.05,4.05], color=TEAL, lw=0.8, ls="--")
ax.text(9.15, 4.2, "Uso posterior", ha="center", fontsize=9, color=ORANGE, style="italic")
ax.plot([8.4, 9.9],[4.05,4.05], color=ORANGE, lw=0.8, ls="--")
fig.savefig(OUT+"fig1_flujo.png", bbox_inches="tight", facecolor="white"); plt.close(fig)

# ---------- Figura 2: red con dos caminos ----------
fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=200)
ax.set_xlim(-0.6, 10.6); ax.set_ylim(-0.4, 4.2); ax.axis("off")
nodes = {"G": (0.8, 0.9), "C": (9.2, 0.9), "G500": (0.8, 3.2), "C500": (9.2, 3.2)}
# camino 1: directo (geográficamente corto, descartado)
ax.plot([0.8, 9.2], [0.9, 0.9], color=GREY, lw=2.2, ls=(0,(6,3)), zorder=1)
ax.text(5.0, 0.55, "Línea 220 kV  ·  70 km  ·  X = 28,0 Ω  (0,0579 pu)", ha="center", va="top", fontsize=9, color=DARK)
ax.text(5.0, 1.15, "Camino 1: más corto en distancia (descartado)", ha="center", va="bottom", fontsize=9.5, color=GREY, fontweight="bold")
# camino 2: via 500 kV (eléctricamente corto, seleccionado)
ax.plot([0.8, 0.8], [0.9, 3.2], color=ORANGE, lw=3.2, zorder=1)
ax.plot([9.2, 9.2], [0.9, 3.2], color=ORANGE, lw=3.2, zorder=1)
ax.plot([0.8, 9.2], [3.2, 3.2], color=ORANGE, lw=3.2, zorder=1)
ax.text(5.0, 3.5, "Línea 500 kV  ·  150 km  ·  X = 49,5 Ω  (0,0198 pu)", ha="center", va="bottom", fontsize=9, color=DARK)
ax.text(5.0, 3.95, "Camino 2: más corto eléctricamente (seleccionado)", ha="center", va="bottom", fontsize=9.5, color=ORANGE, fontweight="bold")
ax.text(1.0, 2.05, "Trafo\n220/500 kV\n0,016 pu", ha="left", va="center", fontsize=8.5, color=DARK)
ax.text(9.0, 2.05, "Trafo\n500/220 kV\n0,016 pu", ha="right", va="center", fontsize=8.5, color=DARK)
# nodos
for name,(x,y) in nodes.items():
    ax.scatter([x],[y], s=260, color=TEAL if name in ("G","C") else "#5FA6B9", edgecolor="white", lw=1.5, zorder=3)
ax.text(0.8, 0.9, "G", ha="center", va="center", fontsize=9, color="white", fontweight="bold", zorder=4)
ax.text(9.2, 0.9, "C", ha="center", va="center", fontsize=9, color="white", fontweight="bold", zorder=4)
ax.text(0.8, 3.2, "G'", ha="center", va="center", fontsize=9, color="white", fontweight="bold", zorder=4)
ax.text(9.2, 3.2, "C'", ha="center", va="center", fontsize=9, color="white", fontweight="bold", zorder=4)
ax.text(0.8, 0.35, "Central (inyección)\nbarra 220 kV", ha="center", va="top", fontsize=8.5, color=TEAL)
ax.text(9.2, 0.35, "Consumo (retiro)\nbarra 220 kV", ha="center", va="top", fontsize=8.5, color=TEAL)
ax.text(0.3, 3.2, "barra\n500 kV", ha="right", va="center", fontsize=8, color=TEAL)
ax.text(9.7, 3.2, "barra\n500 kV", ha="left", va="center", fontsize=8, color=TEAL)
fig.savefig(OUT+"fig2_red.png", bbox_inches="tight", facecolor="white"); plt.close(fig)

# ---------- Figura 3: comparación distancia vs reactancia ----------
fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), dpi=200)
labels = ["Camino 1\n(directo 220 kV)", "Camino 2\n(vía 500 kV)"]
km = [70, 150]; xpu = [0.0579, 0.0518]
for ax, vals, title, unit, win in [(axes[0], km, "Distancia geográfica", "km", 0), (axes[1], xpu, "Distancia eléctrica (suma de X)", "pu", 1)]:
    colors = [GREY, GREY]; colors[win] = ORANGE if ax is axes[1] else TEAL
    bars = ax.bar(labels, vals, color=colors, width=0.55)
    for b, v in zip(bars, vals):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()*1.02, f"{v:,.4f} {unit}".replace(".",",") if unit=="pu" else f"{v} {unit}", ha="center", va="bottom", fontsize=9, color=DARK)
    ax.set_title(title, fontsize=10.5, color=DARK, fontweight="bold")
    ax.set_ylim(0, max(vals)*1.25)
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(GREY); ax.spines["bottom"].set_color(GREY)
    ax.tick_params(axis="y", labelsize=8, colors=GREY); ax.tick_params(axis="x", labelsize=9)
    ax.set_yticks([])
axes[0].text(0.5, -0.32, "Más corto: Camino 1", transform=axes[0].transAxes, ha="center", fontsize=9, color=TEAL, fontweight="bold")
axes[1].text(0.5, -0.32, "Más corto: Camino 2 → el que elige la metodología", transform=axes[1].transAxes, ha="center", fontsize=9, color=ORANGE, fontweight="bold")
fig.tight_layout(w_pad=3)
fig.savefig(OUT+"fig3_comparacion.png", bbox_inches="tight", facecolor="white"); plt.close(fig)

# ---------- Figura 4: sensibilidad ----------
fig, ax = plt.subplots(figsize=(7.2, 2.6), dpi=200)
import numpy as np
err = np.linspace(-25, 25, 101)
x1 = 0.0579*(1+err/100)
ax.plot(err, x1, color=TEAL, lw=2.2, label="X Camino 1 (directo) según error en X_ENT")
ax.axhline(0.0518, color=ORANGE, lw=2.2, label="X Camino 2 (vía 500 kV) = 0,0518 pu")
flip = (0.0518/0.0579-1)*100
ax.axvline(flip, color=DARK, lw=1, ls=":")
ax.fill_between(err, 0.03, 0.08, where=err<flip, color=TEAL, alpha=0.08)
ax.fill_between(err, 0.03, 0.08, where=err>=flip, color=ORANGE, alpha=0.08)
ax.text(flip-0.8, 0.0785, f"cambio de camino\n(error ≈ {flip:.1f} %)".replace(".",","), ha="right", va="top", fontsize=8.5, color=DARK)
ax.text(-24, 0.034, "Gana Camino 1", fontsize=9, color=TEAL, fontweight="bold")
ax.text(12, 0.034, "Gana Camino 2", fontsize=9, color=ORANGE, fontweight="bold")
ax.axvspan(-15, 15, color=GREY, alpha=0.10)
ax.text(6, 0.0785, "tolerancia ±15 % de la validación de X_ENT", ha="center", va="top", fontsize=8.5, color=GREY)
ax.set_xlim(-25, 25); ax.set_ylim(0.03, 0.08)
ax.set_xlabel("Error en la reactancia de la línea directa [%]", fontsize=9, color=DARK)
ax.set_ylabel("Suma de X del camino [pu]", fontsize=9, color=DARK)
for s in ["top","right"]: ax.spines[s].set_visible(False)
ax.tick_params(labelsize=8)
ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5,-0.28), ncol=2, frameon=False)
fig.savefig(OUT+"fig4_sensibilidad.png", bbox_inches="tight", facecolor="white"); plt.close(fig)
print("ok")
