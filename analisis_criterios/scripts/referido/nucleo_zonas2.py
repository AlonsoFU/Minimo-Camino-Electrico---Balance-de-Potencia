exec(open('listado_verif.py').read().split("out = {'zonas'")[0])
N = set(pd.read_pickle(OUT + 'nucleo_N2.pkl'))
R = pd.read_excel('/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/listado_tramos.xlsx', sheet_name='Revisión')
zon = {}
for z, g in R.groupby('Zona', sort=False):
    if z == 'Independiente':
        for t in g.Tramo: zon[t] = [t]
    else: zon[z] = list(g.Tramo)
rows = []
for z, l in zon.items():
    ln = [t for t in l if t in N]
    if not ln and len(l) == 1: continue
    r = {'Zona': z, 'tramos': len(l), 'de los 50': len(ln)}
    for v, (an, modo) in VAR.items():
        M = est_f(True, an, modo, []); Z = est_f(True, an, modo, l); C = est_f(True, an, modo, ln)
        d = dif(C, Z); r[v] = f"{d['barras']} b / {d['mm']:.1f}"
    rows.append(r)
pd.set_option('display.width', 220); print(pd.DataFrame(rows).to_string(index=False))
# acumulado por etapa solo con los 50 vs acumulado completo
ac, acn = [], []
for e_ in sorted(R.Orden.unique()):
    g = R[R.Orden == e_]; ac += list(g.Tramo); acn += [t for t in g.Tramo if t in N]
    s = []
    for v, (an, modo) in VAR.items():
        d = dif(est_f(True, an, modo, acn), est_f(True, an, modo, ac)); s.append(f"{v} {d['barras']} b / {d['mm']:.1f}")
    print('etapa', e_, len(acn), 'de', len(ac), ' | '.join(s))
print('Kimal en los 50:', [t for t in zon['Kimal'] if t in N])
print('Mulchén en los 50:', [t for t in zon['Mulchén'] if t in N])
