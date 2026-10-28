import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyBboxPatch
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
DARK="#404040"; GREY="#9A9A9A"; A="#30849B"; B="#E8752A"; TR="#7B5EA7"; WIN="#2E7D32"
S='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/fig/'
def trafo(ax,x,y,c=TR):
    for dx in (-0.17,0.17):
        ax.add_patch(Circle((x+dx,y),0.24,fc='white',ec='none',zorder=3)); 
    for dx in (-0.17,0.17): ax.add_patch(Circle((x+dx,y),0.24,fill=False,ec=c,lw=2,zorder=4))
def nodo(ax,x,y,t,c=DARK,sq=False,pos='below'):
    ax.scatter(x,y,s=330 if sq else 220,marker='s' if sq else 'o',color=c if sq else 'white',edgecolor=c if not sq else 'white',lw=2.2,zorder=6)
    off={'below':(0,-0.5,'center','top'),'right':(0.3,0,'left','center'),'above':(0,0.42,'center','bottom')}[pos]
    ax.text(x+off[0],y+off[1],t,ha=off[2],va=off[3],fontsize=12,color=c,fontweight='bold',zorder=7)
def L(ax,p,q,c,lw=3): ax.plot([p[0],q[0]],[p[1],q[1]],color=c,lw=lw,zorder=2,solid_capstyle='round')
def lab(ax,x,y,t,c=DARK,fs=11.5): ax.text(x,y,t,ha='center',va='center',fontsize=fs,color=c,zorder=8,bbox=dict(boxstyle='round,pad=0.25',fc='white',ec='none'))
def tabla(ax,x,y,filas,ganaH,ganaR):
    ax.text(x,y,'',fontsize=1)
    hdr=f"{'':12s}"
    txt=[('','Hoy','«Referido»')]+filas
    for i,(a,h,r) in enumerate(txt):
        yy=y-0.55*i; w='bold' if i==0 else 'normal'
        ax.text(x,yy,a,fontsize=12.5,color=DARK,fontweight='bold',va='center')
        ax.text(x+2.0,yy,h,fontsize=12.5,color=(WIN if i==ganaH else DARK),fontweight=('bold' if i in (0,ganaH) else 'normal'),va='center',ha='center')
        ax.text(x+3.6,yy,r,fontsize=12.5,color=(WIN if i==ganaR else DARK),fontweight=('bold' if i in (0,ganaR) else 'normal'),va='center',ha='center')

