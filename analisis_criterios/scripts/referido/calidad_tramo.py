exec(open('cadena.py').read().split("base = estado([])")[0])
exec('cdf ='+open('banco.py').read().split('cdf =',1)[1].split('rows = []')[0])
c = pd.read_pickle(OUT + 'cadena.pkl'); base = c['base']
src = lambda b: b if b in coord else R0.loc[b, 'nodo']
PNa = R0['PN2604']; filas = []
for b in c['dec']:
    s = estado([b]); ch = s[s != base.reindex(s.index)]
    if ch.empty: continue
    k0 = pd.Series({x: km(src(x), base[x]) for x in ch.index}); k1 = pd.Series({x: km(src(x), ch[x]) for x in ch.index})
    dk = k1 - k0; mw = S.mw.reindex(ch.index).fillna(0)
    dp = (ch.map(precio) - base.reindex(ch.index).map(precio)).abs() * mw / 1000
    mej = dk < -5; emp = dk > 5
    pn = (ch == PNa.reindex(ch.index)).astype(int) - (base.reindex(ch.index) == PNa.reindex(ch.index)).astype(int)
    filas.append({'Tramo': b, 'Barras que cambian': len(ch), 'MM$/mes': round(dp.sum(), 1),
                  'Mejoran (más cerca)': int(mej.sum()), 'Empeoran (más lejos)': int(emp.sum()), 'Sin cambio claro / sin coord.': int(len(ch) - mej.sum() - emp.sum()),
                  'MM$ en barras que mejoran': round(dp[mej].sum(), 1), 'MM$ en barras que empeoran': round(dp[emp].sum(), 1),
                  'PN2604: gana / pierde': f'{int((pn > 0).sum())} / {int((pn < 0).sum())}'})
Q = pd.DataFrame(filas)
Q['Balance'] = np.select([Q['MM$ en barras que mejoran'] > 2 * Q['MM$ en barras que empeoran'], Q['MM$ en barras que empeoran'] > 2 * Q['MM$ en barras que mejoran']],
                         ['Mejora', 'Empeora'], 'Mixto')
Q.loc[(Q['Mejoran (más cerca)'] + Q['Empeoran (más lejos)']) == 0, 'Balance'] = 'Sin evaluar'
Q = Q.sort_values('MM$/mes', ascending=False); Q.to_pickle(OUT + 'calidad_tramo.pkl')
pd.set_option('display.width', 250)
print(Q.head(15).drop(columns=['Sin cambio claro / sin coord.']).to_string(index=False))
print(Q.Balance.value_counts().to_string()); print(Q.groupby('Balance')['MM$/mes'].sum().round(0).to_string())
