exec(open('cadena.py').read().split("base = estado([])")[0])
exec('cdf ='+open('banco.py').read().split('cdf =',1)[1].split('rows = []')[0])
c = pd.read_pickle(OUT + 'cadena.pkl'); todos = c['bloques']
def corr(rf, an):
    o = escenario(oper, rf, an)
    for b in todos:
        for i in bloques[b]:
            if an is None or not an.loc[i]: o.loc[i, 'X'] = xsug[i] / (ref.loc[i] if not rf else 1)
    return asignar(pesos(o)[1])
src = lambda b: b if b in coord else R0.loc[b, 'nodo']
res = []
for nom, rf, an, base in [('Hoy', False, None, S['mod_actual']), ('Referido + trafo troncal', True, m3, c['base'])]:
    nuevo = corr(rf, an); ch = nuevo[nuevo != base.reindex(nuevo.index)]
    k0 = pd.Series({b: km(src(b), base[b]) for b in ch.index}); k1 = pd.Series({b: km(src(b), ch[b]) for b in ch.index})
    ok = k0.notna() & k1.notna(); k0, k1 = k0[ok], k1[ok]; mw = S.mw.reindex(k0.index).fillna(0)
    res.append({'Criterio': nom, 'Barras que cambian': len(ch), 'Se acercan': int((k1 < k0 - 1).sum()), 'Se alejan': int((k1 > k0 + 1).sum()),
                'Estaban a >100 km y quedan a <100 km': int(((k0 > 100) & (k1 < 100)).sum()), 'Al revés (<100 → >100 km)': int(((k0 < 100) & (k1 > 100)).sum()),
                'km mediana antes → después': f'{k0.median():.0f} → {k1.median():.0f}',
                'Con iny/ret: se acercan / se alejan': f'{int(((k1 < k0 - 1) & (mw > 0)).sum())} / {int(((k1 > k0 + 1) & (mw > 0)).sum())}'})
    if nom == 'Referido + trafo troncal':
        d = pd.DataFrame({'antes': base.reindex(k0.index), 'km_antes': k0.round(0), 'después': ch.reindex(k0.index), 'km_después': k1.round(0), 'MW': mw.round(1)})
        print(d[(d.km_antes > 100) & (d.km_después < 100)].sort_values('MW', ascending=False).head(10).to_string())
        print(d[(d.km_antes < 100) & (d.km_después > 100)].sort_values('MW', ascending=False).head(10).to_string())
print(pd.DataFrame(res).T.to_string())
