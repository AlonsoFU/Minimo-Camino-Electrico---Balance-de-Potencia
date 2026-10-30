import sys, warnings, contextlib, io
warnings.filterwarnings("ignore")
sys.path.insert(0, '/home/user/balance-de-potencia-anual/src/minimo_camino/domain')
import minimo_camino as mc, pandas as pd, numpy as np, networkx as nx
from datetime import date
from math import radians, sin, cos, asin, sqrt
OUT='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/'
U='/tmp/claude-0/-home-user-Minimo-Camino-Electrico---Balance-de-Potencia/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/up/bal.xlsm'
INP='/home/user/balance-de-potencia-anual/data/minimo_camino/inputs/2025/pre/'; ENT=INP+'Ent2026.xlsx'
EPS=1e-6
A287=['GUARDIAMARINA_023','LIQCAU________110','RECINTO_______013','RECINTO_______033','SENORAZA______066','FUENTECILLA___066','GUARDIAMARINA_013','LIQCAU1_______220','SENORAZA______220']
A288=['TSAN_JOAQUIN__110']
# ---------- insumos del módulo (ENT tal cual) ----------
barras=mc.cargar_barras(ENT); lineas=mc.cargar_lineas(ENT); linman=mc.cargar_linman(ENT)
full=pd.read_excel(ENT,sheet_name='lineas',header=4)
lineas['tipo']=lineas['N_linea'].map(dict(zip(full['Nº'],full['Trafo o Linea'])))
nm=dict(zip(barras['N'].astype(int),barras['Barra']))
rb=pd.read_excel(ENT,sheet_name='barras',header=None).iloc[5:]
sector=dict(zip(rb[9],rb[0]))
pncp=pd.read_excel(INP+'Barras_PNCP.xlsx',sheet_name='barras',usecols='B:E',header=None)
for i in range(10):
    if any('NombrePNCP' in str(v) for v in pncp.iloc[i].values): pncp.columns=pncp.iloc[i].values; pncp=pncp.iloc[i+1:].reset_index(drop=True); break
pncp=pncp.dropna(subset=['NombreEnt']); PN=set(pncp['NombreEnt']); sub_t=dict(zip(pncp['NombreEnt'],pncp['Subsistema']))
SUBEST_PN={t[:14] for t in PN}
base=pd.read_excel(INP+'Base_Potencia_2601_pre.xlsx',sheet_name='03 INPUT DS SUBSISTEMAS',usecols='B:C',header=None); base.columns=base.iloc[3].values; base=base.iloc[4:].reset_index(drop=True)
rev=pd.read_csv('/home/user/balance-de-potencia-anual/data/minimo_camino/revision/2025/pre/revision_subsistemas.csv')
base=pd.concat([base,rev[['barra_balance_fisico','subsistema']].rename(columns={'barra_balance_fisico':'Barra','subsistema':'Subsistema'})],ignore_index=True).drop_duplicates('Barra')
bb=base.merge(barras,on='Barra',how='left'); se=bb[bb['N'].isna()][['Barra','Subsistema']]; bb=bb.dropna(subset=['N']); bb['N']=bb['N'].astype(int)
sub_b=dict(zip(base['Barra'],base['Subsistema']))
mapeo=mc.generar_mapeo_sin_ent(barras['Barra'].dropna().tolist(),se['Barra'].dropna().tolist())
ents=set(barras['Barra']); ref=rev.drop_duplicates('barra_balance_fisico').set_index('barra_balance_fisico')['barra_referencia']
for b in list(mapeo):
    if b in ref.index and ref[b] in ents: mapeo[b]=(ref[b],'REVISION_SUBSISTEMAS')
oper=mc.filtrar_operativas(lineas,linman,date(2025,12,31)).merge(lineas[['N_linea','tipo']],on='N_linea',how='left')
A=oper['Barra A'].map(nm); B=oper['Barra B'].map(nm); T=oper['tipo']=='T'
m1=T&(A.str[:14].isin(SUBEST_PN)|B.str[:14].isin(SUBEST_PN))
escen={'actual':oper.copy()}
o=oper.copy(); o.loc[m1,'X']=EPS; escen['criterio1']=o
o=oper.copy(); o.loc[T,'X']=EPS; escen['criterio2']=o
print('trafos anulados: criterio1',int(m1.sum()),' criterio2',int(T.sum()))
kv=lambda n: int(n[-3:]) if isinstance(n,str) and n[-3:].isdigit() else None
res={}
for k,op in escen.items():
    with contextlib.redirect_stdout(io.StringIO()):
        agr=mc.agrupar_lineas(op[['N_linea','Nombre','Barra A','Barra B','V','R','X']])
        cam=mc.construir_grafo_y_shortest_paths(mc.agregar_barras_aisladas(agr,barras))
        r=mc.calcular_minima_distancia(cam,barras,pncp,bb); r,_=mc.copiar_resultados_proxy(r,se,mapeo)
    G=nx.Graph()
    for _,e in agr.dropna(subset=['Xfinal']).iterrows():
        if e['Xfinal']>0: G.add_edge(nm[int(e['Barra_A'])],nm[int(e['Barra_B'])],w=float(e['Xfinal']))
    res[k]=(r.drop_duplicates('NomBarra_A').set_index('NomBarra_A'),G)
