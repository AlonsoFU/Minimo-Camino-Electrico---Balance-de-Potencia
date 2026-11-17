"""Corre TODAS las pruebas de datos para un criterio y registra cada recálculo en SQLite.
Uso: python registro.py <clave>  con clave en: tt_x, tt_z, sub_x, sub_z.  Reanudable por etapa."""
import sys, sqlite3, time, json, random, datetime
exec(open('dec_criterios.py').read().split("CR = {")[0])
exec('cdf ='+open('banco.py').read().split('cdf =',1)[1].split('rows = []')[0])
from itertools import combinations
CRIT = {'tt_x': ('Referido + trafo troncal, X', m3, 'X'), 'tt_z': ('Referido + trafo troncal, |Z|', m3, 'Z'),
        'sub_x': ('Referido + misma subestación, X', m1, 'X'), 'sub_z': ('Referido + misma subestación, |Z|', m1, 'Z')}
clave = sys.argv[1]; NOMBRE, AN, MODO = CRIT[clave]
DB = OUT + f'registro_{clave}.sqlite'; con = sqlite3.connect(DB)
con.executescript('''CREATE TABLE IF NOT EXISTS pruebas(id INTEGER PRIMARY KEY, criterio TEXT, etapa TEXT, detalle TEXT, n_tramos INT, tramos TEXT,
  barras_cambian INT, mm_mes REAL, desde_cache INT, segundos REAL, fecha TEXT);
CREATE TABLE IF NOT EXISTS cambios(prueba_id INT, barra TEXT, troncal_base TEXT, troncal_nueva TEXT, mw REAL);
CREATE TABLE IF NOT EXISTS etapas(criterio TEXT, etapa TEXT, estado TEXT, inicio TEXT, fin TEXT, resumen TEXT);''')
hechas = {r[0] for r in con.execute("SELECT etapa FROM etapas WHERE criterio=? AND estado='ok'", (NOMBRE,))}
o0c = esc2(True, AN)
def estado_(apl):
    o = o0c.copy()
    for b in apl:
        for i in bloques[b]:
            if AN.loc[i]: continue
            o.loc[i, 'X'] = xsug[i]; o.loc[i, 'R'] = rs[i] * ref.loc[i]
    return asignar(pesos_z(o, MODO))
base = estado_([]); CACHE = {}
src = lambda b: b if b in coord else R0.loc[b, 'nodo']
def prueba(etapa, detalle, tramos):
    k = frozenset(tramos); t0 = time.time(); cache = k in CACHE
    if not cache:
        s = estado_(sorted(k)); ch = s[s != base.reindex(s.index)]
        mwc = S.mw.reindex(ch.index).fillna(0); mm = float(((ch.map(precio) - base.reindex(ch.index).map(precio)).abs() * mwc / 1000).sum())
        CACHE[k] = (ch, mm)
    ch, mm = CACHE[k]
    cur = con.execute('INSERT INTO pruebas(criterio,etapa,detalle,n_tramos,tramos,barras_cambian,mm_mes,desde_cache,segundos,fecha) VALUES(?,?,?,?,?,?,?,?,?,?)',
                      (NOMBRE, etapa, detalle, len(k), ' + '.join(sorted(k)), len(ch), round(mm, 3), int(cache), round(time.time() - t0, 3), datetime.datetime.now().isoformat(timespec='seconds')))
    if not cache and len(ch):
        con.executemany('INSERT INTO cambios VALUES(?,?,?,?,?)', [(cur.lastrowid, b, base[b], ch[b], float(S.mw.get(b, 0))) for b in ch.index])
    return ch, mm
def etapa(nombre, fn):
    if nombre in hechas: print(nombre, 'ya hecha', flush=True); return json.loads(con.execute("SELECT resumen FROM etapas WHERE criterio=? AND etapa=? AND estado='ok'", (NOMBRE, nombre)).fetchone()[0])
    con.execute('DELETE FROM pruebas WHERE criterio=? AND etapa=?', (NOMBRE, nombre)); ini = datetime.datetime.now().isoformat(timespec='seconds')
    res = fn(); con.execute('INSERT INTO etapas VALUES(?,?,?,?,?,?)', (NOMBRE, nombre, 'ok', ini, datetime.datetime.now().isoformat(timespec='seconds'), json.dumps(res, ensure_ascii=False)))
    con.commit(); print(nombre, res if len(json.dumps(res)) < 400 else '(ok)', flush=True); return res
candb = [b for b in bloques if not all(AN.loc[i] for i in bloques[b])]
# 1. individual
def f_ind():
    out = {}
    for b in candb:
        ch, mm = prueba('1 individual', 'tramo solo', [b])
        if len(ch): out[b] = [len(ch), round(mm, 1)]
    con.commit(); return out
DEC = etapa('1 individual', f_ind); dec = sorted(DEC)
# 2. conjuntos
def f_conj():
    a = prueba('2 conjuntos', 'decisivos juntos', dec); b_ = prueba('2 conjuntos', 'todos juntos', candb)
    return {'decisivos': len(dec), 'decisivos_juntos': [len(a[0]), round(a[1], 1)], 'todos_juntos': [len(b_[0]), round(b_[1], 1)]}
etapa('2 conjuntos', f_conj)
# 3. grupos (4 agrupaciones) sobre no decisivos
nod = [b for b in candb if b not in DEC]
def lat(b):
    i = bloques[b][0]
    for n in (nm[int(oper.loc[i, 'Barra A'])], nm[int(oper.loc[i, 'Barra B'])]):
        if n in coord: return coord[n][0]
    return 0.0
Gb = nx.Graph()
for (u, v), x in pesos_z(o0c, MODO).items():
    if x > 0: Gb.add_edge(nm[u], nm[v], w=float(x))
