"""Verificación del listado de tramos: efecto por zona con los tramos del listado, independencia entre zonas y
unidades, avance acumulado por ronda, y qué pasa si se omite cada tramo. 4 variantes del método nuevo."""
import re
exec(open('zonas_pct.py').read().split("out = []")[0])
XL = 'listado_v1.xlsx'
Lst = pd.read_excel(XL, sheet_name='Listado')
LISTA = list(Lst.Tramo); todos = list(bloques)
P = PNa.reindex(B.index)
VAR = {'TT-X': (m3, 'X'), 'TT-R': (m3, 'Z'), 'MS-X': (m1, 'X'), 'MS-R': (m1, 'Z')}
gr = Lst['Se puede corregir solo'].str.extract(r'grupo (\d+)')[0]
Lst['unidad'] = [f'grupo {g}' if isinstance(g, str) else ('Mulchén' if z == 'Mulchén' else t) for g, z, t in zip(gr, Lst.Zona, Lst.Tramo)]
ZON = {z: list(g.Tramo) for z, g in Lst[Lst.Zona != 'Independiente'].groupby('Zona', sort=False)}
ZON['Independientes de más de 2 MM$/mes'] = list(Lst[(Lst.Zona == 'Independiente') & (Lst.Orden == 4)].Tramo)
ZON['Independientes chicos'] = list(Lst[(Lst.Zona == 'Independiente') & (Lst.Orden == 6)].Tramo)
UNI = {u: list(g.Tramo) for u, g in Lst.groupby('unidad', sort=False)}
RON = {r: list(g.Tramo) for r, g in Lst.groupby('Orden')}
mwS = S.mw
def dif(a, b):
    """barras donde a difiere de b (b = referencia) -> métricas"""
    ch = a[a != b.reindex(a.index)]; ch = ch[b.reindex(ch.index).notna()]
    if not len(ch): return {'barras': 0, 'cerca': 0, 'lejos': 0, 'km': None, 'mm': 0.0, 'sube': 0.0, 'baja': 0.0, 'mapa': {}}
    dk = pd.Series({x: km(src(x), ch[x]) - km(src(x), b[x]) for x in ch.index}, dtype=float)
    dp = (ch.map(precio) - b.reindex(ch.index).map(precio)) * mwS.reindex(ch.index).fillna(0) / 1000
    return {'barras': len(ch), 'cerca': int((dk < -5).sum()), 'lejos': int((dk > 5).sum()), 'km': round(float(dk.mean()), 1) if dk.notna().any() else None,
            'mm': round(float(dp.abs().sum()), 1), 'sube': round(float(dp[dp > 0].sum()), 1), 'baja': round(float(dp[dp < 0].sum()), 1), 'mapa': dict(ch)}
def desv(m1_, m2_, base):
    """MM$ y barras en que dos mapas de cambio difieren"""
    ks = [k for k in set(m1_) | set(m2_) if m1_.get(k) != m2_.get(k)]
    mm = sum(abs(precio.get(m1_.get(k, base[k]), 0) - precio.get(m2_.get(k, base[k]), 0)) * float(mwS.get(k, 0) or 0) / 1000 for k in ks)
    return len(ks), round(mm, 1)
