"""Banco de criterios: misma red del módulo, distintas métricas de distancia eléctrica."""
import sys, warnings, contextlib, io
warnings.filterwarnings("ignore")
sys.path.insert(0, '/home/user/balance-de-potencia-anual/src/minimo_camino/domain')
import minimo_camino as mc, pandas as pd, numpy as np, networkx as nx
from datetime import date
from math import radians, sin, cos, asin, sqrt
OUT = '/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/'
INP = '/home/user/balance-de-potencia-anual/data/minimo_camino/inputs/2025/pre/'; ENT = INP + 'Ent2026.xlsx'
EPS = 1e-6
VREF = 220.0
ev = pd.read_pickle('/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/docs/scripts/analisis/criterios_ev.pkl')

barras = mc.cargar_barras(ENT); lineas = mc.cargar_lineas(ENT); linman = mc.cargar_linman(ENT)
full = pd.read_excel(ENT, sheet_name='lineas', header=4)
lineas['tipo'] = lineas['N_linea'].map(dict(zip(full['Nº'], full['Trafo o Linea'])))
nm = dict(zip(barras['N'].astype(int), barras['Barra']))
pncp = pd.read_excel(INP + 'Barras_PNCP.xlsx', sheet_name='barras', usecols='B:E', header=None)
for i in range(10):
    if any('NombrePNCP' in str(v) for v in pncp.iloc[i].values):
        pncp.columns = pncp.iloc[i].values; pncp = pncp.iloc[i + 1:].reset_index(drop=True); break
pncp = pncp.dropna(subset=['NombreEnt']); PN = set(pncp['NombreEnt']); sub_t = dict(zip(pncp['NombreEnt'], pncp['Subsistema']))
SUBEST_PN = {t[:14] for t in PN}
oper = mc.filtrar_operativas(lineas, linman, date(2025, 12, 31)).merge(lineas[['N_linea', 'tipo']], on='N_linea', how='left')
A = oper['Barra A'].map(nm); B = oper['Barra B'].map(nm); T = oper['tipo'] == 'T'
m1 = T & (A.str[:14].isin(SUBEST_PN) | B.str[:14].isin(SUBEST_PN))
m3 = T & (A.isin(PN) | B.isin(PN))                       # solo trafos que tocan la barra troncal
ref = (VREF / oper['V'].astype(float)) ** 2               # factor para referir Ω a 220 kV

esc = {}
esc['actual'] = oper.copy()
o = oper.copy(); o.loc[m1, 'X'] = EPS; esc['C1'] = o
o = oper.copy(); o.loc[T, 'X'] = EPS; esc['C2'] = o
o = oper.copy(); o.loc[m3, 'X'] = EPS; esc['C3_trafo_troncal'] = o
o = oper.copy(); o['X'] = o['X'] * ref; esc['P_ref220'] = o
o = oper.copy(); o['X'] = o['X'] * ref; o.loc[m1, 'X'] = EPS; esc['P_C1'] = o
o = oper.copy(); o['X'] = o['X'] * ref; o.loc[T, 'X'] = EPS; esc['P_C2'] = o


def grafo(op):
    with contextlib.redirect_stdout(io.StringIO()):
        agr = mc.agrupar_lineas(op[['N_linea', 'Nombre', 'Barra A', 'Barra B', 'V', 'R', 'X']])
    G = nx.Graph()
    for _, e in agr.dropna(subset=['Xfinal']).iterrows():
        if e['Xfinal'] > 0:
            G.add_edge(nm[int(e['Barra_A'])], nm[int(e['Barra_B'])], w=float(e['Xfinal']))
    return G


def thevenin(G):
    """Reactancia efectiva entre pares (distancia de resistencia) por componente conexa."""
    out = {}
    for comp in nx.connected_components(G):
        nodes = sorted(comp); ix = {n: i for i, n in enumerate(nodes)}; n = len(nodes)
        if n < 2: continue
        Lp = np.zeros((n, n))
        for u, v, d in G.subgraph(nodes).edges(data=True):
            g = 1.0 / d['w']; i, j = ix[u], ix[v]
            Lp[i, i] += g; Lp[j, j] += g; Lp[i, j] -= g; Lp[j, i] -= g
        Z = np.linalg.pinv(Lp, hermitian=True)
        out.update({nd: (Z, ix) for nd in nodes})
    return out


grafos = {k: grafo(v) for k, v in esc.items()}
th = {'TH_ohm': (grafos['actual'], thevenin(grafos['actual'])),
      'TH_ref220': (grafos['P_ref220'], thevenin(grafos['P_ref220']))}

cdf = pd.read_excel(INP + 'conversor_coordenadas_Nodos.xlsx', sheet_name=0, header=None); cdf.columns = cdf.iloc[3].values; cdf = cdf.iloc[4:]
coord = {r['BarraFacturación']: (float(r['Latitud']), float(r['Longitud'])) for _, r in cdf[['BarraFacturación', 'Latitud', 'Longitud']].dropna().iterrows()}


def km(a, b):
    if a not in coord or b not in coord: return np.nan
    la1, lo1 = map(radians, coord[a]); la2, lo2 = map(radians, coord[b])
    return 2 * 6371 * asin(sqrt(sin((la2 - la1) / 2) ** 2 + cos(la1) * cos(la2) * sin((lo2 - lo1) / 2) ** 2))


def elegir(dist):
    """min con empate alfabético (como el módulo). Devuelve troncal, d1, margen relativo."""
    c = sorted((round(d, 9), t) for t, d in dist.items() if np.isfinite(d))
    if not c: return None, np.nan, np.nan, False
    d1 = c[0][0]; emp = len(c) > 1 and abs(c[1][0] - d1) < 1e-6
    mrg = (c[1][0] - d1) / d1 if len(c) > 1 and d1 > 0 else np.nan
    return c[0][1], d1, mrg, emp


rows = []
for _, r in ev.iterrows():
    b = r['barra']; nodo = b if not r['sustituta'] else (r['sustituta'] if r['sustituta'] != 'SIN_MATCH' else None)
    sub = r['subsistema']; cand = [t for t in PN if sub_t.get(t) == sub]
    row = {'barra': b, 'nodo': nodo, 'sub': sub, 'PN2604': r['PN2604'], 'mod_actual': r['actual_troncal']}
    # troncal geográficamente más cercana
    gk = {t: km(b if b in coord else nodo, t) for t in cand}
    gk = {t: d for t, d in gk.items() if np.isfinite(d)}
    row['geo_mas_cercana'] = min(gk, key=gk.get) if gk else None
    for k, G in grafos.items():
        if nodo not in G: continue
        d = nx.single_source_dijkstra_path_length(G, nodo, weight='w')
        t, d1, mrg, emp = elegir({x: d.get(x, np.inf) for x in cand})
        row.update({f'{k}': t, f'{k}_d': d1, f'{k}_mrg': mrg, f'{k}_emp': emp})
    for k, (G, Zs) in th.items():
        if nodo not in Zs: continue
        Z, ix = Zs[nodo]; i = ix[nodo]
        dist = {x: Z[i, i] + Z[ix[x], ix[x]] - 2 * Z[i, ix[x]] for x in cand if x in ix}
        t, d1, mrg, emp = elegir(dist)
        row.update({f'{k}': t, f'{k}_d': d1, f'{k}_mrg': mrg, f'{k}_emp': emp})
    rows.append(row)
R = pd.DataFrame(rows)
R.to_pickle(OUT + 'banco.pkl')
print('validación actual propio vs módulo:', (R['actual'] == R['mod_actual']).mean(), len(R))
