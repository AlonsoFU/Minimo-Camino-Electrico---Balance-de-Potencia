"""Grupos mínimos dentro de cada zona: subconjuntos de sus imprescindibles que, corregidos solos, no dejan ninguna
barra en una troncal distinta de la base y del resultado final de la zona (4 variantes). Y tipo de cada tramo solo."""
import itertools, multiprocessing as mp
exec(open('listado_verif.py').read().split("out = {'zonas'")[0])
N = set(pd.read_pickle(OUT + 'nucleo_N.pkl'))
REV = pd.read_excel('/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/listado_tramos.xlsx', sheet_name='Revisión')
ZT = {z: list(g.Tramo) for z, g in REV[REV.Zona != 'Independiente'].groupby('Zona', sort=False)}
BASE = {v: est_f(True, *VAR[v], []) for v in VAR}
FZ = {(z, v): est_f(True, *VAR[v], l) for z, l in ZT.items() for v in VAR}
FL = {v: est_f(True, *VAR[v], list(REV.Tramo)) for v in VAR}
def mal(l, ref):
    """por variante: (barras en troncal equivocada, MM$ equivocado, barras que ya llegan al final, barras finales)"""
    o = {}
    for v in VAR:
        a = est_f(True, *VAR[v], list(l)); M = BASE[v]; F = ref[v]
        ch = (a != M.reindex(a.index)); w = ch & (a != F.reindex(a.index)); fin = (F != M.reindex(F.index))
        tr = a[w]; mm = float(((tr.map(precio) - F.reindex(tr.index).map(precio)).abs() * mwS.reindex(tr.index).fillna(0) / 1000).sum())
        o[v] = (int(w.sum()), round(mm, 1), int((ch & ~w).sum()), int(fin.sum()))
    return o
def job(args):
    z, c = args; return z, c, mal(c, {v: FZ[(z, v)] for v in VAR})
def tramo_job(t):
    z = REV.set_index('Tramo').loc[t, 'Zona']; ref = {v: FZ[(z, v)] for v in VAR} if z != 'Independiente' else FL
    return t, mal([t], ref)
if __name__ == '__main__':
    tareas = []
    for z, l in ZT.items():
        I = [t for t in l if t in N]
        for k in range(1, len(I) + 1):
            for c in itertools.combinations(I, k): tareas.append((z, c))
    print('combinaciones:', len(tareas), flush=True)
    with mp.Pool(4) as p:
        RES = p.map(job, tareas, chunksize=8)
        TR = dict(p.map(tramo_job, list(REV.Tramo), chunksize=4))
    pd.to_pickle({'RES': RES, 'TR': TR}, OUT + 'grupos_min.pkl')
    seguro = {(z, c) for z, c, o in RES if all(x[0] == 0 for x in o.values())}
    for z, l in ZT.items():
        I = [t for t in l if t in N]; rest = list(I); bloques = []
        while rest:
            # el subconjunto seguro más chico (dentro de lo que queda) cuyo complemento también es seguro
            cand = [c for k in range(1, len(rest) + 1) for c in itertools.combinations(rest, k)
                    if (z, tuple(sorted(c, key=I.index))) in seguro and (len(c) == len(rest) or (z, tuple(sorted(set(rest) - set(c), key=I.index))) in seguro)]
            b = cand[0]; bloques.append(b); rest = [t for t in rest if t not in b]
        # verificar que toda unión de bloques es segura
        ok = all((z, tuple(sorted(sum(map(list, u), []), key=I.index))) in seguro for k in range(1, len(bloques) + 1) for u in itertools.combinations(bloques, k))
        print(f'{z}: {len(I)} imprescindibles -> {len(bloques)} grupos; uniones seguras: {ok}')
        for b in bloques: print('   ', ' + '.join(b))
