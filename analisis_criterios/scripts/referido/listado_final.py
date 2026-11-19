"""Listado final de tramos a revisar: zonas definitivas (interacción por pares > 1 MM$/mes en alguna de las 4 variantes),
efecto de cada zona, verificación de independencia, avance por ronda y hoja de revisión para llenar."""
exec(open('listado_verif.py').read().split("out = {'zonas'")[0])
PR = pd.read_pickle(OUT + 'listado_pares.pkl'); LOO = pd.read_pickle(OUT + 'listado_verif.pkl')['loo']
UNIp = PR['UNI']
# ---- zonas definitivas
renom = {'grupo 3': 'Melipilla–Isla de Maipo', 'grupo 4': 'Atacama (Cardones–Maitencillo–D.Almagro)', 'grupo 9': 'Dichas 220',
         'grupo 2': 'Aconcagua (Calera–S.Rafael)', 'grupo 10': 'Codegua 66', 'grupo 8': 'El Laurel 220', 'grupo 1': 'Kimal',
         'grupo 5': 'Maule–Itahue–Teno–Linares', 'grupo 7': 'Maule–Itahue–Teno–Linares', 'grupo 6': 'Santiago oriente', 'Mulchén': 'Mulchén'}
zona_prev = dict(zip(Lst.Tramo, Lst.Zona))
Zf = {}
for u, l in UNIp.items():
    for t in l: Zf[t] = renom.get(u, zona_prev[t] if zona_prev[t] in ('Ventanas', 'Maule–Itahue–Teno–Linares', 'Santiago oriente') else 'Independiente')
union = {}
for a, b, r in PR['I']:
    if max(m for _, _, m in r) > 1:
        za = {Zf[t] for t in UNIp[a]}; zb = {Zf[t] for t in UNIp[b]}
        union.setdefault(frozenset([a, b]), r)
# fusiones con interacción > 1 MM$/mes (pares del archivo listado_pares.pkl)
fus = {'S.FERNANDO____154->S.FERNANDO____066': 'Maule–Itahue–Teno–Linares', 'RENCA_________110->T_ALTAMIRANO__110': 'Santiago oriente',
       'TAPS.RAFAEL___110->TOTORALILLO___110': 'Aconcagua (Calera–S.Rafael)', 'S.RAFAEL______110->S.RAFAEL______013': 'Aconcagua (Calera–S.Rafael)'}
Zf.update(fus)
for k, r in union.items():
    zs = {Zf[t] for u in k for t in UNIp[u]}
    if len(zs) > 1: print('ATENCIÓN fusión no aplicada:', [u for u in k], zs, r)
Lst['Zona'] = Lst.Tramo.map(Zf)
ORD = {'Ventanas': 1, 'Maule–Itahue–Teno–Linares': 2, 'Santiago oriente': 3, 'Mulchén': 3, 'Melipilla–Isla de Maipo': 4,
       'Atacama (Cardones–Maitencillo–D.Almagro)': 4, 'Dichas 220': 4, 'Aconcagua (Calera–S.Rafael)': 4, 'Kimal': 5, 'Codegua 66': 6, 'El Laurel 220': 6}
