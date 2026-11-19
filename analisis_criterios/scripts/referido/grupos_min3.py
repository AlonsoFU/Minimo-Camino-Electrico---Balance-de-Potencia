"""Grupos mínimos dentro de cada zona (4 variantes). Una partición de los imprescindibles de la zona en grupos es válida
si, para cualquier unión de grupos, corregirla da exactamente la superposición de los efectos de cada grupo por
separado (mismas barras, misma troncal) y ninguna barra queda en una troncal distinta de la base y del final.
Así cada grupo muestra su efecto real solo, en cualquier orden. Se parte de grupos de un tramo y se fusiona la
menor unión que no cumple, hasta que todas cumplen."""
import itertools, multiprocessing as mp
exec(open('listado_verif.py').read().split("out = {'zonas'")[0])
N = set(pd.read_pickle(OUT + 'nucleo_N2.pkl'))
REV = pd.read_excel('/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/listado_tramos.xlsx', sheet_name='Revisión')
ZT = {z: list(g.Tramo) for z, g in REV[REV.Zona != 'Independiente'].groupby('Zona', sort=False)}
BASE = {v: est_f(True, *VAR[v], []) for v in VAR}
def mapa(l):
    o = {}
    for v in VAR:
        a = est_f(True, *VAR[v], list(l)); M = BASE[v]; o[v] = {k: x for k, x in a.items() if x != M.get(k)}
    return o
def job(args): z, c = args; return z, c, mapa(c)
if __name__ == '__main__':
    tareas = [(z, c) for z, l in ZT.items() for k in range(1, len([t for t in l if t in N]) + 1) for c in itertools.combinations([t for t in l if t in N], k)]
    tareas += [(z, tuple(l)) for z, l in ZT.items()]
    MP = pd.read_pickle(OUT + 'grupos_mapas.pkl')   # mapas de todas las combinaciones del núcleo anterior (contiene al nuevo)
    falta = [(z, c) for z, c in tareas if (z, frozenset(c)) not in MP]
    with mp.Pool(4) as p: RES = p.map(job, falta, chunksize=8)
    MP.update({(z, frozenset(c)): m for z, c, m in RES}); print('calculadas nuevas:', len(falta))
    FZ = {z: MP[(z, frozenset(l))] for z, l in ZT.items()}
    out = {}
    for z, l in ZT.items():
        I = [t for t in l if t in N]
        if not I: out[z] = []; continue
        F = FZ[z]
        def cumple(bl):
            U = frozenset().union(*bl); m = MP[(z, U)]
            for v in VAR:
                sup = {}
                for b in bl: sup.update(MP[(z, frozenset(b))][v])
                if m[v] != sup: return False
                if any(F[v].get(k) != x for k, x in m[v].items()): return False
            return True
        B = [frozenset([t]) for t in I]
        while True:
            malo = None
            for k in range(1, len(B) + 1):
                for u in itertools.combinations(B, k):
                    if not cumple(u): malo = u; break
                if malo: break
            if not malo: break
            if len(malo) == 1:
                # el grupo solo deja barras mal: unirlo con el menor conjunto de otros grupos que lo deje bien
                otros = [b for b in B if b != malo[0]]
                for k in range(1, len(otros) + 1):
                    hit = next((u for u in itertools.combinations(otros, k) if cumple((frozenset().union(malo[0], *u),))), None)
                    if hit: malo = (malo[0],) + hit; break
            B = [b for b in B if b not in malo] + [frozenset().union(*malo)]
        B = sorted(B, key=lambda b: min(I.index(t) for t in b)); out[z] = [sorted(b, key=I.index) for b in B]
        # efecto de cada grupo solo (rango 4 variantes)
        print(f'{z}: {len(I)} imprescindibles -> {len(B)} grupos')
        for b in out[z]:
            m = MP[(z, frozenset(b))]; print('    ', ' + '.join(b), '| barras', [len(m[v]) for v in VAR])
    pd.to_pickle({'grupos': out, 'MP': MP, 'FZ': FZ}, OUT + 'grupos_min2.pkl')
