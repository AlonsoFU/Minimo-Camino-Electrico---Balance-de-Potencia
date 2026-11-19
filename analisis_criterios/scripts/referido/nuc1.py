"""Núcleo del listado: el menor conjunto que reproduce el resultado final de la lista en las 4 variantes,
y qué unidad mínima necesita cada tramo para que su corrección no deje barras en una troncal transitoria."""
exec(open('listado_verif.py').read().split("out = {'zonas'")[0])
E = {v: (lambda l, an=an, modo=modo: est_f(True, an, modo, l)) for v, (an, modo) in VAR.items()}
M = {v: E[v]([]) for v in VAR}; FL = {v: E[v](LISTA) for v in VAR}; FT = {v: E[v](todos) for v in VAR}
for v in VAR: d = dif(FL[v], FT[v]); print(v, 'lista vs 668: barras', d['barras'], 'MM$', d['mm'])
mm0 = dict(zip(Lst.Tramo, pd.to_numeric(Lst['MM$/mes (solo, promedio)'], errors='coerce').fillna(0)))
crit = dict(zip(Lst.Tramo, Lst['Crítico / vecino'].str.startswith('Crítico')))
igual = lambda l: all((E[v](l).reindex(FL[v].index).fillna('') == FL[v].fillna('')).all() for v in VAR)
# 1) núcleo: quitar de a uno (vecinos primero, después críticos de menor a mayor plata) si el resultado final no cambia
ordenq = sorted(LISTA, key=lambda t: (crit[t], mm0[t]))
N = list(LISTA)
for t in ordenq:
    c = [x for x in N if x != t]
    if igual(c): N = c
print('núcleo:', len(N), 'de', len(LISTA), ' críticos en núcleo:', sum(crit[t] for t in N), ' vecinos en núcleo:', sum(not crit[t] for t in N))
print('fuera del núcleo críticos:', [t for t in LISTA if t not in N and crit[t]])
pd.to_pickle(N, OUT + 'nucleo_N.pkl')
