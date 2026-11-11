exec(open('con_r.py').read().split("ESC = {")[0])
o=oper.copy(); o['A']=o['Barra A'].astype(int).map(nm); o['B']=o['Barra B'].astype(int).map(nm); o['tipo2']=np.where(T,'T','L')
z=o[o.X<0.01]
print('tramos con X < 0,01 Ω en el ENT:',len(z),' trafos:',int((z.tipo2=='T').sum()),' líneas:',int((z.tipo2=='L').sum()))
print(z[['Nombre','V','X','tipo2']].to_string())
