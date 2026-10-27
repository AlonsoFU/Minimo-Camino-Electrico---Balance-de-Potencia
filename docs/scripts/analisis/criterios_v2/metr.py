import pandas as pd, numpy as np, sys
sys.path.insert(0,'.')
from math import radians, sin, cos, asin, sqrt
INP='/home/user/balance-de-potencia-anual/data/minimo_camino/inputs/2025/pre/'
cdf=pd.read_excel(INP+'conversor_coordenadas_Nodos.xlsx',sheet_name=0,header=None); cdf.columns=cdf.iloc[3].values; cdf=cdf.iloc[4:]
coord={r['BarraFacturación']:(float(r['Latitud']),float(r['Longitud'])) for _,r in cdf[['BarraFacturación','Latitud','Longitud']].dropna().iterrows()}
def km(a,b):
    if a not in coord or b not in coord: return np.nan
    la1,lo1=map(radians,coord[a]); la2,lo2=map(radians,coord[b]); return 2*6371*asin(sqrt(sin((la2-la1)/2)**2+cos(la1)*cos(la2)*sin((lo2-lo1)/2)**2))
R=pd.read_pickle('banco.pkl'); R=R[R['actual'].notna()]
K=[c for c in sys.argv[1].split(',')] if len(sys.argv)>1 else ['PN2604','actual','C1','C2','C3_trafo_troncal','P_ref220','TH_ohm','TH_ref220']
src=lambda r: r['barra'] if r['barra'] in coord else r['nodo']
out={}
for k in K:
    d=R.apply(lambda r: km(src(r),r[k]),axis=1)
    o={'= PN2604':int((R[k]==R['PN2604']).sum()),'= geo más cercana':int((R[k]==R['geo_mas_cercana']).sum()),
       'km mediana':round(d.median(),1),'km media':round(d.mean(),1),'>100 km':int((d>100).sum()),'>200 km':int((d>200).sum())}
    if k+'_mrg' in R: o['margen <2%']=int((R[k+'_mrg']<0.02).sum()); o['empates']=int(R[k+'_emp'].sum())
    out[k]=o
print(pd.DataFrame(out).to_string())
casos=['LAPALMA_______013','TILCOCO_______154','LA_REINA______110','JADRESIC______220','PANGUIPULLI___023','S.FERNANDO____066','CONCEPCION____066','SANTA_ELENA___013']
C=R[R['barra'].isin(casos)|R['barra'].str.startswith(('LAPALMA','LA_PALMA','TILCOCO','LA_REINA','JADRESIC','PANGUIP','S.FERNANDO','CONCEPCION','STA_ELENA','SANTA_ELENA'))]
print(C[['barra']+K].to_string())
