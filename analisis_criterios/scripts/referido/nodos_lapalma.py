import pickle, networkx as nx, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
S='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/'
G=pickle.load(open(S+'grafos.pkl','rb')); g0=G['actual']; g1=G['P_ref220']
DARK="#404040"; GREY="#8C8C8C"; WIN="#2E7D32"; HOY="#C0392B"; REF="#30849B"
COL={66:'#E8752A',154:'#E9B44C',220:'#5B6E7A','T':'#7B5EA7'}
fmt=lambda v:f"{v:,.1f}".replace(',','X').replace('.',',').replace('X','.')
o='LAPALMA_______013'
# nodos clave de cada camino (los intermedios se agrupan en el tramo)
claves={'A':['LAPALMA_______013','LAPALMA_______066','ITAHUE________066','S.FERNANDO____066','S.FERNANDO____154','TINGUIRIRICA__154','TINGUIRIRICA__220','CANDELARIA____220'],
        'B':['LAPALMA_______013','LAPALMA_______066','ITAHUE________066','ITAHUE________154','ITAHUE________220']}
nombre={'LAPALMA_______013':'La Palma\n13 kV','LAPALMA_______066':'La Palma\n66 kV','ITAHUE________154':'Itahue\n154 kV','ITAHUE________220':'ITAHUE\n220 kV','LINARES_______066':'Linares\n66 kV','ITAHUE________066':'Itahue\n66 kV','S.FERNANDO____066':'S. Fernando\n66 kV','S.FERNANDO____154':'S. Fernando\n154 kV',
        'TINGUIRIRICA__154':'Tinguiririca\n154 kV','TINGUIRIRICA__220':'Tinguiririca\n220 kV','CANDELARIA____220':'CANDELARIA\n220 kV',
        'PARRAL________066':'Parral\n66 kV','PARRAL________154':'Parral\n154 kV','MAULE_________154':'Maule\n154 kV','MAULE_________220':'Maule\n220 kV','ANCOA_________220':'ANCOA\n220 kV'}
via={('LAPALMA_______066','ITAHUE________066'):'por Talca',('LINARES_______066','ITAHUE________066'):'por S. Javier y Talca',('ITAHUE________066','S.FERNANDO____066'):'por Curicó y Teno',
     ('LINARES_______066','PARRAL________066'):'por Longaví y Retiro',('PARRAL________154','MAULE_________154'):'por Linares 154'}
P={'A':nx.dijkstra_path(g0,o,'CANDELARIA____220',weight='w'),'B':nx.dijkstra_path(g1,o,'ITAHUE________220',weight='w')}
def tramos(k):
    p=P[k]; ks=claves[k]; idx=[p.index(n) for n in ks]; out=[]
    for i,j,a,b in zip(idx,idx[1:],ks,ks[1:]):
        seg=p[i:j+1]; r=sum(g0[x][y]['w'] for x,y in zip(seg,seg[1:])); f=sum(g1[x][y]['w'] for x,y in zip(seg,seg[1:]))
        t='T' if a[-3:]!=b[-3:] else int(a[-3:]); out.append((a,b,r,f,t,len(seg)-1))
    return out
fig,ax=plt.subplots(figsize=(17,8.5),dpi=170); ax.set_xlim(-0.6,12.6); ax.set_ylim(-0.4,6.2); ax.axis('off')
for k,y,dest in [('A',4.3,'Candelaria (a 199 km) — rodeo por 66 kV'),('B',1.0,'Itahue (a 58 km) — sube por los trafos de Itahue')]:
    tr=tramos(k); n=len(tr); xs=[i*11.2/ (len(claves['A'])-1) for i in range(n+1)]
    ax.text(-0.5,y+1.15,f"Camino {k} → {dest}",fontsize=14,fontweight='bold',color=DARK)
    tot0=sum(t[2] for t in tr); tot1=sum(t[3] for t in tr)
    for i,(a,b,r,f,t,m) in enumerate(tr):
        x0,x1=xs[i],xs[i+1]
        ax.plot([x0,x1],[y,y],color=COL[t],lw=6 if t!='T' else 3,zorder=1,solid_capstyle='butt',ls='-' if t!='T' else (0,(2,1.2)))
        xm=(x0+x1)/2
        tipo='trafo' if t=='T' else f'línea {t} kV'+(f' ({m} tramos)' if m>1 else '')
        ax.text(xm,y+0.33,tipo+('\n'+via[(a,b)] if (a,b) in via else ''),ha='center',va='bottom',fontsize=10,color=GREY)
        ax.text(xm,y-0.30,f"hoy  {fmt(r)}",ha='center',va='top',fontsize=11.5,color=HOY,fontweight='bold')
        ax.text(xm,y-0.62,f"ref.  {fmt(f)}",ha='center',va='top',fontsize=11.5,color=REF,fontweight='bold')
    for i,nd in enumerate(claves[k]):
        last=i==len(claves[k])-1
        ax.add_patch(Circle((xs[i],y),0.17 if not last else 0.22,fc='white' if not last else (REF if k=='B' else HOY),ec=DARK,lw=2,zorder=3))
        ax.text(xs[i],y+(0.30 if i%2==0 else 0.30),'',zorder=4)
        ax.text(xs[i],y-1.05,nombre[nd],ha='center',va='top',fontsize=10.5,color=DARK,fontweight='bold' if last or i==0 else 'normal')
    xe=xs[-1]+0.45
    ax.text(xe,y+0.12,f"hoy  {fmt(tot0)} Ω"+("  ← gana" if k=='A' else ""),fontsize=13.5,fontweight='bold',color=HOY,va='bottom')
    ax.text(xe,y-0.12,f"ref.  {fmt(tot1)} Ω"+("  ← gana" if k=='B' else ""),fontsize=13.5,fontweight='bold',color=REF,va='top')
ax.set_title('La Palma 13 kV: dos caminos, valor de cada tramo hoy (sin transformar) y referido a 220 kV',fontsize=16,color=DARK,fontweight='bold')
fig.text(0.5,-0.03,'Los dos primeros tramos son comunes. Desde Itahue 66 kV, hoy el rodeo hasta Candelaria suma 79,1 Ω y los trafos de Itahue 134,6 Ω: gana Candelaria.\nReferido, el rodeo suma 399,7 Ω (su línea de 66 kV pasa de 29,7 a 330,1) y los trafos 223,8 Ω: gana Itahue.',
         ha='center',fontsize=12,color=DARK)
fig.tight_layout(rect=(0,0.04,1,1)); fig.savefig(S+'fig/nodos_lapalma.png',bbox_inches='tight',facecolor='white')
for k in 'AB': print(k,[(a[:10],b[:10],round(r,1),round(f,1),m) for a,b,r,f,t,m in tramos(k)])
