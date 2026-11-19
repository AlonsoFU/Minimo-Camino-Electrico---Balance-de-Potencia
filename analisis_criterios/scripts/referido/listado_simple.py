"""Listado simple: datos/listado_tramos.xlsx con 5 hojas sin información repetida (Leeme, Etapas, Grupos, Tramos, Resto).
Todo el detalle queda en datos/listado_tramos_respaldo.xlsx (lo genera el mismo código de listado_excel2.py)."""
src_ = open('listado_excel2.py').read().replace("X = DAT + 'listado_tramos.xlsx'", "X = DAT + 'listado_tramos_respaldo.xlsx'")
exec(src_)
BASE_TXT = ('BASE: método nuevo = reactancias referidas a 220 kV y medidas hasta la subestación troncal. Los efectos son el rango de sus 4 variantes '
            '(anular solo el trafo troncal o toda la subestación; con X o con R), contra el mismo método con el ENT actual. '
            'Dato corregido = valor sugerido de la validación ENT–CNE–Infotécnica.')
R_ = Rev.copy(); R_['imp'] = R_['Imprescindible (de los 48)'] == 'Sí'; R_['t'] = R_['Tramo (nombre ENT)']
_ren = {'Taps.Rafael': 'Tap S.Rafael', 'Isladmaipo': 'Isla de Maipo', 'Elmonte': 'El Monte', 'Elmaiten': 'El Maitén', 'Elpaico': 'El Paico', 'Ellaurel': 'El Laurel',
        'Santaclara': 'Santa Clara', 'Crucerosalaux': 'Crucero Sal Aux', 'Mulchen': 'Mulchén', 'Charrua': 'Charrúa', 'San Cristobal': 'San Cristóbal', 'Concepcion': 'Concepción',
        'N.Pichirropul': 'N. Pichirropulli', 'Tap Loma Col': 'Tap Loma Colorada', 'Polvora': 'Pólvora', 'S.Andres': 'S.Andrés'}
def lindo(t):
    n = corto(t)
    for a, b in _ren.items(): n = n.replace(a, b)
    return n
R_['Nombre'] = R_.t.map(lindo)
R_['G'] = [lindo(t) if g.startswith('Independiente') else g for g, t in zip(R_.Grupo, R_.t)]
R_['Gv'] = ['— (solo)' if g.startswith('Independiente') else g for g in R_.Grupo]   # lo que se muestra
I = R_[R_.imp].copy()
rg = lambda a, d=0: '—' if len(a) == 0 else (f'{min(a):.{d}f}' if round(min(a), d) == round(max(a), d) else f'{min(a):.{d}f} a {max(a):.{d}f}')
nivel = {'Baja': 0, 'Media': 1, 'Alta': 2}
# ---- Grupos: una fila por grupo
gr = []
for (e_, z, g), d in I.groupby(['Etapa', 'Zona', 'G'], sort=False):
    l = list(d.t); ef = [dif(est_f(True, *VAR[v], l), BASE[v]) for v in VAR]
    peor = max(d.t, key=lambda t: mal_solo.get(t, 0)); nmal = mal_solo.get(peor, 0)
    nota = f'No corregir a medias: {lindo(peor)} solo deja {nmal} barras en una troncal equivocada.' if len(l) > 1 and nmal > 0 else ('Los tramos solo tienen efecto juntos.' if len(l) > 1 else '')
    if z == 'Mulchén': nota = 'Ninguno mueve solo. Corregir a medias puede mover 270 MM$/mes.'
    if z == 'Kimal': nota = 'No corregir a medias: L.Changos–Kimal 500 solo mueve 227 MM$/mes y deja 10 barras en una troncal equivocada.'
    cf = d['Confianza del valor sugerido']; baja = int((cf == 'Baja').sum())
    gr.append({'Etapa': e_, 'Zona': z, 'Grupo': d.Gv.iloc[0], 'Tramos que se corrigen juntos': ', '.join(d.Nombre), 'N': len(l),
               'Barras que cambian': rg([x['barras'] for x in ef]), 'Más cerca': rg([x['cerca'] for x in ef]), 'Más lejos': rg([x['lejos'] for x in ef]),
               'MM$/mes': rg([x['mm'] for x in ef]), 'Confianza más baja del grupo': min(cf, key=nivel.get), 'Nota': nota})
