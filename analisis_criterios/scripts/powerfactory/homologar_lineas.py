"""Homologa las líneas del ENT (validación ENT–CNE–Infotécnica) con las líneas del modelo PowerFactory.
1) Por extremos: cada barra del ENT se busca en PowerFactory (mismo método que homologar.py) y se buscan líneas PF
   cuyos dos extremos caigan en esas subestaciones. 2) Si no, por el nombre de la línea PF ("A - B 154 kV C1")."""
import math
src = open('homologar.py').read(); exec(src[:src.index('rows = []')])
L = leer('502b0ca7-line.txt'); L['R1n'], L['X1n'], L['km'], L['par'] = num(L.R1), num(L.X1), num(L.Length), num(L['Par.no.'])
L = L[L['Out of Service'] != '1'].reset_index(drop=True)
V = pd.read_pickle('/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/validacion.pkl')
E = V[V.voltaje_a_ENT == V.voltaje_b_ENT].copy().reset_index(drop=True)
key = {(f, n): k for f, n, k in zip(B['In Folder'], B.Name, B.kv)}
unico = B.groupby('Name')['In Folder'].agg(list)
def lado(sub, term):
    if (sub, term) in key: return sub, term
    if sub == '' and term in unico.index and len(unico[term]) == 1: return unico[term][0], term
    return None
L['ai'] = [lado(a, b) for a, b in zip(L['Terminal i'], L['Terminal i [5]'])]
L['aj'] = [lado(a, b) for a, b in zip(L['Terminal j'], L['Terminal j [7]'])]
L['kv'] = [key.get(x) if x else None for x in L.ai]
def buscar(b, tope=0.04, minimo=0.85):
    """candidatos PF (carpeta, terminal) para una barra del ENT"""
    q, k = obj_forma(b); tq = tri(q); res = []
    for v, l in idx.items():
        pen = kv_pen(k, v)
        if pen is None: continue
        for x, tx, refs in l:
            j = len(tq & tx) / max(1, len(tq | tx))
            if j < 0.2 and not (len(q) >= 5 and x.startswith(q)): continue
            r = difflib.SequenceMatcher(None, q, x).ratio()
            if len(q) >= 5 and (x.startswith(q) or q.startswith(x) and len(x) >= 5): r = max(r, 0.95)
            res.append((r - pen, refs))
    if not res: return 0, set()
    m = max(r for r, _ in res)
    if m < minimo: return m, set()
    out = set()
    for r, refs in res:
        if r >= m - tope: out |= refs
    return m, out
barrasE = sorted(set(E.barra_a) | set(E.barra_b)); C = {b: buscar(b) for b in barrasE}
GRIDS = set(B.Grid)
def es_sub(f):
    return not (f in GRIDS or re.match(r'^\d{2}-', f) or ' - ' in f or '–' in f or f.endswith('-MT') or f.startswith(('110 kV', '220 kV', '66 kV', '154 kV', '500 kV')))
# índice de líneas PF por subestación y por (carpeta, terminal)
por = collections.defaultdict(set)
for i, (ai, aj) in enumerate(zip(L.ai, L.aj)):
    for x in (ai, aj):
        if x:
            por[x].add(i)
            if es_sub(x[0]): por[x[0]].add(i)
def lineas_de(cands):
    s = set()
    for f, n in cands: s |= por.get((f, n), set()) | (por.get(f, set()) if es_sub(f) else set())
    return s
def toca(i, cands):
    fs = {f for f, _ in cands if es_sub(f)}
    return [x for x in (L.ai[i], L.aj[i]) if x and (x in cands or x[0] in fs)]
# por nombre: "A - B 154 kV C1"
def extremos_nombre(n):
    n = sin_tildes(n).upper(); n = re.sub(r'\b(C|L)\s*\d\b|\bCIRCUITO\b.*$', ' ', n)
    p = re.split(r'\s+-\s+|\s+–\s+| - |–', n)
    return [norm_pf(x) for x in p[:2]] if len(p) >= 2 else []
L['ext'] = L.Name.map(extremos_nombre)
def sim_nombre(b, ext):
    q, _ = obj_forma(b); return max([difflib.SequenceMatcher(None, q, f).ratio() for e in ext for f in formas_pf(e)] or [0])
