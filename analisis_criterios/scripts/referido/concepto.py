import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyBboxPatch
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
DARK="#404040"; GREY="#A0A0A0"; LT="#D5D5D5"; WIN="#2E7D32"; A="#30849B"; B="#E8752A"; TR="#7B5EA7"
S='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/fig/'

def trafo(ax,x,y,c,lw=2):
    ax.add_patch(Circle((x,y-0.17),0.25,fill=False,ec=c,lw=lw,zorder=4)); ax.add_patch(Circle((x,y+0.17),0.25,fill=False,ec=c,lw=lw,zorder=4))
    ax.add_patch(Circle((x,y-0.17),0.25,fc='white',ec='none',zorder=3)); ax.add_patch(Circle((x,y+0.17),0.25,fc='white',ec='none',zorder=3))
def barra(ax,x,y,txt,c=DARK,sq=False,dx=0.3,ha='left'):
    if sq: ax.scatter(x,y,s=380,marker='s',color=c,zorder=6,edgecolor='white',lw=1.5)
    else: ax.scatter(x,y,s=260,marker='o',color='white',edgecolor=c,lw=2.4,zorder=6)
    ax.text(x+dx,y,txt,fontsize=12,color=c,va='center',ha=ha,fontweight='bold',zorder=7)
def seg(ax,p,q,c,lw):
    ax.plot([p[0],q[0]],[p[1],q[1]],color=c,lw=lw,zorder=2,solid_capstyle='round')
def lab(ax,x,y,t,c=DARK,fs=12,**k): ax.text(x,y,t,fontsize=fs,color=c,ha='center',va='center',zorder=8,bbox=dict(boxstyle='round,pad=0.25',fc='white',ec='none'),**k)
def caja(ax,x,y,txt,c):
    ax.text(x,y,txt,fontsize=12.5,color=DARK,va='top',ha='left',bbox=dict(boxstyle='round,pad=0.5',fc='white',ec=c,lw=1.8),zorder=9)
def limpiar(ax):
    ax.set_xlim(0,10); ax.set_ylim(-0.4,6.6); ax.axis('off')

# ========== Figura 1: «Referido» ==========
fig,axs=plt.subplots(1,2,figsize=(16,7.6),dpi=160)
for ax,modo in zip(axs,['hoy','ref']):
    limpiar(ax)
    ganaA = modo=='ref'
    cA = A if ganaA else LT; cB = LT if ganaA else B
    # camino A: subir en la misma subestación
    seg(ax,(1.2,1.5),(1.2,4.6),cA,5 if ganaA else 2.5); trafo(ax,1.2,3.05,TR)
    # camino B: 100 km por 66 kV y subir allá
    seg(ax,(1.2,1.5),(8.4,1.5),cB,2.5 if ganaA else 5); seg(ax,(8.4,1.5),(8.4,4.6),cB,2.5 if ganaA else 5); trafo(ax,8.4,3.05,TR)
    barra(ax,1.2,1.5,'Barra analizada\n66 kV',dx=0,ha='center'); ax.texts[-1].set_position((1.2,0.75))
    barra(ax,1.2,4.6,'Troncal A  220 kV',c=A,sq=True); barra(ax,8.4,4.6,'Troncal B\n220 kV',c=B,sq=True,dx=0,ha='center'); ax.texts[-1].set_position((8.4,5.35))
    lab(ax,2.25,3.05,'trafo\n100 Ω',TR)
    lab(ax,7.35,3.05,'trafo\n20 Ω',TR)
    if modo=='hoy':
        lab(ax,4.8,1.5,'línea 66 kV, 100 km\n40 Ω',B)
        ax.set_title('Hoy: se suman los Ω tal como vienen',fontsize=15,color=DARK,fontweight='bold',pad=12)
        caja(ax,3.4,6.45,'A = 100 Ω\nB = 40 + 20 = 60 Ω   → gana B (rodeo de 100 km)',B)
    else:
        lab(ax,4.8,1.5,'línea 66 kV, 100 km\n40 Ω × 11 = 444 Ω',DARK)
        ax.set_title('«Referido»: todo se expresa en Ω de 220 kV',fontsize=15,color=DARK,fontweight='bold',pad=12)
        caja(ax,3.4,6.45,'A = 100 Ω\nB = 444 + 20 = 464 Ω   → gana A (sube en su subestación)',A)
fig.suptitle('Propuesta «Referido»: convertir antes de sumar',fontsize=19,color=DARK,fontweight='bold',y=1.0)
fig.text(0.5,0.035,'El trafo ya viene en Ω de 220 kV, pero la línea viene en Ω de 66 kV. Sumarlos directo es como sumar pesos con dólares.\n'
         'Para llevar un Ω a 220 kV se multiplica por (220 / V)²:   66 kV × 11   ·   110 kV × 4   ·   154 kV × 2   ·   220 kV × 1   ·   500 kV × 0,19',
         ha='center',fontsize=12.5,color=DARK,bbox=dict(boxstyle='round,pad=0.6',fc='#F4F4F4',ec='none'))
