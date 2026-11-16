exec(open('cadena.py').read().split("base = estado([])")[0])
exec('cdf ='+open('banco.py').read().split('cdf =',1)[1].split('rows = []')[0])
src = lambda b: b if b in coord else R0.loc[b, 'nodo']
c = pd.read_pickle(OUT + 'cadena.pkl'); base = c['base']
B = 'L.CHANGOS_____500->KIMAL_________500'
s = estado([B]); ch = s[s != base.reindex(s.index)]
for i in bloques[B]: print(oper.loc[i, 'Nombre'], 'X ENT', round(oper.loc[i, 'X'], 3), 'X sug', round(disc.loc[oper.loc[i, 'Nombre'], 'valor_sugerido'], 3), disc.loc[oper.loc[i, 'Nombre'], 'clasificacion_validacion'])
rows = []
for b in ch.index:
    rows.append({'barra': b, 'nodo': R0.loc[b, 'nodo'], 'antes': base[b], 'km_antes': round(km(src(b), base[b])), 'después': ch[b], 'km_después': round(km(src(b), ch[b])),
                 'MW': round(S.mw.get(b, 0), 1), 'PN2604': R0.loc[b, 'PN2604'], 'coord': coord.get(src(b))})
print(pd.DataFrame(rows).to_string())
for t in ['L.CHANGOS_____500', 'KIMAL_________500', 'KIMAL_________220', 'CRUCERO_______220', 'CARDONES______220', 'OHIGGINS______220', 'ENCUENTRO_____220', 'L.CHANGOS_____220']:
    print(t, coord.get(t), 'precio', precio.get(t))
