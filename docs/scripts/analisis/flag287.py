import sys, warnings, contextlib, io
warnings.filterwarnings("ignore")
sys.path.insert(0,'/home/user/balance-de-potencia-anual/src/minimo_camino/domain')
import minimo_camino as mc, pandas as pd, networkx as nx
from datetime import date
OUT='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/'
INP='/home/user/balance-de-potencia-anual/data/minimo_camino/inputs/2025/pre/'; ENT=INP+'Ent2026.xlsx'
barras=mc.cargar_barras(ENT); lineas=mc.cargar_lineas(ENT); linman=mc.cargar_linman(ENT)
full=pd.read_excel(ENT,sheet_name='lineas',header=4); lineas['tipo']=lineas['N_linea'].map(dict(zip(full['Nº'],full['Trafo o Linea'])))
nm=dict(zip(barras['N'].astype(int),barras['Barra']))
N287={nm[1394]}
pncp=pd.read_excel(INP+'Barras_PNCP.xlsx',sheet_name='barras',usecols='B:E',header=None)
for i in range(10):
    if any('NombrePNCP' in str(v) for v in pncp.iloc[i].values): pncp.columns=pncp.iloc[i].values; pncp=pncp.iloc[i+1:]; break
SUB={t[:14] for t in pncp['NombreEnt'].dropna()}
oper=mc.filtrar_operativas(lineas,linman,date(2025,12,31)).merge(lineas[['N_linea','tipo']],on='N_linea',how='left')
A=oper['Barra A'].map(nm); B=oper['Barra B'].map(nm); T=oper['tipo']=='T'
esc={'actual':oper.copy()}
o=oper.copy(); o.loc[T&(A.str[:14].isin(SUB)|B.str[:14].isin(SUB)),'X']=1e-6; esc['criterio1']=o
o=oper.copy(); o.loc[T,'X']=1e-6; esc['criterio2']=o
ev=pd.read_pickle(OUT+'criterios_ev.pkl')
for k,op in esc.items():
    with contextlib.redirect_stdout(io.StringIO()):
        agr=mc.agrupar_lineas(op[['N_linea','Nombre','Barra A','Barra B','V','R','X']])
    G=nx.Graph()
    for _,e in agr.dropna(subset=['Xfinal']).iterrows():
        if e['Xfinal']>0: G.add_edge(nm[int(e['Barra_A'])],nm[int(e['Barra_B'])],w=float(e['Xfinal']))
    flags=[]
    for _,r in ev.iterrows():
        src=r['barra'] if r['sustituta']=='' else r['sustituta']; t=r[f'{k}_troncal']
        try: p=nx.dijkstra_path(G,src,t,weight='w') if src in G and isinstance(t,str) else []
        except nx.NetworkXNoPath: p=[]
        flags.append(any(x in N287 for x in p))
    ev[f'{k}_pasa_por_287']=flags
ev['marca_287']=ev['afectada_287']|ev['actual_pasa_por_287']|ev['criterio1_pasa_por_287']|ev['criterio2_pasa_por_287']
ev.to_pickle(OUT+'criterios_ev.pkl')
x=ev[ev['marca_287']&~ev['afectada_287']]
print('barras extra cuyo camino pasa por barras del #287:',len(x))
print(x[['barra','PN2604','actual_troncal','criterio1_troncal','criterio2_troncal','MW_abs_h05']].to_string(index=False))
