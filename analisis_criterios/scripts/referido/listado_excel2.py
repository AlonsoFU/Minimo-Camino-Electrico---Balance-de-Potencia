"""Escribe datos/listado_tramos.xlsx (versión de presentación): Leeme, Etapas, Revisión (por bloques), Zonas,
Zonas por variante, Avance por etapa, Verificación y Detalle. Usa los cálculos de listado_excel.py."""
exec(open('listado_excel.py').read().split("Rev = pd.DataFrame({'Orden'")[0])
MP = pd.read_pickle(OUT + 'grupos_mapas.pkl'); BASE = {v: est_f(True, *VAR[v], []) for v in VAR}
L = Lst.set_index('Tramo')
# ---- efecto de cada grupo (rango de las 4 variantes)
def ef_grupo(z, b):
    nb, mm = [], []
    for v in VAR:
        m = MP[(z, frozenset(b))][v]; nb.append(len(m))
        mm.append(sum(abs(precio.get(x, 0) - precio.get(BASE[v][k], 0)) * float(mwS.get(k, 0) or 0) / 1000 for k, x in m.items()))
    r = lambda a, d=0: (f'{min(a):.{d}f}' if round(min(a), d) == round(max(a), d) else f'{min(a):.{d}f} a {max(a):.{d}f}')
    return f'{r(nb)} barras · {r(mm)} MM$/mes'
efg = {}
for z, bl in GR.items():
    for b in bl:
        for t in b: efg[t] = ef_grupo(z, b)
def ef_g(t, z):
    if t in efg: return efg[t]
    if t in NUC: return ef_tramo(t, z) if z == 'Independiente' else ''
    return 'No cambia el final'
# ---- confianza del valor sugerido
def confianza(t):
    r = L.loc[t]; f = str(r['Fuente sugerida']); m = []
    est = {}
    for n, x, c in [('CNE', r['X CNE'], r['Confianza pareo CNE']), ('Infotécnica', r['X Infotécnica'], r['Confianza pareo Infotécnica'])]:
        est[n] = 'no hay' if pd.isna(x) else ('pareo dudoso' if pd.notna(c) and c < 80 else ('valor casi nulo' if x < 0.01 else 'ok'))
    usa = [n for n, k in [('CNE', 'CNE'), ('Infotécnica', 'Infotec')] if k in f or 'Promedio' in f]
    malas_usadas = [n for n in usa if est[n] != 'ok']
    if malas_usadas or (pd.notna(r['X sugerida']) and r['X sugerida'] < 0.01):
        niv = 'Baja'; m += [f'la sugerida usa {n} ({est[n]})' for n in malas_usadas]
        if pd.notna(r['X sugerida']) and r['X sugerida'] < 0.01: m.append('el valor sugerido es casi nulo')
    elif all(v == 'ok' for v in est.values()):
        d_ = max(r['X CNE'], r['X Infotécnica']) / min(r['X CNE'], r['X Infotécnica'])
        niv = 'Alta' if d_ <= 1.2 else ('Media' if d_ <= 2 else 'Baja')
        m.append('CNE e Infotécnica coinciden' if d_ <= 1.2 else f'CNE e Infotécnica difieren {d_:.1f} veces')
    else:
        niv = 'Media'; otra = [n for n in est if est[n] != 'ok'][0]; m.append(f'una sola fuente válida ({otra}: {est[otra]})')
    return niv, '; '.join(m)
