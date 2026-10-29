import pickle, networkx as nx, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
S='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/'
G=pickle.load(open(S+'grafos.pkl','rb')); g0=G['actual']; g1=G['P_ref220']
DARK="#404040"; GREY="#8C8C8C"; WIN="#2E7D32"
CAT={'L66':('Líneas 66 kV  (×11)','#E8752A'),'L154':('Líneas 154 kV  (×2)','#E9B44C'),'TR':('Transformadores  (×2 si su alta es 154 kV; ×1 si es 220 kV)','#7B5EA7'),'L220':('Líneas 220 kV  (×1)','#30849B')}
fmt=lambda v:f"{v:,.1f}".replace(',','X').replace('.',',').replace('X','.')
o='LINARES_______066'
caminos=[('A. Hacia el norte por 66 kV\n(Talca, Curicó, S. Fernando)\n→ Candelaria',nx.dijkstra_path(g0,o,'CANDELARIA____220',weight='w')),
         ('B. Hacia el sur por 66 kV,\nsube en Parral a 154 kV\n→ Ancoa',nx.dijkstra_path(g1,o,'ANCOA_________220',weight='w'))]
def comp(g,p):
    d={k:0.0 for k in CAT}
    for a,b in zip(p,p[1:]):
        ka,kb=int(a[-3:]),int(b[-3:]); w=g[a][b]['w']
        d['TR' if ka!=kb else ('L66' if ka<=66 else 'L154' if ka==154 else 'L220')]+=w
    return d
fig,axs=plt.subplots(1,2,figsize=(14,6.6),dpi=170)
for ax,g,tt,u in [(axs[0],g0,'Sin transformar (como hoy)','Ω'),(axs[1],g1,'Transformado: todo referido a 220 kV («Referido»)','Ω ref.')]:
    vals=[comp(g,p) for _,p in caminos]; tot=[sum(v.values()) for v in vals]; w=tot.index(min(tot)); bot=[0,0]
    for k,(lab,c) in CAT.items():
        h=[v[k] for v in vals]; ax.bar([n for n,_ in caminos],h,bottom=bot,color=c,width=0.55,label=lab,edgecolor='white')
        for i in range(2):
            if h[i]>0.07*max(tot): ax.text(i,bot[i]+h[i]/2,fmt(h[i]),ha='center',va='center',color='white',fontsize=11,fontweight='bold')
        bot=[bot[i]+h[i] for i in range(2)]
    for i in range(2): ax.text(i,tot[i]*1.02,f"{fmt(tot[i])} {u}"+('  ← gana' if i==w else ''),ha='center',va='bottom',fontsize=13,fontweight='bold',color=WIN if i==w else DARK)
    ax.set_ylim(0,max(tot)*1.17); ax.set_title(tt,fontsize=14,color=DARK,fontweight='bold')
    for s_ in ['top','right']: ax.spines[s_].set_visible(False)
    ax.tick_params(axis='x',labelsize=11); ax.set_ylabel('Reactancia acumulada desde Linares 66 kV',color=GREY)
h,l=axs[1].get_legend_handles_labels(); fig.legend(h,l,loc='upper center',bbox_to_anchor=(0.5,0.935),ncol=4,frameon=False,fontsize=11)
fig.suptitle('Linares 66 kV: el mismo par de caminos, sin y con la transformación',fontsize=17,color=DARK,fontweight='bold')
fig.text(0.5,0.0,'Sin transformar, los ~125 km de líneas de 66 kV del camino A suman solo 53 Ω y gana Candelaria (a 222 km). Transformado, esas mismas líneas valen 589 Ω (×11)\n'
         'y gana Ancoa (a 29 km), porque el camino B recorre menos 66 kV y sube antes a 154 kV. Las líneas de 220 kV no cambian (×1).',
         ha='center',fontsize=11.5,color=DARK,bbox=dict(boxstyle='round,pad=0.6',fc='#F4F4F4',ec='none'))
fig.tight_layout(rect=(0,0.08,1,0.89)); fig.savefig(S+'fig/con_sin_transformacion_linares.png',bbox_inches='tight',facecolor='white')
for (n,p) in caminos: print(n.split('\n')[0], {k:round(v,1) for k,v in comp(g0,p).items()}, {k:round(v,1) for k,v in comp(g1,p).items()})
