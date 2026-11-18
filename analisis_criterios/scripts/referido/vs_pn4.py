exec(open('vs_pn.py').read().split("def ev(")[0])
rows = []
kP = pd.Series({b: km(src(b), P[b]) for b in P.index if pd.notna(P[b])})
def ev(a, nom):
    ch = a[a != P.reindex(a.index)]; ch = ch[P.reindex(ch.index).notna()]
    mw = S.mw.reindex(ch.index).fillna(0); dp = (ch.map(precio) - P.reindex(ch.index).map(precio)) * mw / 1000
    ka = pd.Series({b: km(src(b), a[b]) for b in kP.index if b in a.index})
    rows.append({'Escenario': nom, 'MM$ que suben': round(dp[dp > 0].sum()), 'MM$ que bajan': round(dp[dp < 0].sum()), 'Absoluto': round(dp.abs().sum()), 'Neto': round(dp.sum()),
                 'km mediana (todas)': round(ka.median(), 1), 'km promedio (todas)': round(ka.mean(), 1), 'km promedio ponderado por MW': round((ka * S.mw.reindex(ka.index).fillna(0)).sum() / S.mw.reindex(ka.index).fillna(0).sum(), 1)})
ev(P.fillna(B), 'PN2604')
ev(B, 'Actual, datos actuales'); ev(est_f(False, None, 'X', todos), 'Actual, datos corregidos')
for nom, an, modo in [('Referido X', None, 'X'), ('Referido R', None, 'Z'), ('Ref + subest. (trafo troncal) X', m3, 'X'), ('Ref + subest. (trafo troncal) R', m3, 'Z'), ('Ref + misma subest. X', m1, 'X'), ('Ref + misma subest. R', m1, 'Z')]:
    ev(est_f(True, an, modo, []), f'{nom}, datos actuales'); ev(est_f(True, an, modo, todos), f'{nom}, datos corregidos')
R = pd.DataFrame(rows); pd.set_option('display.width', 250); print(R.to_string(index=False)); R.to_pickle(OUT + 'vs_pn4.pkl')
