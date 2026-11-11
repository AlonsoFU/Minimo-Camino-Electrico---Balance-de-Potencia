import pandas as pd, numpy as np
OUT='/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/'
X='/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/tramos_decisivos.xlsx'
F=pd.read_pickle(OUT+'decisivos.pkl'); D=pd.read_pickle(OUT+'decisivos_det.pkl'); V=pd.read_pickle(OUT+'validacion.pkl')
plan=pd.DataFrame({'Paso':['1. Normalizar','2. Clasificar','3. Filtrar','4. Probar uno a uno','5. Priorizar','6. Iterar'],
 'Qué se hace':['Marcar diferencias de representación (razón ≈ ×2, ×½, ×3, ×⅓: paralelos, bancos, base MVA)',
  'Clasificación de la validación previa (revision/output/homologacion_clasificada.xlsx): CORRECTO / DISCREPA_* / SIN_REFERENCIA, con valor sugerido',
  'Solo tramos DISCREPA con valor sugerido; se omiten los trafos anulados por el criterio',
  'Se cambia la X de UN tramo al valor sugerido y se recalcula la troncal de las 1.442 barras',
  'Orden por MM$/mes = Σ |Δ precio PN2604| × MW iny+ret / 1000',
  'Corregir los decisivos verificados, recalcular y repetir (pendiente)'],
 'Estado':['Hecho','Hecho (reutilizado)','Hecho','Hecho','Hecho','Pendiente']})
res=[]
for c in ['Ref+Trafo troncal','Hoy']:
    f=F[F.Criterio==c]; d=f[f['Barras que cambian']>0]
    res.append({'Criterio':c,'Tramos DISCREPA probados':len(f),'Decisivos':len(d),'Decisivos con plata':int((d['MM$/mes']>0).sum()),
                'De ellos, posible representación':int((d.iloc[:,9]=='Sí').sum()),'Barras afectadas (únicas)':D[D.Criterio==c].Barra.nunique()})
res=pd.DataFrame(res)
cls=V.clasificacion_validacion.value_counts().rename_axis('Clasificación').reset_index(name='Tramos')
with pd.ExcelWriter(X,engine='openpyxl') as w:
    plan.to_excel(w,sheet_name='Plan',index=False)
    res.to_excel(w,sheet_name='Resumen',index=False); cls.to_excel(w,sheet_name='Resumen',index=False,startrow=len(res)+3)
    for c,n in [('Ref+Trafo troncal','Decisivos Ref+Trafo troncal'),('Hoy','Decisivos Hoy')]:
        F[(F.Criterio==c)&(F['Barras que cambian']>0)].drop(columns='Criterio').sort_values('MM$/mes',ascending=False).to_excel(w,sheet_name=n,index=False)
    D.sort_values(['Criterio','Tramo ENT']).to_excel(w,sheet_name='Barras afectadas',index=False)
    V[['nombre_ENT','clasificacion_validacion','accion_propuesta','X_ENT','X_CNE','X_Infotec','valor_sugerido','fuente_valor_sugerido','posible_representacion','conf_CNE','conf_Infotec']].to_excel(w,sheet_name='Validación tramos',index=False)
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
wb=load_workbook(X)
for ws in wb.worksheets:
    hdr={1} if ws.title!='Resumen' else {1,len(res)+4}
    for r in hdr:
        for c in ws[r]:
            if c.value is not None: c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='30849B'); c.alignment=Alignment(wrap_text=True,vertical='center')
    for col in ws.columns: ws.column_dimensions[col[0].column_letter].width=max(11,min(60,max(len(str(c.value or '')) for c in col[:60])+2))
    if ws.title!='Resumen': ws.freeze_panes='B2'
wb.save(X); print(res.to_string(index=False))
