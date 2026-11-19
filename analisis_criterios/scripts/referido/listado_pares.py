"""Interacción entre unidades del listado (grupo previo, Mulchén o tramo independiente), por pares y en las 4
variantes: dos unidades interactúan si corregirlas juntas no da la unión de corregirlas por separado."""
import itertools, multiprocessing as mp
exec(open('listado_verif.py').read().split("out = {'zonas'")[0])
UN = list(UNI)
def efecto(l, v):
    an, modo = VAR[v]; a = est_f(True, an, modo, l); M = BASE[v]
    return {k: x for k, x in a.items() if x != M.get(k)}
BASE = {v: dict(est_f(True, *VAR[v], [])) for v in VAR}
def solo(u): return u, {v: efecto(UNI[u], v) for v in VAR}
def par(p):
    a, b = p; res = []
    for v in VAR:
        j = efecto(UNI[a] + UNI[b], v); s = dict(SO[a][v]); s.update(SO[b][v])
        ks = [k for k in set(j) | set(s) if j.get(k) != s.get(k)]
        if ks:
            mm = sum(abs(precio.get(j.get(k, BASE[v][k]), 0) - precio.get(s.get(k, BASE[v][k]), 0)) * float(mwS.get(k, 0) or 0) / 1000 for k in ks)
            res.append((v, len(ks), round(mm, 1)))
    return a, b, res
if __name__ == '__main__':
    with mp.Pool(4) as pool:
        SO = dict(pool.map(solo, UN))
    # solo pares donde ambas unidades mueven algo en alguna variante (si una no mueve nada sola, igual puede interactuar: se incluye todo)
    pares = list(itertools.combinations(UN, 2)); print('unidades', len(UN), 'pares', len(pares), flush=True)
    with mp.Pool(4, initializer=lambda d: globals().update(SO=d), initargs=(SO,)) as pool:
        R = pool.map(par, pares, chunksize=20)
    I = [(a, b, r) for a, b, r in R if r]
    pd.to_pickle({'SO': SO, 'I': I, 'UNI': UNI}, OUT + 'listado_pares.pkl')
    for a, b, r in sorted(I, key=lambda x: -max(m for _, _, m in x[2])): print(a[:38], '|', b[:38], '|', r)