CONF = {t: confianza(t) for t in Lst.Tramo}
razon = lambda t: (L.loc[t, 'X ENT'] / L.loc[t, 'X sugerida']) if pd.notna(L.loc[t, 'X sugerida']) and L.loc[t, 'X sugerida'] > 0 else None
T = list(Lst.Tramo)
BLOQ = {
 'IDENTIFICACIÓN': {'Etapa': [L.loc[t, 'Orden'] for t in T], 'Zona': [L.loc[t, 'Zona'] for t in T], 'Grupo': [grupo_de.get(t, '') for t in T], 'Tramo (nombre ENT)': T,
                    'Tipo': [L.loc[t, 'Tipo'] for t in T], 'Tensión (kV)': [L.loc[t, 'Tensión (kV)'] for t in T], 'Unidades en paralelo': [L.loc[t, 'Circuitos/unidades en paralelo'] for t in T]},
 'POR QUÉ IMPORTA': {'Imprescindible (de los 48)': ['Sí' if t in NUC else 'No' for t in T], 'Crítico / vecino': [L.loc[t, 'Crítico / vecino'].split(' (')[0] for t in T],
                     'Solo o en grupo': [tipo(t) for t in T], 'Se corrige junto con': [socios.get(t, '') for t in T],
                     'Si se corrige solo: barras en troncal equivocada': [mal_solo.get(t, 0) for t in T],
                     'Efecto de corregir su grupo': [ef_g(t, L.loc[t, 'Zona']) for t in T], 'Efecto de corregir su zona': [ef_tramo(t, L.loc[t, 'Zona']) for t in T]},
 'DATOS: ENT CONTRA LAS FUENTES': {'X ENT (Ω)': [L.loc[t, 'X ENT'] for t in T], 'X CNE (Ω)': [L.loc[t, 'X CNE'] for t in T], 'X Infotécnica (Ω)': [L.loc[t, 'X Infotécnica'] for t in T],
                     'X sugerida (Ω)': [L.loc[t, 'X sugerida'] for t in T], 'Fuente de la sugerida': [L.loc[t, 'Fuente sugerida'] for t in T], 'ENT / sugerida (veces)': [razon(t) for t in T],
                     'R ENT (Ω)': [L.loc[t, 'R ENT'] for t in T], 'R CNE (Ω)': [L.loc[t, 'R CNE'] for t in T], 'R Infotécnica (Ω)': [L.loc[t, 'R Infotécnica'] for t in T],
                     'Nombre en CNE': [L.loc[t, 'Nombre CNE'] for t in T], 'Nombre en Infotécnica': [L.loc[t, 'Nombre Infotécnica'] for t in T],
                     'Confianza del valor sugerido': [CONF[t][0] for t in T], 'Motivo': [CONF[t][1] for t in T]},
 'PARA LLENAR CON LA FICHA': {c: [''] * len(T) for c in ['X según ficha (Ω)', 'R según ficha (Ω)', 'Ficha (documento y fecha)', '¿Corregir?', 'Valor aplicado (Ω)', 'Responsable', 'Fecha', 'Comentario']}}
Rev = pd.DataFrame({c: v for b in BLOQ.values() for c, v in b.items()})
mm_solo = pd.to_numeric(Lst['MM$/mes (solo, promedio)'], errors='coerce').fillna(0).values
zrank = {z: i for i, z in enumerate(dict.fromkeys(Rev.Zona))}; grank = {t: i for z, bl in GR.items() for i, b in enumerate(bl, 1) for t in b}
Rev['Grupo'] = [g if g else ('Resto de la zona' if z != 'Independiente' else 'Independiente (no cambia el final)') for g, z in zip(Rev.Grupo, Rev.Zona)]
Rev['_k'] = list(zip(Rev.Etapa, Rev.Zona.map(zrank), [0 if i == 'Sí' else 1 for i in Rev['Imprescindible (de los 48)']], [grank.get(t, 0) for t in T],
                     [0 if c == 'Crítico' else 1 for c in Rev['Crítico / vecino']], -mm_solo))
Rev = Rev.sort_values('_k').drop(columns='_k').reset_index(drop=True)
# ---- etapas
que = {1: 'Ventanas', 2: 'Maule–Itahue–Teno–Linares', 3: 'Santiago oriente y Mulchén', 4: 'Aconcagua, Melipilla, Atacama, Dichas 220, Fopaco y Turibe–Esmeralda', 5: 'Kimal',
       6: 'El Laurel 220, Codegua 66 e independientes chicos'}
notae = {1: 'Acerca barras. El valor sugerido del trafo sale de una sola fuente.', 2: 'Acerca mucho. Dos grupos independientes.', 3: 'Aleja barras y es la mitad de la plata: la que más hay que revisar.',
         4: 'Poca plata salvo Aconcagua con R y Fopaco con R.', 5: 'Casi neutro. Sus 6 imprescindibles van juntos.', 6: 'Poca plata: se puede hacer por regla, sin ficha.'}
