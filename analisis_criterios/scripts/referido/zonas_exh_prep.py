exec(open('grupos.py').read().split("t0 = time.time(); TAM = 40")[0])
F = pd.read_pickle(OUT + 'grupos_robusto.pkl')
ends = {b: {nm[int(oper.loc[i, 'Barra A'])] for i in bloques[b]} | {nm[int(oper.loc[i, 'Barra B'])] for i in bloques[b]} for b in bloques}
semillas = {'Las Vegas': 'SANT_SOLAR', 'Calera': 'CALERA.C', 'Chiloé': 'CHILOE', 'Puerto Varas': 'SANGRA', 'Kimal': 'CRUCEROSALAUX'}
for z, k in semillas.items():
    fila = F[F['Combinación'].str.contains(k, regex=False)]
    tr = set(x for c_ in fila['Combinación'] for x in c_.split(' + '))
    nodos = set().union(*[ends[b] for b in tr])
    vec = [b for b in bloques if ends[b] & nodos]
    print(z, 'semilla', len(tr), 'nodos', len(nodos), 'vecinos', len(vec))
