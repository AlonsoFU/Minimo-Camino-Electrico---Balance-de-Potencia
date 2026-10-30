# Más ejemplos: reutiliza mapa() de mapas_v2.py y agrega la asignación PN2604 al título.
S='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/'
src=open(S+'mapas_v2.py').read().split("\nN={")[0]
src=src.replace('fig.suptitle(f"{nombre}: troncal asignada con cada criterio"',
                'fig.suptitle(f"{nombre}: troncal asignada con cada criterio   (PN2604: {PNH.get(src,\'—\')})"')
src=src.replace("y0,y1=min(p[1] for p in pts)-0.06,max(p[1] for p in pts)+0.22",
 "y0,y1=min(p[1] for p in pts)-0.06,max(p[1] for p in pts)+0.10\n    w_,h_=x1-x0,y1-y0\n    if w_<0.75*h_: x0,x1=x0-(0.75*h_-w_)/2,x1+(0.75*h_-w_)/2\n    if h_<0.6*w_: y0,y1=y0-(0.6*w_-h_)/2,y1+(0.6*w_-h_)/2")
src=src.replace("ax.text(0.03,0.985,txt,transform=ax.transAxes,fontsize=10,color=DARK,va='top'",
 "ax.text(0.5,-0.02,txt,transform=ax.transAxes,fontsize=10.5,color=DARK,va='top',ha='center'")
src=src.replace('fig.text(0.5,0.02,','fig.text(0.5,-0.04,')
exec(src)
PNH={}
N={'CANDELARIA____220':'Candelaria','ITAHUE________220':'Itahue','ANCOA_________220':'Ancoa','A.JAHUEL______220':'Alto Jahuel',
   'P.AZUCAR______220':'Pan de Azúcar','NOGALES_______220':'Nogales','L.MAQUIS______220':'Los Maquis','OHIGGINS______220':"O'Higgins",
   'CARDONES______220':'Cardones','D.ALMAGRO_____220':'Diego de Almagro','RAHUE_________220':'Rahue','CIRUELOS______220':'Ciruelos',
   'VALDIVIA______220':'Valdivia','LAGUNILLAS____220':'Lagunillas','HUALPEN_______220':'Hualpén'}
casos=[('OVALLE________066','Ovalle 66 kV',(-72.0,-70.0,-33.2,-29.5),'v3_mapa_ovalle.png',['P.AZUCAR______220','NOGALES_______220'],'P. de Azúcar'),
       ('LINARES_______066','Linares 66 kV',(-72.2,-70.3,-36.8,-33.5),'v3_mapa_linares.png',['ANCOA_________220','ITAHUE________220','CANDELARIA____220'],'Itahue'),
       ('LOS_ANDES_____044','Los Andes 44 kV',(-71.6,-70.0,-33.3,-32.5),'v3_mapa_losandes.png',['L.MAQUIS______220','NOGALES_______220'],'Los Maquis'),
       ('JADRESIC______220','Jadresic 220 kV',(-71.5,-68.5,-28.5,-23.0),'v3_mapa_jadresic.png',['OHIGGINS______220','D.ALMAGRO_____220','CARDONES______220'],'Diego de Almagro'),
       ('PANGUIPULLI___066','Panguipulli 66 kV',(-73.6,-71.6,-41.0,-38.8),'v3_mapa_panguipulli.png',['RAHUE_________220','CIRUELOS______220','VALDIVIA______220'],'Valdivia'),
       ('CONCEPCION____066','Concepción 66 kV',(-73.4,-72.6,-37.4,-36.5),'v3_mapa_concepcion.png',['LAGUNILLAS____220','HUALPEN_______220'],'Lagunillas')]
for s,n,box,out,ts,pn in casos:
    PNH[s]=pn; print('==',n); mapa(s,n,box,out,{k:N[k] for k in ts})