tot = RR[RR.Ronda == RR.Ronda.max()].set_index('Variante')['MM$/mes (acum.)']; rge = lambda a, d=0: f'{a.min():.{d}f}' if round(a.min(), d) == round(a.max(), d) else f'{a.min():.{d}f} a {a.max():.{d}f}'
er = []
for e_ in sorted(Rev.Etapa.unique()):
    g = Rev[Rev.Etapa == e_]; x = RR[RR.Ronda == e_].set_index('Variante'); gi = g[g['Imprescindible (de los 48)'] == 'Sí']
    er.append({'Etapa': e_, 'Qué se revisa': que[e_], 'Tramos': len(g), 'Líneas': int((g.Tipo == 'Línea').sum()), 'Trafos': int((g.Tipo == 'Trafo').sum()), 'Imprescindibles': len(gi),
               'Grupos de imprescindibles': gi.Grupo.nunique() if (gi.Grupo != 'Independiente').all() else gi[gi.Grupo != 'Independiente'].Grupo.nunique() + int((gi.Grupo == 'Independiente').sum()),
               'MM$/mes que mueve la etapa': rge(x['Mueve la ronda: MM$']), 'Plata acumulada (% del total)': rge(x['MM$/mes (acum.)'] / tot * 100),
               'Barras distintas a PN2604 al terminar': rge(x['Distintas a PN2604']), 'Nota': notae[e_]})
g = Rev; gi = g[g['Imprescindible (de los 48)'] == 'Sí']; p0 = RR[RR.Ronda == 0]
er.append({'Etapa': 'Total', 'Qué se revisa': '', 'Tramos': len(g), 'Líneas': int((g.Tipo == 'Línea').sum()), 'Trafos': int((g.Tipo == 'Trafo').sum()), 'Imprescindibles': len(gi),
           'Grupos de imprescindibles': sum(r['Grupos de imprescindibles'] for r in er), 'MM$/mes que mueve la etapa': rge(tot), 'Plata acumulada (% del total)': '100',
           'Barras distintas a PN2604 al terminar': f"hoy: {rge(p0['Distintas a PN2604'])}", 'Nota': 'Rangos: mínimo y máximo de las 4 variantes del método nuevo.'})
ET = pd.DataFrame(er)
leeme = [('Qué es', 'Los 116 tramos (líneas y trafos) del ENT que hay que revisar: difieren de CNE o Infotécnica y cambian la troncal de alguna barra, solos o con otros.'),
         ('', 'Los otros 552 tramos que difieren no mueven ninguna barra: se corrigen al final, por regla.'),
         ('Cómo usarlo', '1. Hoja Etapas: el plan. 2. Hoja Revisión: revisar por etapa, zona y grupo; llenar las columnas amarillas con la ficha. 3. Corregir lo que la ficha confirme y recalcular antes de la etapa siguiente.'),
         ('Imprescindible', '48 tramos. Corrigiendo solo estos se obtiene el mismo resultado que con los 116 (0 barras distintas, 4 variantes), también zona por zona y etapa por etapa. Ninguno sobra.'),
         ('Grupo', 'Imprescindibles que se corrigen juntos. Cada grupo solo da su parte real del resultado, sin barras en una troncal equivocada, y los grupos se suman en cualquier orden.'),
         ('Solo o en grupo', '"Efecto propio": corregido solo ya da su efecto real. "Necesita a su grupo": solo da un efecto falso, incompleto o ninguno.'),
         ('Crítico / vecino', 'Crítico: mueve alguna barra por sí solo (no significa que ese movimiento sea el final). Vecino: solo importa junto con otros. Combinado: Mulchén.'),
         ('Resto de la zona', 'Tramos que no cambian el resultado final si los imprescindibles se corrigen al valor sugerido. Se revisan igual: si la ficha cambia un imprescindible, pueden pasar a importar.'),
         ('Datos', 'X y R en Ω, tal como vienen de la validación ENT–CNE–Infotécnica (homologacion_clasificada.xlsx). X sugerida: el valor que propone la validación; hay que confirmarlo con la ficha.'),
         ('Confianza', 'Del valor sugerido. Una fuente es válida si existe, su pareo de nombres es bueno (80 o más) y su valor no es casi nulo. Alta: las dos son válidas y coinciden (hasta 20 %). Media: difieren hasta 2 veces, o hay una sola válida. Baja: difieren más de 2 veces, o la sugerida usa una fuente no válida. Empezar las fichas por los imprescindibles de confianza baja.'),
         ('Efectos', 'Método nuevo (referido a 220 kV + subestación troncal), contra el mismo método con el ENT actual. Rango de 4 variantes: TT o MS, con X o con R. MM$/mes = Σ |Δ precio| × MW de inyección y retiro.'),
         ('Límite', 'Todo se calculó con los valores sugeridos. Si la ficha da otro valor, o confirma el del ENT, se recalcula.'),
         ('Otras hojas', 'Zonas y Zonas por variante: efecto de cada zona. Avance por etapa: acumulado por variante. Verificación: independencia entre zonas. Detalle: efecto de cada tramo solo.')]
