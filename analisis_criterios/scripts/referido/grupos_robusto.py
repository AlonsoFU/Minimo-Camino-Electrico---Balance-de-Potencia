"""Prueba por grupos repetida con agrupaciones distintas, para ver si se escapan combinaciones."""
exec(open('grupos.py').read().split("t0 = time.time(); TAM = 40")[0])
import random
# troncal más cercana (eléctrica) a cada nodo, para agrupar por troncal
Gb = nx.Graph()
for (u, v), x in pesos(o0)[1].items():
    if x > 0: Gb.add_edge(nm[u], nm[v], w=float(x))
DT = {t: nx.single_source_dijkstra_path_length(Gb, t, weight='w') for t in TRONC if t in Gb}
def tron(b):
    n = nm[int(oper.loc[bloques[b][0], 'Barra A'])]
    c_ = [(DT[t].get(n, 1e9), t) for t in DT]; return min(c_)[1]
def buscar(orden, tam):
    zonas = [orden[i:i + tam] for i in range(0, len(orden), tam)] + [None]; hall = []
    for z in zonas:
        resto = list(z) if z is not None else [x for x in orden if not any(x in h for h in hall)]
        while len(cambia(resto)):
            m = ddmin(resto); hall.append(frozenset(m)); resto = [x for x in resto if x not in m]
    return hall
por_tron = sorted(nod, key=lambda b: (tron(b), lat(b)))
r1 = random.Random(1); al1 = nod[:]; r1.shuffle(al1)
r2 = random.Random(2); al2 = nod[:]; r2.shuffle(al2)
AG = {'Latitud, 40': (nod, 40), 'Troncal más cercana, 40': (por_tron, 40), 'Al azar (1), 40': (al1, 40), 'Al azar (2), 20': (al2, 20)}
res = {}
for k, (o, t) in AG.items():
    NT[0] = 0; t0 = time.time(); res[k] = buscar(o, t)
    print(f'{k}: {len(res[k])} combinaciones, {NT[0]} recálculos, {time.time()-t0:.0f} s', flush=True)
todas = set().union(*res.values())
filas = []
for cmb in sorted(todas, key=lambda s: -len(s)):
    ch = cambia(list(cmb)); _, mm = plata(base, estado(list(cmb)))
    filas.append({'Combinación': ' + '.join(sorted(cmb)), 'Tramos': len(cmb), 'Barras': len(ch), 'MM$/mes': round(mm, 1), **{k: 'Sí' if cmb in v else '' for k, v in res.items()}})
F = pd.DataFrame(filas).sort_values('MM$/mes', ascending=False); F.to_pickle(OUT + 'grupos_robusto.pkl')
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 90); print(F.to_string(index=False))
