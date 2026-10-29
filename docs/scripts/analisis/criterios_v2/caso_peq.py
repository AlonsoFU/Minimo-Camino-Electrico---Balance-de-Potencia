import pickle, networkx as nx, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf"]:
    try: font_manager.fontManager.addfont(f)
    except Exception: pass
plt.rcParams["font.family"]="Carlito"
S='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/'
INP='/home/user/balance-de-potencia-anual/data/minimo_camino/inputs/2025/pre/'
cdf=pd.read_excel(INP+'conversor_coordenadas_Nodos.xlsx',sheet_name=0,header=None); cdf.columns=cdf.iloc[3].values; cdf=cdf.iloc[4:]
C={r['BarraFacturación']:(float(r['Longitud']),float(r['Latitud'])) for _,r in cdf[['BarraFacturación','Latitud','Longitud']].dropna().iterrows()}
G=pickle.load(open(S+'grafos.pkl','rb'))['P_C1']
DARK="#404040"; A="#30849B"; B="#E8752A"; GREY="#9A9A9A"
o='PEQ___________220'; tL='LAGUNAS_______220'; tC='CRUCERO_______220'
pL=nx.dijkstra_path(G,o,tL,weight='w'); pC=nx.dijkstra_path(G,o,tC,weight='w')
dL=nx.dijkstra_path_length(G,o,tL,weight='w'); dC=nx.dijkstra_path_length(G,o,tC,weight='w')
box=(-70.4,-68.6,-22.8,-20.6)
CC={k:v for k,v in C.items() if box[0]<v[0]<box[1] and box[2]<v[1]<box[3]}
fig,ax=plt.subplots(figsize=(9,11.5),dpi=170)
for u,v in G.edges():
    if u in CC and v in CC: ax.plot([CC[u][0],CC[v][0]],[CC[u][1],CC[v][1]],color="#DDDDDD",lw=0.8,zorder=1)
def path(p,c,ls,lw):
    q=[x for x in p if x in CC]; ax.plot([CC[x][0] for x in q],[CC[x][1] for x in q],color=c,lw=lw,ls=ls,zorder=3,solid_capstyle='round')
path(pC,B,'--',3); path(pL,A,'-',5)
for t,c,n in [(tL,A,'Lagunas'),(tC,B,'Crucero')]:
    ax.scatter(*CC[t],s=260,marker='s',color=c,edgecolor='white',lw=1.5,zorder=6); ax.text(CC[t][0]+0.04,CC[t][1],n,fontsize=13,color=c,fontweight='bold',va='center')
ax.scatter(*CC[o],s=180,color='white',edgecolor=DARK,lw=2.2,zorder=6); ax.text(CC[o][0]+0.04,CC[o][1]+0.03,'PEQ 220 kV',fontsize=12.5,color=DARK,fontweight='bold')
for n,lab in [('COLLAHUASI____220','Collahuasi')]:
    if n in CC: ax.text(CC[n][0]+0.04,CC[n][1],lab,fontsize=10.5,color=GREY)
ax.text(0.5,-0.02,f"Todos los criterios (hoy, «Referido», «Referido + Subestación»)\nasignan Lagunas.  PN2604 asigna Crucero.\n\n"
        f"→ Lagunas: {str(round(dL,1)).replace(".",",")} Ω  (a 96 km)\n→ Crucero: {str(round(dC,1)).replace(".",",")} Ω  (a 69 km)\n\n"
        "PEQ cuelga eléctricamente de Lagunas: para llegar a Crucero\nhay que pasar primero por Lagunas y seguir por Collahuasi\ny Encuentro (≈ 65 Ω más).",
        transform=ax.transAxes,va='top',ha='center',fontsize=12,color=DARK,bbox=dict(boxstyle='round,pad=0.5',fc='white',ec='#CCCCCC'))
ys=[CC[x][1] for x in pL+pC if x in CC]; ax.set_ylim(min(ys)-0.25,max(ys)+0.15); ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect(1/0.93)
for s_ in ax.spines.values(): s_.set_color('#DDDDDD')
ax.set_title('PEQ 220 kV: más cerca de Crucero en el mapa, pero conectada a Lagunas',fontsize=14.5,color=DARK,fontweight='bold')
fig.text(0.5,-0.13,'Línea azul = camino a Lagunas (elegido). Línea naranja punteada = camino a Crucero (asociación PN2604). Gris = red del ENT.',ha='center',fontsize=10,color=GREY)
fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig(S+'fig/caso_peq.png',bbox_inches='tight',facecolor='white')
