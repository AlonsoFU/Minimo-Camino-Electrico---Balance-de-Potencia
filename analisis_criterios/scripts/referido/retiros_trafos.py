"""Sensibilidad de las barras con retiro a la X de los trafos de sus caminos («Referido + trafo troncal», X).
Para cada barra: margen = d(2ª troncal) − d(ganadora). Un trafo del camino ganador la da vuelta si su X sube
al menos margen/X (cota inferior); uno del camino a la 2ª, si su X baja al menos margen/X."""
exec(open('con_r.py').read().split("ESC = {")[0])
exec(open('con_r_plata.py').read().split("def monto")[0].replace("S=pd.read_pickle('con_r.pkl')", "S=pd.read_pickle(OUT+'con_r.pkl')"))
V = pd.read_pickle(OUT + 'validacion.pkl').set_index('nombre_ENT')
o = esc(True, m3)
d = o.assign(u=np.minimum(o['Barra A'], o['Barra B']).astype(int), v=np.maximum(o['Barra A'], o['Barra B']).astype(int))
w = 1 / (1 / d['X']).groupby([d.u, d.v]).sum()
es_tr = T.groupby([d.u, d.v]).any()
nombres = d.groupby(['u', 'v'])['Nombre'].apply(list)
G = nx.Graph()
for (u, v), x in w.items():
    if x > 0: G.add_edge(nm[u], nm[v], w=float(x), k=(u, v))
TR = sorted(PN); DP = {t: nx.single_source_dijkstra(G, t, weight='w') for t in TR if t in G}
ret_b = ret.reindex(R0.index).fillna(0); ret_b = ret_b[ret_b > 0]
filas = []
for b in ret_b.index:
    n = R0.loc[b, 'nodo']; cand = [t for t in TR if sub_t.get(t) == R0.loc[b, 'sub'] and t in DP and n in DP[t][0]]
    c = sorted(cand, key=lambda t: (round(DP[t][0][n], 9), t))
    if len(c) < 2: continue
    t1, t2 = c[0], c[1]; d1, d2 = DP[t1][0][n], DP[t2][0][n]; mg = d2 - d1
    e1 = {G[a][z]['k'] for a, z in zip(DP[t1][1][n][:-1], DP[t1][1][n][1:])}
    e2 = {G[a][z]['k'] for a, z in zip(DP[t2][1][n][:-1], DP[t2][1][n][1:])}
    dp = abs(precio.get(t2, np.nan) - precio.get(t1, np.nan))
    for k, lado in [(e, 'sube') for e in e1 - e2] + [(e, 'baja') for e in e2 - e1]:
        if not es_tr.get(k, False) or w[k] < 1e-3: continue
        req = mg / w[k]
        if lado == 'baja' and req >= 1: continue
        filas.append({'barra': b, 'troncal': t1, 'segunda': t2, 'k': k, 'lado': lado, 'cambio_req': req,
                      'ret_MW': ret_b[b], 'MMs': dp * ret_b[b] / 1000})
D = pd.DataFrame(filas)
def resumen(g):
    out = {}
    for lim, lab in [(.2, '≤20 %'), (.5, '≤50 %'), (2.0, '≤×3')]:
        s = g[g.cambio_req <= lim]; out[f'Barras {lab}'] = s.barra.nunique(); out[f'MW retiro {lab}'] = round(s.drop_duplicates('barra').ret_MW.sum(), 1)
        out[f'MM$/mes {lab}'] = round(s.drop_duplicates('barra').MMs.sum(), 1)
    out['Cambio mínimo que da vuelta una barra'] = f"{g.cambio_req.min()*100:.0f} % ({g.loc[g.cambio_req.idxmin(), 'lado']})"
    return pd.Series(out)
Rk = D.groupby('k').apply(resumen)
Rk['Trafo (ENT)'] = [' | '.join(nombres[k]) for k in Rk.index]
Rk['X ENT ref. 220 (Ω)'] = [round(w[k], 2) for k in Rk.index]
def clase(k):
    cl = [V.loc[n, 'clasificacion_validacion'] for n in nombres[k] if n in V.index]
    cl = [c if isinstance(c, str) else c.iloc[0] for c in cl]
    return cl[0] if cl else 'sin homologar'
def ratio(k):
    r = [V.loc[n, 'X_ENT'] / V.loc[n, 'valor_sugerido'] for n in nombres[k] if n in V.index]
    r = [x if np.isscalar(x) else x.iloc[0] for x in r]; r = [x for x in r if pd.notna(x)]
    return round(r[0], 2) if r else np.nan
Rk['Validación'] = [clase(k) for k in Rk.index]; Rk['X ENT ÷ X sugerida'] = [ratio(k) for k in Rk.index]
Rk = Rk.sort_values(['MM$/mes ≤50 %', 'MM$/mes ≤×3'], ascending=False).reset_index(drop=True)
cols = ['Trafo (ENT)', 'X ENT ref. 220 (Ω)', 'Validación', 'X ENT ÷ X sugerida', 'Cambio mínimo que da vuelta una barra'] + [c for c in Rk.columns if c.startswith(('Barras', 'MW', 'MM$'))]
Rk = Rk[cols]; Rk.to_pickle(OUT + 'retiros_trafos.pkl'); D.to_pickle(OUT + 'retiros_trafos_det.pkl')
print('barras con retiro:', len(ret_b), ' MW:', round(ret_b.sum()), '  trafos en sus caminos:', len(Rk))
for lim in ['≤20 %', '≤50 %', '≤×3']:
    print(f'  trafos que dan vuelta ≥1 barra con cambio {lim}:', int((Rk[f"Barras {lim}"] > 0).sum()))
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 45)
print(Rk.head(20)[['Trafo (ENT)', 'Validación', 'X ENT ÷ X sugerida', 'Cambio mínimo que da vuelta una barra', 'Barras ≤50 %', 'MW retiro ≤50 %', 'MM$/mes ≤50 %', 'Barras ≤×3', 'MM$/mes ≤×3']].to_string(index=False))
