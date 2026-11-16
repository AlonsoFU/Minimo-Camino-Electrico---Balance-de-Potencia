exec(open('cadena.py').read().split("base = estado([])")[0])
B = 'L.CHANGOS_____500->KIMAL_________500'
def grafo_w(apl):
    o = o0.copy()
    for b in apl:
        for i in bloques[b]: o.loc[i, 'X'] = xsug[i]
    w = pesos(o)[1]; G = nx.Graph()
    for (u, v), x in w.items():
        if x > 0: G.add_edge(nm[u], nm[v], w=float(x))
    return G
for lab, apl in [('ENT', []), ('corregido', [B])]:
    G = grafo_w(apl)
    for b in ['KELAR_________220', 'JADRESIC______220']:
        d = nx.single_source_dijkstra_path_length(G, b, weight='w')
        print(lab, b, {t[:10]: round(d.get(t, np.nan), 2) for t in ['OHIGGINS______220', 'CRUCERO_______220', 'CARDONES______220', 'ENCUENTRO_____220']})
    print(lab, 'arista L.Changos-Kimal 500 (ref 220):', round(G['L.CHANGOS_____500']['KIMAL_________500']['w'], 2))
