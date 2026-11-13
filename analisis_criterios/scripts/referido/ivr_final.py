import pandas as pd, numpy as np, re
OUT='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/'
X='/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/tramos_sensibles_iny_ret.xlsx'
R=pd.read_pickle(OUT+'ivr_tramos.pkl'); D=pd.read_pickle(OUT+'ivr_tramos_det.pkl')
exec(open(OUT+'ivr_tramos.py').read().split("G = nx.Graph()")[0].split("V = pd.read_pickle")[0].replace("exec(open('con_r.py')","exec(open(OUT+'con_r.py')").replace("exec(open('con_r_plata.py')","exec(open(OUT+'con_r_plata.py')"))
o=esc(True,m3); d=o.assign(u=np.minimum(o['Barra A'],o['Barra B']).astype(int),v=np.maximum(o['Barra A'],o['Barra B']).astype(int))
nombres=d.groupby(['u','v'])['Nombre'].apply(lambda s:' | '.join(s)); es_tr=T.groupby([d.u,d.v]).any()
k_of={n:k for k,n in nombres.items()}
R['Tipo']=['Trafo' if es_tr[k_of[n]] else 'Línea' for n in R['Trafo (ENT)']]
D['nombre']=[nombres[k] for k in D.k]
def con_sug(row):
    r=row['X ENT ÷ X sugerida']
    if pd.isna(r) or not str(row['Validación']).startswith('DISCREPA'): return pd.Series({'Barras si se corrige al sugerido':0,'MM$/mes si se corrige':0.0})
    c=1/r; g=D[D.nombre==row['Trafo (ENT)']]
    s=g[(g.lado=='sube')&(g.cambio_req<=c-1)] if c>1 else g[(g.lado=='baja')&(g.cambio_req<=1-c)]
    s=s.drop_duplicates('barra'); return pd.Series({'Barras si se corrige al sugerido':len(s),'MM$/mes si se corrige':round(s.MMs.sum(),1)})
R=pd.concat([R,R.apply(con_sug,axis=1)],axis=1).rename(columns={'Trafo (ENT)':'Tramo (ENT)'})
R=R[['Tramo (ENT)','Tipo']+[c for c in R.columns if c not in ('Tramo (ENT)','Tipo')]]
R=R.sort_values(['MM$/mes si se corrige','MM$/mes ≤50 %'],ascending=False)
print('tramos en partes decisivas:',len(R),' trafos:',int((R.Tipo=='Trafo').sum()),' líneas:',int((R.Tipo=='Línea').sum()))
print('frágiles (≤20 %):',int((R['Barras ≤20 %']>0).sum()),'  DISCREPA:',int(R['Validación'].astype(str).str.startswith('DISCREPA').sum()),
      '  que cambian algo si se corrigen:',int((R['Barras si se corrige al sugerido']>0).sum()))
pd.set_option('display.width',220); pd.set_option('display.max_colwidth',44)
print(R[R['Barras si se corrige al sugerido']>0][['Tramo (ENT)','Tipo','X ENT ÷ X sugerida','Barras si se corrige al sugerido','MM$/mes si se corrige']].to_string(index=False))
Dx=D.assign(**{'Cambio requerido (%)':(D.cambio_req*100).round(1)}).drop(columns=['k','cambio_req']).rename(columns={'nombre':'Tramo (ENT)','barra':'Barra','troncal':'Troncal','segunda':'Segunda troncal','lado':'X debe','ret_MW':'Iny+ret (MW)','MMs':'MM$/mes'})
nota=pd.DataFrame({'Nota':['«Referido + trafo troncal», X referida a 220 kV. Barras con inyección o retiro (hoja 05, sin Tx): 700, 22.705 MW. Precios PN2604.',
 'Margen = d(2ª troncal) − d(ganadora). Tramo del camino ganador: da vuelta la barra si su X sube ≥ margen/X (cota inferior); del camino a la 2ª: si baja ≥ margen/X.',
 'Tramos comunes a ambos caminos no cambian el orden. Trafos que tocan la barra troncal: anulados, no aplican.',
 '"Si se corrige al sugerido": aplica el valor sugerido de la validación previa (solo DISCREPA) en la dirección que corresponde.']})
with pd.ExcelWriter(X,engine='openpyxl') as w:
    R.to_excel(w,sheet_name='Tramos',index=False); Dx.sort_values('Cambio requerido (%)').to_excel(w,sheet_name='Barras',index=False); nota.to_excel(w,sheet_name='Notas',index=False)
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
wb=load_workbook(X)
for ws in wb.worksheets:
    for c in ws[1]: c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='30849B'); c.alignment=Alignment(wrap_text=True,vertical='center')
    for col in ws.columns: ws.column_dimensions[col[0].column_letter].width=max(11,min(60,max(len(str(c.value or '')) for c in col[:300])+2))
    ws.freeze_panes='B2'
wb.save(X)
