"""Comparación consolidada de criterios (X y |Z|), incluida la lectura intermedia de 'subestación'."""
exec(open('con_r.py').read().split("ESC = {")[0])
exec(open('con_r_plata.py').read().split("def monto")[0].replace("S=pd.read_pickle('con_r.pkl')","S=pd.read_pickle(OUT+'con_r.pkl')"))
B = pd.read_pickle(OUT + 'banco.pkl'); B = B[B.actual.notna()].set_index('barra')
for k, (an, modo) in {'Ref+Trafo troncal (X)': (m3, 'X'), 'Ref+Trafo troncal (|Z|)': (m3, 'Zc')}.items():
    S[k], _ = asigna(grafo_z(esc(True, an), modo))
S['C1'] = B['C1']; S['C2'] = B['C2']
CR = [('Hoy', 'mod_actual', 'Suma Ω sin referir (módulo actual)'),
      ('Anular trafos troncales (C1)', 'C1', 'Hoy + X=0 en trafos de subestaciones con barra troncal, sin referir'),
      ('Anular todos los trafos (C2)', 'C2', 'Hoy + X=0 en todos los trafos, sin referir'),
      ('Referido — X', 'Referido (X)', 'Ω × (220/V)²; lectura estricta: se llega a la barra de 220 kV'),
      ('Referido — |Z|', 'Referido (|Z|)', 'Ídem con R: Σ|Z| por tramo'),
      ('Referido + trafo troncal — X', 'Ref+Trafo troncal (X)', 'Referido + X=0 solo en trafos que tocan la barra troncal (lectura intermedia)'),
      ('Referido + trafo troncal — |Z|', 'Ref+Trafo troncal (|Z|)', 'Ídem con R'),
      ('Referido + Subestación — X', 'Ref+Sub (X)', 'Referido + X=0 en todos los trafos de la subestación troncal (lectura amplia)'),
      ('Referido + Subestación — |Z|', 'Ref+Sub (|Z|)', 'Ídem con R')]
src = lambda b: b if b in coord else B.loc[b, 'nodo']
filas = []
for n, c, d_ in CR:
    d = S[S[c] != S.mod_actual]; dp = d[c].map(precio) - d.mod_actual.map(precio)
    kmb = pd.Series({b: km(src(b), S.loc[b, c]) for b in S.index})
    kmc = pd.Series({b: km(S.loc[b, 'mod_actual'], S.loc[b, c]) for b in d.index})
    filas.append({'Criterio': n, 'Qué hace': d_, '= PN2604': int((S[c] == S.PN2604).sum()),
                  'Cambian vs hoy': len(d), 'Cambian vs hoy a >100 km': int((kmc > 100).sum()),
                  'Barra→troncal >100 km': int((kmb > 100).sum()),
                  'Cambian con iny/ret': int((d.mw > 0).sum()),
                  'MM$/mes movidos vs hoy': round((dp.abs() * d.mw / 1000).sum(), 1),
                  'Neto MM$/mes (+ sube)': round((dp * d.mw / 1000).sum(), 1)})
T_ = pd.DataFrame(filas); print(T_.drop(columns='Qué hace').to_string(index=False))
pares = [('Referido — X', 'Referido — |Z|'), ('Referido + trafo troncal — X', 'Referido + trafo troncal — |Z|'),
         ('Referido + Subestación — X', 'Referido + Subestación — |Z|'), ('Referido — X', 'Referido + trafo troncal — X'),
         ('Referido + trafo troncal — X', 'Referido + Subestación — X')]
col = {n: c for n, c, _ in CR}
P = pd.DataFrame([{'Entre': a, 'y': b, 'Barras distintas': int((S[col[a]] != S[col[b]]).sum())} for a, b in pares])
print(P.to_string(index=False))
OUTX = '/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/comparacion_criterios.xlsx'
D = S[[c for _, c, _ in CR] + ['PN2604']].rename(columns={c: n for n, c, _ in CR}); D.insert(0, 'iny+ret (MW)', S.mw.round(3)); D.index.name = 'Barra'
with pd.ExcelWriter(OUTX, engine='openpyxl') as w:
    T_.to_excel(w, sheet_name='Resumen', index=False)
    P.to_excel(w, sheet_name='Resumen', index=False, startrow=len(T_) + 3)
    pd.DataFrame({'Notas': ['1.442 barras. Precios PN2604 (hoja 03); MW = inyecciones + retiros de la hoja 05 (sin filas Tx).',
        'MM$/mes movidos = Σ |precio troncal criterio − precio troncal hoy| × MW / 1000. Neto: + = sube el precio.',
        'Ω referidos a 220 kV: X·(220/V)², con V = columna V [kV] del ENT. |Z| = √(R²+X²) por tramo, paralelos en complejo.',
        'Trafos anulados: trafo troncal = 60 que tocan la barra troncal; subestación = 83 (incluye 23 internos de niveles menores, pareo por nombre).',
        'PN2604 es referencia, no verdad: coincidir más es una señal, no una prueba.']}).to_excel(w, sheet_name='Resumen', index=False, startrow=len(T_) + len(P) + 6)
    D.to_excel(w, sheet_name='Por barra')
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
wb = load_workbook(OUTX)
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if ws.title == 'Por barra' and c.row == 1 or ws.title == 'Resumen' and c.row in (1, len(T_) + 4, len(T_) + len(P) + 7) and c.value:
                c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='30849B'); c.alignment = Alignment(wrap_text=True, vertical='center')
    for colc in ws.columns: ws.column_dimensions[colc[0].column_letter].width = max(11, min(48, max(len(str(c.value or '')) for c in colc[:40]) + 2))
wb['Por barra'].freeze_panes = 'B2'
wb.save(OUTX)
