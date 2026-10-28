import pickle, pandas as pd, networkx as nx, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
DARK="#404040"; GREY="#8C8C8C"; PAL=["#30849B","#E8752A","#7B5EA7","#5B9A3C"]
S='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/'
INP='/home/user/balance-de-potencia-anual/data/minimo_camino/inputs/2025/pre/'
G=pickle.load(open(S+'grafos.pkl','rb')); Gs={k:G[k] for k in ['actual','P_ref220','P_C1']}
R=pd.read_pickle(S+'banco.pkl'); sub_b=dict(zip(R.nodo,R['sub']))
pncp=pd.read_excel(INP+'Barras_PNCP.xlsx',sheet_name='barras',usecols='B:E',header=None)
for i in range(10):
    if any('NombrePNCP' in str(v) for v in pncp.iloc[i].values): pncp.columns=pncp.iloc[i].values; pncp=pncp.iloc[i+1:]; break
pncp=pncp.dropna(subset=['NombreEnt']); PN=set(pncp['NombreEnt']); sub_t=dict(zip(pncp['NombreEnt'],pncp['Subsistema']))
cdf=pd.read_excel(INP+'conversor_coordenadas_Nodos.xlsx',sheet_name=0,header=None); cdf.columns=cdf.iloc[3].values; cdf=cdf.iloc[4:]
C0={r['BarraFacturación']:(float(r['Longitud']),float(r['Latitud'])) for _,r in cdf[['BarraFacturación','Latitud','Longitud']].dropna().iterrows()}
T3={'actual':'Hoy\nΩ sumados sin referir','P_ref220':'Criterio 1\nΩ referidos a una tensión común','P_C1':'Criterio 2\nreferidos + destino = subestación troncal'}
UN={'actual':'Ω','P_ref220':'Ω ref.','P_C1':'Ω ref.'}
f=lambda v:f"{v:,.1f}".replace(',','X').replace('.',',').replace('X','.')
def mapa(src,nombre,box,out,nombres,nota=''):
    C={k:v for k,v in C0.items() if box[0]<v[0]<box[1] and box[2]<v[1]<box[3]}
    info={}
    for k,g in Gs.items():
        d,p=nx.single_source_dijkstra(g,src,weight='w')
        cand=[x for x in d if x in PN and sub_t.get(x)==sub_b.get(src)]
        t=min(cand,key=lambda x:(round(d[x],6),x)); info[k]=(t,p[t],d)
        print(k,t,round(d[t],1))
    ts=[t for t in nombres if t in {v[0] for v in info.values()}]+[t for t in nombres if t not in {v[0] for v in info.values()}]
    col={t:PAL[i] for i,t in enumerate(ts)}
    pts=[C[x] for x in set(sum([v[1] for v in info.values()],[])+ts+[src]) if x in C]
    x0,x1=min(p[0] for p in pts)-0.10,max(p[0] for p in pts)+0.30; y0,y1=min(p[1] for p in pts)-0.06,max(p[1] for p in pts)+0.22
    fig,axs=plt.subplots(1,3,figsize=(15,7.4),dpi=170)
    for ax,k in zip(axs,Gs):
        for u,v in Gs['actual'].edges():
            if u in C and v in C:
                (a,b),(c,d)=C[u],C[v]
                if x0<=a<=x1 and y0<=b<=y1 and x0<=c<=x1 and y0<=d<=y1: ax.plot([a,c],[b,d],color="#DADADA",lw=0.7,zorder=1)
        t,p,dd=info[k]; pv=[x for x in p if x in C]
        ax.plot([C[x][0] for x in pv],[C[x][1] for x in pv],color=col[t],lw=3.4,zorder=3,solid_capstyle='round',alpha=0.9)
        for tt in ts:
            ax.scatter(*C[tt],s=210,marker='s',color=col[tt],edgecolor='white',lw=1.4,zorder=6)
            ax.text(C[tt][0]+0.035,C[tt][1],nombres[tt],fontsize=10,color=col[tt],fontweight='bold',va='center',zorder=7)
        ax.scatter(*C[src],s=140,marker='o',color='white',edgecolor=DARK,lw=2,zorder=6); ax.text(C[src][0]+0.035,C[src][1]-0.02,nombre,fontsize=9.5,color=DARK,zorder=7,fontweight='bold')
        ax.set_title(T3[k],fontsize=12,color=DARK,fontweight='bold')
        txt=f"Asigna: {nombres[t]}\n"+'\n'.join(f"{nombres[x]}: {f(dd[x])} {UN[k]}" for x in sorted(ts,key=lambda z:dd[z]))
        ax.text(0.03,0.985,txt,transform=ax.transAxes,fontsize=10,color=DARK,va='top',bbox=dict(boxstyle='round,pad=0.45',fc='white',ec=col[t],lw=1.5))
        ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect(1/0.83); ax.set_xticks([]); ax.set_yticks([])
        for s_ in ax.spines.values(): s_.set_color('#DDDDDD')
    fig.suptitle(f"{nombre}: troncal asignada con cada criterio",fontsize=14,color=DARK,fontweight='bold',y=0.995)
    fig.text(0.5,0.02,"Línea gruesa = camino de mínima reactancia hasta la troncal asignada. Gris = red del ENT. "+nota,ha='center',fontsize=9.5,color=GREY)
    fig.tight_layout(rect=(0,0.04,1,0.96)); fig.savefig(S+'fig/'+out,bbox_inches='tight',facecolor='white'); plt.close(fig)
