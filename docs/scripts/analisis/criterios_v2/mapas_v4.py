# Ejemplos Hoy vs «Referido» (2 paneles) agrupados por tipo de cambio.
S='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/'
src=open(S+'mapas_v3.py').read().split("PNH={}")[0].split("exec(src)")[0]
exec(src)  # define src transformado de v2 (sin ejecutar)
src=src.replace("Gs={k:G[k] for k in ['actual','P_ref220','P_C1']}","Gs={k:G[k] for k in ['actual','P_ref220']}")
src=src.replace("fig,axs=plt.subplots(1,3,figsize=(15,7.4),dpi=170)","fig,axs=plt.subplots(1,2,figsize=(11,7.4),dpi=170)")
src=src.replace("'Hoy\\nΩ sumados sin referir'","'Hoy\\nΩ sumados sin referir'")
exec(src)
PNH={}
from PIL import Image
N={'CANDELARIA____220':'Candelaria','ITAHUE________220':'Itahue','ANCOA_________220':'Ancoa','P.AZUCAR______220':'Pan de Azúcar',
   'NOGALES_______220':'Nogales','OHIGGINS______220':"O'Higgins",'ATACAMA_______220':'Atacama','LAGUNILLAS____220':'Lagunillas',
   'HUALPEN_______220':'Hualpén','RAHUE_________220':'Rahue','P.MONTT_______220':'Puerto Montt','MELIPULLI_____220':'Melipulli','L.VILOS_______220':'Los Vilos'}
grupos={'corrige':[('OVALLE________066','Ovalle 66 kV',(-72.0,-70.0,-33.2,-29.5),['P.AZUCAR______220','NOGALES_______220'],'P. de Azúcar'),
                   ('S.JAVIER______066','San Javier 66 kV',(-72.4,-70.3,-36.8,-33.5),['ITAHUE________220','CANDELARIA____220','ANCOA_________220'],'Itahue')],
        'nueva':[('FRUTILLAR_____066','Frutillar 66 kV',(-73.6,-72.4,-41.8,-40.3),['P.MONTT_______220','RAHUE_________220'],'Rahue'),
                 ('TOME__________066','Tomé 66 kV',(-73.4,-72.5,-37.4,-36.4),['HUALPEN_______220','LAGUNILLAS____220'],'Lagunillas')],
        'ninguno':[('COMBARBALA____066','Combarbalá 66 kV',(-72.0,-70.0,-33.2,-29.5),['L.VILOS_______220','NOGALES_______220','P.AZUCAR______220'],'P. de Azúcar'),
                   ('PANIMAVIDA____066','Panimávida 66 kV',(-72.4,-70.3,-37.2,-33.5),['ANCOA_________220','ITAHUE________220','CANDELARIA____220'],'Itahue')]}
tit={'corrige':'«Referido» corrige: vuelve a la asociación de PN2604 (138 barras)',
     'nueva':'«Referido» cambia una barra que hoy coincide con PN2604 (57 barras)',
     'ninguno':'«Referido» elige una tercera troncal, distinta de hoy y de PN2604 (49 barras)'}
for g,cs in grupos.items():
    files=[]
    for s,n,box,ts,pn in cs:
        PNH[s]=pn; out=f'v4_{g}_{s[:8].strip("_").lower()}.png'; print(g,n); mapa(s,n,box,out,{k:N[k] for k in ts}); files.append(S+'fig/'+out)
    ims=[Image.open(f) for f in files]; W=max(i.width for i in ims)
    hdr=110; c=Image.new('RGB',(W,sum(i.height for i in ims)+hdr),'white'); y=hdr
    for i in ims: c.paste(i,((W-i.width)//2,y)); y+=i.height
    from PIL import ImageDraw, ImageFont
    d=ImageDraw.Draw(c); sz=52
    while True:
        fnt=ImageFont.truetype('/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf',sz)
        if d.textlength(tit[g],font=fnt)<W-60 or sz<20: break
        sz-=2
    d.text((W//2,hdr//2),tit[g],fill=(64,64,64),font=fnt,anchor='mm')
    c.save(S+f'fig/referido_ejemplos_{g}.png')
