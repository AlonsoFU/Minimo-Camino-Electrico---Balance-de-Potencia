import sys, warnings, contextlib, io; warnings.filterwarnings("ignore")
sys.path.insert(0,'/home/user/balance-de-potencia-anual/src/minimo_camino/domain')
import minimo_camino as mc, pandas as pd, networkx as nx, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager
from datetime import date
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
TEAL="#30849B"; ORANGE="#E8752A"; GREY="#8C8C8C"; DARK="#404040"
S='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/'
INP='/home/user/balance-de-potencia-anual/data/minimo_camino/inputs/2025/pre/'; ENT=INP+'Ent2026.xlsx'
ev=pd.read_pickle(S+'criterios_ev.pkl')
grp=ev[(ev.criterio1_origen=='Diferencia nueva del criterio')&(ev.PN2604=='CANDELARIA____220')&(ev.criterio1_troncal=='A.JAHUEL______220')]
barras=mc.cargar_barras(ENT); lineas=mc.cargar_lineas(ENT); linman=mc.cargar_linman(ENT)
full=pd.read_excel(ENT,sheet_name='lineas',header=4); lineas['tipo']=lineas['N_linea'].map(dict(zip(full['Nº'],full['Trafo o Linea'])))
nm=dict(zip(barras['N'].astype(int),barras['Barra']))
pncp=pd.read_excel(INP+'Barras_PNCP.xlsx',sheet_name='barras',usecols='B:E',header=None)
for i in range(10):
    if any('NombrePNCP' in str(v) for v in pncp.iloc[i].values): pncp.columns=pncp.iloc[i].values; pncp=pncp.iloc[i+1:]; break
PN=set(pncp['NombreEnt'].dropna()); SUB={t[:14] for t in PN}
op=mc.filtrar_operativas(lineas,linman,date(2025,12,31)).merge(lineas[['N_linea','tipo']],on='N_linea',how='left')
A=op['Barra A'].map(nm); B=op['Barra B'].map(nm); T=op['tipo']=='T'
def G_(o):
    with contextlib.redirect_stdout(io.StringIO()): agr=mc.agrupar_lineas(o[['N_linea','Nombre','Barra A','Barra B','V','R','X']])
    G=nx.Graph()
    for _,e in agr.dropna(subset=['Xfinal']).iterrows():
        if e['Xfinal']>0: G.add_edge(nm[int(e['Barra_A'])],nm[int(e['Barra_B'])],w=float(e['Xfinal']))
    return G
G0=G_(op); o1=op.copy(); o1.loc[T&(A.str[:14].isin(SUB)|B.str[:14].isin(SUB)),'X']=1e-6; G1=G_(o1)
cdf=pd.read_excel(INP+'conversor_coordenadas_Nodos.xlsx',sheet_name=0,header=None); cdf.columns=cdf.iloc[3].values; cdf=cdf.iloc[4:]
C={r['BarraFacturación']:(float(r['Longitud']),float(r['Latitud'])) for _,r in cdf[['BarraFacturación','Latitud','Longitud']].dropna().iterrows()}
src='TILCOCO2______154'
p0=nx.dijkstra_path(G0,src,'CANDELARIA____220',weight='w'); p1=nx.dijkstra_path(G1,src,'A.JAHUEL______220',weight='w')
print('sin coord en caminos:',[x for x in p0+p1 if x not in C])
# bounding box
pts=[C[x] for x in set(p0+p1+list(grp.barra)+['CANDELARIA____220','A.JAHUEL______220']) if x in C]
lo=[p[0] for p in pts]; la=[p[1] for p in pts]
x0,x1=min(lo)-0.12,max(lo)+0.12; y0,y1=min(la)-0.08,max(la)+0.08
fig,ax=plt.subplots(figsize=(8.2,9.2),dpi=200)
for u,v in G0.edges():
    if u in C and v in C:
        (a,b),(c,d)=C[u],C[v]
        if x0<=a<=x1 and y0<=b<=y1 and x0<=c<=x1 and y0<=d<=y1 and (a,b)!=(c,d):
            ax.plot([a,c],[b,d],color="#D5D5D5",lw=0.8,zorder=1)
def path(p,col,lab):
    xs=[C[x][0] for x in p if x in C]; ys=[C[x][1] for x in p if x in C]
    ax.plot(xs,ys,color=col,lw=3.2,zorder=3,label=lab,solid_capstyle='round')
path(p0,TEAL,f"Hoy: Tilcoco 154 → Candelaria, {str(round(nx.dijkstra_path_length(G0,src,"CANDELARIA____220",weight="w"),1)).replace(".",",")} Ω (sube por trafo Tinguiririca, 13,9 Ω)")
path(p1,ORANGE,f"Criterio 1: Tilcoco 154 → Alto Jahuel, {str(round(nx.dijkstra_path_length(G1,src,"A.JAHUEL______220",weight="w"),1)).replace(".",",")} Ω (trafo Alto Jahuel 220/154 de 48,9 Ω pasa a 0)")
g=grp[grp.barra.isin(C)]
ax.scatter([C[b][0] for b in g.barra],[C[b][1] for b in g.barra],s=22,color=ORANGE,alpha=0.55,edgecolor='white',lw=0.5,zorder=4,label=f"Barras que pasan de Candelaria a Alto Jahuel con el criterio 1 ({len(grp)})")
for t,lab,dx in [('CANDELARIA____220','Candelaria 220 kV\n(sin transformadores)',0.03),('A.JAHUEL______220','Alto Jahuel 220 kV\n(trafos a 154, 110 y 66 kV)',0.03)]:
    ax.scatter(*C[t],s=260,color=TEAL,edgecolor='white',lw=1.5,zorder=6,marker='s')
    ax.text(C[t][0]+dx,C[t][1],lab,fontsize=9,color=TEAL,fontweight='bold',va='center',zorder=7)
ax.scatter(*C[src],s=160,color=ORANGE,edgecolor='white',lw=1.5,zorder=6)
ax.text(C[src][0]+0.03,C[src][1]-0.02,"Tilcoco 154 kV\n(190 MW)",fontsize=9,color=ORANGE,fontweight='bold',zorder=7)
for t,lab in [('TINGUIRIRICA__220','Tinguiririca'),('PTENEGRO______220','Puente Negro'),('PAINE_________154','Paine'),('P.CORTES2_____154','Punta de Cortés')]:
    if t in C: ax.text(C[t][0]+0.02,C[t][1]+0.012,lab,fontsize=8,color=DARK,zorder=7)
ax.set_xlim(x0,x1); ax.set_ylim(y0,y1); ax.set_aspect(1/0.83)
ax.set_xlabel("Longitud",color=DARK); ax.set_ylabel("Latitud",color=DARK)
for s in ['top','right']: ax.spines[s].set_visible(False)
ax.legend(loc='upper center',bbox_to_anchor=(0.5,-0.07),fontsize=8.5,frameon=False)
ax.set_title("Efecto del criterio 1: Alto Jahuel atrae barras más cercanas a Candelaria",fontsize=11,color=DARK,fontweight='bold')
fig.savefig(S+'mapa_candelaria_ajahuel.png',bbox_inches='tight',facecolor='white')
print(len(g),'de',len(grp),'barras con coordenadas')
