exec(open('listado_verif.py').read().split("out = {'zonas'")[0])
R = pd.read_excel('/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/listado_tramos.xlsx', sheet_name='Revisión')
rows = []
for z, g in R[R.Zona != 'Independiente'].groupby('Zona', sort=False):
    l = list(g.Tramo); cr = list(g[g['Crítico / vecino'] == 'Crítico'].Tramo)
    for v, (an, modo) in VAR.items():
        M = est_f(True, an, modo, []); Z = est_f(True, an, modo, l); C = est_f(True, an, modo, cr)
        dz = dif(Z, M); d = dif(C, Z)
        rows.append({'Zona': z, 'var': v, 'tramos': len(l), 'críticos': len(cr), 'zona: barras': dz['barras'], 'zona: MM$': dz['mm'], 'solo críticos difiere: barras': d['barras'], 'MM$': d['mm']})
T = pd.DataFrame(rows); pd.set_option('display.width', 220)
print(T.groupby('Zona', sort=False).agg(tramos=('tramos', 'first'), crit=('críticos', 'first'), zb=('zona: barras', 'max'), zmm=('zona: MM$', 'max'), db=('solo críticos difiere: barras', 'max'), dmm=('MM$', 'max')).to_string())
