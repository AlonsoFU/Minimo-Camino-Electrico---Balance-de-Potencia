"""Escribe datos/listado_tramos.xlsx (Leeme, Revisión, Zonas, Zonas por variante, Rondas, Verificación, Detalle)
y reemplaza la hoja 16 de datos/resultados.xlsx con las zonas definitivas."""
exec(open('listado_verif.py').read().split("out = {'zonas'")[0])
F = pd.read_pickle(OUT + 'listado_final.pkl'); Lst, RZ, RV, RR, zord = F['Lst'], F['RZ'], F['RV'], F['RR'], F['zord']
DAT = '/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/'
# independientes como bloque (ronda 4 y ronda 6)
extra = []
for v, (an, modo) in VAR.items():
    M = est_f(True, an, modo, [])
    for nom, l in [('Fopaco (independiente)', ['TAP_FOPACO____154->FOPACO________154']), ('Turibe–Esmeralda (independiente)', ['TURIBE________110->ESMERALDA_____110']),
                   ('Independientes chicos', list(Lst[(Lst.Zona == 'Independiente') & (Lst.Orden == 6)].Tramo))]:
        s = dif(est_f(True, an, modo, l), M)
        extra.append({'Variante': v, 'Zona': nom, 'Tramos': len(l), 'Barras que cambian': s['barras'], 'Más cerca': s['cerca'], 'Más lejos': s['lejos'],
                      'Δ km promedio': s['km'], 'MM$/mes': s['mm'], 'MM$ sube': s['sube'], 'MM$ baja': s['baja']})
indep = set(Lst[Lst.Zona == 'Independiente'].Tramo)
RZv = pd.concat([RZ[~RZ.Zona.isin(indep)], pd.DataFrame(extra)], ignore_index=True)
orden_filas = [z for z in zord if z not in indep]
orden_filas = orden_filas[:orden_filas.index('Kimal')] + ['Fopaco (independiente)', 'Turibe–Esmeralda (independiente)', 'Kimal'] + orden_filas[orden_filas.index('Kimal') + 1:] + ['Independientes chicos', 'Lista completa', 'Todos (668)']
ronda_z = {z: int(Lst[Lst.Zona == z].Orden.iloc[0]) for z in orden_filas if (Lst.Zona == z).any()}
ronda_z.update({'Fopaco (independiente)': 4, 'Turibe–Esmeralda (independiente)': 4, 'Independientes chicos': 6})
lect = {'Ventanas': 'Acerca: 33 de 37 barras quedan más cerca.',
        'Maule–Itahue–Teno–Linares': 'Acerca mucho (unos 50 km). La plata depende de la variante: 6 a 62 MM$/mes.',
        'Santiago oriente': 'Aleja: 19 a 24 barras quedan más lejos y a lo más 1 más cerca. Mucha plata: revisar bien.',
        'Mulchén': 'Aleja unos 53 km. Solo mueve con los 4 tramos juntos; 3 de 4 da 270 MM$/mes.',
        'Aconcagua (Calera–S.Rafael)': 'Depende de X o R: con X aleja (9 de 14 barras), con R acerca (13 de 14).',
        'Melipilla–Isla de Maipo': 'Acerca. Poca plata.', 'Atacama (Cardones–Maitencillo–D.Almagro)': 'Acerca. Poca plata.',
        'Dichas 220': '1 barra, sin plata.', 'Fopaco (independiente)': 'Solo mueve con R: 3 barras a unos 416 km más lejos, 39 MM$/mes. Caso raro (#305): revisar la R en la ficha.',
        'Turibe–Esmeralda (independiente)': 'Acerca 5 barras unos 45 km, 9 MM$/mes.',
        'Kimal': 'Casi neutro corregida completa. Nunca solo L.Changos–Kimal (227 MM$/mes).',
        'El Laurel 220': 'Solo mueve con X (11 barras, 3 MM$/mes).', 'Codegua 66': '1 barra, sin plata.',
        'Independientes chicos': 'Con X acercan unas 40 barras, poca plata (Coronel, Concepción, A. de Ribera y Talcahuano mueven las mismas).',
        'Lista completa': 'Acerca en promedio.', 'Todos (668)': 'Casi igual que la lista: la lista captura el efecto.'}
