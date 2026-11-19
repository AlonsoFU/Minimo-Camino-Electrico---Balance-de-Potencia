exec(open('zonas_pct.py').read().split("out = []")[0])
out = []
for nom, an, modo in [('Trafo troncal, X', m3, 'X'), ('Misma subestación, R', m1, 'Z')]:
    M = est_f(True, an, modo, [])
    for z, l in Z.items():
        a = est_f(True, an, modo, l); ch = a[a != M.reindex(a.index)]
        dk = pd.Series({b: km(src(b), ch[b]) - km(src(b), M[b]) for b in ch.index})
        mw = S.mw.reindex(ch.index).fillna(0); dp = (ch.map(precio) - M.reindex(ch.index).map(precio)).abs() * mw / 1000
        out.append({'Criterio': nom, 'Zona': z, 'Barras': len(ch), 'Más cerca': int((dk < -5).sum()), 'Más lejos': int((dk > 5).sum()), 'Parecido': int((dk.abs() <= 5).sum()),
                    'MM$ más cerca': round(dp[dk < -5].sum()), 'MM$ más lejos': round(dp[dk > 5].sum()), 'km promedio que cambia': round(dk.mean(), 1) if len(dk) else None})
R = pd.DataFrame(out); pd.set_option('display.width', 220); print(R.to_string(index=False)); R.to_pickle(OUT + 'zonas_geo.pkl')
