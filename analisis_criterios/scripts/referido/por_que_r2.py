exec(open('por_que_r.py').read().split("for k, col in")[0])
for k in ['Ref','RefSub']:
    D = pd.read_pickle(OUT+f'por_que_{k}.pkl'); c = D[D.mrg<.05]; dif = (c.rx1-c.rx2).abs()
    print(k, 'margen<5%:', len(c), ' de ellas con R/X distinto entre las 2 rutas (>0,1):', int((dif>.1).sum()),
          ' y que R alcanza a voltear (R/X ganador > segunda):', int((c.rx1>c.rx2+.02).sum()))
def detalle(k, b):
    G = GX[k]; nodo = R0.loc[b,'nodo']; cand=[t for t in PN if sub_t.get(t)==R0.loc[b,'sub']]
    H = nx.Graph(); [H.add_edge(u, v, w=d['x']) for u, v, d in G.edges(data=True)]
    dist, paths = nx.single_source_dijkstra(H, nodo, weight='w')
    for t in sorted(cand, key=lambda t: dist.get(t, 1e9))[:2]:
        p = paths[t]; print(f'  → {t}: X={dist[t]:.1f}', end='')
        R_ = sum(G[p[i]][p[i+1]]['r'] for i in range(len(p)-1)); Z_ = sum(abs(G[p[i]][p[i+1]]['r']+1j*G[p[i]][p[i+1]]['x']) for i in range(len(p)-1))
        print(f'  R={R_:.1f}  Σ|Z|={Z_:.1f}')
        for i in range(len(p)-1):
            d = G[p[i]][p[i+1]]; tp = 'T' if (p[i], p[i+1]) in Tset else 'L'
            print(f'      {tp} {p[i]:18s}→{p[i+1]:18s} X={d["x"]:6.2f} R={d["r"]:6.2f}')
for b in ['LA_REINA______013']:
    for k in ['Ref','RefSub']: print('\n', k, b); detalle(k, b)
