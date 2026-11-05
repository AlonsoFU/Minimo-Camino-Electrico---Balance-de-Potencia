import matplotlib, pickle, re, numpy as np
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
S='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/fig/'
DARK="#404040"; GREY="#8C8C8C"; XC="#30849B"; RC="#C0392B"; ZC="#404040"; TR="#7B5EA7"; LIN="#E8752A"
fmt=lambda v,d=1:f"{v:,.{d}f}".replace(',','X').replace('.',',').replace('X','.')
def corto(n):
    m=re.match(r'(.*?)_*(\d+)$',n); s=m.group(1).replace('_',' ').strip().title(); return f"{s} {int(m.group(2))}"

# ---------- Figura 1: triángulos de impedancia de 3 elementos reales ----------
el=[('Trafo 66/220 kV\nNueva Guindo',1.45,67.88,TR),('Línea 220 kV\nNueva Guindo – Hualpén',0.69,3.95,XC),('Línea 66 kV\nLoma Colorada – Coronel',27.45,33.48,LIN)]
fig,axs=plt.subplots(1,3,figsize=(15,6.2),dpi=170)
for ax,(n,r,x,c) in zip(axs,el):
    z=np.hypot(r,x); L=max(r,x)*1.05
    ax.plot([0,r],[0,0],color=RC,lw=5); ax.plot([r,r],[0,x],color=XC,lw=5); ax.plot([0,r],[0,x],color=ZC,lw=2.5,ls='--')
    ax.set_xlim(-0.25*L,1.1*L); ax.set_ylim(-0.22*L,1.1*L); ax.set_aspect('equal'); ax.axis('off')
    ax.text(r/2,-0.06*L,f"R = {fmt(r,2)}",ha='center',va='top',fontsize=14,color=RC,fontweight='bold')
    ax.text(r+0.04*L,x/2,f"X = {fmt(x,2)}",ha='left',va='center',fontsize=14,color=XC,fontweight='bold')
    ax.text(r/2-0.05*L,x/2+0.08*L,f"|Z| = {fmt(z,2)}",ha='right',va='center',fontsize=14,color=ZC,fontweight='bold',rotation=0)
    ax.set_title(n,fontsize=15,fontweight='bold',color=c)
    ax.text(0.5,-0.02,f"R/X = {fmt(r/x,2)}\n|Z| es {fmt(100*(z/x-1),1)} % mayor que X",transform=ax.transAxes,ha='center',va='top',fontsize=14,color=DARK,
            bbox=dict(boxstyle='round,pad=0.4',fc='#F4F4F4',ec='none'))
fig.suptitle('Qué agrega la R: |Z| = √(R² + X²)   (Ω referidos a 220 kV, datos del ENT)',fontsize=17,fontweight='bold',color=DARK)
fig.text(0.5,-0.04,'En un trafo la R es casi nada: |Z| ≈ X. En una línea de 220 kV, poco. En una línea de 66 kV la R es casi igual a la X y el tramo "se alarga" ~30 %.\nPor eso sumar R castiga los caminos con muchas líneas de baja tensión y favorece los que pasan por trafos.',
         ha='center',va='top',fontsize=14,color=DARK)
fig.tight_layout(rect=(0,0.02,1,0.95)); fig.savefig(S+'r_que_agrega.png',bbox_inches='tight',facecolor='white'); plt.close()