rows = []
for r in E.itertuples():
    sa, ca = C[r.barra_a]; sb, cb = C[r.barra_b]; met = ''; cand = []
    if ca and cb:
        comunes = lineas_de(ca) & lineas_de(cb)
        cand = [i for i in comunes if toca(i, ca) and toca(i, cb) and (L.ai[i] != L.aj[i]) and abs((L.kv[i] or 0) - r.voltaje_a_ENT) < 25]
        met = 'extremos'
    if not cand:
        sc = [(min(sim_nombre(r.barra_a, [e]) for e in L.ext[i][:1]) if False else 0, i) for i in []]
        best = []
        for i, ext in enumerate(L.ext):
            if len(ext) < 2 or L.kv[i] is None or abs(L.kv[i] - r.voltaje_a_ENT) > 25: continue
            s1 = min(sim_nombre(r.barra_a, [ext[0]]), sim_nombre(r.barra_b, [ext[1]])); s2 = min(sim_nombre(r.barra_a, [ext[1]]), sim_nombre(r.barra_b, [ext[0]]))
            s = max(s1, s2)
            if s >= 0.85: best.append((s, i))
        if best:
            m = max(s for s, _ in best); cand = [i for s, i in best if s >= m - 0.02]; met = 'nombre'
    if cand:
        xe = r.X_ENT
        m_ = re.search(r'_(\d)de\d$', r.nombre_ENT); kc = m_.group(1) if m_ else None
        def clave(i):
            ext = L.ext[i]; sn = max(min(sim_nombre(r.barra_a, [ext[0]]), sim_nombre(r.barra_b, [ext[1]])), min(sim_nombre(r.barra_a, [ext[1]]), sim_nombre(r.barra_b, [ext[0]]))) if len(ext) >= 2 else 0
            circ = 0 if kc and re.search(rf'\b[CL]\s*{kc}\b|\({kc}\)|C{kc}$', L.Name[i]) else 1
            return (-round(sn, 2), circ)       # primero el nombre, después el número de circuito; nunca la X
        i = min(cand, key=clave); sn = -clave(i)[0]
        xs = r.valor_sugerido
        rows.append({'nombre_ENT': r.nombre_ENT, 'kv': r.voltaje_a_ENT, 'X_ENT': xe, 'X_CNE': r.X_CNE, 'X_Infotec': r.X_Infotec, 'X_sugerida': xs, 'clasificacion': r.clasificacion_validacion,
                     'linea_PF': L.Name[i], 'X1_PF': L.X1n[i], 'R1_PF': L.R1n[i], 'km_PF': L.km[i], 'par_PF': L.par[i], 'candidatos_PF': len(cand), 'metodo': met, 'similitud_nombre': sn,
                     'otras_PF': ' | '.join(sorted({L.Name[j] for j in cand if j != i}))[:200]})
    else:
        rows.append({'nombre_ENT': r.nombre_ENT, 'kv': r.voltaje_a_ENT, 'X_ENT': r.X_ENT, 'X_CNE': r.X_CNE, 'X_Infotec': r.X_Infotec, 'X_sugerida': r.valor_sugerido,
                     'clasificacion': r.clasificacion_validacion, 'metodo': 'sin pareo', 'falta': ('a ' if not ca else '') + ('b' if not cb else '')})
H = pd.DataFrame(rows); H.to_pickle('homologacion_lineas_pf.pkl')
print(H.metodo.value_counts().to_dict())
ok = H[H.metodo != 'sin pareo']
def cerca(a, b): return (a > 0) & (b > 0) & ((a / b).between(1 / 1.2, 1.2))
print('PF coincide (±20 %) con ENT:', cerca(ok.X1_PF, ok.X_ENT).sum(), ' con CNE:', cerca(ok.X1_PF, ok.X_CNE).sum(), ' con Infotec:', cerca(ok.X1_PF, ok.X_Infotec).sum(), ' con la sugerida:', cerca(ok.X1_PF, ok.X_sugerida).sum(), ' de', len(ok))
print('PF lejos de todas (ninguna ±20 %):', (~(cerca(ok.X1_PF, ok.X_ENT) | cerca(ok.X1_PF, ok.X_CNE) | cerca(ok.X1_PF, ok.X_Infotec))).sum())
pd.set_option('display.width', 250, 'display.max_colwidth', 45)
print(ok.sample(20, random_state=4)[['nombre_ENT', 'linea_PF', 'X_ENT', 'X_CNE', 'X_Infotec', 'X1_PF', 'candidatos_PF', 'metodo']].to_string(index=False))
