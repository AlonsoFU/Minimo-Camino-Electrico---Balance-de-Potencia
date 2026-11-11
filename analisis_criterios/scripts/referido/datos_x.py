"""Sensibilidad a los datos: reemplazar X del ENT por la referencia homologada (CNE / Infotécnica)."""
exec(open('con_r.py').read().split("ESC = {")[0])
h = pd.read_excel('/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/revision/homologacion_infotecnica_CNE_peajes.xlsx', sheet_name='homologacion_2025-12')
h['Xref'] = np.where(h.revision.astype(str).isin(['1', 'CNE']), h.X_CNE, np.where(h.revision.astype(str) == 'Infotec', h.X_Infotec, np.nan))
h['fuente'] = np.where(h.revision.astype(str).isin(['1', 'CNE']), 'CNE', np.where(h.revision.astype(str) == 'Infotec', 'Infotec', 'sin referencia'))
h['ratio'] = h.Xref / h.X_ENT
h['tr'] = h.voltaje_a_ENT != h.voltaje_b_ENT
ref_x = h.dropna(subset=['Xref']).set_index('nombre_ENT')
print('filas homologación', len(h), ' con referencia válida', len(ref_x), ' en oper:', oper['Nombre'].isin(ref_x.index).sum(), 'de', len(oper))
v = h.dropna(subset=['Xref'])
for tipo_, m in [('líneas', ~v.tr), ('trafos', v.tr)]:
    r = v.ratio[m]
    print(f'  {tipo_}: n={m.sum()}  <5%: {(abs(r-1)<.05).sum()}  5-20%: {((abs(r-1)>=.05)&(abs(r-1)<.2)).sum()}  20-50%: {((abs(r-1)>=.2)&(abs(r-1)<.5)).sum()}  >50%: {(abs(r-1)>=.5).sum()}  (ref mayor: {(r>1.2).sum()}, ref menor: {(r<0.8).sum()})')
print('sin referencia válida:', (h.fuente == 'sin referencia').sum())
S = pd.read_pickle(OUT + 'con_r.pkl'); s3 = pd.read_pickle(OUT + 'ref_trafo_directo.pkl'); S['Ref+Trafo troncal (X)'] = s3
def con_datos(umbral):
    o = oper.copy(); mp = o['Nombre'].map(ref_x['Xref']); rt = mp / o['X']
    m = mp.notna() & (abs(rt - 1) >= umbral); o.loc[m, 'X'] = mp[m]; return o, int(m.sum())
base = {'Hoy': ('mod_actual', False, None), 'Referido': ('Referido (X)', True, None), 'Ref+Trafo troncal': ('Ref+Trafo troncal (X)', True, m3), 'Ref+Subestación': ('Ref+Sub (X)', True, m1)}
res = {}
for u in [0.2, 0.0]:
    o, n = con_datos(u); print(f'\n== reemplazo si |dif| >= {int(u*100)}%: {n} tramos cambiados')
    for k, (c, rf, an) in base.items():
        oo = o.copy()
        if rf: oo['X'] = oo['X'] * ref
        if an is not None: oo.loc[an, 'X'] = EPS
        s, _ = asigna(grafo_z(oo, 'X')); res[(u, k)] = s
        print(f'  {k:18s} = PN2604: {int((S[c]==S.PN2604).sum())} → {int((s==S.PN2604.reindex(s.index)).sum())}   barras que cambian por datos: {int((s!=S[c].reindex(s.index)).sum())}')
pd.to_pickle(res, OUT + 'datos_x.pkl')
