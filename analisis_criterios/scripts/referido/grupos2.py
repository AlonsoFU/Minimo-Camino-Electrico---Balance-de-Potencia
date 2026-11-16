exec(open('grupos.py').read().split("t0 = time.time(); TAM = 40")[0])
H = pd.read_pickle(OUT + 'grupos.pkl'); usados = {x for h in H['Combinación'] for x in h.split(' + ')}
resto = [x for x in nod if x not in usados]; hall = []
while True:
    ch = cambia(resto)
    if not len(ch): break
    m = ddmin(resto); chm = cambia(m); _, mm = plata(base, estado(m))
    hall.append({'Combinación': ' + '.join(m), 'Tramos': len(m), 'Barras que cambian': len(chm), 'MM$/mes': round(mm, 1), 'Barras': ', '.join(chm.index)}); print(hall[-1], flush=True)
    resto = [x for x in resto if x not in m]
print('pruebas', NT[0]); pd.DataFrame(hall).to_pickle(OUT + 'grupos2.pkl')
