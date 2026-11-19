"""Segunda pasada sobre el núcleo: quitar cada tramo si el resultado final de la lista (4 variantes) no cambia."""
exec(open('listado_verif.py').read().split("out = {'zonas'")[0])
REV = pd.read_excel('/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/listado_tramos.xlsx', sheet_name='Revisión')
LISTA = list(REV.Tramo); FL = {v: est_f(True, *VAR[v], LISTA) for v in VAR}
igual = lambda l: all((est_f(True, *VAR[v], l).reindex(FL[v].index).fillna('') == FL[v].fillna('')).all() for v in VAR)
N = list(pd.read_pickle(OUT + 'nucleo_N.pkl')); print('N', len(N), igual(N))
cambio = True; quitados = []
while cambio:
    cambio = False
    for t in list(N):
        c = [x for x in N if x != t]
        if igual(c): N = c; quitados.append(t); cambio = True
print('quitados:', quitados, ' queda:', len(N))
# ¿es mínimo? ningún tramo se puede quitar
print('mínimo (ninguno sobra):', all(not igual([x for x in N if x != t]) for t in N))
pd.to_pickle(N, OUT + 'nucleo_N2.pkl')
