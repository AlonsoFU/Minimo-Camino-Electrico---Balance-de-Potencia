import pandas as pd, numpy as np, warnings; warnings.filterwarnings('ignore')
U='/tmp/claude-0/-home-user-Minimo-Camino-Electrico---Balance-de-Potencia/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/up/bal.xlsm'
f=pd.read_excel(U,sheet_name='05. BALANCE FÍSICO',header=None).iloc[6:][[7,13,14]]; f.columns=['barra','mw','tipo']
f['mw']=pd.to_numeric(f.mw,errors='coerce').fillna(0); g=f[f.tipo!='Tx']
iny=g[g.mw>0].groupby('barra').mw.sum(); ret=-g[g.mw<0].groupby('barra').mw.sum(); mw=iny.add(ret,fill_value=0)
p3=pd.read_excel(U,sheet_name='03. PRECIOS DE NUDO',header=None,usecols='B:D').iloc[4:]; p3.columns=['f','t','precio']
precio=p3[p3['f']=='PN2604'].set_index('t')['precio'].astype(float)
S=pd.read_pickle('con_r.pkl'); S['mw']=S.index.map(mw).fillna(0)
def monto(a,b):
    d=S[S[a]!=S[b]]; dp=(d[b].map(precio)-d[a].map(precio)); m=dp.abs()*d.mw/1000
    return pd.Series({'barras':len(d),'con iny/ret':int((d.mw>0).sum()),'MM$/mes':round(m.sum(),1),'neto MM$/mes (+ sube)':round((dp*d.mw/1000).sum(),1)})
out={}
for k in ['Referido (X)','Referido (|Z|)','Ref+Sub (X)','Ref+Sub (|Z|)']: out[f'Hoy → {k}']=monto('mod_actual',k)
out['Referido: X → |Z|']=monto('Referido (X)','Referido (|Z|)'); out['Ref+Sub: X → |Z|']=monto('Ref+Sub (X)','Ref+Sub (|Z|)')
print(pd.DataFrame(out).T.to_string())
d=S[S['Ref+Sub (X)']!=S['Ref+Sub (|Z|)']]
d=d.assign(dp=(d['Ref+Sub (|Z|)'].map(precio)-d['Ref+Sub (X)'].map(precio)))
print(d.groupby(['Ref+Sub (X)','Ref+Sub (|Z|)']).agg(n=('mw','size'),mw=('mw','sum'),dp=('dp','first')).to_string())
print(d[['Ref+Sub (X)','Ref+Sub (|Z|)','PN2604','mw']].sort_values('mw',ascending=False).head(25).to_string())
print(precio.reindex(['LAGUNILLAS____220','HUALPEN_______220','C.NAVIA_______220','C.CHENA_______220','L.MAQUIS______220','NOGALES_______220']))
