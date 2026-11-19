import pandas as pd, re
exec(open('zonas_pct.py').read().split("for z, l in Z.items():")[0].split("exec(open('dos_por_dos.py')")[0])
D = pd.read_excel('/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/lista_revision.xlsx', sheet_name='Lista')
src_ = open('zonas_pct.py').read(); exec(src_[src_.index('kimal_v ='):src_.index('for z, l in Z.items():')])
V = pd.read_pickle('validacion.pkl'); V['b'] = V.nombre_ENT.str.replace(r'_\dde\d$', '', regex=True); info = V.drop_duplicates('b').set_index('b')
orden = {'Ventanas': 1, 'Maule–Itahue–Teno–Linares': 2, 'Santiago oriente': 3, 'Mulchén': 3, 'Resto comunes': 4, 'Kimal': 5}
zona_de = {t: z for z, l in Z.items() for t in l}
todos = sorted(set(D.Tramo) | set(zona_de))
rows = []
for t in todos:
    d = D[D.Tramo == t].iloc[0] if (D.Tramo == t).any() else None
    va, vb = (info.loc[t, 'voltaje_a_ENT'], info.loc[t, 'voltaje_b_ENT']) if t in info.index else (None, None)
    vs = re.findall(r'_(\d+)(?:->|$)', t)
    tipo = 'Trafo' if (va is not None and va != vb) or (len(set(vs)) > 1) else 'Línea'
    z = zona_de.get(t, 'Resto de la lista')
    rows.append({'Orden': orden.get(z, 4), 'Zona': z, 'Tipo': tipo, 'Tramo': t, 'Tensión (kV)': '/'.join(sorted(set(vs), key=lambda x: -int(x))) if vs else '',
                 'En variantes (de 4)': int(d['En cuántos criterios']) if d is not None else '', 'MM$/mes (solo, promedio)': d['MM$/mes (solo, promedio)'] if d is not None else '',
                 'X ENT': round(info.loc[t, 'X_ENT'], 3) if t in info.index else '', 'X sugerida': round(info.loc[t, 'valor_sugerido'], 3) if t in info.index and pd.notna(info.loc[t, 'valor_sugerido']) else '',
                 'Validación X': info.loc[t, 'clasificacion_validacion'] if t in info.index else ''})
R = pd.DataFrame(rows).sort_values(['Orden', 'Zona', 'Tipo', 'MM$/mes (solo, promedio)'], ascending=[True, True, True, False], key=lambda s: pd.to_numeric(s, errors='coerce').fillna(-1) if s.name == 'MM$/mes (solo, promedio)' else s)
print(len(R), R.Tipo.value_counts().to_dict()); print(R.groupby(['Orden', 'Zona', 'Tipo']).size().to_string())
X = '/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/listado_tramos.xlsx'
with pd.ExcelWriter(X, engine='openpyxl') as w:
    pd.DataFrame({'Nota': ['Tramos a revisar (lista de 112 más los de las 6 zonas), agrupados por tipo. Orden: 1 Ventanas, 2 Maule–Itahue–Teno–Linares, 3 Santiago oriente y Mulchén (alejan: revisar bien), 4 resto, 5 Kimal (completa, nunca a medias).',
                          'MM$/mes: efecto del tramo corregido solo, promedio de las 4 variantes (guía para priorizar). Confirmar cada valor con la ficha antes de corregir.']}).to_excel(w, sheet_name='Leeme', index=False)
    R.to_excel(w, sheet_name='Todos', index=False)
    R[R.Tipo == 'Trafo'].to_excel(w, sheet_name='Trafos', index=False); R[R.Tipo == 'Línea'].to_excel(w, sheet_name='Líneas', index=False)
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
wb = load_workbook(X)
for ws in wb.worksheets:
    for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='30849B'); c.alignment = Alignment(wrap_text=True, vertical='center')
    for col in ws.columns: ws.column_dimensions[col[0].column_letter].width = max(10, min(60, max(len(str(v.value or '')) for v in col) + 2))
    ws.freeze_panes = 'A2'
wb.save(X)
