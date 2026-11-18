exec(open('vs_pn.py').read().split("def ev(")[0])
rows = []
def ev(a, nom):
    ch = a[a != P.reindex(a.index)]; ch = ch[P.reindex(ch.index).notna()]
    k0 = pd.Series({b: km(src(b), P[b]) for b in ch.index}); k1 = pd.Series({b: km(src(b), ch[b]) for b in ch.index}); dk = k0 - k1
    mw = S.mw.reindex(ch.index).fillna(0); dp = (ch.map(precio) - P.reindex(ch.index).map(precio)) * mw / 1000
    kall = pd.Series({b: km(src(b), a[b]) for b in a.index})
    rows.append({'Escenario': nom, 'Barras distintas a PN2604': len(ch), 'Con iny/ret': int((mw > 0).sum()), 'MM$/mes movidos': round(dp.abs().sum()),
                 'Neto MM$/mes (+ sube)': round(dp.sum()), 'Más cerca que PN2604': int((dk > 5).sum()), 'Más lejos que PN2604': int((dk < -5).sum()),
                 'Barras a >100 km de su troncal': int((kall > 100).sum())})
ev(P.fillna(B), 'PN2604 (asignación vigente)')
ev(B, 'Módulo actual (método actual + ENT)')
ev(est_f(False, None, 'X', todos), 'Método actual + datos corregidos')
for nom, an, modo in [('Trafo troncal, X', m3, 'X'), ('Trafo troncal, |Z|', m3, 'Z'), ('Misma subestación, X', m1, 'X'), ('Misma subestación, |Z|', m1, 'Z')]:
    ev(est_f(True, an, modo, []), f'Nuevo {nom} + datos actuales'); ev(est_f(True, an, modo, todos), f'Nuevo {nom} + datos corregidos')
R = pd.DataFrame(rows); pd.set_option('display.width', 250); print(R.to_string(index=False)); R.to_pickle(OUT + 'vs_pn.pkl')
