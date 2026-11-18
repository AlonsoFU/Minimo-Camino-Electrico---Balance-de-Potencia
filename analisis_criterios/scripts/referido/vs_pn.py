exec(open('dos_por_dos.py').read().split("todos = list(bloques)")[0])
P = PNa.reindex(B.index); todos = list(bloques)
def ev(a, nom):
    ch = a[a != P.reindex(a.index)]; ch = ch[P.reindex(ch.index).notna()]
    k0 = pd.Series({b: km(src(b), P[b]) for b in ch.index}); k1 = pd.Series({b: km(src(b), ch[b]) for b in ch.index}); dk = k0 - k1
    mw = S.mw.reindex(ch.index).fillna(0); mm = float(((ch.map(precio) - P.reindex(ch.index).map(precio)).abs() * mw / 1000).sum())
    print(f'{nom:42s} distintas a PN2604 {len(ch):4d} | {mm:5.0f} MM$/mes | más cerca {int((dk>5).sum()):3d}  más lejos {int((dk<-5).sum()):3d}  parecido {int((dk.abs()<=5).sum()):3d}')
ev(B, 'Módulo actual (método actual + ENT)')
ev(est_f(False, None, 'X', todos), 'Método actual + datos corregidos')
ev(est_f(True, m3, 'X', []), 'Nuevo trafo troncal X + ENT')
ev(est_f(True, m3, 'X', todos), 'Nuevo trafo troncal X + datos corregidos')
ev(est_f(True, m1, 'Z', []), 'Nuevo misma subest. |Z| + ENT')
ev(est_f(True, m1, 'Z', todos), 'Nuevo misma subest. |Z| + datos corregidos')
