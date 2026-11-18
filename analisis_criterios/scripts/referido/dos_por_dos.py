exec(open('final_vs_base.py').read().split("CRIT = {")[0])
def est_f(rf, an, modo, apl):
    o0c = esc2(rf, an); o = o0c.copy()
    for b in apl:
        for i in bloques[b]:
            if an is not None and an.loc[i]: continue
            f = ref.loc[i] if rf else 1
            o.loc[i, 'X'] = xsug[i] / ref.loc[i] * f; o.loc[i, 'R'] = rs[i] * f
    return asignar(pesos_z(o, modo))
todos = list(bloques)
HA = est_f(False, None, 'X', []); HC = est_f(False, None, 'X', todos)
print('control base:', int((HA == B.reindex(HA.index)).sum()), '/', len(HA))
rows = []
for nom, a in [('Actual + datos actuales', HA), ('Actual + datos corregidos', HC)]:
    m = metr(a, B); rows.append({'Escenario': nom, 'Barras distintas a lo actual': m[0], 'MM$/mes vs actual': m[1], '= PN2604': m[2], '>100 km': m[3]})
for nom, an, modo in [('Trafo troncal, X', m3, 'X'), ('Misma subestación, |Z|', m1, 'Z')]:
    NA = est_f(True, an, modo, []); NC = est_f(True, an, modo, todos)
    for lab, a in [('datos actuales', NA), ('datos corregidos', NC)]:
        m = metr(a, B); rows.append({'Escenario': f'Nuevo ({nom}) + {lab}', 'Barras distintas a lo actual': m[0], 'MM$/mes vs actual': m[1], '= PN2604': m[2], '>100 km': m[3]})
    d = metr(NC, HC); rows.append({'Escenario': f'Solo efecto del método, con datos corregidos ({nom})', 'Barras distintas a lo actual': d[0], 'MM$/mes vs actual': d[1], '= PN2604': None, '>100 km': None})
R = pd.DataFrame(rows); pd.set_option('display.width', 220); print(R.to_string(index=False)); R.to_pickle(OUT + 'dos_por_dos.pkl')