rng = lambda s: (f'{s.min():g}' if s.min() == s.max() else f'{s.min():g} a {s.max():g}') if s.notna().any() else '—'
rows = []
for z in orden_filas:
    g = RZv[RZv.Zona == z]
    rows.append({'Ronda': ronda_z.get(z, ''), 'Zona': z, 'Tramos': int(g.Tramos.iloc[0]), 'Barras que cambian': rng(g['Barras que cambian']), 'Más cerca': rng(g['Más cerca']),
                 'Más lejos': rng(g['Más lejos']), 'Δ km promedio': rng(g['Δ km promedio'].round(0)), 'MM$/mes': rng(g['MM$/mes'].round(0)), 'Lectura': lect.get(z, '')})
ZS = pd.DataFrame(rows)
# efecto de la zona en cada fila de revisión
efz = {}
for z in orden_filas:
    r = ZS[ZS.Zona == z].iloc[0]; efz[z] = f"{r['Barras que cambian']} barras · {r['Más cerca']} cerca / {r['Más lejos']} lejos · {r['MM$/mes']} MM$/mes"
def ef_tramo(t, z):
    if z != 'Independiente': return efz[z]
    g = RZ[RZ.Zona == t]; return f"{rng(g['Barras que cambian'])} barras · {rng(g['Más cerca'])} cerca / {rng(g['Más lejos'])} lejos · {rng(g['MM$/mes'].round(1))} MM$/mes"
NUC = set(pd.read_pickle(OUT + 'nucleo_N2.pkl'))
GR = pd.read_pickle(OUT + 'grupos_min2.pkl')['grupos']; TRs = pd.read_pickle(OUT + 'grupos_min.pkl')['TR']
import re as _re
def corto(t):
    a, b = t.split('->'); na, va = _re.match(r'(.*?)_*(\d+)$', a).groups(); nb, vb = _re.match(r'(.*?)_*(\d+)$', b).groups()
    na, nb = na.strip('_').replace('_', ' ').title(), nb.strip('_').replace('_', ' ').title(); va, vb = str(int(va)), str(int(vb))
    return f'{na} {va}/{vb}' if va != vb else f'{na}–{nb} {va}'
corta = {'Maule–Itahue–Teno–Linares': 'Maule', 'Aconcagua (Calera–S.Rafael)': 'Aconcagua', 'Melipilla–Isla de Maipo': 'Melipilla',
         'Atacama (Cardones–Maitencillo–D.Almagro)': 'Atacama', 'Santiago oriente': 'Santiago oriente'}
grupo_de, socios = {}, {}
for z, bl in GR.items():
    for i, b in enumerate(bl, 1):
        lab = corta.get(z, z) + (f' {i}' if len(bl) > 1 else '')
        for t in b: grupo_de[t] = lab; socios[t] = ', '.join(corto(x) for x in b if x != t)
for t in Lst.Tramo:
    if t in NUC and t not in grupo_de: grupo_de[t] = 'Independiente'; socios[t] = ''
def tipo(t):
    if t not in NUC: return 'No cambia el resultado final'
    if socios[t] != '': return 'Necesita a su grupo'
    return 'Efecto propio' if mal_solo.get(t, 0) == 0 else 'Efecto propio, casi (deja barras mal por menos de 1 MM$/mes)'
mal_solo = {t: max(x[0] for x in TRs[t].values()) for t in TRs}
Rev = pd.DataFrame({'Orden': Lst.Orden, 'Zona': Lst.Zona, 'Crítico / vecino': Lst['Crítico / vecino'].str.split(' \\(').str[0],
                    'Imprescindible (de los 48)': ['Sí' if t in NUC else '' for t in Lst.Tramo], 'Grupo': [grupo_de.get(t, '') for t in Lst.Tramo],
                    'Se corrige junto con': [socios.get(t, '') for t in Lst.Tramo], 'Efecto': [tipo(t) for t in Lst.Tramo],
                    'Solo: barras en troncal equivocada (máx.)': [mal_solo.get(t, 0) for t in Lst.Tramo], 'Tipo': Lst.Tipo, 'Tramo': Lst.Tramo,
                    'Tensión (kV)': Lst['Tensión (kV)'], 'Unidades en paralelo': Lst['Circuitos/unidades en paralelo'], 'X ENT (Ω)': Lst['X ENT'], 'X sugerida (Ω)': Lst['X sugerida'],
                    'Fuente sugerida': Lst['Fuente sugerida'], 'Fuentes confiables (1/CNE/Infotec/0)': Lst['revision (1 / CNE / Infotec / 0)'],
                    'Efecto de corregir su zona (4 variantes)': [ef_tramo(t, z) for t, z in zip(Lst.Tramo, Lst.Zona)],
                    'Si se omite: MM$/mes': Lst['Si se omite: MM$/mes (máx. 4 variantes)'],
                    'X según ficha (Ω)': '', 'R según ficha (Ω)': '', 'Ficha (documento y fecha)': '', '¿Corregir?': '', 'Valor aplicado (Ω)': '', 'Responsable': '', 'Fecha': '', 'Comentario': ''})
