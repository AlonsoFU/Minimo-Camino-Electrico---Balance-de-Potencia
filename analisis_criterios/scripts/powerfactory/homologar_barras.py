"""Homologa las barras del Balance (y las 50 troncales PNCP) con las barras del modelo PowerFactory, solo por nombre y
tensión. Entrada: exportación de terminales (ElmTerm) del Administrador de datos. Salida: una propuesta con puntaje,
para revisar a mano los casos dudosos."""
import re, unicodedata, difflib, collections
exec(open('leer_exportacion.py').read())
B = leer('a5d1a870-trm.txt'); B['kv'] = num(B['Nom.L-L Volt.'])
banco = pd.read_pickle('/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/banco.pkl')
obj = pd.DataFrame({'barra': sorted(set(banco.barra) | set(banco.PN2604.dropna()))})
obj['troncal'] = obj.barra.isin(set(banco.PN2604.dropna()))

def sin_tildes(s): return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
RUIDO = r'\b(S/E|SE|SUBESTACION|CENTRAL|C\.T\.|CT|PLANTA|SECCIONADORA|MT|BT|AT|KV|BP\d*|BB\d*|BARRA|BARRAS|TERMINAL|N°\s*\d+|NO\s*\d+|C\d|SECCION)\b'
def norm_pf(s):
    s = sin_tildes(s).upper().replace('_', ' ')
    s = re.sub(r'\(\d+\)', ' ', s); s = re.sub(r'\d+([.,]\d+)?\s*KV', ' ', s); s = re.sub(RUIDO, ' ', s)
    s = re.sub(r"[^A-Z0-9. ]", ' ', s); s = re.sub(r'\b\d+([.,]\d+)?\b', ' ', s)
    return ' '.join(s.split())
def formas_pf(n):
    """compacto completo, con iniciales para todas las palabras menos la última, y solo palabras largas"""
    w = n.replace('.', ' ').split()
    if not w: return set()
    f = {''.join(w)}
    if len(w) > 1:
        f.add(''.join(x[0] for x in w[:-1]) + w[-1]); f.add(w[0][0] + ''.join(w[1:]))
        f.add(''.join(x for x in w if x not in ('LOS', 'LAS', 'LA', 'EL', 'DE', 'DEL', 'SAN', 'SANTA', 'NUEVA', 'NUEVO', 'ALTO', 'TAP')))
    return {x for x in f if x}
def obj_forma(b):
    m = re.match(r'^(.*?)_*(\d{3})$', b)
    base, kv = (m.group(1), int(m.group(2))) if m else (re.sub(r'_+\d*_?[A-Z]?$', '', b), None)
    base = sin_tildes(base).upper().replace('_', ' ').strip()
    return base.replace('.', '').replace(' ', ''), kv
KV = {13: (13.0, 13.2, 13.8, 12.5, 13.5), 12: (12.0, 12.5), 66: (66.0, 69.0), 23: (23.0, 22.0, 24.0), 15: (15.0, 14.8), 110: (110.0,), 220: (220.0,), 154: (154.0,), 500: (500.0,),
      44: (44.0,), 33: (33.0, 34.5), 100: (100.0,), 4: (4.16,), 2: (2.4,)}
def kv_ok(k, v): return True if k is None else any(abs(v - x) < 0.05 for x in KV.get(k, (float(k),)))
MT = (12, 13, 15, 20, 23)
def kv_pen(k, v):
    if kv_ok(k, v): return 0.0
    if k in MT and 11.5 <= v <= 24.5: return 0.05          # media tensión con otro valor nominal
    return None
# candidatos: cada terminal aporta dos nombres (su carpeta y su propio nombre)
cand = collections.defaultdict(set)   # (forma, kv) -> {(carpeta, terminal)}
for f, n, v, u in zip(B['In Folder'], B.Name, B.kv, B.Usage):
    if pd.isna(v): continue
    for s in (f, n):
        for x in formas_pf(norm_pf(s)):
            if len(x) >= 3: cand[(x, round(v, 2))].add((f, n))
porkv = collections.defaultdict(list)
for (x, v), refs in cand.items(): porkv[v].append((x, refs))
def tri(s): return {s[i:i + 3] for i in range(len(s) - 2)} if len(s) > 2 else {s}
idx = {v: [(x, tri(x), refs) for x, refs in l] for v, l in porkv.items()}
rows = []
for b, tr in zip(obj.barra, obj.troncal):
    q, k = obj_forma(b); tq = tri(q); res = []
    for v, l in idx.items():
        pen = kv_pen(k, v)
        if pen is None: continue
        for x, tx, refs in l:
            j = len(tq & tx) / max(1, len(tq | tx))
            if j < 0.2 and not (len(q) >= 5 and x.startswith(q)): continue
            r = difflib.SequenceMatcher(None, q, x).ratio()
            if len(q) >= 5 and (x.startswith(q) or q.startswith(x) and len(x) >= 5): r = max(r, 0.95)   # abreviatura: A.MELIP ~ ALTOMELIPILLA no; AMELIP ~ AMELIPILLA sí
            res.append((r - pen, x, v, refs))
    res.sort(key=lambda t: -t[0])
    # agrupar por subestación (carpeta) para el segundo mejor distinto
    best = res[0] if res else None; seg = next((t for t in res[1:] if best and {f for f, _ in t[3]} != {f for f, _ in best[3]}), None)
    if best:
        carp = sorted({f for f, _ in best[3]}); term = sorted({n for _, n in best[3]})
        sc, mg = round(best[0], 3), round(best[0] - (seg[0] if seg else 0), 3)
        conf = 'Alta' if sc >= 0.95 and (mg >= 0.05 or len(carp) == 1) else ('Media' if sc >= 0.8 else 'Baja')
        rows.append({'barra_balance': b, 'troncal': tr, 'kv': k, 'forma_buscada': q, 'forma_pf': best[1], 'kv_pf': best[2], 'subestacion_pf': ' | '.join(carp[:3]),
                     'terminales_pf': ' | '.join(term[:4]), 'puntaje': sc, 'margen': mg, 'segunda_opcion': (' | '.join(sorted({f for f, _ in seg[3]})[:2]) + f' ({seg[0]:.2f})') if seg else '', 'confianza': conf})
    else:
        rows.append({'barra_balance': b, 'troncal': tr, 'kv': k, 'forma_buscada': q, 'confianza': 'Sin candidato'})
H = pd.DataFrame(rows); H.to_pickle('homologacion_pf.pkl')
print(H.confianza.value_counts().to_dict()); print('troncales:', H[H.troncal].confianza.value_counts().to_dict())
pd.set_option('display.width', 250, 'display.max_colwidth', 45)
for c in ['Alta', 'Media', 'Baja']: print('==', c); print(H[H.confianza == c][['barra_balance', 'forma_pf', 'kv_pf', 'subestacion_pf', 'puntaje', 'segunda_opcion']].sample(min(12, (H.confianza == c).sum()), random_state=1).to_string(index=False))
print(H[H.troncal][['barra_balance', 'subestacion_pf', 'terminales_pf', 'puntaje', 'confianza']].to_string(index=False))
