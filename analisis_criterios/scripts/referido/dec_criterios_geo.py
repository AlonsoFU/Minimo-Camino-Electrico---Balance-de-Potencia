"""Tramos decisivos (por bloque de paralelos) según criterio: hoy, Referido + trafo troncal y Referido + Subestación, con X y con |Z|."""
exec(open('cadena.py').read().split("base = estado([])")[0])
exec('cdf ='+open('banco.py').read().split('cdf =',1)[1].split('rows = []')[0])
src = lambda b: b if b in coord else R0.loc[b, 'nodo']
oper['R'] = pd.to_numeric(oper['R'], errors='coerce').fillna(0)
def rsug(i):
    r = disc.loc[oper.loc[i, 'Nombre']]; f = str(r.fuente_valor_sugerido)
    v = r.R_CNE if 'CNE' in f and 'Info' not in f else (r.R_Infotec if 'Info' in f and 'CNE' not in f else np.nanmean([r.R_CNE, r.R_Infotec]))
    return v if pd.notna(v) else oper.loc[i, 'R'] * r.valor_sugerido / oper.loc[i, 'X']
rs = {i: rsug(i) for i in xsug}
def pesos_z(o, modo):
    d = o.assign(u=np.minimum(o['Barra A'], o['Barra B']).astype(int), v=np.maximum(o['Barra A'], o['Barra B']).astype(int))
    if modo == 'X': return 1 / (1 / d['X']).groupby([d.u, d.v]).sum()
    z = (d['R'] + 1j * d['X']); return (1 / (1 / z).groupby([d.u, d.v]).sum()).abs()
def esc2(rf, an):
    o = oper.copy()
    if rf: o['X'] = o['X'] * ref; o['R'] = o['R'] * ref
    if an is not None: o.loc[an, ['X', 'R']] = EPS
    return o
CR = {'Hoy (X)': (False, None, 'X'), 'Ref + trafo troncal (X)': (True, m3, 'X'), 'Ref + trafo troncal (|Z|)': (True, m3, 'Z'),
      'Ref + Subestación (X)': (True, m1, 'X'), 'Ref + Subestación (|Z|)': (True, m1, 'Z')}
out = []; det = []
for nom, (rf, an, modo) in CR.items():
    o0c = esc2(rf, an); b0 = asignar(pesos_z(o0c, modo)); n = nmm = 0; bar = set()
    for b in bloques:
        idx = [i for i in bloques[b] if an is None or not an.loc[i]]
        if not idx: continue
        o = o0c.copy()
        for i in idx:
            f = ref.loc[i] if rf else 1
            o.loc[i, 'X'] = xsug[i] / ref.loc[i] * f; o.loc[i, 'R'] = rs[i] * f
        s = asignar(pesos_z(o, modo)); ch, mm = plata(b0, s)
        if len(ch):
            n += 1; nmm += mm; bar |= set(ch.index)
            dk = pd.Series({x: km(src(x), ch[x]) - km(src(x), b0[x]) for x in ch.index}); mwc = S.mw.reindex(ch.index).fillna(0)
            dpp = (ch.map(precio) - b0.reindex(ch.index).map(precio)).abs() * mwc / 1000
            mj, em = dpp[dk < -5].sum(), dpp[dk > 5].sum(); nm_, ne_ = int((dk < -5).sum()), int((dk > 5).sum())
            bal = 'Sin evaluar' if nm_ + ne_ == 0 else ('Mejora' if (mj > 2 * em or (mj == em == 0 and nm_ > ne_)) else ('Empeora' if (em > 2 * mj or (mj == em == 0 and ne_ > nm_)) else 'Mixto'))
            det.append({'Criterio': nom, 'Tramo': b, 'Barras': len(ch), 'MM$/mes': mm, 'Balance': bal})
    out.append({'Criterio': nom, 'Bloques decisivos': n, 'Barras afectadas (unión)': len(bar), 'MM$/mes (suma de a uno)': round(nmm)})
    print(out[-1], flush=True)
pd.DataFrame(out).to_pickle(OUT + 'dec_criterios.pkl'); D = pd.DataFrame(det); D.to_pickle(OUT + 'dec_criterios_det.pkl')
print(D.groupby(['Criterio', 'Balance']).agg(tramos=('Tramo', 'size'), MM=('MM$/mes', 'sum')).round(0).unstack(fill_value=0).to_string())