nota = ['QUÉ ES: los 116 tramos (líneas y trafos) del ENT cuyo dato difiere de CNE o Infotécnica y que cambian la troncal de alguna barra, solos o junto con otros. Los otros 552 tramos que difieren no mueven ninguna barra.',
        'BASE: método nuevo «Referido + subestación troncal» (reactancias referidas a 220 kV y medidas hasta la subestación troncal), en 4 variantes: TT (anula solo el trafo que toca la barra troncal) o MS (toda la subestación), con X o con |Z| (R). Dato corregido = valor sugerido de la validación (homologación ENT–CNE–Infotécnica). Cada efecto se mide contra el mismo método con el ENT actual.',
        'CÓMO USARLO: revisar por Orden (ronda) y por Zona en la hoja Revisión. Cada zona se corrige completa, nunca a medias. Llenar las columnas amarillas con la ficha; recién entonces se aplica la corrección y se recalcula.',
        'ZONA: tramos que se corrigen juntos porque corregir solo una parte deja barras en una troncal que no es la final. Se definió por interacción: dos tramos o grupos interactúan si corregirlos juntos no da lo mismo que corregirlos por separado (prueba por pares, 820 pares en las 4 variantes; umbral 1 MM$/mes). Independiente: se puede corregir solo.',
        'CRÍTICO: cambia la troncal de alguna barra por sí solo. VECINO: solo importa junto con un crítico de su zona. COMBINADO: Mulchén, ningún tramo mueve solo; mueven los 4 juntos.',
        'ORDEN: 1 Ventanas; 2 Maule–Itahue–Teno–Linares; 3 Santiago oriente y Mulchén (alejan barras: revisar bien); 4 Aconcagua, Melipilla–Isla de Maipo, Atacama, Dichas 220, Fopaco y Turibe–Esmeralda; 5 Kimal (completa); 6 El Laurel, Codegua e independientes chicos.',
        'VERIFICACIÓN (hoja Verificación): cada zona da el mismo efecto corregida sola que dentro de la lista completa (Ventanas difiere en 6 barras y 0,3 MM$/mes). La lista completa da lo mismo que corregir los 668 salvo 5–14 barras y 2–4 MM$/mes. Coronel, Concepción 154/66, A. de Ribera 154/66 y Talcahuano 154/66 mueven las mismas barras: cualquiera de ellos basta, y juntos no se contradicen.',
        'IMPRESCINDIBLE (48 tramos): con solo estos corregidos se obtiene exactamente el mismo resultado que con los 116, en las 4 variantes (0 barras distintas), y ninguno se puede quitar sin cambiarlo. Funciona también zona por zona y etapa por etapa (única diferencia: Codegua 66, 1 barra y 0,1 MM$/mes). El conjunto no es único (se obtuvo quitando tramos de a uno, en dos pasadas) y vale para los valores sugeridos: si la ficha da otro valor o confirma el del ENT, se recalcula. Los demás se revisan igual, pero no cambian el resultado.',
        'GRUPO: imprescindibles que se corrigen juntos para ver su efecto real. Corregido solo, cada grupo da exactamente su parte del resultado final, sin dejar barras en una troncal equivocada, y cualquier combinación de grupos da la suma de sus efectos (probado con todas las combinaciones, 4 variantes). EFECTO: "Efecto propio" = el tramo solo ya da su efecto real; "Necesita a su grupo" = solo da un efecto falso, incompleto o ninguno (ej. Maule 154/66 solo deja 21 barras en una troncal equivocada). "Solo: barras en troncal equivocada": cuántas barras deja mal el tramo corregido solo (máximo de las 4 variantes).',
        'Fuentes confiables: 1 = CNE e Infotécnica confiables; CNE = solo CNE; Infotec = solo Infotécnica; 0 = ninguna. "Si se omite": cuánto cambia el resultado final si ese tramo no se corrige (máximo de las 4 variantes).',
        'MM$/mes = Σ |Δ precio| × MW de inyección y retiro de las barras que cambian. "Más cerca / más lejos": la troncal nueva queda a más de 5 km más cerca o más lejos de la barra que la anterior.',
        'Hojas: Revisión (para llenar) · Zonas (resumen, rango de las 4 variantes) · Zonas por variante · Rondas (avance acumulado y contra PN2604) · Verificación · Detalle (valores CNE e Infotécnica, R, pareo y efecto de cada tramo solo).']
