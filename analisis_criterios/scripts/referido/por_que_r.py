exec(open('con_r.py').read().split("ESC = {")[0])
S = pd.read_pickle(OUT + 'con_r.pkl')
Tset = set(zip(oper.loc[T,'Barra A'].astype(int).map(nm), oper.loc[T,'Barra B'].astype(int).map(nm)))
Tset |= {(b, a) for a, b in Tset}
GX = {'Ref': grafo_z(esc(True, None), 'Zc'), 'RefSub': grafo_z(esc(True, m1), 'Zc')}
def info(G, nodo, cand):
    """por troncal: ΣX, ΣR, Σ|Z|, % de X en trafos del camino mínimo en X"""
    H = nx.Graph(); [H.add_edge(u, v, w=d['x']) for u, v, d in G.edges(data=True)]
    dist, paths = nx.single_source_dijkstra(H, nodo, weight='w'); out = {}
    for t in cand:
        if t not in paths: continue
        p = paths[t]; e = [(p[i], p[i+1]) for i in range(len(p)-1)]
        x = sum(G[a][b]['x'] for a, b in e); r = sum(G[a][b]['r'] for a, b in e)
        xt = sum(G[a][b]['x'] for a, b in e if (a, b) in Tset)
        out[t] = dict(X=x, R=r, Z=sum(abs(G[a][b]['r'] + 1j*G[a][b]['x']) for a, b in e), pctT=xt/x if x > 0 else np.nan, n=len(e))
    return out
for k, col in [('Ref', 'Referido (X)'), ('RefSub', 'Ref+Sub (X)')]:
    G = GX[k]; rows = []
    for b, r in R0.iterrows():
        if r.nodo not in G: continue
        cand = [t for t in PN if sub_t.get(t) == r['sub']]
        inf = info(G, r.nodo, cand)
        c = sorted(inf, key=lambda t: inf[t]['X'])
        if len(c) < 2 or inf[c[0]]['X'] <= 0: continue
        a, s = inf[c[0]], inf[c[1]]
        rows.append(dict(barra=b, mrg=(s['X']-a['X'])/a['X'], rx1=a['R']/a['X'], rx2=s['R']/s['X'], pT1=a['pctT'], pT2=s['pctT'],
                         x1=a['X'], cambia=S.loc[b, col] != S.loc[b, col.replace('X', '|Z|')]))
    D = pd.DataFrame(rows)
    print(f"\n=== {k} ===  barras {len(D)}")
    print(' margen X <2%:', int((D.mrg<.02).sum()), ' <5%:', int((D.mrg<.05).sum()), ' <10%:', int((D.mrg<.10).sum()))
    print(' % de la X del camino ganador que está en trafos (mediana):', round(D.pT1.median()*100), '%')
    print(' R/X del camino ganador (mediana):', round(D.rx1.median(), 2))
    print(' |R/X ganador − R/X segunda| mediana:', round((D.rx1-D.rx2).abs().median(), 2))
    print(' X del camino ganador (mediana, Ω a 220):', round(D.x1.median(), 1))
    print(' las que cambian con |Z|: n', int(D.cambia.sum()), ' margen mediano', round(D[D.cambia].mrg.median()*100, 1), '%',
          ' R/X ganador', round(D[D.cambia].rx1.median(), 2), ' R/X segunda', round(D[D.cambia].rx2.median(), 2))
    D.to_pickle(OUT + f'por_que_{k}.pkl')
