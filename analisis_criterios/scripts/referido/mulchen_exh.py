exec(open('grupos.py').read().split("t0 = time.time(); TAM = 40")[0])
from itertools import combinations
cl = [b for b in nod if any(k in b for k in ['LOS_NOTROS', 'MULCHEN', 'SANTACLARA', 'CHARRUA_______220', 'SANTA_CLARA', 'LOS_OLMOS', 'PICOLTUE'])]
print('tramos de la zona:', len(cl)); print(cl)
res = []
for k in range(1, min(4, len(cl)) + 1):
    for cmb in combinations(cl, k):
        ch = cambia(list(cmb))
        if len(ch):
            _, mm = plata(base, estado(list(cmb))); res.append((k, cmb, len(ch), round(mm, 1)))
print('recálculos', NT[0])
for k, cmb, n, mm in sorted(res, key=lambda r: (-r[3], r[0]))[:15]: print(k, n, mm, ' + '.join(cmb))
