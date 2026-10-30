import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
DARK="#404040"; GREY="#9A9A9A"; A="#30849B"; B="#E8752A"; TR="#7B5EA7"; RED="#C0392B"
S='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/fig/'
def trafo(ax,x,y,c=TR):
    for dx in (-0.2,0.2): ax.add_patch(Circle((x+dx,y),0.3,fc='white',ec='none',zorder=3))
    for dx in (-0.2,0.2): ax.add_patch(Circle((x+dx,y),0.3,fill=False,ec=c,lw=2.2,zorder=4))
def lab(ax,x,y,t,c=DARK,fs=12.5,w='normal'): ax.text(x,y,t,ha='center',va='center',fontsize=fs,color=c,fontweight=w,zorder=8,bbox=dict(boxstyle='round,pad=0.3',fc='white',ec='none'))
fig,axs=plt.subplots(3,1,figsize=(14,11),dpi=160,gridspec_kw={'height_ratios':[1,1,1]})
rows=[('El mismo circuito, tal como viene en el ENT (mezcla)', '10 Ω\n(en 66 kV)','57 Ω\n(en 154 kV)','10 + 57 = 67 Ω',RED,'Se suman Ω de dos «monedas» distintas: el resultado no corresponde a ninguna tensión.'),
      ('Todo referido a 154 kV (multiplicar lo de 66 kV por (154/66)² = 5,44)','10 × 5,44 = 54,4 Ω','57 Ω','54,4 + 57 = 111,4 Ω',A,'Consistente.'),
      ('Todo referido a 66 kV (dividir lo de 154 kV por 5,44)','10 Ω','57 / 5,44 = 10,5 Ω','10 + 10,5 = 20,5 Ω',A,'Consistente. Es el mismo circuito: 111,4 / 20,5 = 5,44.')]
for ax,(tt,xl,xt,tot,c,nota) in zip(axs,rows):
    ax.set_xlim(0,14); ax.set_ylim(0,3); ax.axis('off')
    ax.plot([1,4.6],[1.5,1.5],color=DARK,lw=3); ax.plot([5.4,8.5],[1.5,1.5],color=DARK,lw=3); trafo(ax,5.0,1.5)
    for x,t in [(1,'Barra 66 kV'),(8.5,'Barra 154 kV')]:
        ax.scatter(x,1.5,s=200,color='white',edgecolor=DARK,lw=2.2,zorder=6); ax.text(x,0.95,t,ha='center',fontsize=12,color=DARK,fontweight='bold')
    ax.text(2.8,2.45,'línea 66 kV',ha='center',fontsize=11.5,color=GREY); ax.text(5.0,2.45,'trafo 154/66 kV, 56 MVA',ha='center',fontsize=11.5,color=GREY)
    lab(ax,2.8,1.95,xl,c if c==A else DARK); lab(ax,5.0,0.75,xt,TR)
    ax.text(9.3,1.75,'Total:',fontsize=13,color=DARK,va='center'); ax.text(10.2,1.75,tot,fontsize=15,color=c,fontweight='bold',va='center')
    ax.text(9.3,1.05,nota,fontsize=11.5,color=c,va='center',wrap=True)
    ax.set_title(tt,fontsize=14,color=DARK,fontweight='bold',loc='left')
fig.suptitle('¿Qué significa «referir» a una tensión?',fontsize=18,color=DARK,fontweight='bold',y=0.995)
fig.text(0.5,0.01,'Regla: Ω vistos desde el lado de tensión V₂ = Ω vistos desde V₁ × (V₂ / V₁)².  Da lo mismo a qué tensión se refiera todo (66, 154 o 220 kV):\n'
         'solo cambia la escala y el orden entre caminos se mantiene. Lo que no se puede es mezclar. Valores reales del trafo Itahue 154/66 kV T1 (CNE: 56 MVA, 57 Ω en 154 kV).',
         ha='center',fontsize=11.5,color=DARK,bbox=dict(boxstyle='round,pad=0.6',fc='#F4F4F4',ec='none'))
fig.tight_layout(rect=(0,0.07,1,0.97)); fig.savefig(S+'concepto_que_es_referir.png',bbox_inches='tight',facecolor='white')