X = DAT + 'listado_tramos.xlsx'
with pd.ExcelWriter(X, engine='openpyxl') as w:
    pd.DataFrame(leeme, columns=['Tema', 'Explicación']).to_excel(w, sheet_name='Leeme', index=False)
    ET.to_excel(w, sheet_name='Etapas', index=False)
    Rev.to_excel(w, sheet_name='Revisión', index=False, startrow=1)
    ZS.rename(columns={'Ronda': 'Etapa'}).to_excel(w, sheet_name='Zonas', index=False)
    RZv.assign(o=RZv.Zona.map({z: i for i, z in enumerate(orden_filas)})).sort_values(['Variante', 'o']).drop(columns='o').to_excel(w, sheet_name='Zonas por variante', index=False)
    RR.sort_values(['Variante', 'Ronda']).rename(columns=lambda c: c.replace('ronda', 'etapa').replace('Ronda', 'Etapa')).to_excel(w, sheet_name='Avance por etapa', index=False)
    RV.to_excel(w, sheet_name='Verificación', index=False)
    Lst.drop(columns=['unidad', 'Se puede corregir solo'], errors='ignore').rename(columns={'Orden': 'Etapa'}).to_excel(w, sheet_name='Detalle', index=False)
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as CL
from openpyxl.worksheet.datavalidation import DataValidation
wb = load_workbook(X); azul = '30849B'
def cab(ws, fila=1):
    for c in ws[fila]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor=azul); c.alignment = Alignment(wrap_text=True, vertical='center')
def anchos(ws, fila=1, mx=48):
    for col in ws.iter_cols(min_row=fila + 1):
        ws.column_dimensions[CL(col[0].column)].width = max(9, min(mx, max((len(str(v.value)) for v in col if v.value is not None), default=6) + 2))
for n in ['Zonas por variante', 'Avance por etapa', 'Verificación', 'Detalle']: cab(wb[n]); anchos(wb[n]); wb[n].freeze_panes = 'A2'; wb[n].row_dimensions[1].height = 45
wb['Detalle'].freeze_panes = 'F2'
ws = wb['Leeme']; cab(ws); ws.column_dimensions['A'].width = 20; ws.column_dimensions['B'].width = 150
for r in ws.iter_rows(min_row=2): r[0].font = Font(bold=True); r[0].alignment = Alignment(vertical='top'); r[1].alignment = Alignment(wrap_text=True, vertical='top')
for n, wz in [('Etapas', {'B': 62, 'H': 16, 'I': 16, 'J': 20, 'K': 70}), ('Zonas', {'B': 42, 'I': 95})]:
    ws = wb[n]; cab(ws); anchos(ws); ws.row_dimensions[1].height = 45; ws.freeze_panes = 'A2'
    for k, v in wz.items(): ws.column_dimensions[k].width = v
    for r in ws.iter_rows(min_row=2):
        for c in r: c.alignment = Alignment(wrap_text=True, vertical='top')
ws = wb['Etapas']; ws.row_dimensions[1].height = 62
for k, v in {'A': 8, 'C': 9, 'D': 9, 'E': 9, 'F': 16, 'G': 18, 'H': 18, 'I': 18, 'J': 24}.items(): ws.column_dimensions[k].width = v
for r in ws.iter_rows(min_row=1):
    for c in r:
        if c.column_letter not in ('B', 'K'): c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        elif c.row > 1: c.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True, indent=1)
