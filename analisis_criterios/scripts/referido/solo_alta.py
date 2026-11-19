exec(open('listado_verif.py').read().split("out = {'zonas'")[0])
f = '/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/listado_tramos.xlsx'
T = pd.read_excel(f, sheet_name='Tramos', header=1)
T['g'] = T.Etapa.astype(str) + '|' + T.Grupo + T.apply(lambda r: r['Tramo'] if '(solo)' in r.Grupo else '', axis=1)
todos48 = list(T['Código ENT'])
esc = {'Solo confianza alta': list(T[T.Confianza == 'Alta']['Código ENT']),
       'Alta, solo grupos completos': list(T[T.groupby('g').Confianza.transform(lambda s: (s == 'Alta').all())]['Código ENT']),
       'Alta y media': list(T[T.Confianza != 'Baja']['Código ENT']),
       'Alta y media, solo grupos completos': list(T[T.groupby('g').Confianza.transform(lambda s: (s != 'Baja').all())]['Código ENT']),
       'Los 48': todos48}
rows = []
for v, (an, modo) in VAR.items():
    M = est_f(True, an, modo, []); F = est_f(True, an, modo, todos48); fin = dif(F, M)
    for n, l in esc.items():
        a = est_f(True, an, modo, l); s = dif(a, M)
        w = a[(a != M.reindex(a.index)) & (a != F.reindex(a.index))]
        mmw = float(((w.map(precio) - F.reindex(w.index).map(precio)).abs() * mwS.reindex(w.index).fillna(0) / 1000).sum())
        bien = int(((a != M.reindex(a.index)) & (a == F.reindex(a.index))).sum())
        rows.append({'var': v, 'Escenario': n, 'tramos': len(l), 'barras': s['barras'], 'mm': s['mm'], 'bien': bien, 'final': fin['barras'], 'mm final': fin['mm'], 'mal': len(w), 'mm mal': round(mmw, 1), 'cerca': s['cerca'], 'lejos': s['lejos']})
R = pd.DataFrame(rows); pd.set_option('display.width', 230); print(R.to_string(index=False))
g = T.groupby('g').Confianza.agg(lambda s: '/'.join(sorted(s)))
print(T[T.groupby('g').Confianza.transform(lambda s: (s == 'Alta').all())][['Etapa', 'Grupo', 'Tramo']].to_string(index=False))
print(T[(T.Confianza == 'Alta') & ~T.groupby('g').Confianza.transform(lambda s: (s == 'Alta').all())][['Etapa', 'Grupo', 'Tramo']].to_string(index=False))