GRU = pd.DataFrame(gr)
# ---- Etapas: una fila por etapa
tot = RR[RR.Ronda == RR.Ronda.max()].set_index('Variante')['MM$/mes (acum.)']; et = []
for e_ in sorted(R_.Etapa.unique()):
    d = I[I.Etapa == e_]; x = RR[RR.Ronda == e_].set_index('Variante')
    et.append({'Etapa': e_, 'Qué se revisa': que[e_], 'Tramos imprescindibles': len(d), 'Líneas': int((d.Tipo == 'Línea').sum()), 'Trafos': int((d.Tipo == 'Trafo').sum()),
               'Grupos': d.G.nunique(), 'Resto de la zona (por regla)': int(((R_.Etapa == e_) & ~R_.imp).sum()), 'MM$/mes que mueve': rg(list(x['Mueve la ronda: MM$'])),
               'Plata acumulada (%)': rg(list(x['MM$/mes (acum.)'] / tot * 100)), 'Nota': notae[e_]})
et.append({'Etapa': 'Total', 'Qué se revisa': '', 'Tramos imprescindibles': len(I), 'Líneas': int((I.Tipo == 'Línea').sum()), 'Trafos': int((I.Tipo == 'Trafo').sum()), 'Grupos': len(GRU),
           'Resto de la zona (por regla)': int((~R_.imp).sum()), 'MM$/mes que mueve': rg(list(tot)), 'Plata acumulada (%)': '100', 'Nota': 'Después de cada etapa se recalcula.'})
ETA = pd.DataFrame(et)
# ---- Tramos: una fila por tramo imprescindible, solo sus datos
ng = I.groupby(['Etapa', 'Zona', 'G']).t.transform('size')
TRA = pd.DataFrame({'Etapa': I.Etapa.values, 'Grupo': I.Gv.values, 'Tramo': I.Nombre.values,
                    '¿Se puede corregir solo?': ['Sí' if n == 1 else ('No: con el otro de su grupo' if n == 2 else f'No: con los otros {n - 1} de su grupo') for n in ng], 'Tipo': I.Tipo.values, 'Circuitos o unidades': I['Unidades en paralelo'].values,
                    'X ENT (Ω)': I['X ENT (Ω)'].values, 'X CNE (Ω)': I['X CNE (Ω)'].values, 'X Infotécnica (Ω)': I['X Infotécnica (Ω)'].values, 'X sugerida (Ω)': I['X sugerida (Ω)'].values,
                    'Confianza': I['Confianza del valor sugerido'].values, 'Motivo': I.Motivo.values, 'Nombre en Infotécnica': I['Nombre en Infotécnica'].values, 'Código ENT': I.t.values,
                    'X según ficha (Ω)': '', 'R según ficha (Ω)': '', 'Ficha (documento y fecha)': '', '¿Corregir?': '', 'Responsable y fecha': '', 'Comentario': ''})
N_ = R_[~R_.imp]
RES = pd.DataFrame({'Etapa': N_.Etapa.values, 'Zona': N_.Zona.values, 'Tramo': N_.Nombre.values, 'Tipo': N_.Tipo.values, 'X ENT (Ω)': N_['X ENT (Ω)'].values, 'X sugerida (Ω)': N_['X sugerida (Ω)'].values,
                    'Confianza': N_['Confianza del valor sugerido'].values, 'Código ENT': N_.t.values})
