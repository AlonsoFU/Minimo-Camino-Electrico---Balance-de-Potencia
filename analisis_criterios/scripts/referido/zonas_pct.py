exec(open('dos_por_dos.py').read().split("todos = list(bloques)")[0])
L = pd.read_excel('/home/user/Minimo-Camino-Electrico---Balance-de-Potencia/analisis_criterios/datos/lista_revision.xlsx', sheet_name='Lista').Tramo.tolist()
kimal_v = ['A_____________100->CHUQUICAMATA__100','CRUCERO_______220->PALPANA_______220','SALARCHUQAUX__220->CHUQUICAMATA__220','CUMBRES_______500->JADRESIC______500','ENCUENTRO_____220->TS.GORDA_E____220','KIMAL_________220->CRUCEROSALAUX_220','KIMAL_________220->M.ELENA_______220','KIMAL_________220->ENCUENTRO_____220','KIMAL_________500->KIMAL_________220','L.CHANGOS_____500->L.CHANGOS_____220','TAPLOA________220->KIMAL_________220','NUEVA_CHUQUI__220->CALAMA________220','NUEVA_CHUQUI__220->CHUQUICAMATA__220','NUEVA_CHUQUI__220->SALAR_________220','TOCOPILLA_____220->TAPLOA________220','SALAR_________220->SALARCHUQAUX__220']
Z = {'Kimal': ['L.CHANGOS_____500->KIMAL_________500','CRUCERO_______220->KIMAL_________220'] + kimal_v,
     'Santiago oriente': ['L.ALMENDROS___220->L.ALMENDROS___110','EL_SALTO______110->SAN_CRISTOBAL_110','EL_SALTO______110->TAP_LA_DEHESA_110','SAN_CRISTOBAL_110->TAP_RECOLETA__110'],
     'Ventanas': ['VENTANAS______220->VENTANAS______110','MIRAFLORES____110->TORQUEMADA____110'],
     'Maule–Itahue–Teno–Linares': ['TENO__________154->TENO__________066','MAULE_________154->MAULE_________066','ITAHUE________154->ITAHUE________066','LINARES_______154->LINARES_______066','RAUQUEN_______066->TENO__________066','CHIMBARONGO___066->QUINTA________066'],
     'Mulchén': ['LOS_NOTROS____220->MULCHEN_______220','MULCHEN_______220->SANTACLARA____220','SANTACLARA____220->CHARRUA_______220','LOS_NOTROS____220->CHARRUA_______220'],
     'Resto comunes': ['ISLADMAIPO____066->ELMONTE_______066','TURIBE________110->ESMERALDA_____110','A.MELIP_______220->DICHAS________220','ALGARROBAL____220->MAITENCILLO___220']}
for z, l in Z.items():
    falt = [t for t in l if t not in bloques]
    if falt: print('no está en bloques:', z, falt)
    Z[z] = [t for t in l if t in bloques]
out = []
for nom, an, modo in [('Trafo troncal, X', m3, 'X'), ('Misma subestación, R', m1, 'Z')]:
    M = est_f(True, an, modo, []); T = est_f(True, an, modo, [t for t in L if t in bloques])
    def eff(a):
        ch = a[a != M.reindex(a.index)]; mw = S.mw.reindex(ch.index).fillna(0)
        return set(ch.index), float(((ch.map(precio) - M.reindex(ch.index).map(precio)).abs() * mw / 1000).sum())
    tb, tm = eff(T)
    for z, l in Z.items():
        b, m = eff(est_f(True, an, modo, l))
        out.append({'Criterio': nom, 'Zona': z, 'Tramos': len(l), 'Barras que cambian': len(b), 'MM$/mes': round(m), '% de la plata del total': round(100 * m / tm), '% de las barras del total': round(100 * len(b & tb) / len(tb)), 'MM$ por tramo': round(m / len(l), 1)})
    out.append({'Criterio': nom, 'Zona': 'TOTAL (lista completa)', 'Tramos': len([t for t in L if t in bloques]), 'Barras que cambian': len(tb), 'MM$/mes': round(tm), '% de la plata del total': 100, '% de las barras del total': 100, 'MM$ por tramo': None})
R = pd.DataFrame(out); pd.set_option('display.width', 220); print(R.to_string(index=False)); R.to_pickle(OUT + 'zonas_pct.pkl')
