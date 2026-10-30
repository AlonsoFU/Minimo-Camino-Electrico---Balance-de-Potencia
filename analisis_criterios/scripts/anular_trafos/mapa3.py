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
TEAL="#30849B"; ORANGE="#E8752A"; PURPLE="#7B5EA7"; GREY="#8C8C8C"; DARK="#404040"
S='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/'
INP='/home/user/balance-de-potencia-anual/data/minimo_camino/inputs/2025/pre/'; ENT=INP+'Ent2026.xlsx'
ev=pd.read_pickle(S+'criterios_ev.pkl')
grp=ev[(ev.criterio1_origen=='Diferencia nueva del criterio')&(ev.PN2604=='CANDELARIA____220')&(ev.criterio1_troncal=='A.JAHUEL______220')]
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
C={r['BarraFacturación']:(float(r['Longitud']),float(r['Latitud'])) for _,r in cdf[['BarraFacturación','Latitud','Longitud']].dropna().iterrows()}
C={k:v for k,v in C.items() if -71.6<v[0]<-70.3 and -35.0<v[1]<-33.4}
print('sin coordenada válida en caminos se omiten')
src='TILCOCO2______154'
colT={'CANDELARIA____220':TEAL,'A.JAHUEL______220':ORANGE}
info={}
for k,G in Gs.items():
    t=ev.loc[ev.barra==src,f'{k}_troncal'].iloc[0]
    d,p=nx.single_source_dijkstra(G,src,weight='w'); info[k]=(t,d[t],p[t],{x:round(d[x],1) for x in ['CANDELARIA____220','A.JAHUEL______220']})
    print(k,t,round(d[t],1),info[k][3],' > '.join(x.replace('_','') for x in p[t]))
    print('   grupo:',grp[f'{k}_troncal'].value_counts().to_dict())
pts=[C[x] for x in set(sum([v[2] for v in info.values()],[])+list(grp.barra)+['CANDELARIA____220','A.JAHUEL______220']) if x in C]
x0,x1=min(p[0] for p in pts)-0.1,max(p[0] for p in pts)+0.28; y0,y1=min(p[1] for p in pts)-0.06,max(p[1] for p in pts)+0.2
titles={'actual':'Hoy (módulo y PN2604)','criterio1':'Criterio 1\ntrafos de subestaciones troncales en 0','criterio2':'Criterio 2\ntodos los trafos en 0'}
fig,axs=plt.subplots(1,3,figsize=(15,8.2),dpi=180)
for ax,k in zip(axs,['actual','criterio1','criterio2']):
    G=Gs['actual']
    for u,v in G.edges():
        if u in C and v in C:
            (a,b),(c,d)=C[u],C[v]
            if x0<=a<=x1 and y0<=b<=y1 and x0<=c<=x1 and y0<=d<=y1: ax.plot([a,c],[b,d],color="#DADADA",lw=0.7,zorder=1)
    t,dist,p,dd=info[k]; col=colT.get(t,PURPLE)
    pv=[x for x in p if x in C]; print(k,'omitidas en camino:',[x for x in p if x not in C])
    ax.plot([C[x][0] for x in pv],[C[x][1] for x in pv],color=col,lw=3.2,zorder=3,solid_capstyle='round')
    for _,r in grp.iterrows():
        if r.barra in C: ax.scatter(*C[r.barra],s=20,color=colT.get(r[f'{k}_troncal'],PURPLE),edgecolor='white',lw=0.4,zorder=4,alpha=0.85)
    for tt,lab in [('CANDELARIA____220','Candelaria'),('A.JAHUEL______220','Alto Jahuel')]:
        ax.scatter(*C[tt],s=200,marker='s',color=colT[tt],edgecolor='white',lw=1.4,zorder=6)
        ax.text(C[tt][0]+0.025,C[tt][1],lab,fontsize=9.5,color=colT[tt],fontweight='bold',va='center',zorder=7)
    ax.scatter(*C[src],s=120,color=col,edgecolor=DARK,lw=1.2,zorder=6)
    ax.text(C[src][0]-0.02,C[src][1]+0.02,'Tilcoco 154',fontsize=8.5,color=DARK,ha='right',zorder=7)
    nC=int((grp[f'{k}_troncal']=='CANDELARIA____220').sum()); nA=int((grp[f'{k}_troncal']=='A.JAHUEL______220').sum())
    ax.set_title(titles[k],fontsize=11.5,color=DARK,fontweight='bold')
    ax.text(0.03,0.985,f"Tilcoco → {t[:11].rstrip('_').replace('A.JAHUEL','Alto Jahuel').title()}: {str(round(dist,1)).replace('.',',')} Ω\n"
                      f"A Candelaria {str(dd['CANDELARIA____220']).replace('.',',')} Ω · a Alto Jahuel {str(dd['A.JAHUEL______220']).replace('.',',')} Ω\n"
                      f"Grupo de 35 barras: {nC} Candelaria · {nA} Alto Jahuel",transform=ax.transAxes,fontsize=9,color=DARK,va='top',
                      bbox=dict(boxstyle='round,pad=0.4',fc='white',ec='#CCCCCC'))
    ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect(1/0.83); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_color('#DDDDDD')
fig.suptitle("Tilcoco 154 kV y las 35 barras de la zona: troncal asignada en cada caso",fontsize=13,color=DARK,fontweight='bold',y=0.99)
fig.text(0.5,0.015,"Color de cada barra = troncal asignada (azul Candelaria, naranja Alto Jahuel). Línea gruesa = camino de Tilcoco 154 kV hasta su troncal.",ha='center',fontsize=9.5,color=GREY)
fig.tight_layout(rect=(0,0.03,1,0.96))
fig.savefig(S+'mapa_tilcoco_3casos.png',bbox_inches='tight',facecolor='white')
