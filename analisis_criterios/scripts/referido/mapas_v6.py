# Tres casos en que Hoy, «Referido» y «Referido + Subestación» dan troncales distintas.
S='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/'
src=open(S+'mapas_v3.py').read().split("PNH={}")[0]
exec(src)
PNH={}
N={'CANDELARIA____220':'Candelaria','ITAHUE________220':'Itahue','ANCOA_________220':'Ancoa','A.JAHUEL______220':'Alto Jahuel',
   'C.CHENA_______220':'Cerro Chena','C.NAVIA_______220':'Cerro Navia'}
casos=[('LINARES_______066','Linares 66 kV',(-72.2,-70.3,-36.8,-33.5),['CANDELARIA____220','ANCOA_________220','ITAHUE________220'],'Itahue'),
       ('RANCAGUA______154','Rancagua 154 kV',(-71.3,-70.4,-34.5,-33.3),['C.CHENA_______220','CANDELARIA____220','A.JAHUEL______220'],'Alto Jahuel'),
       ('VITACURA______110','Vitacura 110 kV',(-71.0,-70.4,-33.75,-33.2),['C.CHENA_______220','A.JAHUEL______220','C.NAVIA_______220'],'Cerro Navia')]
for s_,n,box,ts,pn in casos:
    PNH[s_]=pn; mapa(s_,n,box,f'tres_criterios_{s_[:8].strip("_").lower()}.png',{k:N[k] for k in ts})
