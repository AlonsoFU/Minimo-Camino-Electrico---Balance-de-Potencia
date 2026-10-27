import sys, warnings, contextlib, io; warnings.filterwarnings("ignore")
sys.path.insert(0,'/home/user/balance-de-potencia-anual/src/minimo_camino/domain')
import minimo_camino as mc, pandas as pd, networkx as nx, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager
from datetime import date
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
DARK="#404040"; GREY="#8C8C8C"; PAL=["#30849B","#E8752A","#7B5EA7"]
S='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/'
INP='/home/user/balance-de-potencia-anual/data/minimo_camino/inputs/2025/pre/'; ENT=INP+'Ent2026.xlsx'
barras=mc.cargar_barras(ENT); lineas=mc.cargar_lineas(ENT); linman=mc.cargar_linman(ENT)
full=pd.read_excel(ENT,sheet_name='lineas',header=4); lineas['tipo']=lineas['N_linea'].map(dict(zip(full['Nº'],full['Trafo o Linea'])))
nm=dict(zip(barras['N'].astype(int),barras['Barra']))
pncp=pd.read_excel(INP+'Barras_PNCP.xlsx',sheet_name='barras',usecols='B:E',header=None)
for i in range(10):
    if any('NombrePNCP' in str(v) for v in pncp.iloc[i].values): pncp.columns=pncp.iloc[i].values; pncp=pncp.iloc[i+1:]; break
PN=set(pncp['NombreEnt'].dropna()); SUB={t[:14] for t in PN}
op=mc.filtrar_operativas(lineas,linman,date(2025,12,31)).merge(lineas[['N_linea','tipo']],on='N_linea',how='left')
A=op['Barra A'].map(nm); B=op['Barra B'].map(nm); T=op['tipo']=='T'
def G_(o):
    with contextlib.redirect_stdout(io.StringIO()): agr=mc.agrupar_lineas(o[['N_linea','Nombre','Barra A','Barra B','V','R','X']])
    G=nx.Graph()
    for _,e in agr.dropna(subset=['Xfinal']).iterrows():
        if e['Xfinal']>0: G.add_edge(nm[int(e['Barra_A'])],nm[int(e['Barra_B'])],w=float(e['Xfinal']))
    return G
o1=op.copy(); o1.loc[T&(A.str[:14].isin(SUB)|B.str[:14].isin(SUB)),'X']=1e-6
o2=op.copy(); o2.loc[T,'X']=1e-6
Gs={'actual':G_(op),'criterio1':G_(o1),'criterio2':G_(o2)}
cdf=pd.read_excel(INP+'conversor_coordenadas_Nodos.xlsx',sheet_name=0,header=None); cdf.columns=cdf.iloc[3].values; cdf=cdf.iloc[4:]
C0={r['BarraFacturación']:(float(r['Longitud']),float(r['Latitud'])) for _,r in cdf[['BarraFacturación','Latitud','Longitud']].dropna().iterrows()}
ev=pd.read_pickle(S+'criterios_ev.pkl'); sub_b=dict(zip(ev.barra,ev.subsistema)); sub_t=dict(zip(pncp['NombreEnt'],pncp['Subsistema']))
def mapa(src,nombre,box,out,nombres):
    C={k:v for k,v in C0.items() if box[0]<v[0]<box[1] and box[2]<v[1]<box[3]}
    info={}
    for k,G in Gs.items():
        d,p=nx.single_source_dijkstra(G,src,weight='w')
        cand=[x for x in d if x in PN and sub_t.get(x)==sub_b.get(src)]
        t=min(cand,key=lambda x:d[x]); info[k]=(t,p[t],d)
        print(k,t,round(d[t],1),' > '.join(x.replace('_','') for x in p[t]),'| X:',' ; '.join(f"{G[u][v]['w']:.1f}" for u,v in zip(p[t][:-1],p[t][1:])))
    ts=list(dict.fromkeys(v[0] for v in info.values())); col={t:PAL[i] for i,t in enumerate(ts)}
    pts=[C[x] for x in set(sum([v[1] for v in info.values()],[])+ts+[src]) if x in C]
    x0,x1=min(p[0] for p in pts)-0.08,max(p[0] for p in pts)+0.22; y0,y1=min(p[1] for p in pts)-0.05,max(p[1] for p in pts)+0.16
    T3={'actual':'Hoy (módulo y PN2604)','criterio1':'Criterio 1\ntrafos de subestaciones troncales en 0','criterio2':'Criterio 2\ntodos los trafos en 0'}
    f=lambda v:str(round(v,1)).replace('.',',')
    fig,axs=plt.subplots(1,3,figsize=(15,7.2),dpi=180)
    for ax,k in zip(axs,['actual','criterio1','criterio2']):
        for u,v in Gs['actual'].edges():
            if u in C and v in C:
                (a,b),(c,d)=C[u],C[v]
                if x0<=a<=x1 and y0<=b<=y1 and x0<=c<=x1 and y0<=d<=y1: ax.plot([a,c],[b,d],color="#DADADA",lw=0.7,zorder=1)
        t,p,dd=info[k]; pv=[x for x in p if x in C]
        ax.plot([C[x][0] for x in pv],[C[x][1] for x in pv],color=col[t],lw=3.2,zorder=3,solid_capstyle='round')
        for tt in ts:
            ax.scatter(*C[tt],s=200,marker='s',color=col[tt],edgecolor='white',lw=1.4,zorder=6)
            ax.text(C[tt][0]+0.03,C[tt][1],nombres[tt],fontsize=9.5,color=col[tt],fontweight='bold',va='center',zorder=7)
        ax.scatter(*C[src],s=130,color=col[t],edgecolor=DARK,lw=1.2,zorder=6); ax.text(C[src][0]+0.03,C[src][1]-0.015,nombre,fontsize=9,color=DARK,zorder=7)
        ax.set_title(T3[k],fontsize=11.5,color=DARK,fontweight='bold')
        ax.text(0.03,0.985,f"Asigna: {nombres[t]}\n"+'\n'.join(f"{nombres[x]}: {f(dd[x])} Ω" for x in sorted(ts,key=lambda z:dd[z])),transform=ax.transAxes,fontsize=9.5,color=DARK,va='top',bbox=dict(boxstyle='round,pad=0.4',fc='white',ec='#CCCCCC'))
        ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect(1/0.83); ax.set_xticks([]); ax.set_yticks([])
        for s_ in ax.spines.values(): s_.set_color('#DDDDDD')
    fig.suptitle(f"{nombre}: troncal asignada en cada caso",fontsize=13,color=DARK,fontweight='bold',y=0.99)
    fig.text(0.5,0.02,"Línea gruesa = camino de mínima reactancia hasta la troncal asignada.",ha='center',fontsize=9.5,color=GREY)
    fig.tight_layout(rect=(0,0.04,1,0.96)); fig.savefig(S+out,bbox_inches='tight',facecolor='white')
print('--- Santa Elena 13')
mapa('SANTA_ELENA___013','Santa Elena 13 kV',(-71.0,-70.4,-33.75,-33.25),'mapa_santaelena13.png',{'C.CHENA_______220':'Cerro Chena','C.NAVIA_______220':'Cerro Navia','A.JAHUEL______220':'Alto Jahuel'})
print('--- Colchagua 15')
mapa('COLCHAGUA_____015','Colchagua 15 kV',(-71.6,-70.3,-35.3,-33.6),'mapa_colchagua15.png',{'CANDELARIA____220':'Candelaria','ITAHUE________220':'Itahue'})
