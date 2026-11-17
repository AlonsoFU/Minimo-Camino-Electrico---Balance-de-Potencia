import sqlite3, json, pandas as pd
exec(open('con_r_plata.py').read().split("def monto")[0].replace("S=pd.read_pickle('con_r.pkl')","S=pd.read_pickle('/tmp/claude-0/-home-user/aef6561c-d05e-5d6f-b069-1de59162b42e/scratchpad/c3/con_r.pkl')"))
out = []
for k in ['tt_x', 'tt_z', 'sub_x', 'sub_z']:
    c = sqlite3.connect(f'registro_{k}.sqlite'); crit = c.execute('select criterio from etapas limit 1').fetchone()[0]
    P = pd.read_sql('select * from pruebas', c); C = pd.read_sql('select * from cambios', c)
    first = P[P.desde_cache == 0].drop_duplicates('tramos').set_index('tramos')['id']   # prueba calculada para cada conjunto
    chg = C.groupby('prueba_id').apply(lambda g: {r.barra: (r.troncal_base, r.troncal_nueva, r.mw) for r in g.itertuples()}).to_dict()
    ch_of = lambda tr: chg.get(first.get(tr), {})
    dec = json.loads(c.execute("select resumen from etapas where etapa='1 individual'").fetchone()[0]); dec = set(dec)
    mat = set(); 
    Z = P[(P.etapa == '4 zonas') & (P.n_tramos >= 2) & (P.n_tramos <= 4) & P.detalle.str.contains('combinación|par')].drop_duplicates('tramos')
    for tr in Z.tramos:
        ts = tr.split(' + '); comb = ch_of(tr); uni = {}
        for t in ts: uni.update(ch_of(t))
        dif = set(comb) ^ set(uni)
        mm = 0.0
        for b in dif:
            bt, nt, mw = comb.get(b) or uni.get(b)
            mm += abs(precio.get(nt, 0) - precio.get(bt, 0)) * mw / 1000
        if mm > 1: mat |= set(ts) - dec
    zres = json.loads(c.execute("select resumen from etapas where etapa='4 zonas'").fetchone()[0])
    vec_all = {v for z in zres for v in z['vecinos_que_interactuan']}
    peso = [z for z in zres if abs(z['mm_zona_completa'] - z['mm_solo_decisivos']) > 1]
    out.append({'Criterio': crit, 'Recálculos registrados': len(P), 'Decisivos': len(dec), 'Vecinos con alguna interacción': len(vec_all),
                'Vecinos con interacción > 1 MM$/mes': len(mat), 'Total a revisar': len(dec | mat),
                'Zonas donde los vecinos cambian la plata (>1 MM$)': len(peso)})
    pd.to_pickle({'dec': dec, 'mat': mat, 'zres': zres}, f'post_{k}.pkl')
R = pd.DataFrame(out); pd.set_option('display.width', 250); print(R.to_string(index=False)); R.to_pickle('post_registro.pkl')
