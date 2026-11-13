exec(open('con_r.py').read().split("ESC = {")[0])
V = pd.read_pickle(OUT + 'validacion.pkl'); F = pd.read_pickle(OUT + 'decisivos.pkl')
t = V[(V.voltaje_a_ENT != V.voltaje_b_ENT) & V.valor_sugerido.notna() & (V.X_ENT > 0)].copy()
x3 = t[abs(np.log(t.X_ENT / t.valor_sugerido / 3)) < np.log(1.1)]
nom_m3 = set(oper.loc[m3, 'Nombre']); nom_m1 = set(oper.loc[m1, 'Nombre']); nom_op = set(oper['Nombre'])
dec = set(F[(F.Criterio == 'Ref+Trafo troncal') & (F['Barras que cambian'] > 0)]['Tramo ENT'])
x3 = x3.assign(operativo=x3.nombre_ENT.isin(nom_op), anulado=x3.nombre_ENT.isin(nom_m3), decisivo=x3.nombre_ENT.isin(dec))
print('×3 total:', len(x3), ' operativos:', int(x3.operativo.sum()), ' anulados (tocan troncal):', int(x3.anulado.sum()),
      ' quedan relevantes:', int((x3.operativo & ~x3.anulado).sum()), ' decisivos:', int(x3.decisivo.sum()))
print(x3[x3.anulado].nombre_ENT.to_string(index=False))
print('--- decisivos:'); print(x3[x3.decisivo].nombre_ENT.to_string(index=False))
d = F[(F.Criterio == 'Ref+Trafo troncal') & (F['Barras que cambian'] > 0)]
print('\nDecisivos totales Ref+Trafo troncal:', len(d), ' (los trafos que tocan troncal ya se omitieron en la prueba)')
