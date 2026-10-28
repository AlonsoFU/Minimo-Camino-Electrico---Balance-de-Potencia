src=open('banco.py').read().split("grafos = {k")[0]
exec(src)
import networkx as nx
R=pd.read_pickle(OUT+'banco.pkl'); R=R[R.actual.notna()]
o=oper.copy(); o['X']=np.sqrt(o['R'].fillna(0)**2+o['X']**2)*ref; Gz=grafo(o)
o2=o.copy(); o2.loc[m1,'X']=EPS; Gz1=grafo(o2)
o3=oper.copy(); o3['X']=np.sqrt(o3['R'].fillna(0)**2+o3['X']**2); Gz0=grafo(o3)
ff=oper.copy(); ff['rx']=ff['R']/ff['X']
print('R/X mediana por tensión (líneas y trafos):'); print(ff.groupby('V')['rx'].median().round(2).to_string())
def asigna(G):
    out={}
    for _,r in R.iterrows():
        if r.nodo not in G: continue
        d=nx.single_source_dijkstra_path_length(G,r.nodo,weight='w')
        c=[t for t in PN if sub_t.get(t)==r['sub'] and t in d]
        if c: out[r.barra]=min(c,key=lambda t:(round(d[t],6),t))
    return pd.Series(out)
for nom,G,ref_ in [('Hoy con |Z|',Gz0,'actual'),('Referido con |Z|',Gz,'P_ref220'),('Ref+Sub con |Z|',Gz1,'P_C1')]:
    s=asigna(G); base=R.set_index('barra')[ref_].reindex(s.index)
    pn=R.set_index('barra')['PN2604'].reindex(s.index)
    print(f'{nom:18s} cambian vs X sola: {int((s!=base).sum()):4d}  = PN2604: {int((s==pn).sum())} (con X: {int((base==pn).sum())})')
    if nom=='Referido con |Z|':
        ch=pd.DataFrame({'X':base,'Z':s,'PN':pn})[s!=base]; print(ch.groupby(['X','Z']).size().sort_values(ascending=False).head(8).to_string())
s=asigna(Gz1); base=R.set_index('barra')['P_C1'].reindex(s.index); mrg=(R.set_index('barra')['P_C1_mrg']).reindex(s.index)
ch=pd.DataFrame({'X':base,'Z':s,'mrg':mrg})[s!=base]
print(ch.groupby(['X','Z']).size().sort_values(ascending=False).head(8).to_string()); print('margen relativo con X de las que cambian: mediana',round(ch.mrg.median()*100,2),'%  <2%:',int((ch.mrg<0.02).sum()),'de',len(ch))
