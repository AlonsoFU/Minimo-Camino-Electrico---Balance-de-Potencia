"""Todo el análisis de datos con «Referido + misma subestación» y |Z|: decisivos, calidad, cadena, combinaciones y validación de R."""
exec(open('dec_criterios.py').read().split("CR = {")[0])
exec('cdf ='+open('banco.py').read().split('cdf =',1)[1].split('rows = []')[0])
import time
src = lambda b: b if b in coord else R0.loc[b, 'nodo']
o0c = esc2(True, m1)
def estado(apl):
    o = o0c.copy()
    for b in apl:
        for i in bloques[b]:
            if m1.loc[i]: continue
            o.loc[i, 'X'] = xsug[i]; o.loc[i, 'R'] = rs[i] * ref.loc[i]
    return asignar(pesos_z(o, 'Z'))
base = estado([]); print('reproduce Ref+Sub |Z|:', int((base == S['Ref+Sub (|Z|)'].reindex(base.index)).sum()), '/', len(base), flush=True)
PNa = R0['PN2604']
def calidad(ch, b0):
    dk = pd.Series({x: km(src(x), ch[x]) - km(src(x), b0[x]) for x in ch.index}); mwc = S.mw.reindex(ch.index).fillna(0)
    dpp = (ch.map(precio) - b0.reindex(ch.index).map(precio)).abs() * mwc / 1000
    pn = (ch == PNa.reindex(ch.index)).astype(int) - (b0.reindex(ch.index) == PNa.reindex(ch.index)).astype(int)
    return int((dk < -5).sum()), int((dk > 5).sum()), dpp[dk < -5].sum(), dpp[dk > 5].sum(), int((pn > 0).sum()), int((pn < 0).sum())
t0 = time.time(); ind = {}
for b in bloques:
    if all(m1.loc[i] for i in bloques[b]): continue
    s = estado([b]); ch, mm = plata(base, s)
    ind[b] = (set(ch.index), mm, ch)
dec = [b for b in ind if ind[b][0]]; print('decisivos:', len(dec), 'probados:', len(ind), round(time.time() - t0), 's', flush=True)
filas = []
for b in dec:
    ch = ind[b][2]; nm_, ne_, mj, em, pg, pp = calidad(ch, base)
    geo = 'Sin evaluar' if nm_ + ne_ == 0 else ('Mejora' if mj > 2 * em or (mj == em == 0 and nm_ > ne_) else ('Empeora' if em > 2 * mj or (mj == em == 0 and ne_ > nm_) else 'Mixto'))
    pn = pg - pp
    d = ('A. Cambiar' if geo == 'Mejora' and pn >= 0 else 'B. Revisar ficha' if (geo == 'Mejora' and pn < 0) or (geo == 'Empeora' and pn > 0)
         else 'C. No cambiar sin ficha' if geo == 'Empeora' else 'D. Sin señal clara')
    filas.append({'Tramo': b, 'Barras': len(ch), 'MM$/mes': round(ind[b][1], 1), 'Más cerca': nm_, 'Más lejos': ne_, 'PN2604 gana/pierde': f'{pg}/{pp}', 'Geografía': geo, 'Decisión': d})
Q = pd.DataFrame(filas).sort_values('MM$/mes', ascending=False); print(Q.Decisión.value_counts().to_string(), flush=True)
union = set().union(*[ind[b][0] for b in dec])
sj = estado(dec); chj, mmj = plata(base, sj); sa = estado(list(ind)); cha, mma = plata(base, sa)
cad = {'De a uno (unión)': (len(union), None), 'Decisivos juntos': (len(chj), round(mmj)), 'Todos juntos': (len(cha), round(mma)),
       'Solo al combinar': (len(set(chj.index) - union), None), 'Se cancelan al combinar': (len(union - set(chj.index)), None)}
print(cad, flush=True)
cur, apl, pasos, pend = base, [], [], sorted(dec, key=lambda b: -ind[b][1])
while pend:
    best = None
    for b in pend:
        s = estado(apl + [b]); ch, mm = plata(cur, s)
        if best is None or mm > best[2] or (mm == best[2] and len(ch) > len(best[1])): best = (b, ch, mm, s)
    b, ch, mm, s = best
    if len(ch) == 0: break
    apl.append(b); pend.remove(b); cur = s; _, mmc = plata(base, cur)
    pasos.append({'Paso': len(apl), 'Tramo': b, 'Barras del paso': len(ch), 'MM$ del paso': round(mm, 1), 'Barras acum.': int((cur != base.reindex(cur.index)).sum()), 'MM$ acum.': round(mmc, 1), 'Solo: barras': len(ind[b][0])})
