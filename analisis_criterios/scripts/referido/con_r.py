"""«Referido» y «Referido + Subestación» con R: |Z| en vez de X. Compara contra hoy y PN2604."""
src = open('banco.py').read().split("grafos = {k")[0]
exec(src)
b_=open('banco.py').read(); exec('cdf ='+b_.split('cdf =',1)[1].split('rows = []')[0])
R0 = pd.read_pickle(OUT + 'banco.pkl'); R0 = R0[R0.actual.notna()].set_index('barra')
oper['R'] = pd.to_numeric(oper['R'], errors='coerce').fillna(0)

def grafo_z(op, modo):
    """modo 'X': solo X (como hoy). 'Zc': paralelo complejo 1/Zeq=Σ1/Zi, peso |Zeq|.
    'Zm': paralelo sobre módulos 1/|Z|eq=Σ1/|Zi| (aproximación)."""
    d = op.copy(); a = d['Barra A'].astype(int); b = d['Barra B'].astype(int)
    d['u'] = np.minimum(a, b); d['v'] = np.maximum(a, b)
    d['Z'] = d['R'] + 1j * d['X']
    G = nx.Graph()
    for (u, v), g in d.groupby(['u', 'v']):
        if modo == 'X': z = 1 / (1 / g['X']).sum(); r = 0; x = z
        elif modo == 'Zm': z = 1 / (1 / np.abs(g['Z'])).sum(); r = x = np.nan
        else: zc = 1 / (1 / g['Z']).sum(); z = abs(zc); r, x = zc.real, zc.imag
        if z > 0: G.add_edge(nm[u], nm[v], w=float(z), r=float(r), x=float(x))
    return G

def esc(rx_ref, anular):
    o = oper.copy()
    if rx_ref: o['X'] = o['X'] * ref; o['R'] = o['R'] * ref
    if anular is not None: o.loc[anular, ['X', 'R']] = EPS
    return o

def asigna(G, exacto=False):
    out, mrg = {}, {}
    for b, r in R0.iterrows():
        if r.nodo not in G: continue
        cand = [t for t in PN if sub_t.get(t) == r['sub']]
        if exacto:   # |ΣR + jΣX| del camino más corto (suma de |Z|) a cada troncal
            dist, paths = nx.single_source_dijkstra(G, r.nodo, weight='w')
            dd = {}
            for t in cand:
                if t not in paths: continue
                p = paths[t]; rr = sum(G[p[i]][p[i+1]]['r'] for i in range(len(p)-1))
                xx = sum(G[p[i]][p[i+1]]['x'] for i in range(len(p)-1)); dd[t] = abs(rr + 1j*xx)
        else:
            dist = nx.single_source_dijkstra_path_length(G, r.nodo, weight='w'); dd = {t: dist[t] for t in cand if t in dist}
        t, d1, m, _ = elegir(dd)
        if t: out[b] = t; mrg[b] = m
    return pd.Series(out), pd.Series(mrg)

ESC = {
  'Hoy (X)':                  (False, None, 'X'),
  'Referido (X)':             (True,  None, 'X'),
  'Referido (|Z|)':           (True,  None, 'Zc'),
  'Ref+Sub (X)':              (True,  m1,   'X'),
  'Ref+Sub (|Z|)':            (True,  m1,   'Zc'),
  'Hoy (|Z|) sin referir':    (False, None, 'Zc'),
}
res = {}; G = {}
for k, (rf, an, modo) in ESC.items():
    G[k] = grafo_z(esc(rf, an), modo); res[k], res[k + '_mrg'] = asigna(G[k])
# sensibilidades de supuestos
res['Referido (|Z| exacto camino)'], _ = asigna(G['Referido (|Z|)'], exacto=True)
res['Ref+Sub (|Z| exacto camino)'], _ = asigna(G['Ref+Sub (|Z|)'], exacto=True)
for k, (rf, an) in {'Referido (|Z| paralelo módulos)': (True, None), 'Ref+Sub (|Z| paralelo módulos)': (True, m1)}.items():
    res[k], _ = asigna(grafo_z(esc(rf, an), 'Zm'))
o = oper.copy(); o['X'] = (o['R'] + o['X']) * ref; res['Referido (R+X)'], _ = asigna(grafo_z(o, 'X'))
o.loc[m1, 'X'] = EPS; res['Ref+Sub (R+X)'], _ = asigna(grafo_z(o, 'X'))

S = pd.DataFrame({k: v for k, v in res.items() if not k.endswith('_mrg')})
S['PN2604'] = R0['PN2604']; S['mod_actual'] = R0['mod_actual']
print('validación Hoy(X) propio == módulo:', (S['Hoy (X)'] == S['mod_actual']).sum(), '/', S['mod_actual'].notna().sum())
print('validación Referido(X) == banco:', (S['Referido (X)'] == R0['P_ref220']).sum(), ' Ref+Sub(X) == banco:', (S['Ref+Sub (X)'] == R0['P_C1']).sum())
src_ = lambda b: b if b in coord else R0.loc[b, 'nodo']
filas = {}
for k in [c for c in S.columns if c not in ('PN2604', 'mod_actual')]:
    ch = S[k] != S['mod_actual']
    kmh = pd.Series({b: km(S.loc[b, 'mod_actual'], S.loc[b, k]) for b in S.index[ch]})
    d = pd.Series({b: km(src_(b), S.loc[b, k]) for b in S.index})
    filas[k] = {'= PN2604': int((S[k] == S.PN2604).sum()), 'cambian vs hoy': int(ch.sum()),
                'de ellas >100 km': int((kmh > 100).sum()), 'barra→troncal >100 km': int((d > 100).sum())}
print(pd.DataFrame(filas).T.to_string())
for a, b in [('Referido (X)', 'Referido (|Z|)'), ('Ref+Sub (X)', 'Ref+Sub (|Z|)')]:
    dd = S[S[a] != S[b]]; mg = res[a + '_mrg'].reindex(dd.index)
    print(f'\n{a} vs {b}: {len(dd)} barras distintas; margen con X <5%: {int((mg<0.05).sum())}  <10%: {int((mg<0.10).sum())}')
    print(dd.groupby([a, b]).size().sort_values(ascending=False).to_string())
    print('de esas, cuál coincide con PN2604 →', a, int((dd[a] == dd.PN2604).sum()), '|', b, int((dd[b] == dd.PN2604).sum()))
S.to_pickle(OUT + 'con_r.pkl')
