import sqlite3, json, pandas as pd, networkx as nx
exec(open('con_r_plata.py').read().split("def monto")[0].replace("S=pd.read_pickle('con_r.pkl')","S=pd.read_pickle('/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/con_r.pkl')"))
exec(open('metr.py').read().split("R=pd.read_pickle")[0])
R0 = pd.read_pickle('banco.pkl').set_index('barra'); src = lambda b: b if b in coord else R0.loc[b, 'nodo']
X = '/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/listado_tramos.xlsx'
Lst = pd.read_excel(X, sheet_name='Listado'); tram = set(Lst.Tramo)
Gi = nx.Graph(); Gi.add_nodes_from(tram); met = {}
for k, lab in [('tt_x', 'TT-X'), ('sub_z', 'MS-R')]:
    c = sqlite3.connect(f'registro_{k}.sqlite')
    P = pd.read_sql('select * from pruebas', c); C = pd.read_sql('select * from cambios', c)
    first = P[P.desde_cache == 0].drop_duplicates('tramos').set_index('tramos')['id']
    chg = {pid: g for pid, g in C.groupby('prueba_id')}
    def ch_of(tr):
        g = chg.get(first.get(tr)); return {} if g is None else {r.barra: (r.troncal_base, r.troncal_nueva, r.mw) for r in g.itertuples()}
    # métricas individuales
    for t in tram:
        d = ch_of(t); up = dn = 0.0; cer = lej = 0; dks = []
        for b, (bt, nt, mw) in d.items():
            dp = (precio.get(nt, 0) - precio.get(bt, 0)) * mw / 1000
            up += max(dp, 0); dn += min(dp, 0)
            try:
                dk = km(src(b), nt) - km(src(b), bt)
            except Exception:
                dk = float('nan')
            if dk == dk:
                dks.append(dk); cer += dk < -5; lej += dk > 5
        met.setdefault(t, {}).update({f'{lab} barras': len(d), f'{lab} MM$ sube': round(up, 1), f'{lab} MM$ baja': round(dn, 1),
                                      f'{lab} más cerca': cer, f'{lab} más lejos': lej, f'{lab} Δ km promedio': round(sum(dks) / len(dks), 1) if dks else None})
    # interacciones (combinaciones chicas con desviación > 1 MM$)
    Zt = P[(P.etapa == '4 zonas') & (P.n_tramos.between(2, 4)) & P.detalle.str.contains('combinación|par')].drop_duplicates('tramos')
    for tr in Zt.tramos:
        ts = tr.split(' + '); comb = ch_of(tr); uni = {}
        for t in ts: uni.update(ch_of(t))
        mm = 0.0
        for b in set(comb) ^ set(uni):
            bt, nt, mw = comb.get(b) or uni.get(b); mm += abs(precio.get(nt, 0) - precio.get(bt, 0)) * mw / 1000
        if mm > 1:
            ts2 = [t for t in ts if t in tram]
            for i in range(len(ts2)):
                for j in range(i + 1, len(ts2)): Gi.add_edge(ts2[i], ts2[j])
grupo = {}
for i, comp in enumerate(sorted(nx.connected_components(Gi), key=len, reverse=True), 1):
    for t in comp: grupo[t] = (i, len(comp))
M = pd.DataFrame(met).T
Lst['Se puede corregir solo'] = Lst.Tramo.map(lambda t: 'Sí' if grupo[t][1] == 1 else f'No: con {grupo[t][1] - 1} más (grupo {grupo[t][0]})')
Lst = Lst.join(M, on='Tramo')
resto = Lst[Lst.Zona == 'Resto de la lista']
print('resto:', len(resto), ' se pueden corregir solos:', int((resto['Se puede corregir solo'] == 'Sí').sum()))
print('kimal en grupos:', Lst[Lst.Zona == 'Kimal']['Se puede corregir solo'].value_counts().to_dict())
r2 = resto.assign(mm=pd.to_numeric(resto['MM$/mes (solo, promedio)'], errors='coerce')).sort_values('mm', ascending=False)
print('resto MM$ (solo, prom): suma', round(r2.mm.sum(), 1), ' >2 MM$:', int((r2.mm > 2).sum()), ' top:', r2[['Tramo', 'mm', 'Se puede corregir solo']].head(8).to_string(index=False))
with pd.ExcelWriter(X, engine='openpyxl', mode='a', if_sheet_exists='replace') as w: Lst.to_excel(w, sheet_name='Listado', index=False)
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
wb = load_workbook(X); ws = wb['Listado']
for c in ws[1]: c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='30849B'); c.alignment = Alignment(wrap_text=True, vertical='center')
for col in ws.columns: ws.column_dimensions[col[0].column_letter].width = max(10, min(45, max(len(str(v.value or '')) for v in col) + 2))
ws.freeze_panes = 'E2'; wb.save(X)
