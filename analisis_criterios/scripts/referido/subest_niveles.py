exec(open('con_r.py').read().split("ESC = {")[0])
import re
vol=lambda n: int(re.search(r'(\d+)$',n).group(1))
o=oper[m1].copy(); o['A']=o['Barra A'].astype(int).map(nm); o['B']=o['Barra B'].astype(int).map(nm)
o['par']=[f"{max(vol(a),vol(b))}/{min(vol(a),vol(b))}" for a,b in zip(o.A,o.B)]
o['toca_troncal']=o.A.isin(PN)|o.B.isin(PN)
print('trafos anulados en Ref+Sub:',len(o),' tocan directo la barra troncal:',int(o.toca_troncal.sum()))
print(o.groupby(['par','toca_troncal']).size().unstack(fill_value=0).to_string())
print(o[~o.toca_troncal][['A','B']].head(15).to_string())
S=pd.read_pickle(OUT+'con_r.pkl')
G3=grafo_z(esc(True,m3),'X'); s3,_=asigna(G3)
print('\nReferido + solo trafo que toca la troncal: =PN2604',int((s3==S.PN2604.reindex(s3.index)).sum()),
      ' cambian vs hoy',int((s3!=S.mod_actual.reindex(s3.index)).sum()),
      ' distintas de Referido',int((s3!=S['Referido (X)'].reindex(s3.index)).sum()),' distintas de Ref+Sub',int((s3!=S['Ref+Sub (X)'].reindex(s3.index)).sum()))
s3.to_pickle(OUT+'ref_trafo_directo.pkl')