P = pd.DataFrame(pasos); print(P.head(12).to_string(index=False), flush=True)
nod = [b for b in ind if b not in dec]
def lat(b):
    i = bloques[b][0]
    for n in (nm[int(oper.loc[i, 'Barra A'])], nm[int(oper.loc[i, 'Barra B'])]):
        if n in coord: return coord[n][0]
    return 0.0
nod = sorted(nod, key=lat)
def cambia(g): s = estado(list(g)); return s[s != base.reindex(s.index)]
def ddmin(g):
    n = 2
    while len(g) >= 2:
        k = max(1, len(g) // n); partes = [g[i:i + k] for i in range(0, len(g), k)]; red = False
        for p in partes:
            if len(cambia(p)): g, n, red = p, 2, True; break
        if not red:
            for p in partes:
                comp = [x for x in g if x not in p]
                if comp and len(cambia(comp)): g, n, red = comp, max(n - 1, 2), True; break
        if not red:
            if n >= len(g): break
            n = min(len(g), 2 * n)
    return g
comb = []
for z in [nod[i:i + 40] for i in range(0, len(nod), 40)] + [None]:
    resto = list(z) if z is not None else [x for x in nod if not any(x in c_['Combinación'].split(' + ') for c_ in comb)]
    while len(cambia(resto)):
        m = ddmin(resto); chm = cambia(m); _, mm = plata(base, estado(m))
        nm_, ne_, *_ = calidad(chm, base)
        comb.append({'Combinación': ' + '.join(m), 'Tramos': len(m), 'Barras': len(chm), 'MM$/mes': round(mm, 1), 'Más cerca/más lejos': f'{nm_}/{ne_}'})
        print(comb[-1], flush=True); resto = [x for x in resto if x not in m]
C = pd.DataFrame(comb)
# validación de R (misma regla del 15 %)
Vr = V.copy()
Vr['R_ref'] = np.where(Vr.fuente_valor_sugerido.astype(str).str.contains('CNE') & ~Vr.fuente_valor_sugerido.astype(str).str.contains('Info'), Vr.R_CNE,
               np.where(Vr.fuente_valor_sugerido.astype(str).str.contains('Info') & ~Vr.fuente_valor_sugerido.astype(str).str.contains('CNE'), Vr.R_Infotec, Vr[['R_CNE', 'R_Infotec']].mean(axis=1)))
ok = Vr.R_ref.notna() & (Vr.R_ENT > 0)
dr = (Vr.R_ENT / Vr.R_ref - 1).abs()
RV = pd.DataFrame({'Grupo': ['Con referencia de R', 'R coincide (<15 %)', 'R difiere (≥15 %)', 'R difiere y X coincide', 'R_ENT = 0'],
                   'Tramos': [int(ok.sum()), int((ok & (dr < .15)).sum()), int((ok & (dr >= .15)).sum()),
                              int((ok & (dr >= .15) & Vr.clasificacion_validacion.str.startswith('CORRECTO')).sum()), int((Vr.R_ENT == 0).sum())]})
print(RV.to_string(index=False))
X_ = '/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/resultados_refsub_z.xlsx'
with pd.ExcelWriter(X_, engine='openpyxl') as w:
    Q.to_excel(w, sheet_name='1 Decisivos y calidad', index=False)
    pd.DataFrame([{'Medición': k, 'Barras': v[0], 'MM$/mes': v[1]} for k, v in cad.items()]).to_excel(w, sheet_name='2 Efectos en cadena', index=False)
    P.to_excel(w, sheet_name='3 Secuencia', index=False); C.to_excel(w, sheet_name='4 Combinaciones', index=False); RV.to_excel(w, sheet_name='5 Validación R', index=False)
pd.to_pickle({'Q': Q, 'cad': cad, 'P': P, 'C': C, 'RV': RV}, OUT + 'ref_sub_z.pkl'); print('listo', round(time.time() - t0), 's')
