"""Efectos en cadena: corregir tramos (por bloque de paralelos) de a uno vs juntos, y secuencia que recalcula en cada paso."""
src = open('decisivos.py').read().split("CRIT = {")[0]
exec(src)
import re, time
s3 = pd.read_pickle(OUT + 'ref_trafo_directo.pkl')
o0 = escenario(oper, True, m3)
disc = V[V.clasificacion_validacion.str.startswith('DISCREPA') & V.valor_sugerido.notna()].drop_duplicates('nombre_ENT').set_index('nombre_ENT')
sel = oper['Nombre'].isin(disc.index) & ~m3
oper_b = oper.loc[sel, 'Nombre'].str.replace(r'_\dde\d$', '', regex=True)
bloques = {b: list(idx) for b, idx in oper_b.groupby(oper_b).groups.items()}
xsug = {i: disc.loc[oper.loc[i, 'Nombre'], 'valor_sugerido'] * ref.loc[i] for i in oper.index[sel]}
def estado(aplicados):
    o = o0.copy()
    for b in aplicados:
        for i in bloques[b]: o.loc[i, 'X'] = xsug[i]
    return asignar(pesos(o)[1])
def plata(a, b):
    ch = b[b != a.reindex(b.index)]; mwc = S.mw.reindex(ch.index).fillna(0)
    return ch, float(((ch.map(precio) - a.reindex(ch.index).map(precio)).abs() * mwc / 1000).sum())
base = estado([]); print('base reproduce:', int((base == s3.reindex(base.index)).sum()), '/', len(base), ' bloques:', len(bloques))
t0 = time.time(); ind = {}
for b in bloques:
    s = estado([b]); ch, mm = plata(base, s); ind[b] = (set(ch.index), mm)
print('prueba individual por bloque:', round(time.time() - t0), 's')
dec = [b for b, (c, mm) in ind.items() if c]; print('bloques decisivos solos:', len(dec), ' con plata:', sum(1 for b in dec if ind[b][1] > 0))
union = set().union(*[ind[b][0] for b in dec])
sj = estado(dec); chj, mmj = plata(base, sj)
sa = estado(list(bloques)); cha, mma = plata(base, sa)
print(f'De a uno (unión): {len(union)} barras | Juntos solo decisivos: {len(chj)} barras, {mmj:.0f} MM$ | Juntos TODOS: {len(cha)} barras, {mma:.0f} MM$')
print('  barras que cambian solo al combinar decisivos (cadena):', len(set(chj.index) - union), ' que se cancelan al combinar:', len(union - set(chj.index)))
print('  barras extra por los no decisivos combinados:', len(set(cha.index) - set(chj.index)))
# secuencia greedy recalculando
cur, apl, pasos = base, [], []
pend = sorted(dec, key=lambda b: -ind[b][1])
while pend:
    best = None
    for b in pend:
        s = estado(apl + [b]); ch, mm = plata(cur, s)
        if best is None or mm > best[2] or (mm == best[2] and len(ch) > len(best[1])): best = (b, ch, mm, s)
    b, ch, mm, s = best
    if len(ch) == 0: break
    apl.append(b); pend.remove(b); cur = s
    _, mmc = plata(base, cur)
    pasos.append({'Paso': len(apl), 'Bloque corregido': b, 'Barras que cambian en este paso': len(ch), 'MM$/mes del paso': round(mm, 1),
                  'Barras acumuladas vs base': int((cur != base.reindex(cur.index)).sum()), 'MM$/mes acumulado vs base': round(mmc, 1),
                  'Solo (de a uno): barras': len(ind[b][0]), 'Solo: MM$/mes': round(ind[b][1], 1)})
P = pd.DataFrame(pasos); print(P.to_string(index=False))
print('quedan sin efecto tras la secuencia:', len(pend))
pd.to_pickle({'ind': ind, 'P': P, 'base': base, 'sj': sj, 'sa': sa, 'dec': dec, 'bloques': list(bloques)}, OUT + 'cadena.pkl')
