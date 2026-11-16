"""Prueba exhaustiva por zona: todas las combinaciones (hasta 4, o todas si son ≤10 tramos) de los tramos que difieren
en el entorno (2 saltos) de cada combinación encontrada. Detecta interacciones y compara zona completa vs parcial."""
exec(open('zonas_exh_prep.py').read().split("for z, k in semillas.items():")[0])
from itertools import combinations
Gt = nx.Graph()
for (u, v), x in pesos(o0)[1].items(): Gt.add_edge(nm[u], nm[v])
semillas['Mulchén'] = 'LOS_NOTROS____220->MULCHEN'
filas, resumen = [], []
for z, k in semillas.items():
    fila = F[F['Combinación'].str.contains(k, regex=False)]
    tr = set(x for c_ in fila['Combinación'] for x in c_.split(' + '))
    n1 = set().union(*[ends[b] for b in tr]); n2 = n1 | {w for n in n1 if n in Gt for w in Gt[n]}
    vec = sorted(b for b in bloques if ends[b] & n2)
    sing = {b: set(cambia([b]).index) for b in vec}
    kmax = len(vec) if len(vec) <= 10 else 4
    NT[0] = 0; t0 = time.time(); inter = []
    for r in range(2, kmax + 1):
        for cmb in combinations(vec, r):
            ch = cambia(list(cmb)); u = set().union(*[sing[b] for b in cmb])
            if set(ch.index) != u:
                _, mm = plata(base, estado(list(cmb))); inter.append((r, cmb, len(ch), mm, len(set(ch.index) - u), len(u - set(ch.index))))
    full = cambia(vec); _, mmf = plata(base, estado(vec))
    mx = max(inter, key=lambda t: t[3]) if inter else None
    resumen.append({'Zona': z, 'Tramos en la zona': len(vec), 'Combinaciones probadas': NT[0], 'Con interacción': len(inter),
                    'Zona completa: barras': len(full), 'Zona completa: MM$/mes': round(mmf, 1),
                    'Peor parcial: MM$/mes': round(mx[3], 1) if mx else 0, 'Peor parcial: tramos': ' + '.join(mx[1]) if mx else ''})
    print(resumen[-1], f'{time.time()-t0:.0f} s', flush=True)
    for r, cmb, n, mm, nuevas, canc in inter: filas.append({'Zona': z, 'Combinación': ' + '.join(cmb), 'Tramos': r, 'Barras': n, 'MM$/mes': round(mm, 1), 'Nuevas por interacción': nuevas, 'Canceladas': canc})
R = pd.DataFrame(resumen); I = pd.DataFrame(filas); pd.to_pickle({'R': R, 'I': I}, OUT + 'zonas_exh.pkl')
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 80); print(R.to_string(index=False))
