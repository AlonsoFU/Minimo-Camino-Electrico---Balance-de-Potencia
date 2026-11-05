exec(open('por_que_r.py').read().split("for k, col in")[0])
print('trafos operativos', int(T.sum()), ' anulados en Ref+Sub (subestación con barra troncal):', int(m1.sum()), ' se mantienen:', int((T & ~m1).sum()))
G = GX['RefSub']
def dos_rutas(b):
    nodo = R0.loc[b,'nodo']; cand=[t for t in PN if sub_t.get(t)==R0.loc[b,'sub']]
    H = nx.Graph(); [H.add_edge(u, v, w=d['x']) for u, v, d in G.edges(data=True)]
    dist, paths = nx.single_source_dijkstra(H, nodo, weight='w')
    out=[]
    for t in sorted(cand, key=lambda t: dist.get(t, 1e9))[:2]:
        p=paths[t]; out.append((t,[(p[i],p[i+1],'T' if (p[i],p[i+1]) in Tset else 'L',G[p[i]][p[i+1]]['x'],G[p[i]][p[i+1]]['r']) for i in range(len(p)-1)]))
    return out
import pickle
res={}
for b in ['LA_REINA______013','S.RAFAEL______013','ANDALIEN______013']:
    rr=dos_rutas(b); res[b]=rr; print('\n',b, 'X:',S.loc[b,'Ref+Sub (X)'],' |Z|:',S.loc[b,'Ref+Sub (|Z|)'])
    for t,e in rr:
        print('  ->',t, 'X=%.2f R=%.2f'%(sum(x for *_,x,r in e),sum(r for *_,x,r in e)))
        for a,c,tp,x,r in e: print('     %s %-18s→%-18s X=%6.2f R=%6.2f'%(tp,a,c,x,r))
pickle.dump(res,open(OUT+'r_rutas.pkl','wb'))
