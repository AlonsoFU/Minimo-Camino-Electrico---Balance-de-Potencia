import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyArrowPatch
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
S='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/fig/'
DARK="#404040"; GREY="#8C8C8C"; HOY="#C0392B"; REF="#30849B"; TR="#7B5EA7"; L66="#E8752A"
fmt=lambda v,d=2:f"{v:,.{d}f}".replace(',','X').replace('.',',').replace('X','.')
nodos=['La Palma\n13 kV','La Palma\n66 kV','Itahue\n66 kV','Itahue\n154 kV','ITAHUE\n220 kV']
tramos=[('trafo 66/13 kV','viene en Ω de 66 kV',60.80,66,TR,True),
        ('línea 66 kV (por Talca)','viene en Ω de 66 kV',10.65,66,L66,False),
        ('trafo 154/66 kV','viene en Ω de 154 kV',85.70,154,TR,True),
        ('trafo 220/154 kV','viene en Ω de 220 kV',48.85,220,TR,True)]
xs=[0,4,8,12,16]; yH,yR=5.2,1.3
fig,ax=plt.subplots(figsize=(17,9),dpi=170); ax.set_xlim(-1.2,21.5); ax.set_ylim(-0.6,7.6); ax.axis('off')
def fila(y,col):
    for i,(t,src,x,v,c,istr) in enumerate(tramos):
        ax.plot([xs[i],xs[i+1]],[y,y],color=c,lw=6 if not istr else 3.5,ls='-' if not istr else (0,(2,1.2)),zorder=1)
    for i,x in enumerate(xs):
        ax.scatter(x,y,s=520,color='white' if i<4 else col,edgecolor=DARK,lw=2,zorder=3)
ax.text(-1.1,yH+1.75,'1) Sin referir (como hoy): se suman los Ω tal como vienen en el ENT',fontsize=15,fontweight='bold',color=HOY)
ax.text(-1.1,yR+1.15,'2) Referido a 220 kV: cada Ω se multiplica por (220 / tensión en que viene)²',fontsize=15,fontweight='bold',color=REF)
fila(yH,HOY); fila(yR,REF)
for i,n in enumerate(nodos):
    ax.text(xs[i],yH+0.5,n,ha='center',va='bottom',fontsize=11.5,color=DARK,fontweight='bold' if i in (0,4) else 'normal')
    ax.text(xs[i],yR-0.5,n,ha='center',va='top',fontsize=11.5,color=DARK,fontweight='bold' if i in (0,4) else 'normal')
totH=totR=0
for i,(t,src,x,v,c,istr) in enumerate(tramos):
    xm=(xs[i]+xs[i+1])/2; fac=(220/v)**2; r=x*fac; totH+=x; totR+=r
    ax.text(xm,yH+0.55,f"{t}\n({src})",ha='center',va='bottom',fontsize=10.5,color=GREY)
    ax.text(xm,yH-0.42,f"{fmt(x)} Ω",ha='center',va='top',fontsize=15,fontweight='bold',color=HOY)
    ax.add_patch(FancyArrowPatch((xm,yH-1.0),(xm,yR+1.6),arrowstyle='-|>',mutation_scale=18,color=GREY,lw=1.5))
    ax.text(xm+0.15,yH-1.75,f"× (220/{v})²\n= × {fmt(fac)}",ha='left',va='center',fontsize=12.5,color=DARK,fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3',fc='#FFF6E5' if fac>1 else '#EEF5F7',ec='none'))
    ax.text(xm,yR+0.45,f"{fmt(x)} × {fmt(fac)}",ha='center',va='bottom',fontsize=11.5,color=GREY)
    ax.text(xm,yR-0.42,f"= {fmt(r)} Ω",ha='center',va='top',fontsize=15,fontweight='bold',color=REF)
ax.text(17.0,yH,f"Total\n{fmt(totH)} Ω",fontsize=16,fontweight='bold',color=HOY,va='center')
ax.text(17.0,yR,f"Total\n{fmt(totR)} Ω",fontsize=16,fontweight='bold',color=REF,va='center')
ax.set_title('Mismo camino, sin referir y referido a 220 kV  (La Palma 13 kV → Itahue 220 kV)',fontsize=17,color=DARK,fontweight='bold')
fig.text(0.5,0.02,'La tensión del factor es la de la columna V [kV] del ENT: la de la línea, o la de alta en los trafos. Lo de 66 kV se multiplica ×11,11, lo de 154 kV ×2,04 y lo de 220 kV no cambia.\n'
         'Así todo queda en la misma «moneda» (Ω de 220 kV) antes de sumar.',ha='center',fontsize=12,color=DARK,bbox=dict(boxstyle='round,pad=0.6',fc='#F4F4F4',ec='none'))
fig.tight_layout(rect=(0,0.07,1,1)); fig.savefig(S+'didactico_referir_lapalma.png',bbox_inches='tight',facecolor='white')
print(totH,totR)
