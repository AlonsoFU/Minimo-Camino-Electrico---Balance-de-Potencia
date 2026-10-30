src=open('banco.py').read().split("grafos = {k")[0]
exec(src)
import networkx as nx
fix={'ITAHUE________220->ITAHUE________154':15.568356,'ITAHUE________154->ITAHUE________066_1de2':2*13.07,
     'ITAHUE________154->ITAHUE________066_2de2':2*13.07,'LINARES_______154->LINARES_______066':18.95}
def con_cne(o):
    o=o.copy()
    for n,x in fix.items():
        m=o['Nombre']==n; assert m.sum()==1,n; o.loc[m,'X']=x*(1 if 'actual' else 1)
    return o
o0=esc['actual']; oc=con_cne(oper)
ocr=oc.copy(); ocr['X']=ocr['X']*ref
casos={'Hoy (ENT)':grafo(o0),'Hoy con trafos CNE':grafo(oc),'Referido (ENT)':grafo(esc['P_ref220']),'Referido con trafos CNE':grafo(ocr)}
for b in ['LAPALMA_______013','CURICO________066','LINARES_______066','TENO__________154']:
    print('==',b)
    for k,G in casos.items():
        d=nx.single_source_dijkstra_path_length(G,b,weight='w')
        c=sorted((round(d[t],1),t[:10]) for t in ['ITAHUE________220','ANCOA_________220','CANDELARIA____220'] if t in d)
        print(f'  {k:25s}',c)
