import pandas as pd, numpy as np, sys
exec(open('metr.py').read().split("R=pd.read_pickle")[0])
R=pd.read_pickle('banco.pkl'); R=R[R['actual'].notna()]
src=lambda r: r['barra'] if r['barra'] in coord else r['nodo']
K=sys.argv[1].split(',') if len(sys.argv)>1 else ['C1','C2','C3_trafo_troncal','P_ref220','TH_ohm','TH_ref220']
o={}
for k in K:
    cor=(R['actual']!=R['PN2604'])&(R[k]==R['PN2604']); nue=(R['actual']==R['PN2604'])&(R[k]!=R['PN2604'])
    sub=R[nue]; dk=sub.apply(lambda r: km(src(r),r[k]),axis=1); dp=sub.apply(lambda r: km(src(r),r['PN2604']),axis=1)
    diff=R[R[k]!=R['PN2604']]; dk2=diff.apply(lambda r: km(src(r),r[k]),axis=1); dp2=diff.apply(lambda r: km(src(r),r['PN2604']),axis=1)
    o[k]={'corrige':int(cor.sum()),'nuevas':int(nue.sum()),'nuevas más lejos':int((dk>dp+5).sum()),'nuevas más cerca':int((dk<dp-5).sum()),
          'difieren':len(diff),'dif: más lejos que PN':int((dk2>dp2+5).sum()),'dif: más cerca que PN':int((dk2<dp2-5).sum())}
print(pd.DataFrame(o).to_string())
