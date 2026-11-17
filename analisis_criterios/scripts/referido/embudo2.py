exec(open('embudo.py').read().split("en_parte, pasa = set(), set()")[0])
E = pd.read_pickle(OUT + 'embudo.pkl'); falt = dec - E['pasa']
baja = {b for b in bloques if all(xsug[i] < o0.loc[i, 'X'] for i in bloques[b])}
sube = {b for b in bloques if all(xsug[i] > o0.loc[i, 'X'] for i in bloques[b])}
print('de los 31 no captados: bajan X', len(falt & baja), ' suben X', len(falt & sube), ' en parte decisiva', len(falt & E['en_parte']))
print('de los 668: bajan', len(baja), 'suben', len(sube))