mm0 = dict(zip(Lst.Tramo, pd.to_numeric(Lst['MM$/mes (solo, promedio)'], errors='coerce').fillna(0)))
Lst['Orden'] = [ORD.get(z, 4 if mm0[t] > 2 else 6) for z, t in zip(Lst.Zona, Lst.Tramo)]
Lst['Crítico / vecino'] = ['Combinado (solo mueve en conjunto)' if z == 'Mulchén' else c for z, c in zip(Lst.Zona, Lst['Crítico / vecino'])]
nz = Lst.Zona.value_counts()
Lst['Se puede corregir solo'] = ['Sí' if z == 'Independiente' else f'No: con su zona ({nz[z]} tramos)' for z in Lst.Zona]
# ---- efecto por zona, independencia y rondas (4 variantes)
LISTA = list(Lst.Tramo); ZON = {z: list(g.Tramo) for z, g in Lst[Lst.Zona != 'Independiente'].groupby('Zona', sort=False)}
for t in Lst[Lst.Zona == 'Independiente'].Tramo: ZON[t] = [t]
zord = sorted(ZON, key=lambda z: (Lst.set_index('Tramo').loc[ZON[z][0], 'Orden'], -sum(mm0[t] for t in ZON[z])))
rz, rv, rr = [], [], []
for v, (an, modo) in VAR.items():
    e = lambda l: est_f(True, an, modo, l)
    M, FL, FT = e([]), e(LISTA), e(todos)
    for z in zord:
        l = ZON[z]; s = dif(e(l), M); mg = dif(FL, e([t for t in LISTA if t not in l])); d = desv(s['mapa'], mg['mapa'], M)
        rz.append({'Variante': v, 'Zona': z, 'Tramos': len(l), 'Barras que cambian': s['barras'], 'Más cerca': s['cerca'], 'Más lejos': s['lejos'], 'Δ km promedio': s['km'],
                   'MM$/mes': s['mm'], 'MM$ sube': s['sube'], 'MM$ baja': s['baja']})
        rv.append({'Variante': v, 'Zona': z, 'Sola: barras': s['barras'], 'Sola: MM$': s['mm'], 'En la lista: barras': mg['barras'], 'En la lista: MM$': mg['mm'], 'Difieren: barras': d[0], 'Difieren: MM$': d[1]})
    for nom, l in [('Lista completa', LISTA), ('Todos (668)', todos)]:
        s = dif(e(l), M); rz.append({'Variante': v, 'Zona': nom, 'Tramos': len(l), 'Barras que cambian': s['barras'], 'Más cerca': s['cerca'], 'Más lejos': s['lejos'],
                                     'Δ km promedio': s['km'], 'MM$/mes': s['mm'], 'MM$ sube': s['sube'], 'MM$ baja': s['baja']})
    d = dif(FL, FT); rv.append({'Variante': v, 'Zona': 'Lista completa contra los 668', 'Difieren: barras': d['barras'], 'Difieren: MM$': d['mm']})
    ac = []; prev = M; p0 = dif(M, P)
    rr.append({'Variante': v, 'Ronda': 0, 'Tramos acumulados': 0, 'Barras que cambian (acum.)': 0, 'MM$/mes (acum.)': 0, 'Mueve la ronda: barras': 0, 'Mueve la ronda: MM$': 0,
               'Falta para el final: barras': dif(M, FL)['barras'], 'Falta para el final: MM$': dif(M, FL)['mm'], 'Distintas a PN2604': p0['barras'], 'MM$/mes vs PN2604': p0['mm']})
    for r in sorted(Lst.Orden.unique()):
        ac += list(Lst[Lst.Orden == r].Tramo); a = e(ac); s = dif(a, M); g = dif(a, prev); prev = a; f = dif(a, FL); p = dif(a, P)
        rr.append({'Variante': v, 'Ronda': int(r), 'Tramos acumulados': len(ac), 'Barras que cambian (acum.)': s['barras'], 'Más cerca (acum.)': s['cerca'], 'Más lejos (acum.)': s['lejos'],
                   'MM$/mes (acum.)': s['mm'], 'Mueve la ronda: barras': g['barras'], 'Mueve la ronda: MM$': g['mm'], 'Falta para el final: barras': f['barras'],
                   'Falta para el final: MM$': f['mm'], 'Distintas a PN2604': p['barras'], 'MM$/mes vs PN2604': p['mm']})
    print(v, 'ok', flush=True)
RZ, RV, RR = pd.DataFrame(rz), pd.DataFrame(rv), pd.DataFrame(rr)
lo = LOO.groupby('Tramo').agg(b=('lista barras', 'max'), m=('lista mm', 'max'))
Lst['Si se omite: barras (máx. 4 variantes)'] = Lst.Tramo.map(lo.b); Lst['Si se omite: MM$/mes (máx. 4 variantes)'] = Lst.Tramo.map(lo.m)
Lst = Lst.sort_values(['Orden', 'Zona', 'Crítico / vecino', 'MM$/mes (solo, promedio)'], ascending=[True, True, True, False], key=lambda s: s.map({z: i for i, z in enumerate(zord)}) if s.name == 'Zona' else s)
pd.to_pickle({'Lst': Lst, 'RZ': RZ, 'RV': RV, 'RR': RR, 'zord': zord}, OUT + 'listado_final.pkl')
pd.set_option('display.width', 260, 'display.max_rows', 300)
print(RZ[~RZ.Zona.isin([t for t in ZON if len(ZON[t]) == 1])].to_string(index=False)); print(RV[RV['Difieren: barras'].fillna(0) > 0].to_string(index=False)); print(RR.to_string(index=False))
print(Lst.groupby(['Orden', 'Zona'], sort=False).size().to_string())
