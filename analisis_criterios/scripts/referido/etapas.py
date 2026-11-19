exec(open('listado_verif.py').read().split("out = {'zonas'")[0])
N = pd.read_pickle(OUT + 'nucleo_N.pkl')
R = pd.read_excel('/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/listado_tramos.xlsx', sheet_name='Revisión')
RR = pd.read_excel('/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/listado_tramos.xlsx', sheet_name='Rondas')
LISTA = list(R.Tramo); print('lista 116:', len(LISTA), ' N:', len(N), ' N ⊂ lista:', set(N) <= set(LISTA))
for v, (an, modo) in VAR.items():
    FL = est_f(True, an, modo, LISTA); FN = est_f(True, an, modo, N); FT = est_f(True, an, modo, todos)
    print(v, 'N vs lista: barras distintas', int((FN != FL.reindex(FN.index)).sum()), '| lista vs 668:', dif(FL, FT)['barras'], dif(FL, FT)['mm'])
R['nuc'] = R.Tramo.isin(N)
rows = []
for r, g in R.groupby('Orden'):
    x = RR[RR.Ronda == r]; tot = RR[RR.Ronda == 6].set_index('Variante')['MM$/mes (acum.)']
    pct = (x.set_index('Variante')['MM$/mes (acum.)'] / tot * 100)
    rows.append({'Etapa': r, 'Zonas': ', '.join(dict.fromkeys(g.Zona)), 'Tramos': len(g), 'Líneas': int((g.Tipo == 'Línea').sum()), 'Trafos': int((g.Tipo == 'Trafo').sum()),
                 'Críticos': int((g['Crítico / vecino'] == 'Crítico').sum()), 'Vecinos+comb.': int((g['Crítico / vecino'] != 'Crítico').sum()), 'En los 50': int(g.nuc.sum()),
                 'MM$ etapa': f"{x['Mueve la ronda: MM$'].min():.0f}–{x['Mueve la ronda: MM$'].max():.0f}", '% plata acum.': f"{pct.min():.0f}–{pct.max():.0f}",
                 'Distintas PN2604 acum.': f"{x['Distintas a PN2604'].min()}–{x['Distintas a PN2604'].max()}"})
pd.set_option('display.width', 250, 'display.max_colwidth', 90); print(pd.DataFrame(rows).to_string(index=False))
print(RR[RR.Ronda == 0][['Variante', 'Distintas a PN2604']].to_string(index=False))
