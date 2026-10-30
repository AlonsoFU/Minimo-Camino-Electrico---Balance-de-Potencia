import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
S='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/fig/'
DARK="#404040"; GREY="#8C8C8C"; WIN="#2E7D32"; TR="#7B5EA7"; L66="#E8752A"; L220="#5B6E7A"
fmt=lambda v,d=2:f"{v:,.{d}f}".replace(',','X').replace('.',',').replace('X','.')
# valores reales del ENT (Ω, a la tensión V [kV] de cada fila)
caminos=[('A','RAHUE 220 kV (a 62 km)','#E8752A',[('línea 66 kV','5 tramos, por Frutillar',19.146,66,L66,False),('trafo 220/66 kV','Pilauco → Rahue',31.111,220,TR,True)]),
         ('B','PUERTO MONTT 220 kV (a 37 km)','#30849B',[('trafo 220/66 kV','en Llanquihue',67.879,220,TR,True),('línea 220 kV','Llanquihue → P. Montt',6.096,220,L220,False)])]
fig,axs=plt.subplots(1,2,figsize=(18,7.6),dpi=170)
for ax,ref in zip(axs,[False,True]):
    ax.set_xlim(-0.5,12.2); ax.set_ylim(-0.2,7.0); ax.axis('off')
    xs=[0.5,4.3,8.1]; tot={}
    for (k,dest,cd,tr),y in zip(caminos,[5.0,1.6]):
        t=0
        for i,(nm,det,x,v,c,istr) in enumerate(tr):
            x0,x1=xs[i],xs[i+1]; f=(220/v)**2 if ref else 1; val=x*f; t+=val; xm=(x0+x1)/2
            ax.plot([x0,x1],[y,y],color=c,lw=7 if not istr else 4,ls='-' if not istr else (0,(2,1.2)),zorder=1)
            ax.text(xm,y+0.35,f"{nm}\n{det}",ha='center',va='bottom',fontsize=11,color=GREY)
            if ref:
                ax.text(xm,y-0.32,f"{fmt(x)} × (220/{v})²",ha='center',va='top',fontsize=12.5,color=DARK)
                ax.text(xm,y-0.78,f"= {fmt(val)} Ω",ha='center',va='top',fontsize=15,fontweight='bold',color=L66 if v==66 else DARK)
            else:
                ax.text(xm,y-0.32,f"{fmt(x)} Ω",ha='center',va='top',fontsize=15,fontweight='bold',color=DARK)
        tot[k]=t
        ax.scatter(xs[0],y,s=480,color='white',edgecolor=DARK,lw=2.5,zorder=3); ax.text(xs[0],y-0.4,'Llanquihue\n66 kV',ha='center',va='top',fontsize=11,fontweight='bold',color=DARK)
        ax.scatter(xs[1],y,s=380,color='white',edgecolor=DARK,lw=2,zorder=3)
        ax.scatter(xs[2],y,s=650,marker='s',color=cd,edgecolor='white',lw=2,zorder=3); ax.text(xs[2],y+0.4,dest.replace(' (','\n('),ha='center',va='bottom',fontsize=11.5,fontweight='bold',color=DARK)
    w=min(tot,key=tot.get)
    for k,y in zip('AB',[5.0,1.6]):
        ax.text(8.7,y,f"Total {fmt(tot[k])} Ω"+("  ← gana" if k==w else ""),va='center',fontsize=15,fontweight='bold',color=WIN if k==w else DARK)
    ax.set_title('Sin referir (como hoy)' if not ref else 'Referido a 220 kV: cada Ω × (220 / tensión)²',fontsize=16,fontweight='bold',color=DARK)
fig.suptitle('Ejemplo simple: las dos salidas de Llanquihue 66 kV, cada una con una línea y un trafo',fontsize=18,fontweight='bold',color=DARK,y=1.0)
fig.text(0.5,0.0,'(220/66)² = 11,11 y (220/220)² = 1. Los trafos y la línea de 220 kV ya vienen en Ω de 220 kV, así que no cambian; solo la línea de 66 kV se multiplica × 11,11.\n'
         'Sin referir, sus 19,15 Ω hacen ganar a Rahue. Referida vale 212,73 Ω y gana Puerto Montt (lo mismo que PN2604).',
         ha='center',fontsize=12.5,color=DARK,bbox=dict(boxstyle='round,pad=0.6',fc='#F4F4F4',ec='none'))
fig.tight_layout(rect=(0,0.08,1,0.96)); fig.savefig(S+'simple_llanquihue.png',bbox_inches='tight',facecolor='white')
