exec(open('vs_pn.py').read().split("def ev(")[0])
rows = []
def ev(a, nom, prev=None):
    ch = a[a != P.reindex(a.index)]; ch = ch[P.reindex(ch.index).notna()]
    k0 = pd.Series({b: km(src(b), P[b]) for b in ch.index}); k1 = pd.Series({b: km(src(b), ch[b]) for b in ch.index}); dk = k0 - k1
    mw = S.mw.reindex(ch.index).fillna(0); dp = (ch.map(precio) - P.reindex(ch.index).map(precio)) * mw / 1000
    kall = pd.Series({b: km(src(b), a[b]) for b in a.index})
    r = {'Escenario': nom, '= PN2604': int((a == P.reindex(a.index)).sum()), 'Distintas a PN2604': len(ch), 'Con iny/ret': int((mw > 0).sum()),
         'MM$/mes movidos': round(dp.abs().sum()), 'Neto MM$/mes (+ sube)': round(dp.sum()), 'Más cerca que PN2604': int((dk > 5).sum()),
         'Más lejos que PN2604': int((dk < -5).sum()), '>100 km de su troncal': int((kall > 100).sum())}
    if prev is not None:
        m = a != prev.reindex(a.index); pa = prev.reindex(a.index) == P.reindex(a.index); pc = a == P.reindex(a.index)
        r.update({'Cambian al corregir datos': int(m.sum()), '…pasan a = PN2604': int((m & pc & ~pa).sum()), '…dejan de = PN2604': int((m & ~pc & pa).sum()),
                  '…cambian entre troncales ≠ PN2604': int((m & ~pc & ~pa).sum())})
    rows.append(r)
ev(P.fillna(B), 'PN2604 (asignación vigente)')
A0 = B; C0 = est_f(False, None, 'X', todos)
ev(A0, 'Actual (sin referir), datos actuales = módulo'); ev(C0, 'Actual (sin referir), datos corregidos', A0)
for nom, an, modo in [('Referido, X', None, 'X'), ('Referido, R (|Z|)', None, 'Z'), ('Referido + trafo troncal, X', m3, 'X'), ('Referido + trafo troncal, R (|Z|)', m3, 'Z'),
                      ('Referido + misma subestación, X', m1, 'X'), ('Referido + misma subestación, R (|Z|)', m1, 'Z')]:
    A = est_f(True, an, modo, []); C = est_f(True, an, modo, todos)
    ev(A, f'{nom}, datos actuales'); ev(C, f'{nom}, datos corregidos', A)
R = pd.DataFrame(rows); pd.set_option('display.width', 300); pd.set_option('display.max_columns', 30); print(R.to_string(index=False)); R.to_pickle(OUT + 'vs_pn3.pkl')
