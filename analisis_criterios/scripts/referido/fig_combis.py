import matplotlib, json, pandas as pd, numpy as np
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
D='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/'
DARK="#404040"; GREY="#BDBDBD"; ACC="#30849B"; RED="#C0392B"; OK="#7FB77E"
j=json.load(open(D+'traza.json')); T=pd.read_pickle(D+'traza.pkl')
fig=plt.figure(figsize=(16,8.6),dpi=160)
# Panel 1: zonas
ax=fig.add_axes([0.03,0.12,0.42,0.72]); ax.axis('off'); ax.set_xlim(0,10); ax.set_ylim(0,10)
ax.text(0,9.7,'Paso 1 · Probar por zonas',fontsize=17,fontweight='bold',color=DARK)
ax.text(0,9.1,f"{j['n_tramos']} tramos que solos no cambian nada, ordenados de norte a sur\ny agrupados en {j['zonas']} zonas de ~40. Cada zona se aplica completa y se recalcula.",fontsize=12,color=DARK,va='top')
for k,v in enumerate(j['zres']):
    r,cc=divmod(k,4); x=0.3+cc*2.4; y=6.3-r*1.45
    col=RED if v else GREY
    ax.add_patch(FancyBboxPatch((x,y),2.0,1.05,boxstyle='round,pad=0.04',fc=col,ec='white',alpha=0.9 if v else 0.55))
    ax.text(x+1.0,y+0.68,f'Zona {k+1}',ha='center',fontsize=11.5,color='white' if v else DARK,fontweight='bold')
    ax.text(x+1.0,y+0.25,(f'{v} barra cambia' if v==1 else f'{v} barras cambian') if v else 'se descarta',ha='center',fontsize=10,color='white' if v else DARK)
ax.text(0,0.55,'Rojas: algo cambia → se buscan las combinaciones dentro de la zona (2 pares en zona 1, 1 en zona 12 y 1 en zona 15).\nAl final, se prueba todo lo restante junto para captar combinaciones entre zonas.',fontsize=11.5,color=DARK,va='top')
# Panel 2: reducción
ax2=fig.add_axes([0.53,0.2,0.44,0.55])
ok=T[T.cambia>0]; ns=[j['resto']]+list(ok.n); pas=[0]+list(ok.index+1)
ax2.step(pas,ns,where='post',color=ACC,lw=2.5); ax2.scatter(pas,ns,color=ACC,zorder=3,s=28)
ax2.set_yscale('log'); ax2.set_yticks([3,5,10,20,50,100,300,616]); ax2.set_yticklabels(['3','5','10','20','50','100','300','616'])
ax2.set_xlabel('Recálculos realizados',fontsize=12,color=DARK); ax2.set_ylabel('Tramos que siguen en el grupo sospechoso',fontsize=12,color=DARK)
for s in ['top','right']: ax2.spines[s].set_visible(False)
ax2.tick_params(colors=DARK)
for p,n in zip(pas,ns):
    if n in (616,308,154,77,38,20,10,5,3): ax2.annotate(str(n),(p,n),textcoords='offset points',xytext=(6,6),fontsize=10.5,color=DARK)
fig.text(0.53,0.86,'Paso 2 · Aislar la combinación (entre zonas)',fontsize=17,fontweight='bold',color=DARK)
fig.text(0.53,0.835,'Se parte el grupo y se queda con la parte que aún cambia algo; si ninguna parte sola cambia, se prueba quitando partes.\nSe repite hasta que no se puede quitar ningún tramo.',fontsize=12,color=DARK,va='top')
ax2.text(0.98,0.97,f"{len(T)} recálculos: de 616 tramos a 3\n\nLos Notros–Mulchén + Mulchén–Santa Clara\n+ Santa Clara–Charrúa (220 kV)\n\nSolo los tres juntos cambian 4 barras:\nMulchén, Los Olmos y Picoltué (×2)\nCharrúa → Cautín, ~65 → ~118 km\n36 MM$/mes",
         transform=ax2.transAxes,ha='right',va='top',fontsize=11.5,color=DARK,bbox=dict(boxstyle='round,pad=0.6',fc='#FDEDEC',ec='none'))
fig.text(0.5,0.035,'Resultado total: ~390 recálculos encuentran 6 combinaciones (15 barras, ~41 MM$/mes). Probar todos los pares serían ~194 mil recálculos y todos los tríos ~40 millones.\n«Referido + trafo troncal», X. Se prueban líneas y trafos (circuitos en paralelo como un bloque).',
         ha='center',fontsize=12,color=DARK,bbox=dict(boxstyle='round,pad=0.6',fc='#F4F4F4',ec='none'))
fig.suptitle('Cómo se buscaron las combinaciones de tramos que solo juntos cambian la asignación',fontsize=19,fontweight='bold',color=DARK,y=0.985)
fig.savefig(D+'fig/busqueda_combinaciones.png',bbox_inches='tight',facecolor='white')
