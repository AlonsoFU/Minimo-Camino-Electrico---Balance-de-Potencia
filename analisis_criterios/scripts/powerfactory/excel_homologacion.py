import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
H = pd.read_pickle('homologacion_pf.pkl')
o = {'Alta': 2, 'Media': 1, 'Baja': 0, 'Sin candidato': -1}
H = H.assign(_o=H.confianza.map(o)).sort_values(['troncal', '_o', 'barra_balance'], ascending=[False, True, True]).drop(columns='_o')
P = pd.DataFrame({'Barra Balance': H.barra_balance, 'Troncal PNCP': H.troncal.map({True: 'Sí', False: ''}), 'kV': H.kv,
                  'Subestación PowerFactory (propuesta)': H.subestacion_pf, 'Barras PowerFactory': H.terminales_pf, 'kV PowerFactory': H.kv_pf,
                  'Puntaje': H.puntaje, 'Segunda opción': H.segunda_opcion, 'Confianza': H.confianza,
                  '¿Correcta? (Sí/No)': '', 'Subestación correcta (si no)': '', 'Comentario': ''})
res = pd.crosstab(H.confianza, H.troncal.map({True: 'Troncales PNCP', False: 'Otras barras'}), margins=True, margins_name='Total').reindex(['Alta', 'Media', 'Baja', 'Sin candidato', 'Total'])
leeme = [('Qué es', 'Propuesta de correspondencia entre las barras del Balance (1.445, incluidas las 50 troncales PNCP) y las barras del modelo PowerFactory, solo por nombre y tensión.'),
         ('Fuente', 'Exportación de terminales (ElmTerm) del Administrador de datos de PowerFactory: 31.667 barras, nombre, carpeta o subestación y kV.'),
         ('Cómo se hizo', 'Se normalizan los nombres (sin tildes, sin "S/E", "kV", números ni sufijos) y se comparan con las barras del Balance de la misma tensión, considerando abreviaturas (L. = Los/Las, A. = Alto, P. = Puerto/Pan…). En media tensión se acepta otro valor nominal (13,2 contra 15 kV) con una penalización.'),
         ('Confianza', 'Alta: puntaje ≥ 0,95 y sin otra subestación cercana en puntaje. Media: puntaje ≥ 0,80. Baja: menor. Sin candidato: no hay barra parecida con esa tensión (no está en el modelo o se llama muy distinto).'),
         ('Qué falta', 'Revisar a mano las de confianza media, baja y sin candidato (columnas amarillas), empezando por las troncales. Las de confianza alta se revisaron con una muestra y salieron bien, pero no una por una.'),
         ('Para qué', 'Es lo único que hay que homologar para calcular el mínimo camino con los datos de PowerFactory: la red se arma con los nombres de PowerFactory (#307).')]
X = '/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/homologacion_powerfactory.xlsx'
with pd.ExcelWriter(X, engine='openpyxl') as w:
    pd.DataFrame(leeme, columns=['Tema', 'Explicación']).to_excel(w, sheet_name='Leeme', index=False)
    res.to_excel(w, sheet_name='Resumen'); P.to_excel(w, sheet_name='Propuesta', index=False)
wb = load_workbook(X); az = PatternFill('solid', fgColor='30849B'); am = PatternFill('solid', fgColor='F2C14E')
for ws in wb.worksheets:
    for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = az; c.alignment = Alignment(wrap_text=True, vertical='center')
    ws.freeze_panes = 'A2'
ws = wb['Leeme']; ws.column_dimensions['A'].width = 16; ws.column_dimensions['B'].width = 140
for r in ws.iter_rows(min_row=2): r[0].font = Font(bold=True); r[1].alignment = Alignment(wrap_text=True, vertical='top')
ws = wb['Resumen']; ws.column_dimensions['A'].width = 16
for k in 'BCD': ws.column_dimensions[k].width = 16
ws = wb['Propuesta']; ws.freeze_panes = 'B2'; ws.auto_filter.ref = f'A1:L{ws.max_row}'
for k, v in {'A': 20, 'B': 9, 'C': 6, 'D': 44, 'E': 44, 'F': 9, 'G': 8, 'H': 40, 'I': 12, 'J': 12, 'K': 30, 'L': 30}.items(): ws.column_dimensions[k].width = v
for c in ws[1][9:]: c.fill = am; c.font = Font(bold=True, color='1F2A44')
col = {'Alta': '2E7D32', 'Media': 'B7791F', 'Baja': 'B23A48', 'Sin candidato': 'B23A48'}
for r in ws.iter_rows(min_row=2):
    r[8].font = Font(bold=True, color=col[r[8].value])
    if r[1].value == 'Sí': r[0].font = Font(bold=True)
dv = DataValidation(type='list', formula1='"Sí,No"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'J2:J{ws.max_row}')
wb.save(X); print(res)
