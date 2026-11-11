"""Tramos decisivos: corregir la X de UN tramo (valor sugerido de la validación previa) y ver qué barras cambian de troncal."""
exec(open('con_r.py').read().split("ESC = {")[0])
exec(open('con_r_plata.py').read().split("def monto")[0].replace("S=pd.read_pickle('con_r.pkl')", "S=pd.read_pickle(OUT+'con_r.pkl')"))
import time
V = pd.read_excel('/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/revision/output/homologacion_clasificada.xlsx')
V['ratio'] = V.valor_sugerido / V.X_ENT
rep = lambda r: any(abs(np.log(r / f)) < np.log(1.05) for f in (2, .5, 3, 1/3)) if pd.notna(r) and r > 0 else False
V['posible_representacion'] = V.ratio.map(rep)
TRONC = sorted(PN); nodo = R0['nodo']; sub = R0['sub']
cand = {b: [t for t in TRONC if sub_t.get(t) == sub[b]] for b in R0.index}
key = lambda a, b: (min(a, b), max(a, b))

def pesos(o):
    """X equivalente por par de barras (paralelos combinados)."""
    d = o.assign(u=np.minimum(o['Barra A'], o['Barra B']).astype(int), v=np.maximum(o['Barra A'], o['Barra B']).astype(int))
    return d, (1 / (1 / d['X']).groupby([d.u, d.v]).sum())

def asignar(w):
    G = nx.Graph()
    for (u, v), x in w.items():
        if x > 0: G.add_edge(nm[u], nm[v], w=float(x))
    D = {t: nx.single_source_dijkstra_path_length(G, t, weight='w') for t in TRONC if t in G}
    out = {}
    for b in R0.index:
        n = nodo[b]
        c = sorted((round(D[t][n], 9), t) for t in cand[b] if t in D and n in D[t])
        if c: out[b] = c[0][1]
    return pd.Series(out)

def escenario(o, rf, an):
    o = o.copy()
    if rf: o['X'] = o['X'] * ref
    if an is not None: o.loc[an, 'X'] = EPS
    return o

CRIT = {'Ref+Trafo troncal': (True, m3, 'Ref+Trafo troncal (X)'), 'Hoy': (False, None, 'mod_actual')}
s3 = pd.read_pickle(OUT + 'ref_trafo_directo.pkl'); S['Ref+Trafo troncal (X)'] = s3
disc = V[V.clasificacion_validacion.str.startswith('DISCREPA') & V.valor_sugerido.notna()].set_index('nombre_ENT')
filas, det = [], []
for crit, (rf, an, col) in CRIT.items():
    o = escenario(oper, rf, an); d, w0 = pesos(o)
    base = asignar(w0); print(crit, 'reproduce:', int((base == S[col].reindex(base.index)).sum()), '/', len(base))
    t0 = time.time()
    for i, r in d[d['Nombre'].isin(disc.index)].iterrows():
        if an is not None and an.loc[i]: continue          # trafo anulado: su X no importa
        info = disc.loc[r['Nombre']]
        if isinstance(info, pd.DataFrame): info = info.iloc[0]
        xn = info.valor_sugerido * (ref.loc[i] if rf else 1)
        dd = d.copy(); dd.loc[i, 'X'] = xn
        k = (int(r.u), int(r.v)); w = w0.copy(); w.loc[k] = 1 / (1 / dd.loc[(dd.u == k[0]) & (dd.v == k[1]), 'X']).sum()
        s = asignar(w); ch = s[s != base.reindex(s.index)]
        dp = (ch.map(precio) - base.reindex(ch.index).map(precio)); mw = S.mw.reindex(ch.index).fillna(0)
        filas.append({'Criterio': crit, 'Tramo ENT': r['Nombre'], 'Tipo': 'Trafo' if T.loc[i] else 'Línea', 'V [kV]': r['V'],
                      'X ENT (Ω)': oper.loc[i, 'X'], 'X sugerida (Ω)': info.valor_sugerido, 'Fuente sugerida': info.fuente_valor_sugerido,
                      'Clasificación': info.clasificacion_validacion, 'Acción propuesta (validación previa)': info.accion_propuesta,
                      'Posible diferencia de representación (×2, ×1/3…)': 'Sí' if info.posible_representacion else 'No',
                      'Barras que cambian': len(ch), 'Con iny/ret': int((mw > 0).sum()),
                      'MW iny+ret': round(mw.sum(), 2), 'MM$/mes': round((dp.abs() * mw / 1000).sum(), 1)})
        for b in ch.index: det.append({'Criterio': crit, 'Tramo ENT': r['Nombre'], 'Barra': b, 'Troncal con ENT': base[b], 'Troncal corregida': ch[b],
                                       'MW iny+ret': round(S.mw.get(b, 0), 2), 'Δ precio ($/kW/mes)': round(dp[b], 1)})
    print(crit, 'tramos probados en', round(time.time() - t0), 's')
F = pd.DataFrame(filas); Dt = pd.DataFrame(det)
F.to_pickle(OUT + 'decisivos.pkl'); Dt.to_pickle(OUT + 'decisivos_det.pkl'); V.to_pickle(OUT + 'validacion.pkl')
for crit in CRIT:
    f = F[F.Criterio == crit]; dcs = f[f['Barras que cambian'] > 0]
    print(f'\n{crit}: probados {len(f)}  decisivos {len(dcs)}  con plata {int((dcs["MM$/mes"]>0).sum())}  barras afectadas (únicas) {Dt[Dt.Criterio==crit].Barra.nunique()}')
    print(dcs.sort_values('MM$/mes', ascending=False).head(15)[['Tramo ENT', 'X ENT (Ω)', 'X sugerida (Ω)', 'Clasificación', 'Posible diferencia de representación (×2, ×1/3…)', 'Barras que cambian', 'MM$/mes']].to_string(index=False))