# ---------- Figuras 2-4: dos rutas que se separan ----------
rutas=pickle.load(open('/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/r_rutas.pkl','rb'))
def fig_rutas(b,arch,titulo):
    (t1,e1),(t2,e2)=rutas[b]
    k=0
    while k<min(len(e1),len(e2)) and e1[k][:2]==e2[k][:2]: k+=1
    com=e1[:k]; ramas=[(t1,e1[k:]),(t2,e2[k:])]
    nmax=max(len(r) for _,r in ramas); W=2.7
    fig,ax=plt.subplots(figsize=(2.2+W*(nmax+1)+4.2,7.4),dpi=170); ax.axis('off')
    yc,ys=0,[2.6,-2.6]; x0,x1=0,W
    # tramo común
    Xc=sum(e[3] for e in com); Rc=sum(e[4] for e in com); Zc=sum(np.hypot(e[3],e[4]) for e in com)
    ax.plot([x0,x1],[yc,yc],color=GREY,lw=7,solid_capstyle='round',zorder=1)
    ax.scatter(x0,yc,s=700,color='white',edgecolor=DARK,lw=2.5,zorder=3); ax.text(x0,yc-0.55,corto(com[0][0]),ha='center',va='top',fontsize=13,fontweight='bold',color=DARK)
    ax.text((x0+x1)/2,yc+0.95,f"tramo común ({len(com)} tramos)\nX {fmt(Xc)} · R {fmt(Rc)}",ha='center',va='bottom',fontsize=12.5,color=GREY)
    ax.text((x0+x1)/2,yc-0.4,"igual para\nlas dos rutas",ha='center',va='top',fontsize=11,color=GREY,style='italic')
    ax.scatter(x1,yc,s=450,color='white',edgecolor=DARK,lw=2,zorder=3); ax.text(x1-0.15,yc+0.35,corto(com[-1][1]),ha='right',va='bottom',fontsize=13,color=DARK,fontweight='bold')
    tot=[]
    for (t,r),y in zip(ramas,ys):
        xs=[x1+W*(i+1) for i in range(len(r))]; px,py=x1,yc
        for i,(a,c,tp,x,rr) in enumerate(r):
            nx_,ny_=xs[i],y
            anul=tp=='T' and x<1e-3
            col=GREY if anul else (TR if tp=='T' else LIN)
            ax.plot([px,nx_],[py,ny_],color=col,lw=3 if anul else 6,ls=(0,(1.5,1.2)) if tp=='T' else '-',zorder=1,alpha=0.6 if anul else 1)
            mx,my=(px+nx_)/2,(py+ny_)/2
            if anul: lab="trafo ANULADO\n(subestación troncal)"; ax.text(mx,my+0.3,lab,ha='center',va='bottom',fontsize=10.5,color=GREY,fontweight='bold')
            else:
                tipo='trafo (se mantiene)' if tp=='T' else 'línea'
                dg=abs(py-ny_)>0.1
                ax.text(mx+(0.3 if dg else 0),my+(0 if dg else 0.32),f"{tipo}\nX {fmt(x)} · R {fmt(rr)}",ha='left' if dg else 'center',va='center' if dg else 'bottom',fontsize=13,color=TR if tp=='T' else LIN,fontweight='bold')
                ax.text(mx-(0.3 if dg else 0),my-(0 if dg else 0.3),f"|Z| {fmt(np.hypot(x,rr))}",ha='right' if dg else 'center',va='center' if dg else 'top',fontsize=13,color=DARK)
            last=i==len(r)-1
            ax.scatter(nx_,ny_,s=800 if last else 380,marker='s' if last else 'o',color=XC if last else 'white',edgecolor='white' if last else DARK,lw=2,zorder=3)
            ax.text(nx_,ny_-(0.55 if not last else 0.6),corto(c),ha='center',va='top',fontsize=12.5 if not last else 14,fontweight='bold' if last else 'normal',color=DARK)
            px,py=nx_,ny_
        Xr=sum(e[3] for e in r); Rr=sum(e[4] for e in r); Zr=sum(np.hypot(e[3],e[4]) for e in r); tot.append((t,Xr,Rr,Zr))
    # tabla
    xt=x1+W*nmax+1.2
    (ta,Xa,Ra,Za),(tb,Xb,Rb,Zb)=tot
    gx=0 if Xa<=Xb else 1; gz=0 if Za<=Zb else 1
    for j,((t,Xr,Rr,Zr),y) in enumerate(zip(tot,ys)):
        s=(f"{corto(t)} — desde la separación\n"
           f"Solo X:  {fmt(Xr)} Ω   {'← gana' if j==gx else ''}\n"
           f"R:          {fmt(Rr)} Ω\n"
           f"Con R (Σ|Z|):  {fmt(Zr)} Ω   {'← gana' if j==gz else ''}")
        ax.text(xt,y,s,ha='left',va='center',fontsize=14,color=DARK,linespacing=1.5,bbox=dict(boxstyle='round,pad=0.6',fc='#EEF5F7' if j==gz else '#FFF1E0',ec='none'))
    ax.set_xlim(-1.2,xt+4.6); ax.set_ylim(-4.6,4.4)
    ax.set_title(titulo,fontsize=19,fontweight='bold',color=DARK)
    fig.text(0.5,0.01,'«Referido + Subestación», Ω referidos a 220 kV. Línea naranja = línea; morado punteado = trafo. Los trafos de subestaciones SIN barra troncal se mantienen con su X y su R;\n'
             'solo se anula el trafo de la subestación troncal (gris). El tramo común suma lo mismo a las dos rutas, así que no decide nada.',ha='center',fontsize=12.5,color=DARK)
    fig.tight_layout(rect=(0,0.06,1,1)); fig.savefig(S+arch,bbox_inches='tight',facecolor='white'); plt.close()
fig_rutas('ANDALIEN______013','r_andalien.png','Andalién 13 kV: con X gana Lagunillas; con R gana Hualpén')
fig_rutas('S.RAFAEL______013','r_san_rafael.png','San Rafael 13 kV: con X gana Los Maquis; con R gana Nogales')
fig_rutas('LA_REINA______013','r_la_reina.png','La Reina 13 kV: con X gana Cerro Navia; con R gana Cerro Chena')
