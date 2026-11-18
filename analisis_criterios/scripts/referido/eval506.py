exec(open('dos_por_dos.py').read().split("todos = list(bloques)")[0])
todos = list(bloques)
for nom, an, modo in [('Trafo troncal, X', m3, 'X'), ('Misma subestación, |Z|', m1, 'Z')]:
    NC = est_f(True, an, modo, todos); ch = NC[NC != B.reindex(NC.index)]
    k0 = pd.Series({b: km(src(b), B[b]) for b in ch.index}); k1 = pd.Series({b: km(src(b), ch[b]) for b in ch.index}); dk = k1 - k0
    mw = S.mw.reindex(ch.index).fillna(0); dp = (ch.map(precio) - B.reindex(ch.index).map(precio)).abs() * mw / 1000
    pn0 = B.reindex(ch.index) == PNa.reindex(ch.index); pn1 = ch == PNa.reindex(ch.index)
    cerca, lejos, igual = dk < -5, dk > 5, dk.abs() <= 5
    print(f'\n{nom}: cambian {len(ch)}  | más cerca {int(cerca.sum())} ({dp[cerca].sum():.0f} MM$)  más lejos {int(lejos.sum())} ({dp[lejos].sum():.0f} MM$)  parecido ±5 km {int(igual.sum())}  sin coord {int(dk.isna().sum())}')
    print(f'   PN2604: gana {int((pn1 & ~pn0).sum())}  pierde {int((~pn1 & pn0).sum())}  | ambas señales a favor {int((cerca & (pn1 | ~pn0)).sum())}  ambas en contra {int((lejos & ~pn1 & pn0).sum())}')
    print(f'   distancia mediana de las que cambian: {k0.median():.0f} → {k1.median():.0f} km; >100 km: {int((k0>100).sum())} → {int((k1>100).sum())}')
    w = pd.DataFrame({'antes': B.reindex(ch.index), 'km0': k0.round(), 'despues': ch, 'km1': k1.round(), 'MM': dp.round(1)})[lejos].sort_values('MM', ascending=False)
    print('   peores (más lejos, más plata):'); print(w.head(6).to_string())