for c in ws[ws.max_row]: c.font = Font(bold=True)
# ---- Revisión
ws = wb['Revisión']; hdr = [c.value for c in ws[2]]; col = {h: i + 1 for i, h in enumerate(hdr)}
colores = {'IDENTIFICACIÓN': '1F4E5F', 'POR QUÉ IMPORTA': '30849B', 'DATOS: ENT CONTRA LAS FUENTES': '5B7083', 'PARA LLENAR CON LA FICHA': 'F2C14E'}
for b, cs in BLOQ.items():
    a, z = col[list(cs)[0]], col[list(cs)[-1]]; ws.merge_cells(start_row=1, start_column=a, end_row=1, end_column=z)
    amar = b.startswith('PARA'); c = ws.cell(1, a, b); c.fill = PatternFill('solid', fgColor=colores[b]); c.font = Font(bold=True, color='1F2A44' if amar else 'FFFFFF', size=12)
    c.alignment = Alignment(horizontal='center', vertical='center')
    for j in range(a, z + 1):
        h = ws.cell(2, j); h.fill = PatternFill('solid', fgColor=colores[b]); h.font = Font(bold=True, color='1F2A44' if amar else 'FFFFFF'); h.alignment = Alignment(wrap_text=True, vertical='center')
ws.row_dimensions[1].height = 22; ws.row_dimensions[2].height = 62; ws.freeze_panes = 'E3'; ws.auto_filter.ref = f'A2:{CL(len(hdr))}{ws.max_row}'
W = {'Etapa': 7, 'Zona': 26, 'Grupo': 24, 'Tramo (nombre ENT)': 40, 'Tipo': 7, 'Tensión (kV)': 10, 'Unidades en paralelo': 10, 'Imprescindible (de los 48)': 13, 'Crítico / vecino': 11,
     'Solo o en grupo': 26, 'Se corrige junto con': 52, 'Si se corrige solo: barras en troncal equivocada': 14, 'Efecto de corregir su grupo': 36, 'Efecto de corregir su zona': 52,
     'Fuente de la sugerida': 22, 'ENT / sugerida (veces)': 10, 'Nombre en CNE': 36, 'Nombre en Infotécnica': 40, 'Confianza del valor sugerido': 12, 'Motivo': 46, 'Ficha (documento y fecha)': 28, '¿Corregir?': 11, 'Comentario': 40}
for h, i in col.items(): ws.column_dimensions[CL(i)].width = W.get(h, 13)
CENTRO = {'Etapa', 'Tipo', 'Tensión (kV)', 'Unidades en paralelo', 'Imprescindible (de los 48)', 'Crítico / vecino', 'Si se corrige solo: barras en troncal equivocada', 'ENT / sugerida (veces)', 'Confianza del valor sugerido'}
gris = Font(color='7F7F7F'); banda = PatternFill('solid', fgColor='EAF3F5'); linea = Border(top=Side(style='thin', color='30849B')); i0 = col['X según ficha (Ω)']
prev = None; on = False; pz = None
for r in ws.iter_rows(min_row=3):
    key = (r[1].value, r[2].value)
    if key != prev: on = not on; prev = key
    imp = r[col['Imprescindible (de los 48)'] - 1].value == 'Sí'
    for c in r:
        if on and c.column < i0: c.fill = banda
        if not imp and c.column < i0: c.font = gris
        if r[1].value != pz: c.border = linea
        h = hdr[c.column - 1]
        if h.endswith('(Ω)') and c.column < i0: c.number_format = '0.000'
        if h == 'ENT / sugerida (veces)': c.number_format = '0.0'
        if h in CENTRO: c.alignment = Alignment(horizontal='center')
        if h in ('Fuente de la sugerida', 'Nombre en CNE', 'Solo o en grupo', 'Efecto de corregir su grupo', 'Motivo'): c.alignment = Alignment(horizontal='left', indent=1)
    pz = r[1].value
    if imp: r[col['Imprescindible (de los 48)'] - 1].font = Font(bold=True, color='B23A48'); r[col['Tramo (nombre ENT)'] - 1].font = Font(bold=True)
    a = r[col['Confianza del valor sugerido'] - 1]
    a.font = Font(bold=True, color={'Baja': 'B23A48', 'Media': 'B7791F', 'Alta': '2E7D32'}[a.value])
dv = DataValidation(type='list', formula1='"Sí,No,Pendiente"', allow_blank=True); ws.add_data_validation(dv); k = CL(col['¿Corregir?']); dv.add(f'{k}3:{k}{ws.max_row}')
wb.save(X)
pd.set_option('display.width', 250, 'display.max_colwidth', 70); print(ET.to_string(index=False)); print(Rev.shape); print(pd.crosstab(Rev['Imprescindible (de los 48)'], Rev['Confianza del valor sugerido']))
