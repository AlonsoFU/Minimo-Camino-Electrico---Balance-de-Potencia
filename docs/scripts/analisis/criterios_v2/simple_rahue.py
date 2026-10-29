import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
S='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/fig/'
DARK="#404040"; GREY="#8C8C8C"; HOY="#C0392B"; REF="#30849B"; TR="#7B5EA7"; L66="#E8752A"
fmt=lambda v,d=2:f"{v:,.{d}f}".replace(',','X').replace('.',',').replace('X','.')
tramos=[('línea 66 kV','viene en Ω de 66 kV',19.146,66,L66,False),('trafo 220/66 kV','viene en Ω de 220 kV',31.111,220,TR,True)]
xs=[0.5,5.5,10.5]; yH,yR=4.6,0.9
fig,ax=plt.subplots(figsize=(14,7.4),dpi=170); ax.set_xlim(-1.2,15.5); ax.set_ylim(-0.6,6.6); ax.axis('off')
for y,col,lab,c in [(yH,HOY,'1) Sin referir (como hoy)',HOY),(yR,REF,'2) Referido a 220 kV',REF)]:
    for i,(nm,src,x,v,cc,istr) in enumerate(tramos):
        ax.plot([xs[i],xs[i+1]],[y,y],color=cc,lw=8 if not istr else 4.5,ls='-' if not istr else (0,(2,1.2)),zorder=1)
    ax.scatter(xs[0],y,s=600,color='white',edgecolor=DARK,lw=2.5,zorder=3); ax.scatter(xs[1],y,s=450,color='white',edgecolor=DARK,lw=2,zorder=3)
    ax.scatter(xs[2],y,s=800,marker='s',color=col,edgecolor='white',lw=2,zorder=3)
    ax.text(-1.1,y+1.05,lab,fontsize=15,fontweight='bold',color=c)
    for x,n in zip(xs,['Llanquihue\n66 kV','Pilauco\n66 kV','RAHUE\n220 kV']):
        ax.text(x,y-0.45,n,ha='center',va='top',fontsize=11.5,color=DARK,fontweight='bold' if x!=xs[1] else 'normal')
tH=tR=0
for i,(nm,src,x,v,c,istr) in enumerate(tramos):
    xm=(xs[i]+xs[i+1])/2; f=(220/v)**2; r=x*f; tH+=x; tR+=r
    ax.text(xm,yH+0.35,f"{nm}\n({src})",ha='center',va='bottom',fontsize=11,color=GREY)
    ax.text(xm,yH-0.3,f"{fmt(x)} Ω",ha='center',va='top',fontsize=16,fontweight='bold',color=HOY)
    ax.add_patch(FancyArrowPatch((xm,yH-0.95),(xm,yR+0.95),arrowstyle='-|>',mutation_scale=20,color=GREY,lw=1.6))
    ax.text(xm+0.2,(yH+yR)/2+0.05,f"× (V_ref / V)²\n= (220 / {v})²\n= {fmt(f)}",ha='left',va='center',fontsize=14,fontweight='bold',color=DARK,
            bbox=dict(boxstyle='round,pad=0.35',fc='#FFF1E0' if f>1 else '#EEF5F7',ec='none'))
    ax.text(xm,yR+0.35,f"{fmt(x)} × (220 / {v})²",ha='center',va='bottom',fontsize=12,color=GREY)
    ax.text(xm,yR-0.3,f"= {fmt(r)} Ω",ha='center',va='top',fontsize=16,fontweight='bold',color=REF if v==220 else L66)
ax.text(11.4,yH,f"Total\n{fmt(tH)} Ω",fontsize=17,fontweight='bold',color=HOY,va='center')
ax.text(11.4,yR,f"Total\n{fmt(tR)} Ω",fontsize=17,fontweight='bold',color=REF,va='center')
ax.set_title('Llanquihue 66 kV → Rahue 220 kV: el mismo camino, sin referir y referido',fontsize=17,fontweight='bold',color=DARK)
fig.text(0.5,0.02,'V_ref = 220 kV (tensión a la que se refiere todo); V = tensión en que viene cada Ω (columna V [kV] del ENT).\nLa línea viene en 66 kV: (220/66)² = 11,11. El trafo viene en 220 kV (su lado de alta): (220/220)² = 1, queda igual.',
         ha='center',fontsize=12.5,color=DARK,bbox=dict(boxstyle='round,pad=0.6',fc='#F4F4F4',ec='none'))
fig.tight_layout(rect=(0,0.06,1,1)); fig.savefig(S+'simple_rahue.png',bbox_inches='tight',facecolor='white')