out = {'zonas': [], 'indep_zonas': [], 'unidades': [], 'rondas': [], 'loo': [], 'criticos': []}
for v, (an, modo) in VAR.items():
    e = lambda l: est_f(True, an, modo, l)
    M, FL, FT = e([]), e(LISTA), e(todos)
    mFL = dif(FL, M)
    # 1-2 zonas: sola, y marginal dentro de la lista completa y de los 668
    for z, l in ZON.items():
        s = dif(e(l), M); mg = dif(FL, e([t for t in LISTA if t not in l])); mgT = dif(FT, e([t for t in todos if t not in l]))
        out['zonas'].append({'var': v, 'Zona': z, 'tramos': len(l), **{k: s[k] for k in ['barras', 'cerca', 'lejos', 'km', 'mm', 'sube', 'baja']}})
        d1 = desv(s['mapa'], mg['mapa'], M); d2 = desv(s['mapa'], mgT['mapa'], M)
        out['indep_zonas'].append({'var': v, 'Zona': z, 'sola barras': s['barras'], 'sola mm': s['mm'], 'marginal en lista barras': mg['barras'], 'marginal en lista mm': mg['mm'],
                                   'difieren barras': d1[0], 'difieren mm': d1[1], 'marginal en 668 barras': mgT['barras'], 'marginal en 668 mm': mgT['mm'], 'difieren 668 barras': d2[0], 'difieren 668 mm': d2[1]})
    for nom, l in [('Lista completa', LISTA), ('Todos (668)', todos)]:
        s = dif(e(l), M); out['zonas'].append({'var': v, 'Zona': nom, 'tramos': len(l), **{k: s[k] for k in ['barras', 'cerca', 'lejos', 'km', 'mm', 'sube', 'baja']}})
    # 3 unidades (grupos e independientes): sola vs marginal en la lista
    for u, l in UNI.items():
        s = dif(e(l), M); mg = dif(FL, e([t for t in LISTA if t not in l])); d = desv(s['mapa'], mg['mapa'], M)
        out['unidades'].append({'var': v, 'unidad': u, 'tramos': len(l), 'sola barras': s['barras'], 'sola mm': s['mm'], 'marginal barras': mg['barras'], 'marginal mm': mg['mm'], 'difieren barras': d[0], 'difieren mm': d[1]})
    # 4 acumulado por ronda
    ac = []; prev = M
    for r in sorted(RON):
        ac += RON[r]; a = e(ac); s = dif(a, M); p = dif(a, P); mg = dif(a, prev); prev = a
        out['rondas'].append({'var': v, 'ronda': r, 'tramos acum': len(ac), 'barras': s['barras'], 'cerca': s['cerca'], 'lejos': s['lejos'], 'km': s['km'], 'mm': s['mm'],
                              'ronda barras': mg['barras'], 'ronda mm': mg['mm'], 'dist PN': p['barras'], 'mm PN': p['mm'], 'faltan vs lista barras': dif(a, FL)['barras'], 'faltan vs lista mm': dif(a, FL)['mm']})
    p0 = dif(M, P); out['rondas'].append({'var': v, 'ronda': 0, 'tramos acum': 0, 'barras': 0, 'mm': 0, 'dist PN': p0['barras'], 'mm PN': p0['mm'], 'faltan vs lista barras': mFL['barras'], 'faltan vs lista mm': mFL['mm']})
    # 5 omitir cada tramo: dentro de su zona y dentro de la lista
    zona_t = {t: z for z, l in ZON.items() for t in l}
    Zres = {z: e(l) for z, l in ZON.items()}
    for t in LISTA:
        z = zona_t[t]; a = dif(e([x for x in ZON[z] if x != t]), Zres[z]); b = dif(e([x for x in LISTA if x != t]), FL)
        out['loo'].append({'var': v, 'Tramo': t, 'zona barras': a['barras'], 'zona mm': a['mm'], 'lista barras': b['barras'], 'lista mm': b['mm']})
    # 6 solo críticos de la zona
    for z, l in ZON.items():
        cr = [t for t in l if Lst.set_index('Tramo').loc[t, 'Crítico / vecino'].startswith('Crítico')]
        a = dif(e(cr), Zres[z]); out['criticos'].append({'var': v, 'Zona': z, 'críticos': len(cr), 'vecinos': len(l) - len(cr), 'difieren barras': a['barras'], 'difieren mm': a['mm']})
    print(v, 'ok', flush=True)
R = {k: pd.DataFrame(x) for k, x in out.items()}; pd.to_pickle(R, OUT + 'listado_verif.pkl')
pd.set_option('display.width', 260, 'display.max_rows', 400, 'display.max_columns', 30)
for k in ['zonas', 'indep_zonas', 'rondas', 'criticos']: print('==', k); print(R[k].to_string(index=False))
u = R['unidades']; print('== unidades con diferencia'); print(u[(u['difieren barras'] > 0)].to_string(index=False))