leeme = [('Qué es', 'Los tramos del ENT (líneas y trafos) que hay que revisar con ficha, en el orden en que conviene hacerlo.'),
         ('Base', BASE_TXT.replace('BASE: ', '')),
         ('Hojas', 'Etapas: el plan. Grupos: qué se corrige junto y cuánto mueve. Tramos: los 48 imprescindibles con sus datos, para llenar con la ficha. Resto: 68 tramos que no cambian el resultado.'),
         ('Imprescindibles', '48 tramos. Corrigiendo solo estos se obtiene el mismo resultado que con los 116 que mueven alguna barra (0 barras distintas, en las 4 variantes), y casi el mismo que con los 668 que difieren de las fuentes (5 a 14 barras, 2 a 4 MM$/mes).'),
         ('Grupo', 'Tramos que se corrigen juntos (hoja Tramos, columna "¿Se puede corregir solo?"). Cada grupo solo da su efecto real y los grupos se suman en cualquier orden. Un tramo de un grupo corregido solo puede dar un efecto falso.'),
         ('Confianza', 'Del valor sugerido. Alta: CNE e Infotécnica son válidas y coinciden (hasta 20 %). Media: difieren hasta 2 veces, o hay una sola válida. Baja: difieren más de 2 veces, o la sugerida usa una fuente mal pareada o con valor casi nulo.'),
         ('Efectos', 'Barras que cambian de troncal; cuántas quedan a más de 5 km más cerca o más lejos; MM$/mes = Σ |Δ precio| × MW de inyección y retiro.'),
         ('Límite', 'Todo se calculó con los valores sugeridos. Si la ficha da otro valor, o confirma el del ENT, se recalcula.'),
         ('Respaldo', 'listado_tramos_respaldo.xlsx: todo por tramo (R, nombres en CNE, efecto por zona y por variante), avance por etapa contra PN2604 y verificaciones.')]
X = DAT + 'listado_tramos.xlsx'
with pd.ExcelWriter(X, engine='openpyxl') as w:
    pd.DataFrame(leeme, columns=['Tema', 'Explicación']).to_excel(w, sheet_name='Leeme', index=False)
    ETA.to_excel(w, sheet_name='Etapas', index=False, startrow=1); GRU.to_excel(w, sheet_name='Grupos', index=False, startrow=1)
    TRA.to_excel(w, sheet_name='Tramos', index=False, startrow=1); RES.to_excel(w, sheet_name='Resto', index=False, startrow=1)
wb = load_workbook(X); thin = Side(style='thin', color='30849B'); colc = {'Baja': 'B23A48', 'Media': 'B7791F', 'Alta': '2E7D32'}
ws = wb['Leeme']; cab(ws); ws.column_dimensions['A'].width = 18; ws.column_dimensions['B'].width = 140
for r in ws.iter_rows(min_row=2): r[0].font = Font(bold=True); r[0].alignment = Alignment(vertical='top'); r[1].alignment = Alignment(wrap_text=True, vertical='top')
def hoja(n, df, texto, anch, izq, llenar=0, alto=40):
    ws = wb[n]; nc = len(df.columns); ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=nc)
    c = ws.cell(1, 1, texto); c.font = Font(italic=True, color='1F2A44'); c.fill = PatternFill('solid', fgColor='FFF4D6'); c.alignment = Alignment(wrap_text=True, vertical='center')
    ws.row_dimensions[1].height = 34; ws.row_dimensions[2].height = alto; cab(ws, 2); ws.freeze_panes = 'A3'
    for j, h in enumerate(df.columns, 1):
        ws.column_dimensions[CL(j)].width = anch.get(h, 12)
        if llenar and j > nc - llenar: ws.cell(2, j).fill = PatternFill('solid', fgColor='F2C14E'); ws.cell(2, j).font = Font(bold=True, color='1F2A44')
    for r in ws.iter_rows(min_row=3):
        for c in r:
            h = df.columns[c.column - 1]
            c.alignment = Alignment(horizontal='left', indent=1, wrap_text=True, vertical='center') if h in izq else Alignment(horizontal='center', vertical='center')
            if h.endswith('(Ω)') and not (llenar and c.column > nc - llenar): c.number_format = '0.000'
            if h.startswith('Confianza') and c.value in colc: c.font = Font(bold=True, color=colc[c.value])
    return ws
