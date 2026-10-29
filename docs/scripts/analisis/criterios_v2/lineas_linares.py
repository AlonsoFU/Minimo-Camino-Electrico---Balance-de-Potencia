import pickle, networkx as nx, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
S='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/'
G=pickle.load(open(S+'grafos.pkl','rb')); g0=G['actual']; g1=G['P_ref220']
DARK="#404040"; GREY="#8C8C8C"; WIN="#2E7D32"
COL={'L66':'#E8752A','L154':'#E9B44C','TR':'#7B5EA7','L220':'#30849B'}
LAB={'L66':'línea 66 kV','L154':'línea 154 kV','TR':'transformador','L220':'línea 220 kV'}
fmt=lambda v:f"{v:,.1f}".replace(',','X').replace('.',',').replace('X','.')
nom=lambda n:{'LINARES_______066':'Linares 66','CANDELARIA____220':'Candelaria','ANCOA_________220':'Ancoa','ITAHUE________066':'Itahue 66',
              'TALCA1________066':'Talca','CURICO________066':'Curicó','S.FERNANDO____066':'S.Fernando 66','S.FERNANDO____154':'154',
              'TINGUIRIRICA__154':'Tinguiririca 154','TINGUIRIRICA__220':'220','LONGAVI_______066':'Longaví','PARRAL________066':'Parral 66',
              'PARRAL________154':'154','LINARES_______154':'Linares 154','MAULE_________154':'Maule 154','MAULE_________220':'220',
              'S.JAVIER______066':'S.Javier','TENO__________066':'Teno'}.get(n)
o='LINARES_______066'
P={'A':nx.dijkstra_path(g0,o,'CANDELARIA____220',weight='w'),'B':nx.dijkstra_path(g1,o,'ANCOA_________220',weight='w')}
def tipo(a,b):
    ka,kb=int(a[-3:]),int(b[-3:]); return 'TR' if ka!=kb else ('L66' if ka<=66 else 'L154' if ka==154 else 'L220')
fig,axs=plt.subplots(2,1,figsize=(16,9.5),dpi=170)
for ax,g,tt,u in [(axs[0],g0,'Sin transformar (como hoy): los Ω se suman tal como vienen','Ω'),(axs[1],g1,'Transformado («Referido»): cada Ω se multiplica por (220 / tensión)²','Ω ref.')]:
    tot={k:sum(g[a][b]['w'] for a,b in zip(p,p[1:])) for k,p in P.items()}; w=min(tot,key=tot.get); xmax=max(tot.values())
    for row,(k,p,y,dest) in enumerate([( 'A',P['A'],1.0,'→ Candelaria (a 222 km)'),('B',P['B'],0.0,'→ Ancoa (a 29 km)')]):
        x=0; last=-1e9
        ax.text(-xmax*0.01,y,f'Camino {k}',ha='right',va='center',fontsize=13,fontweight='bold',color=DARK)
        for a,b in zip(p,p[1:]):
            wv=g[a][b]['w']; t=tipo(a,b)
            ax.add_patch(Rectangle((x,y-0.17),wv,0.34,fc=COL[t],ec='white',lw=1.2))
            if wv>xmax*0.035: ax.text(x+wv/2,y,fmt(wv),ha='center',va='center',fontsize=9.5,color='white',fontweight='bold')
            n=nom(b)
            if n and b!=p[-1] and (x+wv)-last>xmax*0.065:
                last=x+wv; ax.plot([x+wv,x+wv],[y+0.17,y+0.27],color=GREY,lw=0.8); ax.text(x+wv,y+0.30,n,ha='center',va='bottom',fontsize=9,color=DARK,rotation=0)
            x+=wv
        ax.text(x+xmax*0.01,y,f"{fmt(tot[k])} {u}  {dest}"+("  ← gana" if k==w else ""),va='center',fontsize=12.5,fontweight='bold',color=WIN if k==w else DARK)
    ax.set_xlim(-xmax*0.07,xmax*1.42); ax.set_ylim(-0.5,1.6); ax.axis('off'); ax.set_title(tt,fontsize=14,color=DARK,fontweight='bold',loc='left')
    ax.plot([0,0],[-0.3,1.3],color=DARK,lw=1); ax.text(0,-0.38,'Linares 66 kV',ha='center',fontsize=10,color=DARK,fontweight='bold')
from matplotlib.patches import Patch
fig.legend([Patch(color=c) for c in COL.values()],[f"{LAB[k]}  (×{ {'L66':'11','L154':'2','TR':'1 o 2','L220':'1'}[k]})" for k in COL],loc='upper center',ncol=4,frameon=False,fontsize=11.5,bbox_to_anchor=(0.5,0.955))
fig.suptitle('Linares 66 kV: cada tramo del camino, sin y con la transformación (largo de cada tramo = su reactancia)',fontsize=16,color=DARK,fontweight='bold')
fig.text(0.5,0.01,'Sin transformar, los 17 tramos de 66 kV del camino A son cortos (53 Ω en total). Al transformar se alargan ×11 (589 Ω) y el camino A pasa a ser casi el doble que el B.',ha='center',fontsize=11.5,color=DARK)
fig.tight_layout(rect=(0,0.03,1,0.92)); fig.savefig(S+'fig/tramos_linares.png',bbox_inches='tight',facecolor='white')