DT = {t: nx.single_source_dijkstra_path_length(Gb, t, weight='w') for t in TRONC if t in Gb}
def tron(b):
    n = nm[int(oper.loc[bloques[b][0], 'Barra A'])]; return min((DT[t].get(n, 1e9), t) for t in DT)[1]
def ddmin(g, pred):
    n = 2
    while len(g) >= 2:
        k = max(1, len(g) // n); partes = [g[i:i + k] for i in range(0, len(g), k)]; red = False
        for p in partes:
            if pred(p): g, n, red = p, 2, True; break
        if not red:
            for p in partes:
                comp = [x for x in g if x not in p]
                if comp and pred(comp): g, n, red = comp, max(n - 1, 2), True; break
        if not red:
            if n >= len(g): break
            n = min(len(g), 2 * n)
    return g
def f_grupos():
    r1 = random.Random(1); a1 = nod[:]; r1.shuffle(a1); r2 = random.Random(2); a2 = nod[:]; r2.shuffle(a2)
    AG = {'latitud-40': (sorted(nod, key=lat), 40), 'troncal-40': (sorted(nod, key=lambda b: (tron(b), lat(b))), 40), 'azar1-40': (a1, 40), 'azar2-20': (a2, 20)}
    comb = {}
    for ag, (orden, tam) in AG.items():
        zonas = [orden[i:i + tam] for i in range(0, len(orden), tam)] + [None]; hall = []
        for zi, z in enumerate(zonas):
            det = f'{ag} zona {zi + 1}' if z is not None else f'{ag} entre zonas'
            resto = list(z) if z is not None else [x for x in orden if not any(x in h for h in hall)]
            while resto and len(prueba('3 grupos', det, resto)[0]):
                m = ddmin(resto, lambda g: len(prueba('3 grupos', det + ' (búsqueda)', g)[0]) > 0); hall.append(set(m))
                comb.setdefault(' + '.join(sorted(m)), []).append(ag); resto = [x for x in resto if x not in m]
        con.commit()
    return comb
COMB = etapa('3 grupos', f_grupos)
# 4. zonas: decisivos + combinaciones + vecinos que difieren a 2 saltos; pruebas decisivo+vecinos
ends = {b: {nm[int(oper.loc[i, 'Barra A'])] for i in bloques[b]} | {nm[int(oper.loc[i, 'Barra B'])] for i in bloques[b]} for b in candb}
Gt = nx.Graph()
for (u, v) in pesos_z(o0c, MODO).index: Gt.add_edge(nm[u], nm[v])
semilla = set(dec) | {x for c_ in COMB for x in c_.split(' + ')}
H = nx.Graph(); H.add_nodes_from(semilla)
for b in semilla:
    n2 = ends[b] | {w for n in ends[b] if n in Gt for w in Gt[n]}
    for x in candb:
        if ends[x] & n2: H.add_edge(b, x)
ZONAS = sorted(nx.connected_components(H), key=len, reverse=True)
def f_zonas():
    SING = {}
    def sing(b):
        if b not in SING: SING[b] = frozenset(prueba('4 zonas', 'tramo solo (referencia)', [b])[0].index)
        return SING[b]
    out = []
    for zi, z in enumerate(ZONAS, 1):
        zl = sorted(z); d_ = sorted(z & set(dec)); det = f'zona {zi}'; inter = set()
        def dev(Sx, det_):
            ch = prueba('4 zonas', det_, list(Sx))[0]; return set(ch.index) != set().union(*[sing(b) for b in Sx])
        if len(zl) <= 20:
            for r in range(2, min(4, len(zl)) + 1):
                for cmb in combinations(zl, r):
                    if set(cmb) & set(dec) and dev(cmb, det + f' combinación de {r}'): inter |= set(cmb)
        else:
            for d in d_:
                for o in zl:
                    if o != d and dev((d, o), det + ' par decisivo+vecino'): inter |= {d, o}
                rest = [o for o in zl if o != d]
                while rest and dev([d] + rest, det + ' decisivo+resto'):
                    m = ddmin(rest, lambda g: dev([d] + list(g), det + ' decisivo+resto (búsqueda)')); inter |= {d} | set(m); rest = [x for x in rest if x not in m]
        a = prueba('4 zonas', det + ' solo decisivos', d_) if d_ else ([], 0); f = prueba('4 zonas', det + ' zona completa', zl)
        out.append({'zona': zi, 'tramos': len(zl), 'decisivos': len(d_), 'vecinos_que_interactuan': sorted(inter - set(dec)),
                    'mm_solo_decisivos': round(a[1], 1), 'mm_zona_completa': round(f[1], 1)})
        con.commit(); print(' zona', zi, len(zl), 'listo', flush=True)
    return out
Zres = etapa('4 zonas', f_zonas)
vec = sorted({v for z in Zres for v in z['vecinos_que_interactuan']})
con.execute('CREATE TABLE IF NOT EXISTS resumen(criterio TEXT, clave TEXT, valor TEXT)')
con.execute('DELETE FROM resumen WHERE criterio=?', (NOMBRE,))
for k_, v_ in {'tramos probados': len(candb), 'decisivos': len(dec), 'combinaciones encontradas': len(COMB), 'zonas': len(ZONAS),
               'vecinos que interactúan': len(vec), 'total a revisar': len(set(dec) | set(vec)), 'lista a revisar': ' | '.join(sorted(set(dec) | set(vec)))}.items():
    con.execute('INSERT INTO resumen VALUES(?,?,?)', (NOMBRE, k_, str(v_)))
con.commit(); print('FIN', NOMBRE, 'decisivos', len(dec), 'vecinos', len(vec), 'total', len(set(dec) | set(vec)), 'pruebas', con.execute('SELECT COUNT(*) FROM pruebas').fetchone()[0])