ws = hoja('Etapas', ETA, BASE_TXT, {'Qué se revisa': 62, 'Tramos imprescindibles': 15, 'Resto de la zona (por regla)': 14, 'MM$/mes que mueve': 13, 'Plata acumulada (%)': 13, 'Nota': 64}, {'Qué se revisa', 'Nota'})
for c in ws[ws.max_row]: c.font = Font(bold=True)
def bandas(ws, clave, repetir, solo=None):
    """banda por grupo, línea al cambiar de etapa y valores repetidos en gris"""
    prev = None; on = False; pe = None; banda = PatternFill('solid', fgColor='EAF3F5')
    for r in ws.iter_rows(min_row=3):
        k = tuple(r[i].value for i in clave)
        if solo is not None and '(solo)' in str(r[1].value): k += (r[solo].value,)
        nuevo = k != prev
        if nuevo: on = not on
        for c in r:
            if on and (c.fill is None or c.fill.fgColor.rgb in ('00000000', None)): c.fill = banda
            if r[0].value != pe: c.border = Border(top=thin)
        if not nuevo:
            for i in repetir: r[i].font = Font(color='B0B7BD')
        prev = k; pe = r[0].value
ws = hoja('Grupos', GRU, BASE_TXT, {'Zona': 28, 'Grupo': 24, 'Tramos que se corrigen juntos': 62, 'N': 5, 'Barras que cambian': 11, 'Más cerca': 9, 'Más lejos': 9, 'MM$/mes': 11,
                                    'Confianza más baja del grupo': 13, 'Nota': 62}, {'Zona', 'Grupo', 'Tramos que se corrigen juntos', 'Nota'}, alto=48)
bandas(ws, (0, 1), (0, 1))
ws = hoja('Tramos', TRA, BASE_TXT + ' Llenar las columnas amarillas con la ficha; se corrige lo que la ficha confirme y se recalcula el grupo.',
          {'Grupo': 24, 'Tramo': 30, '¿Se puede corregir solo?': 24, 'Tipo': 8, 'Circuitos o unidades': 10, 'Confianza': 10, 'Motivo': 42, 'Nombre en Infotécnica': 40, 'Código ENT': 40,
           'X según ficha (Ω)': 12, 'R según ficha (Ω)': 12, 'Ficha (documento y fecha)': 26, '¿Corregir?': 11, 'Responsable y fecha': 18, 'Comentario': 36},
          {'Grupo', 'Tramo', 'Motivo', 'Nombre en Infotécnica', 'Código ENT'}, llenar=6, alto=48)
bandas(ws, (0, 1), (0, 1), solo=2); ws.freeze_panes = 'E3'; ws.auto_filter.ref = f'A2:{CL(len(TRA.columns))}{ws.max_row}'
for r in ws.iter_rows(min_row=3):
    r[2].font = Font(bold=True); r[13].font = Font(color='7F7F7F'); r[3].font = Font(bold=True, color='2E7D32' if r[3].value == 'Sí' else 'B23A48')
dv = DataValidation(type='list', formula1='"Sí,No,Pendiente"', allow_blank=True); ws.add_data_validation(dv); k = CL(list(TRA.columns).index('¿Corregir?') + 1); dv.add(f'{k}3:{k}{ws.max_row}')
ws = hoja('Resto', RES, 'Estos 68 tramos no cambian el resultado final si los 48 imprescindibles se corrigen al valor sugerido. Se corrigen por regla, sin ficha. Si la ficha cambia un imprescindible, se recalcula y alguno puede pasar a importar.',
          {'Zona': 38, 'Tramo': 32, 'Tipo': 8, 'Confianza': 10, 'Código ENT': 40}, {'Zona', 'Tramo', 'Código ENT'})
bandas(ws, (0, 1), (0, 1))
wb.save(X)
pd.set_option('display.width', 260, 'display.max_colwidth', 75, 'display.max_rows', 100)
print(ETA.drop(columns='Nota').to_string(index=False)); print(GRU.drop(columns='Nota').to_string(index=False)); print(GRU[GRU.Nota != ''][['Grupo', 'Nota']].to_string(index=False)); print(TRA.shape, RES.shape)
