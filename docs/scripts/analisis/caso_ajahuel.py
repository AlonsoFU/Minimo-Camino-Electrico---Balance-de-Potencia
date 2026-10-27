import sys, warnings, contextlib, io; warnings.filterwarnings("ignore")
sys.path.insert(0,'/home/user/balance-de-potencia-anual/src/minimo_camino/domain')
import minimo_camino as mc, pandas as pd, networkx as nx
from datetime import date
ev=pd.read_pickle('/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/criterios_ev.pkl')
g=ev[(ev.criterio1_origen=='Diferencia nueva del criterio')&(ev.PN2604=='CANDELARIA____220')&(ev.criterio1_troncal=='A.JAHUEL______220')].sort_values('MW_abs_h05',ascending=False)
print(g[['barra','MW_abs_h05','actual_X','criterio1_X']].head(8).to_string(index=False))
INP='/home/user/balance-de-potencia-anual/data/minimo_camino/inputs/2025/pre/'; ENT=INP+'Ent2026.xlsx'
barras=mc.cargar_barras(ENT); lineas=mc.cargar_lineas(ENT); linman=mc.cargar_linman(ENT)
full=pd.read_excel(ENT,sheet_name='lineas',header=4); lineas['tipo']=lineas['N_linea'].map(dict(zip(full['Nº'],full['Trafo o Linea'])))
nm=dict(zip(barras['N'].astype(int),barras['Barra']))
pncp=pd.read_excel(INP+'Barras_PNCP.xlsx',sheet_name='barras',usecols='B:E',header=None)
for i in range(10):
    if any('NombrePNCP' in str(v) for v in pncp.iloc[i].values): pncp.columns=pncp.iloc[i].values; pncp=pncp.iloc[i+1:]; break
SUB={t[:14] for t in pncp['NombreEnt'].dropna()}
op=mc.filtrar_operativas(lineas,linman,date(2025,12,31)).merge(lineas[['N_linea','tipo']],on='N_linea',how='left')
A=op['Barra A'].map(nm); B=op['Barra B'].map(nm); T=op['tipo']=='T'
for sub in ['A.JAHUEL','AJAHUEL','CANDELARIA']:
    s=op[T&(A.str.startswith(sub)|B.str.startswith(sub))]
    print(sub,'trafos:',[(f"{nm[a]}–{nm[b]}",round(x,1)) for a,b,x in zip(s['Barra A'],s['Barra B'],s['X'])])
def G_(o):
    with contextlib.redirect_stdout(io.StringIO()): agr=mc.agrupar_lineas(o[['N_linea','Nombre','Barra A','Barra B','V','R','X']])
    G=nx.Graph()
    for _,e in agr.dropna(subset=['Xfinal']).iterrows():
        if e['Xfinal']>0: G.add_edge(nm[int(e['Barra_A'])],nm[int(e['Barra_B'])],w=float(e['Xfinal']))
    return G
o1=op.copy(); o1.loc[T&(A.str[:14].isin(SUB)|B.str[:14].isin(SUB)),'X']=1e-6
b=g.iloc[0]['barra']
for lab,G in [('actual',G_(op)),('criterio1',G_(o1))]:
    d,p=nx.single_source_dijkstra(G,b,weight='w'); print('\n',lab)
    for t in ['CANDELARIA____220','A.JAHUEL______220']:
        print(f"  {t[:10]}: {d[t]:.1f} Ω | "+' > '.join(f"{x.replace('_','')}" for x in p[t]))
        print('     X:',' ; '.join(f"{G[u][v]['w']:.1f}" for u,v in zip(p[t][:-1],p[t][1:])))
