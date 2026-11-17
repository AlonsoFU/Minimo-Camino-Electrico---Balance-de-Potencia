"""Cierra el hueco: combinaciones de tramos decisivos con sus vecinos, en las 16 zonas.
Zonas ≤20 tramos: todas las combinaciones de 2–4 tramos que incluyan al menos un decisivo.
Zonas >20: todos los pares decisivo+otro, más una búsqueda por partición (ddmin) de vecinos que alteran a cada decisivo."""
exec(open('zonas_exh_prep.py').read().split("for z, k in semillas.items():")[0])
from itertools import combinations
import sys
Z = pd.read_pickle(OUT + 'zonas_def.pkl'); c = pd.read_pickle(OUT + 'cadena.pkl'); DEC = set(c['dec'])
SING = {}
def sing(b):
    if b not in SING: SING[b] = frozenset(cambia([b]).index)
    return SING[b]
def dev(S):
    ch = cambia(list(S)); u = set().union(*[sing(b) for b in S]); return set(ch.index) != u, ch
def ddmin_p(g, pred):
    n = 2
    while len(g) >= 2:
        k = max(1, len(g) // n); partes = [g[i:i + k] for i in range(0, len(g), k)]; red = False
        for p in partes:
            if pred(p): g, n, red = p, 2, True; break
        if not red:
            for p in partes:
                comp = [x for x in g if x not in p]
                if comp and pred(comp): g, n, red = comp, max(n - 1, 2), True; break
        if not red:
            if n >= len(g): break
            n = min(len(g), 2 * n)
    return g
plan = [(len(z), len(z & DEC)) for z in Z]; print('zonas (tramos, decisivos):', plan, flush=True)
if len(sys.argv) > 1 and sys.argv[1] == 'plan': raise SystemExit
resumen, inter = [], []
for zi, z in enumerate(Z, 1):
    zl = sorted(z); d_ = sorted(z & DEC); NT[0] = 0; t0 = time.time(); hall = {}
    for b in zl: sing(b)
    if len(zl) <= 20:
        for r in range(2, min(4, len(zl)) + 1):
            for cmb in combinations(zl, r):
                if not (set(cmb) & DEC): continue
                es, ch = dev(cmb)
                if es: hall[frozenset(cmb)] = ch
    else:
        for d in d_:
            for o in zl:
                if o == d: continue
                es, ch = dev((d, o))
                if es: hall[frozenset((d, o))] = ch
            otros = [o for o in zl if o != d]
            restante = otros[:]
            while restante and dev([d] + restante)[0]:
                m = ddmin_p(restante, lambda g: dev([d] + list(g))[0]); SS = frozenset([d] + list(m)); hall[SS] = dev(SS)[1]
                restante = [x for x in restante if x not in m]
    full = cambia(zl); _, mmf = plata(base, estado(zl))
    peor = (0, None)
    for SS, ch in hall.items():
        _, mm = plata(base, estado(list(SS)))
        u = set().union(*[sing(b) for b in SS]); inter.append({'Zona': zi, 'Combinación': ' + '.join(sorted(SS)), "Tramos": len(SS), 'Barras': len(ch), 'MM$/mes': round(mm, 1),
                      'Nuevas por interacción': len(set(ch.index) - u), 'Canceladas': len(u - set(ch.index))})
        if mm > peor[0]: peor = (mm, SS)
    _, mm_sum = plata(base, estado(d_)) if d_ else (None, 0)
    resumen.append({'Zona': zi, 'Tramos': len(zl), 'Decisivos': len(d_), 'Recálculos': NT[0], 'Combinaciones con interacción': len(hall),
                    'Solo decisivos juntos: MM$/mes': round(mm_sum, 1), 'Zona completa: barras': len(full), 'Zona completa: MM$/mes': round(mmf, 1),
                    'Peor parcial: MM$/mes': round(peor[0], 1), 'Decisivos de la zona': ', '.join(x.split('->')[0].strip('_') for x in d_)[:120]})
    print(resumen[-1], f'{time.time()-t0:.0f} s', flush=True)
R = pd.DataFrame(resumen); I = pd.DataFrame(inter); pd.to_pickle({'R': R, 'I': I}, OUT + 'hueco.pkl')
pd.set_option('display.width', 260); pd.set_option('display.max_colwidth', 70); print(R.to_string(index=False))
