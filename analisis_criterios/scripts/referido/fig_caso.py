import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
D='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/'
DARK="#404040"; GREY="#9E9E9E"; ACC="#30849B"; RED="#C0392B"; LIN="#E8752A"; WIN="#2E7D32"
fmt=lambda v:f"{v:.1f}".replace('.',',')
fig,axs=plt.subplots(1,2,figsize=(16,6.6),dpi=160)
for ax,(tit,xl) in zip(axs,[('Con el dato del ENT',10.33),('Con el dato corregido',3.57)]):
    ax.set_xlim(-0.5,10.5); ax.set_ylim(-1.2,6.4); ax.axis('off')
    dO=9.75; dC=0.36+2.15+xl+2.91+0.12; gana_O=dO<dC
    P={'Kelar':(0,3),'Kapatur':(2,3),"O'Higgins":(9,5.2),'L.Changos 500':(4.5,1),'Kimal 500':(7,1),'Crucero':(9,1)}
    def edge(a,b,col,lw,lab,dy=0.25,bold=False,c2=None):
        (x1,y1),(x2,y2)=P[a],P[b]; ax.plot([x1,x2],[y1,y2],color=col,lw=lw,zorder=1,solid_capstyle='round')
        ax.text((x1+x2)/2,(y1+y2)/2+dy,lab,ha='center',fontsize=12.5,color=c2 or col,fontweight='bold' if bold else 'normal')
    edge('Kelar','Kapatur',GREY,5,'2,2  (común)',c2=DARK)
    edge('Kapatur',"O'Higgins",WIN if gana_O else GREY,6 if gana_O else 3,'9,8',dy=0.3,bold=True,c2=DARK)
    edge('Kapatur','L.Changos 500',WIN if not gana_O else GREY,6 if not gana_O else 3,'2,5',dy=-0.6,c2=DARK)
    edge('L.Changos 500','Kimal 500',LIN,8,f'línea L.Changos–Kimal\n{fmt(xl)}',dy=0.35,bold=True)
    edge('Kimal 500','Crucero',WIN if not gana_O else GREY,6 if not gana_O else 3,'3,0',dy=0.3,c2=DARK)
    for n,(x,y) in P.items():
        tro=n in ("O'Higgins",'Crucero')
        ax.scatter(x,y,s=700 if tro else 420,marker='s' if tro else 'o',color=ACC if tro else 'white',edgecolor=ACC if tro else DARK,lw=2,zorder=3)
        ax.text(x,y-0.55,n,ha='center',va='top',fontsize=13 if tro else 12,fontweight='bold' if tro or n=='Kelar' else 'normal',color=DARK)
    ax.text(9.6,5.2,f"total {fmt(2.19+dO)}\n74 km",ha='left',va='center',fontsize=12.5,color=WIN if gana_O else DARK,fontweight='bold' if gana_O else 'normal')
    ax.text(9.6,1,f"total {fmt(2.19+dC)}\n116 km",ha='left',va='center',fontsize=12.5,color=WIN if not gana_O else DARK,fontweight='bold' if not gana_O else 'normal')
    ax.set_title(tit,fontsize=17,fontweight='bold',color=DARK)
    ax.text(5,-1.1,f"Gana {'O\'Higgins (más cerca)' if gana_O else 'Crucero (más lejos)'}",ha='center',fontsize=15,fontweight='bold',color=WIN if gana_O else RED)
fig.suptitle('Barra Kelar 220 kV: corregir la línea L.Changos–Kimal 500 kV la cambia de troncal',fontsize=19,fontweight='bold',color=DARK,y=1.02)
fig.text(0.5,-0.06,'Ω referidos a 220 kV (2 circuitos en paralelo). ENT: 106,8 Ω por circuito; CNE e Infotécnica: 36,9 Ω.\nLo mismo pasa con otras 9 barras (Angamos, Kapatur, TEN…): 227 MM$/mes. Las fuentes dicen que el ENT está mal, pero corregirlo deja las barras más lejos → revisar antes de cambiar.',
         ha='center',fontsize=12.5,color=DARK,bbox=dict(boxstyle='round,pad=0.6',fc='#F4F4F4',ec='none'))
fig.savefig(D+'fig/caso_lchangos_kimal.png',bbox_inches='tight',facecolor='white')
