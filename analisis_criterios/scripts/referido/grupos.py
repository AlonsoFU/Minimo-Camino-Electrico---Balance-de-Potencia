"""Prueba por grupos: ¿combinaciones de tramos NO decisivos cambian la asignación? («Referido + trafo troncal», X)."""
exec(open('cadena.py').read().split("base = estado([])")[0])
exec('cdf ='+open('banco.py').read().split('cdf =',1)[1].split('rows = []')[0])
import time
c = pd.read_pickle(OUT + 'cadena.pkl'); base = c['base']
nod = [b for b in c['bloques'] if b not in c['dec']]
def lat(b):
    i = bloques[b][0]
    for n in (nm[int(oper.loc[i, 'Barra A'])], nm[int(oper.loc[i, 'Barra B'])]):
        if n in coord: return coord[n][0]
    return 0.0
nod = sorted(nod, key=lat)
NT = [0]
def cambia(g):
    NT[0] += 1; s = estado(list(g)); ch = s[s != base.reindex(s.index)]; return ch
def ddmin(g):
    """Subconjunto mínimo de g que todavía produce cambio (Zeller)."""
    n = 2
    while len(g) >= 2:
        k = max(1, len(g) // n); partes = [g[i:i + k] for i in range(0, len(g), k)]; red = False
        for p in partes:
            if len(cambia(p)): g, n, red = p, 2, True; break
        if not red:
            for p in partes:
                comp = [x for x in g if x not in p]
                if comp and len(cambia(comp)): g, n, red = comp, max(n - 1, 2), True; break
        if not red:
            if n >= len(g): break
            n = min(len(g), 2 * n)
    return g
t0 = time.time(); TAM = 40
zonas = [nod[i:i + TAM] for i in range(0, len(nod), TAM)]
hall = []
for zi, z in enumerate(zonas):
    resto = list(z)
    while True:
        ch = cambia(resto)
        if not len(ch): break
        m = ddmin(resto); chm = cambia(m); _, mm = plata(base, estado(m))
        hall.append({'Zona': zi + 1, 'Combinación': ' + '.join(m), 'Tramos': len(m), 'Barras que cambian': len(chm), 'MM$/mes': round(mm, 1)})
        print(hall[-1], flush=True)
        resto = [x for x in resto if x not in m]
print(f'zonas: {len(zonas)}  pruebas: {NT[0]}  tiempo: {time.time()-t0:.0f} s')
# interacciones entre zonas: todo lo que queda junto
quedan = [x for x in nod if not any(x in h['Combinación'].split(' + ') for h in hall)]
chq = cambia(quedan); print('Todos los restantes juntos (entre zonas): barras que cambian', len(chq))
H = pd.DataFrame(hall); H.to_pickle(OUT + 'grupos.pkl'); print(H.to_string(index=False))
