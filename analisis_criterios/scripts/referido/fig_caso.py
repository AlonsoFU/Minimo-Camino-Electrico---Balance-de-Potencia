import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
D='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/'
DARK="#404040"; GREY="#9E9E9E"; ACC="#30849B"; RED="#C0392B"; LIN="#E8752A"
T={'O\'Higgins 220':(-23.692,-70.215),'Crucero 220':(-22.274,-69.566),'Cardones 220':(-27.489,-70.386)}
LC=(-23.152,-70.319); KI=(-22.301,-69.482)
mej=[('Angamos',-23.068,-70.368),('Kelar',-23.033,-70.340),('TEN',-23.091,-70.410),('Kapatur',-23.145,-70.339),('Los Changos',-23.152,-70.319),('Caitán',-23.145,-70.340)]
jad=[('Jadresic',-24.806,-69.850),('Kallpa',-24.926,-69.981)]
fig=plt.figure(figsize=(15,9.2),dpi=160)
ax=fig.add_axes([0.03,0.08,0.4,0.84])
ax.set_xlim(-71.6,-68.6); ax.set_ylim(-27.8,-21.9); ax.set_aspect(1/abs(__import__('math').cos(__import__('math').radians(24.8)))); ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_color('#DDDDDD')
ax.plot([LC[1],KI[1]],[LC[0],KI[0]],color=LIN,lw=5,zorder=2); ax.text((LC[1]+KI[1])/2+0.18,(LC[0]+KI[0])/2-0.15,'L.Changos–Kimal\n500 kV (2 circuitos)',color=LIN,fontsize=11.5,fontweight='bold',va='center')
for n,(la,lo) in T.items():
    ax.scatter(lo,la,marker='s',s=170,color=ACC,zorder=4,edgecolor='white'); ax.text(lo-0.09,la,n,fontsize=12,fontweight='bold',color=ACC,va='center',ha='right')
ax.scatter(KI[1],KI[0],s=60,color=LIN,zorder=4); ax.text(KI[1]+0.08,KI[0]+0.05,'Kimal',fontsize=11,color=LIN)
for n,la,lo in mej+jad:
    ax.scatter(lo,la,s=45,color=DARK,zorder=5)
c=(-23.10,-70.35)
ax.text(c[1]-0.1,c[0]-0.35,'Barras de Mejillones\n(Angamos, Kelar, TEN,\nKapatur, Caitán, L.Changos)',ha='right',fontsize=10.5,color=DARK)
ax.annotate('',xy=(T["O'Higgins 220"][1],T["O'Higgins 220"][0]),xytext=(c[1],c[0]),arrowprops=dict(arrowstyle='->',color=GREY,lw=2,ls='--'))
ax.annotate('',xy=(T['Crucero 220'][1],T['Crucero 220'][0]),xytext=(c[1]+0.02,c[0]+0.03),arrowprops=dict(arrowstyle='->',color=RED,lw=2.4,connectionstyle='arc3,rad=0.35'))
j=(-24.86,-69.91); ax.text(j[1]+0.16,j[0],'Jadresic / Kallpa',fontsize=10.5,color=DARK,va='center')
ax.annotate('',xy=(T['Cardones 220'][1],T['Cardones 220'][0]),xytext=(j[1],j[0]),arrowprops=dict(arrowstyle='->',color=GREY,lw=2,ls='--'))
ax.annotate('',xy=(T['Crucero 220'][1]+0.02,T['Crucero 220'][0]-0.05),xytext=(j[1]+0.02,j[0]+0.05),arrowprops=dict(arrowstyle='->',color=RED,lw=2.4))
ax.plot([],[],color=GREY,ls='--',lw=2,label='Troncal con dato del ENT'); ax.plot([],[],color=RED,lw=2.4,label='Troncal con dato corregido')
ax.legend(loc='lower right',fontsize=11,frameon=False)
fig.text(0.47,0.88,'Un tramo que mueve mucho: L.Changos–Kimal 500 kV',fontsize=19,fontweight='bold',color=DARK)
rows=[('Dato','ENT','Fuentes (CNE ≈ Infotécnica)'),('X por circuito (Ω, a 500 kV)','106,8','36,9  (ENT ≈ 2,9×)'),('Referido a 220 kV, 2 circuitos','10,3','3,6')]
y=0.80
for i,r in enumerate(rows):
    for k,(t,x) in enumerate(zip(r,[0.47,0.70,0.79])):
        fig.text(x,y,t,fontsize=12.5,color=DARK,fontweight='bold' if i==0 or k==0 else 'normal')
    y-=0.04
fig.text(0.47,0.66,'Distancia eléctrica desde Kelar (Ω referidos a 220 kV)',fontsize=13.5,fontweight='bold',color=DARK)
for i,(a,b,c_) in enumerate([('','O\'Higgins','Crucero'),('Con ENT','11,9  ← gana','18,1'),('Corregido','11,9','11,3  ← gana')]):
    for k,(t,x) in enumerate(zip((a,b,c_),[0.47,0.60,0.72])): fig.text(x,0.62-0.037*i,t,fontsize=12.5,color=RED if 'gana' in t and i==2 else DARK,fontweight='bold' if i==0 or k==0 else 'normal')
fig.text(0.47,0.47,'Efecto de corregir solo este tramo',fontsize=13.5,fontweight='bold',color=DARK)
txt=('• 10 barras cambian de troncal, 227 MM$/mes (el tramo de mayor impacto).\n'
     '• Mejillones (6 barras, ~650 MW): O\'Higgins 61–74 km → Crucero 116–126 km. Quedan MÁS LEJOS.\n'
     '• Jadresic y Kallpa: Cardones ~300 km → Crucero ~290 km. Lejos en ambos casos.\n'
     '• Ninguna gana coincidencia con PN2604; 7 la pierden.')
fig.text(0.47,0.44,txt,fontsize=12.5,color=DARK,va='top',linespacing=1.6)
fig.text(0.47,0.24,'Lectura',fontsize=13.5,fontweight='bold',color=DARK)
fig.text(0.47,0.21,('Las tres fuentes coinciden en que el ENT está mal, pero corregirlo empeora la asignación.\n'
     'Causa probable: al referir, la red de 500 kV se acorta ×0,19 y, corregida, queda aún más corta;\n'
     'el camino por 500 kV hacia Kimal pasa a ganar. Es el caso borde de la red de 500 kV.\n'
     '→ No se corrige sin ficha y se revisa junto con la regla para 500 kV.'),fontsize=12.5,color=DARK,va='top',linespacing=1.5,
     bbox=dict(boxstyle='round,pad=0.6',fc='#FDEDEC',ec='none'))
fig.savefig(D+'fig/caso_lchangos_kimal.png',bbox_inches='tight',facecolor='white')