fig.text(0.5,-0.04,'Valores ilustrativos (≈ 0,4 Ω por km de línea). Es el mecanismo del caso La Palma.',ha='center',fontsize=11,color=GREY)
fig.tight_layout(rect=(0,0.1,1,0.96)); fig.savefig(S+'concepto_referido.png',bbox_inches='tight',facecolor='white'); plt.close(fig)

# ========== Figura 2: «Referido + Subestación» (Curicó, valores reales) ==========
fig,axs=plt.subplots(1,2,figsize=(16,7.8),dpi=160)
for ax,modo in zip(axs,['ref','sub']):
    limpiar(ax)
    ganaI = modo=='sub'
    cI = A if ganaI else LT; cC = LT if ganaI else B
    # S/E Itahue (recinto)
    ax.add_patch(FancyBboxPatch((0.25,0.75),2.2,4.75,boxstyle='round,pad=0.1',fill=True,fc='#EAF4F7' if ganaI else '#F7F7F7',ec=A if ganaI else GREY,ls='--',lw=2,zorder=1))
    ax.text(1.35,5.75,'Subestación troncal Itahue',fontsize=12.5,color=A if ganaI else GREY,ha='center',fontweight='bold')
    seg(ax,(4.6,1.5),(1.0,1.5),cI,5 if ganaI else 2.5)
    seg(ax,(1.0,1.5),(1.0,4.6),LT if ganaI else LT,2.5); trafo(ax,1.0,3.05,GREY if ganaI else TR)
    seg(ax,(4.6,1.5),(9.0,1.5),cC,2.5 if ganaI else 5); seg(ax,(9.0,1.5),(9.0,4.6),cC,2.5 if ganaI else 5); trafo(ax,9.0,3.05,TR)
    barra(ax,4.6,1.5,'Curicó 66 kV\n(barra analizada)',dx=0,ha='center'); ax.texts[-1].set_position((4.6,0.65))
    barra(ax,1.0,1.5,'Itahue 66 kV',c=A,dx=0,ha='center'); ax.texts[-1].set_position((1.35,1.05))
    barra(ax,1.0,4.6,'Itahue\n220 kV',c=A,sq=True)
    barra(ax,9.0,4.6,'Candelaria\n220 kV',c=B,sq=True,dx=0,ha='center'); ax.texts[-1].set_position((9.0,5.35))
    lab(ax,3.5,2.05,'66 kV, ~20 km\n94 Ω',A if ganaI else DARK,fs=11.5)
    lab(ax,6.8,1.5,'66 kV ~100 km\n+ trafos + 220 kV',DARK,fs=11.5)
    lab(ax,7.95,3.05,'306 Ω\nen total',B,fs=11.5)
    if modo=='ref':
        lab(ax,1.95,3.05,'trafos\n224 Ω',TR,fs=11.5)
        ax.set_title('«Referido»: hay que llegar a la barra de 220 kV',fontsize=15,color=DARK,fontweight='bold',pad=12)
        caja(ax,3.3,6.45,'Itahue = 94 + 224 = 318 Ω\nCandelaria = 306 Ω   → gana Candelaria (a 121 km)',B)
    else:
        lab(ax,1.95,3.05,'no se\ncuenta',GREY,fs=11.5)
        ax.set_title('«Referido + Subestación»: basta entrar a la subestación',fontsize=15,color=DARK,fontweight='bold',pad=12)
        caja(ax,3.3,6.45,'Itahue = 94 Ω (llega a Itahue 66 kV)\nCandelaria = 306 Ω   → gana Itahue (a 21 km)',A)
fig.suptitle('Propuesta «Referido + Subestación»: el destino es la subestación, no solo su barra de 220 kV',fontsize=18,color=DARK,fontweight='bold',y=1.0)
fig.text(0.5,0.035,'El decreto habla de la distancia a la «subestación» del sistema nacional. Con esta lectura, tocar cualquier barra de la\n'
         'subestación troncal (66, 110, 154 o 220 kV) ya es llegar, y los trafos internos de esa subestación no se suman.',
         ha='center',fontsize=12.5,color=DARK,bbox=dict(boxstyle='round,pad=0.6',fc='#F4F4F4',ec='none'))
fig.text(0.5,-0.04,'Valores reales del ENT (Ω referidos a 220 kV). Costo: favorece a las troncales con barras de varias tensiones (ej. Machalí → Alto Jahuel por su 66 kV).',ha='center',fontsize=11,color=GREY)
fig.tight_layout(rect=(0,0.1,1,0.96)); fig.savefig(S+'concepto_referido_subestacion.png',bbox_inches='tight',facecolor='white'); plt.close(fig)
