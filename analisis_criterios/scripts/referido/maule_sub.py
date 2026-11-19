import itertools
exec(open('listado_verif.py').read().split("out = {'zonas'")[0])
N = set(pd.read_pickle(OUT + 'nucleo_N.pkl'))
R = pd.read_excel('/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/listado_tramos.xlsx', sheet_name='Revisión')
g = R[R.Zona.str.startswith('Maule')]; imp = [t for t in g.Tramo if t in N]; zona = list(g.Tramo)
print(g[['Tramo', 'Crítico / vecino', 'Imprescindible (de los 50)', 'X ENT (Ω)', 'X sugerida (Ω)']].to_string(index=False))
nom = lambda t: t.split('->')[0].strip('_').split('_')[0] + ' ' + t.split('_')[-1] + '/' + t.split('->')[1].split('_')[-1] if t.split('->')[0][:6] == t.split('->')[1][:6] else t.split('->')[0].rstrip('_0123456789').strip('_') + '–' + t.split('->')[1].rstrip('_0123456789').strip('_')
rows = []
for v, (an, modo) in VAR.items():
    M = est_f(True, an, modo, []); F = est_f(True, an, modo, zona)
    fin = set(F.index[F != M.reindex(F.index)])
    for k in range(1, len(imp) + 1):
        for c in itertools.combinations(imp, k):
            a = est_f(True, an, modo, list(c)); ch = set(a.index[a != M.reindex(a.index)])
            ok = len(ch & fin & set(a.index[a == F.reindex(a.index)])); tr = a[(a != M.reindex(a.index)) & (a != F.reindex(a.index))]
            mm_tr = float(((tr.map(precio) - F.reindex(tr.index).map(precio)).abs() * mwS.reindex(tr.index).fillna(0) / 1000).sum())
            rows.append({'var': v, 'k': k, 'combo': ' + '.join(nom(t) for t in c), 'llega al final': ok, 'de': len(fin), 'en troncal equivocada': len(tr), 'MM$ equivocado': round(mm_tr, 1)})
T = pd.DataFrame(rows); pd.set_option('display.width', 250, 'display.max_colwidth', 90, 'display.max_rows', 300)
P = T.pivot_table(index=['k', 'combo'], columns='var', values=['llega al final', 'en troncal equivocada', 'MM$ equivocado'], aggfunc='first')
print(P.to_string())
