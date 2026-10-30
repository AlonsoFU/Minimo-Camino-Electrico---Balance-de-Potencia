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
   'HUALPEN_______220':'Hualpén','RAHUE_________220':'Rahue','P.MONTT_______220':'Puerto Montt','MELIPULLI_____220':'Melipulli','CARDONES______220':'Cardones','D.ALMAGRO_____220':'Diego de Almagro','C.PINTO_______220':'C. Pinto','L.MAQUIS______220':'Los Maquis','L.VILOS_______220':'Los Vilos'}

casos=[('JADRESIC______220','Jadresic 220 kV',(-71.5,-68.5,-28.5,-23.0),['CARDONES______220','OHIGGINS______220','D.ALMAGRO_____220'],'Diego de Almagro',
        'Causa: red de 500 kV. Al referir, 1 km de 500 kV pesa 0,1 km de 220 kV; Cardones (303 km) queda «más cerca» que O\'Higgins (129 km).'),
       ('CUMBRES_______500','Cumbres 500 kV',(-71.5,-69.0,-28.2,-25.5),['CARDONES______220','D.ALMAGRO_____220','C.PINTO_______220'],'Diego de Almagro',
        'Causa: red de 500 kV. Por 500 kV llega a Cardones (143 km) con 10 Ω; Diego de Almagro (17 km) requiere 220 kV y cuesta 18,7 Ω.'),
       ('CURICO________066','Curicó 66 kV',(-72.2,-70.3,-36.2,-33.5),['CANDELARIA____220','ITAHUE________220'],'Itahue',
        'Causa: dato. Los trafos de Itahue en el ENT son 3–7 veces los de la CNE; con valores CNE gana Itahue (21 km).'),
       ('JUNCAL________044','Juncal 44 kV',(-71.6,-69.9,-33.3,-32.5),['NOGALES_______220','L.MAQUIS______220'],'Los Maquis',
        'Causa: casi empate (1.203 vs 1.209, 0,5 %). Se decide por 6 Ω en la red de 110 kV; Los Maquis está a 25 km y Nogales a 102 km.')]
from PIL import Image, ImageDraw, ImageFont
for i in range(0,len(casos),2):
    files=[]; notas=[]
    for s_,n,box,ts,pn,nota in casos[i:i+2]:
        PNH[s_]=pn; out=f'v5_{s_[:8].strip("_").lower()}.png'; mapa(s_,n,box,out,{k:N[k] for k in ts}); files.append(S+'fig/'+out); notas.append(nota)
    ims=[Image.open(f) for f in files]; W=max(im.width for im in ims)+40; hdr=120; nh=80
    c=Image.new('RGB',(W,sum(im.height for im in ims)+hdr+nh*len(ims)),'white'); d=ImageDraw.Draw(c); y=hdr
    t='Casos en que «Referido» da un resultado sin sentido práctico'
    fb=ImageFont.truetype('/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf',50); d.text((W//2,hdr//2),t,fill=(64,64,64),font=fb,anchor='mm')
    fn=ImageFont.truetype('/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf',34)
    for im,nota in zip(ims,notas):
        c.paste(im,((W-im.width)//2,y)); y+=im.height
        sz=34
        while d.textlength(nota,font=fn)>W-80 and sz>18: sz-=2; fn=ImageFont.truetype('/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf',sz)
        d.rounded_rectangle((30,y+8,W-30,y+nh-8),radius=14,fill=(253,236,234)); d.text((W//2,y+nh//2),nota,fill=(160,40,30),font=fn,anchor='mm'); y+=nh
        fn=ImageFont.truetype('/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf',34)
    c.save(S+f'fig/referido_sin_sentido_{i//2+1}.png')