# ---------- referencia PN2604, precios y MW ----------
a4=pd.read_excel(U,sheet_name='04. ASOCIACIÓN DE BARRAS',header=None,usecols='B:D').iloc[4:]; a4.columns=['f','barra','troncal']
pn=a4[a4['f']=='PN2604'].dropna(subset=['barra']).drop_duplicates('barra').set_index('barra')['troncal']
p3=pd.read_excel(U,sheet_name='03. PRECIOS DE NUDO',header=None,usecols='B:D').iloc[4:]; p3.columns=['f','t','precio']
precio=p3[p3['f']=='PN2604'].set_index('t')['precio'].astype(float)
bf=pd.read_excel(U,sheet_name='05. BALANCE FÍSICO',header=None,usecols='H:N').iloc[6:]; bf.columns=['barra','tr','ndp','cons','fp','aj','mw']
bf['mw']=pd.to_numeric(bf['mw'],errors='coerce').fillna(0)
mw_net=bf.groupby('barra')['mw'].sum(); mw_abs=bf.groupby('barra')['mw'].apply(lambda s:s.abs().sum())
cdf=pd.read_excel(INP+'conversor_coordenadas_Nodos.xlsx',sheet_name=0,header=None); cdf.columns=cdf.iloc[3].values; cdf=cdf.iloc[4:]
coord={r['BarraFacturación']:(float(r['Latitud']),float(r['Longitud'])) for _,r in cdf[['BarraFacturación','Latitud','Longitud']].dropna().iterrows()}
def km(a,b):
    if a not in coord or b not in coord: return np.nan
    la1,lo1=map(radians,coord[a]); la2,lo2=map(radians,coord[b]); return 2*6371*asin(sqrt(sin((la2-la1)/2)**2+cos(la1)*cos(la2)*sin((lo2-lo1)/2)**2))
print('troncales sin coordenadas:',[t for t in PN if t not in coord], ' sin sector:',[t for t in PN if t not in sector])
# ---------- tabla por barra ----------
rows=[]
for b,tp in pn.items():
    nodo=b if b in ents else (mapeo.get(b,(None,))[0] or None)
    sec_b=sector.get(nodo) if nodo else None
    row={'barra':b,'sector_barra':sec_b,'subsistema':sub_b.get(b),'sustituta':'' if b in ents else (nodo or 'SIN_MATCH'),
         'afectada_287':b in A287,'afectada_288':b in A288,'MW_neto_h05':round(mw_net.get(b,0),3),'MW_abs_h05':round(mw_abs.get(b,0),3),
         'PN2604':tp,'sector_PN2604':sector.get(tp),'precio_PN2604':precio.get(tp)}
    for k,(r,G) in res.items():
        if b not in r.index: row.update({f'{k}_troncal':None}); continue
        t=r.loc[b,'nomBarra_B']; row[f'{k}_troncal']=t; row[f'{k}_X']=round(r.loc[b,'DistMin'],3); row[f'{k}_empate']=r.loc[b,'Empate']
        if k!='actual':
            row[f'{k}_cambia']=t!=tp
            row[f'{k}_sector']=sector.get(t)
            row[f'{k}_cambio_zona']=(t!=tp) and (sector.get(t)!=sector.get(tp))
            row[f'{k}_km_entre_troncales']=round(km(tp,t),0) if t!=tp else 0
            row[f'{k}_dprecio']=(precio.get(t,np.nan)-precio.get(tp,np.nan)) if t!=tp else 0.0
            row[f'{k}_impacto_MM$mes']=round(row[f'{k}_dprecio']*mw_net.get(b,0)*1000/1e6,3) if t!=tp else 0.0
            # margen y camino
            if nodo in G:
                d,pth=nx.single_source_dijkstra(G,nodo,weight='w')
                cand=sorted((d[x],x) for x in PN if x in d and sub_t.get(x)==sub_b.get(b))
                row[f'{k}_margen_ohm']=round(cand[1][0]-cand[0][0],3) if len(cand)>1 else np.nan
                p=pth.get(t,[]); k0=kv(nodo); kt=kv(t)
                low=[x for x in p[1:-1] if kv(x) is not None and k0 is not None and kv(x)<min(k0,kt or 999) and kv(x)<66]
                row[f'{k}_pasa_por_baja_tension']=len(low)>0
    rows.append(row)
t=pd.DataFrame(rows)
t.to_pickle(OUT+'criterios.pkl'); print('filas',len(t))
