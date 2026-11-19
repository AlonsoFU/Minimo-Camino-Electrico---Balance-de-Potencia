exec(open('zonas_pct.py').read().split("out = []")[0])
t38 = [t for l in Z.values() for t in l]; L2 = [t for t in L if t in bloques]; resto = [t for t in L2 if t not in t38]; todos = list(bloques)
G = dict(Z); G['Resto de la lista'] = resto; G['38 tramos juntos'] = t38; G['Lista completa (112)'] = L2; G['Todos (668)'] = todos
out = []
for nom, an, modo in [('TT-X', m3, 'X'), ('MS-R', m1, 'Z')]:
    M = est_f(True, an, modo, [])
    for z, l in G.items():
        a = est_f(True, an, modo, l); ch = a[a != M.reindex(a.index)]
        dk = pd.Series({b: km(src(b), ch[b]) - km(src(b), M[b]) for b in ch.index}, dtype=float)
        mw = S.mw.reindex(ch.index).fillna(0); mm = float(((ch.map(precio) - M.reindex(ch.index).map(precio)).abs() * mw / 1000).sum())
        out.append({'crit': nom, 'Zona': z, 'Tramos': len(l), 'Barras': len(ch), 'Cerca': int((dk < -5).sum()), 'Lejos': int((dk > 5).sum()), 'km': round(dk.mean(), 1) if len(dk) else 0, 'MM': round(mm)})
R = pd.DataFrame(out); pd.set_option('display.width', 200); print(R.to_string(index=False)); R.to_pickle(OUT + 'tabla_todo.pkl')
