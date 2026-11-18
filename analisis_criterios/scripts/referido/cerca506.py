exec(open('dos_por_dos.py').read().split("todos = list(bloques)")[0])
NC = est_f(True, m3, 'X', list(bloques)); ch = NC[NC != B.reindex(NC.index)]
k0 = pd.Series({b: km(src(b), B[b]) for b in ch.index}); k1 = pd.Series({b: km(src(b), ch[b]) for b in ch.index}); dk = k0 - k1
c = dk[dk > 5]; mw = S.mw.reindex(c.index).fillna(0)
print('más cerca:', len(c), ' reducción mediana', round(c.median()), 'km')
print(pd.cut(c, [5, 20, 50, 100, 1000], labels=['5–20 km', '20–50 km', '50–100 km', '>100 km']).value_counts().sort_index().to_string())
d = pd.DataFrame({'antes': B.reindex(c.index), 'km antes': k0[c.index].round(), 'después': ch[c.index], 'km después': k1[c.index].round(), 'acerca km': c.round(), 'MW': mw.round(1)})
d = d[d.MW > 0].sort_values('acerca km', ascending=False)
print(d.head(10).to_string())
pn_base_dist = int((B != R0['PN2604'].reindex(B.index)).sum()); print('módulo actual distinto de PN2604:', pn_base_dist)