X = DAT + 'listado_tramos.xlsx'
with pd.ExcelWriter(X, engine='openpyxl') as w:
    pd.DataFrame({'Nota': nota}).to_excel(w, sheet_name='Leeme', index=False)
    Rev.to_excel(w, sheet_name='Revisión', index=False)
    ZS.to_excel(w, sheet_name='Zonas', index=False)
    RZv.assign(o=RZv.Zona.map({z: i for i, z in enumerate(orden_filas)})).sort_values(['Variante', 'o']).drop(columns='o').to_excel(w, sheet_name='Zonas por variante', index=False)
    RR.sort_values(['Variante', 'Ronda']).to_excel(w, sheet_name='Rondas', index=False)
    RV.to_excel(w, sheet_name='Verificación', index=False)
    Lst.to_excel(w, sheet_name='Detalle', index=False)
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
wb = load_workbook(X)
for ws in wb.worksheets:
    for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='30849B'); c.alignment = Alignment(wrap_text=True, vertical='center')
    for col in ws.columns: ws.column_dimensions[col[0].column_letter].width = max(9, min(48, max(len(str(v.value or '')) for v in col[1:] or [col[0]]) + 2))
    ws.freeze_panes = 'A2'
ws = wb['Leeme']; ws.column_dimensions['A'].width = 170
for r in ws.iter_rows(min_row=2): r[0].alignment = Alignment(wrap_text=True, vertical='top')
ws = wb['Revisión']; ws.freeze_panes = 'G2'
hd = [c.value for c in ws[1]]; ci = hd.index('Imprescindible (de los 48)')
for r in ws.iter_rows(min_row=2):
    if r[ci].value == 'Sí': r[ci].font = Font(bold=True, color='B23A48')
hdr = [c.value for c in ws[1]]; i0 = hdr.index('X según ficha (Ω)')
for c in ws[1][i0:]: c.fill = PatternFill('solid', fgColor='F2C14E'); c.font = Font(bold=True, color='1F2A44')
for c in ws[1][i0:]: ws.column_dimensions[c.column_letter].width = 16
ws.column_dimensions[ws[1][hdr.index('Comentario')].column_letter].width = 40
ws.column_dimensions[ws[1][hdr.index('Ficha (documento y fecha)')].column_letter].width = 28
dv = DataValidation(type='list', formula1='"Sí,No,Pendiente"', allow_blank=True); ws.add_data_validation(dv)
L_ = ws[1][hdr.index('¿Corregir?')].column_letter; dv.add(f'{L_}2:{L_}{ws.max_row}')
banda = PatternFill('solid', fgColor='EAF3F5'); prev = None; on = False
for r in ws.iter_rows(min_row=2):
    if r[1].value != prev: on = not on; prev = r[1].value
    if on:
        for c in r[:i0]: c.fill = banda
ws = wb['Zonas']; ws.column_dimensions['I'].width = 95; ws.column_dimensions['B'].width = 40
for r in ws.iter_rows(min_row=2):
    for c in r: c.alignment = Alignment(wrap_text=True, vertical='top')
wb['Detalle'].freeze_panes = 'F2'
wb.save(X)
# hoja 16 de resultados.xlsx
from openpyxl.utils.dataframe import dataframe_to_rows
XR = DAT + 'resultados.xlsx'; wb = load_workbook(XR); old = wb['16 Zonas cerca-lejos']; idx = wb.sheetnames.index('16 Zonas cerca-lejos'); wb.remove(old)
ws = wb.create_sheet('16 Zonas cerca-lejos', idx)
H = RZv.assign(o=RZv.Zona.map({z: i for i, z in enumerate(orden_filas)})).sort_values(['Variante', 'o']).drop(columns='o')
for r in dataframe_to_rows(H, index=False, header=True): ws.append(r)
for c in ws[1]: c.font = Font(bold=True)
wb.save(XR)
print(ZS.to_string(index=False)); print(Rev.shape)
