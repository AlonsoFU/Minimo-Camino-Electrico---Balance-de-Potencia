import pandas as pd, networkx as nx, re
src_ = open('listado2.py').read()
exec(src_.split("grupo = {}")[0])            # recalcula Gi, met, Lst (sin escribir)
X = '/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/listado_tramos.xlsx'
Lst = pd.read_excel(X, sheet_name='Listado')
D = pd.read_excel('/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/lista_revision.xlsx', sheet_name='Lista').set_index('Tramo')
var = ['Trafo troncal X', 'Trafo troncal R', 'Misma subest. X', 'Misma subest. R']
def crit(t):
    if t not in D.index: return 'Vecino (acompaña a un crítico)'
    return 'Crítico (cambia la troncal por sí solo)' if any(D.loc[t, v] == 'decisivo' for v in var) else 'Vecino (acompaña a un crítico)'
zona_orig = dict(zip(Lst.Tramo, Lst.Zona))
nombre = lambda t: re.sub(r'\s+', ' ', t.split('->')[0].strip('_').replace('_', ' ')).title()
nueva = {}
mm = dict(zip(Lst.Tramo, pd.to_numeric(Lst['MM$/mes (solo, promedio)'], errors='coerce').fillna(0)))
for comp in nx.connected_components(Gi):
    comp = set(comp); nombradas = {zona_orig[t] for t in comp if zona_orig[t] != 'Resto de la lista'}
    if len(comp) == 1:
        t = next(iter(comp)); nueva[t] = zona_orig[t] if zona_orig[t] != 'Resto de la lista' else 'Independiente'
        continue
    if nombradas:
        z = ' + '.join(sorted(nombradas))
    else:
        top = max(comp, key=lambda t: mm.get(t, 0)); z = f'Grupo {nombre(top)}'
    for t in comp: nueva[t] = zona_orig[t] if zona_orig[t] != 'Resto de la lista' else z
Lst['Zona'] = Lst.Tramo.map(nueva)
Lst.insert(2, 'Crítico / vecino', Lst.Tramo.map(crit))
orden = {'Ventanas': 1, 'Maule–Itahue–Teno–Linares': 2, 'Santiago oriente': 3, 'Mulchén': 3, 'Resto comunes': 4, 'Kimal': 5}
Lst['Orden'] = [orden.get(z, 4 if (z == 'Independiente' and m > 2) else (4 if any(k in z for k in orden) else 6)) for z, m in zip(Lst.Zona, Lst.Tramo.map(mm))]
for z in list(orden):
    Lst.loc[Lst.Zona.str.contains(re.escape(z)) & ~Lst.Zona.isin(orden), 'Orden'] = orden[z]
Lst = Lst.sort_values(['Orden', 'Zona', 'Crítico / vecino', 'MM$/mes (solo, promedio)'], ascending=[True, True, True, False])
print(Lst.groupby(['Orden', 'Zona']).size().to_string()); print(Lst['Crítico / vecino'].value_counts().to_dict())
nota = ['BASE DEL ANÁLISIS: método nuevo «Referido» (reactancias referidas a 220 kV) uniendo la subestación troncal, en 4 variantes: anular solo el trafo que toca la barra troncal (TT) o toda la subestación (MS), con X o con |Z| (R). Los datos corregidos son el valor sugerido de la validación del dueño (homologación ENT–CNE–Infotécnica).',
        'Cada efecto se mide contra el mismo método con el ENT actual. Columnas TT-X y MS-R: efecto de corregir el tramo solo (barras que cambian, MM$/mes que suben y bajan, barras más cerca o más lejos, cambio promedio de km).',
        'Crítico: cambia la troncal de alguna barra por sí solo. Vecino: solo importa junto con un crítico (interacción > 1 MM$/mes); se corrige con su zona.',
        'Zona: tramos que interactúan entre sí y se corrigen juntos. "Grupo X": zona sin nombre previo, nombrada por su tramo de mayor impacto. "Independiente": se puede corregir solo.',
        'Orden: 1 Ventanas, 2 Maule–Itahue–Teno–Linares, 3 Santiago oriente y Mulchén (alejan: revisar bien), 4 resto de comunes e independientes de más de 2 MM$/mes, 5 Kimal (completa), 6 lo que queda.',
        'revision: 1 = CNE e Infotécnica confiables; CNE = solo CNE; Infotec = solo Infotécnica; 0 = ninguna. Confirmar cada valor con la ficha antes de corregir.']
with pd.ExcelWriter(X, engine='openpyxl') as w:
    pd.DataFrame({'Nota': nota}).to_excel(w, sheet_name='Leeme', index=False); Lst.to_excel(w, sheet_name='Listado', index=False)
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
wb = load_workbook(X)
for ws in wb.worksheets:
    for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='30849B'); c.alignment = Alignment(wrap_text=True, vertical='center')
    for col in ws.columns: ws.column_dimensions[col[0].column_letter].width = max(10, min(45, max(len(str(v.value or '')) for v in col) + 2))
wb['Leeme'].column_dimensions['A'].width = 160; wb['Listado'].freeze_panes = 'F2'; wb.save(X)