N={'CANDELARIA____220':'Candelaria','ITAHUE________220':'Itahue','ANCOA_________220':'Ancoa','A.JAHUEL______220':'Alto Jahuel'}
print('LaPalma'); mapa('LAPALMA_______013','La Palma 13 kV',(-72.2,-70.3,-36.2,-33.5),'v2_mapa_lapalma.png',{k:N[k] for k in ['ITAHUE________220','ANCOA_________220','CANDELARIA____220']})
print('Curico'); mapa('CURICO________066','Curicó 66 kV',(-72.2,-70.3,-36.2,-33.5),'v2_mapa_curico.png',{k:N[k] for k in ['ITAHUE________220','CANDELARIA____220']})
print('Machali'); mapa('MACHALI_______066','Machalí 66 kV',(-71.6,-70.3,-34.8,-33.4),'v2_mapa_machali.png',{k:N[k] for k in ['CANDELARIA____220','A.JAHUEL______220']},
     nota="En el criterio 2 basta llegar a cualquier barra de la subestación (A.Jahuel 66 kV).")

# ---- barras apiladas: por qué cambia La Palma (desde Itahue 66 kV) ----
cat={'L66':('Líneas 66 kV','#E8752A'),'TR':('Transformadores','#7B5EA7'),'LAT':('Líneas 154–220 kV','#30849B')}
def tramos(g,p):
    out={'L66':0,'TR':0,'LAT':0}
    for a,b in zip(p,p[1:]):
        w=g[a][b]['w']; ka,kb=int(a[-3:]),int(b[-3:])
        out['TR' if ka!=kb else ('L66' if ka<=66 else 'LAT')]+=w
    return out
o='ITAHUE________066'
pA=['ITAHUE________066','ITAHUE________154','ITAHUE________220']
pB=nx.dijkstra_path(Gs['actual'],o,'CANDELARIA____220',weight='w')
fig,axs=plt.subplots(1,2,figsize=(12,5.6),dpi=170,sharey=False)
for ax,k,tt in zip(axs,['actual','P_ref220'],['Hoy: Ω sumados sin referir','Criterio 1: Ω referidos a una tensión común']):
    g=Gs[k]; vals=[tramos(g,pA),tramos(g,pB)]
    lab=['A. Subir en Itahue\n(trafos 66/154/220)\n→ Itahue','B. Rodeo ~100 km por 66 kV\n(Molina–Curicó–S.Fernando)\n→ Candelaria']
    bot=[0,0]
    for c,(nm_,cl) in cat.items():
        h=[v[c] for v in vals]; ax.bar(lab,h,bottom=bot,color=cl,width=0.55,label=nm_,edgecolor='white')
        for i in range(2):
            if h[i]>0.06*max(sum(v.values()) for v in vals): ax.text(i,bot[i]+h[i]/2,f(h[i]),ha='center',va='center',color='white',fontsize=10.5,fontweight='bold')
        bot=[bot[i]+h[i] for i in range(2)]
    w=0 if bot[0]<bot[1] else 1
    for i in range(2): ax.text(i,bot[i]*1.02,f"{f(bot[i])} {UN[k]}"+("  ← gana" if i==w else ""),ha='center',va='bottom',fontsize=11.5,fontweight='bold',color=('#2E7D32' if i==w else DARK))
    ax.set_title(tt,fontsize=12.5,color=DARK,fontweight='bold'); ax.set_ylim(0,max(bot)*1.18)
    for s_ in ['top','right']: ax.spines[s_].set_visible(False)
    ax.tick_params(axis='x',labelsize=10); ax.set_ylabel('Reactancia desde Itahue 66 kV',color=GREY)
axs[0].legend(frameon=False,fontsize=10.5,loc='upper right')
fig.suptitle('La Palma: por qué hoy se elige el rodeo y con el criterio 1 no',fontsize=14,color=DARK,fontweight='bold')
fig.text(0.5,0.01,'El tramo La Palma → Itahue 66 kV es común a ambos caminos y no se muestra. Referir a 220 kV multiplica los Ω de 66 kV por (220/66)² ≈ 11.',ha='center',fontsize=9.5,color=GREY)
fig.tight_layout(rect=(0,0.04,1,0.95)); fig.savefig(S+'fig/v2_barras_lapalma.png',bbox_inches='tight',facecolor='white')
