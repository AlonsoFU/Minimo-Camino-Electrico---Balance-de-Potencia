exec(open('cadena.py').read().split("base = estado([])")[0])
exec('cdf ='+open('banco.py').read().split('cdf =',1)[1].split('rows = []')[0])
c = pd.read_pickle(OUT + 'cadena.pkl'); base = c['base']; ind = c['ind']
src = lambda b: b if b in coord else R0.loc[b, 'nodo']
filas = []
for b in c['dec']:
    s = estado([b]); ch = s[s != base.reindex(s.index)]
    k0 = pd.Series({x: km(src(x), base[x]) for x in ch.index}); k1 = pd.Series({x: km(src(x), ch[x]) for x in ch.index})
    dk = (k1 - k0).dropna()
    filas.append({'Tramo': b, 'Barras': len(ch), 'MM$/mes': round(ind[b][1], 1), 'Se acercan': int((dk < -1).sum()), 'Se alejan': int((dk > 1).sum()),
                  'Δ km mediano': round(dk.median(), 0) if len(dk) else None,
                  'Troncal antes → después': '; '.join(sorted({f"{base[x][:10].strip('_')}→{ch[x][:10].strip('_')}" for x in ch.index}))[:80]})
G = pd.DataFrame(filas).sort_values('MM$/mes', ascending=False)
G['Sospecha'] = np.where(G['Se alejan'] > G['Se acercan'], 'Sí: aleja', '')
G.to_pickle(OUT + 'geo_tramo.pkl')
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 60)
print(G.head(20).to_string(index=False)); print('\nTramos que alejan más de lo que acercan:', int((G.Sospecha != '').sum()), 'de', len(G))
