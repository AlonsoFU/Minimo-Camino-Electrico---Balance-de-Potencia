import pandas as pd, numpy as np
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
X = '/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/homologacion_powerfactory.xlsx'
H = pd.read_pickle('homologacion_lineas_pf.pkl'); H['b'] = H.nombre_ENT.str.replace(r'_\dde\d$', '', regex=True)
def rel(a, b): return np.where((a > 0) & (b > 0), np.maximum(a, b) / np.minimum(a, b), np.nan)
def veredicto(r):
    if pd.isna(r.get('X1_PF')): return 'Sin pareo'
    s, e = rel(r.X1_PF, r.X_sugerida), rel(r.X1_PF, r.X_ENT)
    if e <= 1.01 and not (s <= 1.2): return 'PowerFactory = ENT (no confirma la corrección)'
    if s <= 1.2: return 'PowerFactory confirma la sugerida' + (' (y también = ENT)' if e <= 1.2 else '')
    if e <= 1.2: return 'PowerFactory cerca del ENT'
    return 'PowerFactory distinto de todas'
H['Veredicto'] = H.apply(veredicto, axis=1)
conf = lambda r: '' if r.metodo == 'sin pareo' else ('Alta' if r.candidatos_PF <= 2 and r.similitud_nombre >= 0.85 else ('Media' if r.similitud_nombre >= 0.75 else 'Baja'))
H['Confianza pareo'] = H.apply(conf, axis=1)
cols = {'nombre_ENT': 'Línea ENT', 'kv': 'kV', 'X_ENT': 'X ENT (Ω)', 'X_CNE': 'X CNE (Ω)', 'X_Infotec': 'X Infotécnica (Ω)', 'X_sugerida': 'X sugerida (Ω)', 'linea_PF': 'Línea PowerFactory',
        'X1_PF': 'X PowerFactory (Ω)', 'R1_PF': 'R PowerFactory (Ω)', 'km_PF': 'Largo PF (km)', 'Confianza pareo': 'Confianza pareo', 'metodo': 'Cómo se pareó', 'Veredicto': 'Veredicto', 'otras_PF': 'Otras líneas PF posibles'}
TL = H[list(cols)].rename(columns=cols)
T = pd.read_excel('/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/listado_tramos.xlsx', sheet_name='Tramos', header=1)
lin = T[T.Tipo == 'Línea'][['Etapa', 'Grupo', 'Tramo', 'Confianza', 'Código ENT']]
IM = lin.merge(H.drop_duplicates('b'), left_on='Código ENT', right_on='b', how='left')
IM = pd.DataFrame({'Etapa': IM.Etapa, 'Grupo': IM.Grupo, 'Tramo': IM.Tramo, 'Confianza sugerida': IM.Confianza, 'X ENT (Ω)': IM.X_ENT, 'X CNE (Ω)': IM.X_CNE,
                   'X Infotécnica (Ω)': IM.X_Infotec, 'X sugerida (Ω)': IM.X_sugerida, 'X PowerFactory (Ω)': IM.X1_PF, 'Línea PowerFactory': IM.linea_PF, 'Veredicto': IM.Veredicto.fillna('Sin pareo')})
res = pd.DataFrame({'Todas las líneas del ENT': TL.Veredicto.value_counts(), 'Líneas imprescindibles': IM.Veredicto.value_counts()}).fillna(0).astype(int)
res.loc['Total'] = res.sum()
wb = load_workbook(X)
for n in ['Líneas imprescindibles', 'Líneas', 'Resumen líneas']:
    if n in wb.sheetnames: del wb[n]
wb.save(X)
with pd.ExcelWriter(X, engine='openpyxl', mode='a') as w:
    res.to_excel(w, sheet_name='Resumen líneas'); IM.to_excel(w, sheet_name='Líneas imprescindibles', index=False); TL.to_excel(w, sheet_name='Líneas', index=False)
wb = load_workbook(X); az = PatternFill('solid', fgColor='30849B')
colv = {'PowerFactory confirma': '2E7D32', 'PowerFactory = ENT': 'B23A48', 'PowerFactory distinto': 'B7791F', 'PowerFactory cerca': 'B7791F', 'Sin pareo': '7F7F7F'}
for n, anchos in [('Resumen líneas', {'A': 52, 'B': 24, 'C': 24}), ('Líneas imprescindibles', {'B': 22, 'C': 30, 'J': 40, 'K': 50}), ('Líneas', {'A': 44, 'G': 44, 'M': 50, 'N': 60})]:
    ws = wb[n]
    for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = az; c.alignment = Alignment(wrap_text=True, vertical='center')
    ws.freeze_panes = 'A2'
    for k, v in anchos.items(): ws.column_dimensions[k].width = v
    hdr = [c.value for c in ws[1]]
    if 'Veredicto' in hdr:
        j = hdr.index('Veredicto')
        for r in ws.iter_rows(min_row=2):
            for k, c in colv.items():
                if str(r[j].value).startswith(k): r[j].font = Font(bold=True, color=c)
        for r in ws.iter_rows(min_row=2):
            for c, h in zip(r, hdr):
                if h.endswith('(Ω)'): c.number_format = '0.000'
        ws.auto_filter.ref = f'A1:{ws.cell(1, len(hdr)).column_letter}{ws.max_row}'
ws = wb['Leeme']
ws.append(['Líneas', 'Se parean por los extremos (barras homologadas que caen en la misma subestación) o, si no, por el nombre de la línea PF. Se elige por nombre y número de circuito, nunca por la X, para no sesgar la comparación.'])
ws.append(['Ojo', 'PowerFactory no es una fuente independiente: su X es idéntica a la del ENT en 316 de 990 líneas (y a la de Infotécnica en 227). Cuando PowerFactory = ENT, no confirma que el ENT esté bien: puede ser el origen del dato.'])
for r in ws.iter_rows(min_row=ws.max_row - 1): r[0].font = Font(bold=True); r[1].alignment = Alignment(wrap_text=True, vertical='top')
order = ['Leeme', 'Resumen', 'Propuesta', 'Resumen líneas', 'Líneas imprescindibles', 'Líneas']; wb._sheets = [wb[n] for n in order]
wb.save(X); print(res); print(IM.Veredicto.value_counts().to_dict())
