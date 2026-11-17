"""Comparación final contra la base actual: Hoy (método actual + ENT) → método nuevo + ENT → método nuevo + datos corregidos."""
exec(open('dec_criterios.py').read().split("CR = {")[0])
exec('cdf ='+open('banco.py').read().split('cdf =',1)[1].split('rows = []')[0])
import sqlite3
src = lambda b: b if b in coord else R0.loc[b, 'nodo']
B = S['mod_actual']; PNa = R0['PN2604']
def metr(a, ref_):
    ch = a[a != ref_.reindex(a.index)]; mwc = S.mw.reindex(ch.index).fillna(0)
    mm = float(((ch.map(precio) - ref_.reindex(ch.index).map(precio)).abs() * mwc / 1000).sum())
    k = pd.Series({b: km(src(b), a[b]) for b in a.index})
    return len(ch), round(mm), int((a == PNa.reindex(a.index)).sum()), int((k > 100).sum())
CRIT = {'tt_x': ('Trafo troncal, X', m3, 'X'), 'tt_z': ('Trafo troncal, |Z|', m3, 'Z'), 'sub_x': ('Misma subestación, X', m1, 'X'), 'sub_z': ('Misma subestación, |Z|', m1, 'Z')}
rows = []
b0 = metr(B, B); rows.append({'Escenario': 'BASE: método actual + ENT', 'Barras distintas a la base': 0, 'MM$/mes vs base': 0, '= PN2604': b0[2], 'Barras a >100 km': b0[3]})
for k, (nom, an, modo) in CRIT.items():
    o0c = esc2(True, an)
    def est(apl):
        o = o0c.copy()
        for b in apl:
            for i in bloques[b]:
                if an.loc[i]: continue
                o.loc[i, 'X'] = xsug[i]; o.loc[i, 'R'] = rs[i] * ref.loc[i]
        return asignar(pesos_z(o, modo))
    c = sqlite3.connect(f'registro_{k}.sqlite')
    lista = [r[0] for r in c.execute("SELECT valor FROM resumen WHERE clave='lista a revisar'")][0].split(' | ')
    cand_ = [b for b in bloques if not all(an.loc[i] for i in bloques[b])]
    M, Fl, Fa = est([]), est(lista), est(cand_)
    for lab, a in [('método nuevo + ENT', M), ('método nuevo + lista corregida', Fl), ('método nuevo + todo corregido', Fa)]:
        m = metr(a, B); rows.append({'Escenario': f'{nom}: {lab}', 'Barras distintas a la base': m[0], 'MM$/mes vs base': m[1], '= PN2604': m[2], 'Barras a >100 km': m[3]})
    chF = set(Fa.index[Fa != B.reindex(Fa.index)]); okL = sum(1 for b in chF if Fl[b] == Fa[b])
    rows[-1]['Lista reproduce el final (barras)'] = f'{okL}/{len(chF)}'
    rows[-1]['Lista: barras del final iguales'] = int((Fl == Fa.reindex(Fl.index)).sum())
    print(nom, 'lista', len(lista), 'reproduce', okL, '/', len(chF), flush=True)
R = pd.DataFrame(rows); pd.set_option('display.width', 250); print(R.to_string(index=False)); R.to_pickle(OUT + 'final_vs_base.pkl')
