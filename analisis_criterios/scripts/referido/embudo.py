"""Embudo analítico: por qué solo ~44 de 668 tramos afectan. Se contrasta con la prueba directa."""
exec(open('cadena.py').read().split("base = estado([])")[0])
c = pd.read_pickle(OUT + 'cadena.pkl'); dec = set(c['dec']); base = c['base']
d0, w0 = pesos(o0)
G = nx.Graph()
for (u, v), x in w0.items():
    if x > 0: G.add_edge(nm[u], nm[v], w=float(x), k=(u, v))
DP = {t: nx.single_source_dijkstra(G, t, weight='w') for t in TRONC if t in G}
# peso corregido por bloque (pares de barras del bloque)
def w_corr(b):
    o = o0.copy()
    for i in bloques[b]: o.loc[i, 'X'] = xsug[i]
    dd = d0.copy(); dd.loc[bloques[b], 'X'] = o.loc[bloques[b], 'X']
    ks = {(int(dd.loc[i, 'u']), int(dd.loc[i, 'v'])) for i in bloques[b]}
    return {k: 1 / (1 / dd.loc[(dd.u == k[0]) & (dd.v == k[1]), 'X']).sum() for k in ks}
WC = {b: w_corr(b) for b in bloques}
en_parte, pasa = set(), set()
for bar in R0.index:
    n = R0.loc[bar, 'nodo']; cand = [t for t in cand_all(bar)] if False else [t for t in TRONC if sub_t.get(t) == R0.loc[bar, 'sub'] and t in DP and n in DP[t][0]]
    cs = sorted(cand, key=lambda t: (round(DP[t][0][n], 9), t))
    if len(cs) < 2: continue
    t1, t2 = cs[0], cs[1]; mg = DP[t2][0][n] - DP[t1][0][n]
    e1 = {G[a][z]['k'] for a, z in zip(DP[t1][1][n][:-1], DP[t1][1][n][1:])}
    e2 = {G[a][z]['k'] for a, z in zip(DP[t2][1][n][:-1], DP[t2][1][n][1:])}
    for b, ks in WC.items():
        for k, wn in ks.items():
            if k in e1 ^ e2:
                en_parte.add(b); dl = wn - w0[k]
                if (k in e1 - e2 and dl > mg) or (k in e2 - e1 and -dl > mg): pasa.add(b)
print('tramos que difieren:', len(bloques))
print('  están en la parte que decide de algún camino (ganador ≠ 2ª):', len(en_parte))
print('  y su corrección supera el margen de alguna barra:', len(pasa))
print('prueba directa (recalcular todo): decisivos', len(dec), '| coinciden', len(pasa & dec), '| solo embudo', len(pasa - dec), '| solo directa', len(dec - pasa))
pd.to_pickle({'en_parte': en_parte, 'pasa': pasa}, OUT + 'embudo.pkl')
