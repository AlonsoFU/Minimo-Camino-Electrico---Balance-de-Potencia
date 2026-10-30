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
DARK="#404040"; GREY="#8C8C8C"
COL={'D.ALMAGRO_____220':"#30849B",'OHIGGINS______220':"#7B5EA7",'C.PINTO_______220':"#E8752A"}
NOM={'D.ALMAGRO_____220':'Diego de Almagro','OHIGGINS______220':"O'Higgins",'C.PINTO_______220':'Carrera Pinto'}
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
for sub in ['JADRESIC','D.ALMAGRO','CUMBRES','OHIGGINS','C.PINTO']:
    s=op[T&(A.str.startswith(sub)|B.str.startswith(sub))]
    print(sub,'trafos:',sorted({(nm[a][-3:],nm[b][-3:],round(x,1)) for a,b,x in zip(s['Barra A'],s['Barra B'],s['X'])}))
cdf=pd.read_excel(INP+'conversor_coordenadas_Nodos.xlsx',sheet_name=0,header=None); cdf.columns=cdf.iloc[3].values; cdf=cdf.iloc[4:]
C={r['BarraFacturación']:(float(r['Longitud']),float(r['Latitud'])) for _,r in cdf[['BarraFacturación','Latitud','Longitud']].dropna().iterrows()}
C={k:v for k,v in C.items() if -71.5<v[0]<-68.0 and -28.5<v[1]<-22.5}
src='JADRESIC______220'
info={}
for k,G in Gs.items():
    d,p=nx.single_source_dijkstra(G,src,weight='w')
    t=min([x for x in d if x in PN],key=lambda x:d[x]); assert t in COL, t; info[k]=(t,p[t],{x:d[x] for x in COL})
    print(k,NOM[t],{NOM[x]:round(v,1) for x,v in info[k][2].items()},' > '.join(x.replace('_','') for x in p[t]))
    print('   X:',' ; '.join(f"{G[u][v]['w']:.1f}" for u,v in zip(p[t][:-1],p[t][1:])))
pts=[C[x] for x in set(sum([v[1] for v in info.values()],[])+list(COL)+[src]) if x in C]
x0,x1=min(p[0] for p in pts)-0.25,max(p[0] for p in pts)+0.45; y0,y1=min(p[1] for p in pts)-0.2,max(p[1] for p in pts)+0.6
T3={'actual':'Hoy: módulo (PN2604 usa Diego de Almagro)','criterio1':'Criterio 1\ntrafos de subestaciones troncales en 0','criterio2':'Criterio 2\ntodos los trafos en 0'}
fig,axs=plt.subplots(1,3,figsize=(15,7.2),dpi=180)
f=lambda v:str(round(v,1)).replace('.',',')
for ax,k in zip(axs,['actual','criterio1','criterio2']):
    for u,v in Gs['actual'].edges():
        if u in C and v in C:
            (a,b),(c,d)=C[u],C[v]
            if x0<=a<=x1 and y0<=b<=y1 and x0<=c<=x1 and y0<=d<=y1: ax.plot([a,c],[b,d],color="#DADADA",lw=0.7,zorder=1)
    t,p,dd=info[k]; pv=[x for x in p if x in C]
    ax.plot([C[x][0] for x in pv],[C[x][1] for x in pv],color=COL[t],lw=3.2,zorder=3,solid_capstyle='round')
    for tt in COL:
        ax.scatter(*C[tt],s=200,marker='s',color=COL[tt],edgecolor='white',lw=1.4,zorder=6)
        ax.text(C[tt][0]+0.09,C[tt][1],NOM[tt],fontsize=9.5,color=COL[tt],fontweight='bold',va='center',zorder=7)
    ax.scatter(*C[src],s=130,color=COL[t],edgecolor=DARK,lw=1.2,zorder=6); ax.text(C[src][0]+0.09,C[src][1],'Jadresic 220',fontsize=9,color=DARK,zorder=7)
    ax.set_title(T3[k],fontsize=11.5,color=DARK,fontweight='bold')
    ax.text(0.03,0.985,f"Asigna: {NOM[t]}\n"+'\n'.join(f"{NOM[x]}: {f(v)} Ω" for x,v in sorted(dd.items(),key=lambda z:z[1])),transform=ax.transAxes,fontsize=9.5,color=DARK,va='top',bbox=dict(boxstyle='round,pad=0.4',fc='white',ec='#CCCCCC'))
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect(1/0.83); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_color('#DDDDDD')
fig.suptitle("Jadresic 220 kV: una troncal distinta en cada caso",fontsize=13,color=DARK,fontweight='bold',y=0.99)
fig.text(0.5,0.02,"Línea gruesa = camino de mínima reactancia hasta la troncal asignada. Jadresic 220 y 500 kV suman unos 2.400 MW en la hoja 05. PN2604 la asocia a Diego de Almagro.",ha='center',fontsize=9.5,color=GREY)
fig.tight_layout(rect=(0,0.04,1,0.96)); fig.savefig(S+'mapa_jadresic_3casos.png',bbox_inches='tight',facecolor='white')