fig,axs=plt.subplots(2,1,figsize=(15,10.5),dpi=160)
# ---------- Caso 1: se separan en 220 kV ----------
ax=axs[0]; ax.set_xlim(0,15); ax.set_ylim(-0.6,4.4); ax.axis('off')
ax.add_patch(FancyBboxPatch((0.3,0.9),5.0,1.6,boxstyle='round,pad=0.1',fc='#EFEFEF',ec='none',zorder=0))
ax.text(2.8,2.75,'TRAMO COMÚN (igual para A y B)',ha='center',fontsize=12,color=GREY,fontweight='bold')
L(ax,(0.8,1.6),(3.2,1.6),DARK); trafo(ax,4.0,1.6); L(ax,(3.2,1.6),(3.75,1.6),DARK); L(ax,(4.25,1.6),(5.6,1.6),DARK)
nodo(ax,0.8,1.6,'Barra\nanalizada 66 kV'); nodo(ax,5.6,1.6,'punto donde\nse separan\n(220 kV)',c=DARK)
lab(ax,2.0,2.05,'línea 66 kV\n10 Ω → ×11 = 111',DARK); lab(ax,4.0,1.05,'trafo 50',TR)
L(ax,(5.6,1.6),(8.6,3.4),A); L(ax,(5.6,1.6),(8.6,-0.2),B)
nodo(ax,8.6,3.4,'Troncal A',c=A,sq=True,pos='right'); nodo(ax,8.6,-0.2,'Troncal B',c=B,sq=True,pos='right')
lab(ax,7.0,2.85,'220 kV: 20 Ω (×1 = 20)',A); lab(ax,7.0,0.35,'220 kV: 30 Ω (×1 = 30)',B)
tabla(ax,10.6,3.0,[('Troncal A','10+50+20 = 80','111+50+20 = 181'),('Troncal B','10+50+30 = 90','111+50+30 = 191')],1,1)
ax.text(10.6,1.25,'Referir agranda el tramo común,\npero lo suma a las dos por igual.\nLa diferencia (10 Ω, en 220 kV) no cambia.\n→ La decisión NO cambia.',fontsize=12.5,color=DARK,va='top')
ax.set_title('Caso 1 · Las alternativas se separan en la red de 220 kV  (1.013 barras: cambian 116, el 11 %)',fontsize=14.5,color=DARK,fontweight='bold',loc='left')
# ---------- Caso 2: se separan en 66 kV ----------
ax=axs[1]; ax.set_xlim(0,15); ax.set_ylim(-0.6,4.4); ax.axis('off')
ax.add_patch(FancyBboxPatch((0.3,0.9),3.3,1.6,boxstyle='round,pad=0.1',fc='#EFEFEF',ec='none',zorder=0))
ax.text(1.95,2.75,'TRAMO COMÚN',ha='center',fontsize=12,color=GREY,fontweight='bold')
L(ax,(0.8,1.6),(3.6,1.6),DARK); nodo(ax,0.8,1.6,'Barra\nanalizada 66 kV'); nodo(ax,3.6,1.6,'punto donde\nse separan\n(66 kV)')
lab(ax,2.2,2.05,'línea 66 kV\n10 Ω → ×11 = 111',DARK)
# A: sube por trafo
L(ax,(3.6,1.6),(5.0,3.4),A); trafo(ax,6.2,3.4,A); L(ax,(5.0,3.4),(5.95,3.4),A); L(ax,(6.45,3.4),(8.6,3.4),A)
lab(ax,6.2,3.95,'trafo 100 (×1 = 100)',A)
# B: sigue en 66 kV
L(ax,(3.6,1.6),(5.0,-0.2),B); L(ax,(5.0,-0.2),(7.4,-0.2),B); trafo(ax,7.8,-0.2,B); L(ax,(8.05,-0.2),(8.6,-0.2),B)
lab(ax,6.2,0.35,'línea 66 kV, 100 km: 40 (×11 = 444)',B); lab(ax,7.8,-0.65,'trafo 20',B)
nodo(ax,8.6,3.4,'Troncal A',c=A,sq=True,pos='right'); nodo(ax,8.6,-0.2,'Troncal B',c=B,sq=True,pos='right')
tabla(ax,10.6,3.0,[('Troncal A','10+100 = 110','111+100 = 211'),('Troncal B','10+40+20 = 70','111+444+20 = 575')],2,1)
ax.text(10.6,1.25,'Aquí una alternativa es «trafo» y la otra\n«línea de 66 kV». Referir multiplica solo\nla línea de 66 kV (×11), no el trafo.\n→ La decisión SÍ cambia (de B a A).',fontsize=12.5,color=DARK,va='top')
ax.set_title('Caso 2 · Las alternativas se separan en la red de menor tensión  (316 barras: cambian 114, el 36 %)',fontsize=14.5,color=DARK,fontweight='bold',loc='left')
fig.suptitle('¿Por qué «Referido» cambia solo algunas barras?  Lo que decide es dónde se separan los caminos',fontsize=17,color=DARK,fontweight='bold',y=0.995)
fig.text(0.5,0.005,'Valores ilustrativos en Ω. Los conteos son reales (1.329 nodos del ENT; se comparan la mejor y la segunda mejor troncal con el método actual).\n'
         'Los 116 cambios del caso 1 ocurren porque, al referir, cambia también el tramo inicial (la barra sube de tensión por otra subestación); solo 3 se deben a la red de 500 kV.',ha='center',fontsize=11,color=GREY)
fig.tight_layout(rect=(0,0.04,1,0.97)); fig.savefig(S+'concepto_donde_se_separan.png',bbox_inches='tight',facecolor='white')
