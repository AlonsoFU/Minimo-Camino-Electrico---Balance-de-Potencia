exec(open('grupos.py').read().split("t0 = time.time(); TAM = 40")[0])
import json
traza = []
def cambia_log(g, etiqueta):
    ch = cambia(g); traza.append({'etapa': etiqueta, 'n': len(g), 'cambia': int(len(ch))}); return ch
zonas = [nod[i:i + 40] for i in range(0, len(nod), 40)]
zres = [int(len(cambia(z))) for z in zonas]
print('tramos', len(nod), 'zonas', len(zonas), 'con cambio', [i + 1 for i, v in enumerate(zres) if v])
H = pd.read_pickle(OUT + 'grupos.pkl'); usados = {x for h in H['Combinación'] for x in h.split(' + ')}
resto = [x for x in nod if x not in usados]
# ddmin con registro, sobre el conjunto entre zonas (donde salió Mulchén)
def ddmin_log(g):
    n = 2; paso = 0
    while len(g) >= 2:
        k = max(1, len(g) // n); partes = [g[i:i + k] for i in range(0, len(g), k)]; red = False
        for p in partes:
            paso += 1
            if len(cambia_log(p, f'{paso}: parte de {len(p)}')): g, n, red = p, 2, True; break
        if not red:
            for p in partes:
                comp = [x for x in g if x not in p]; paso += 1
                if comp and len(cambia_log(comp, f'{paso}: quito {len(p)}, quedan {len(comp)}')): g, n, red = comp, max(n - 1, 2), True; break
        if not red:
            if n >= len(g): break
            n = min(len(g), 2 * n)
    return g
print('resto entre zonas', len(resto), 'cambia', int(len(cambia(resto))))
m = ddmin_log(resto); print('mínimo:', m)
print('pruebas en la búsqueda:', len(traza)); 
T = pd.DataFrame(traza); T.to_pickle(OUT + 'traza.pkl'); print(T.to_string())
json.dump({'n_tramos': len(nod), 'zonas': len(zonas), 'zres': zres, 'resto': len(resto), 'minimo': m}, open(OUT + 'traza.json', 'w'))
