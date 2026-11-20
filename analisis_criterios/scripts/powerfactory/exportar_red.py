"""Exporta la red del proyecto activo de PowerFactory a CSV, para calcular el mínimo camino fuera de PowerFactory.

Cómo usarlo (dentro de PowerFactory):
  1. Abrir el proyecto (modelo del SEN) y activar el caso de estudio y el escenario de operación que corresponden.
  2. En el Administrador de datos, carpeta Scripts del proyecto: Nuevo objeto > Script de Python (ComPython).
  3. En "Archivo de script" elegir este archivo y ejecutar.
  4. Se crea la carpeta CARPETA_SALIDA con un CSV por tipo de elemento y un archivo info.txt.

Solo exporta los elementos relevantes para el cálculo del caso activo (respeta variaciones y escenario), así que
el estado de interruptores y elementos fuera de servicio queda como está en el modelo.
Si un atributo no existe en la versión de PowerFactory, la columna queda vacía (no se cae).
"""
import csv
import datetime
import os

import powerfactory

CARPETA_SALIDA = os.path.join(os.path.expanduser('~'), 'Desktop', 'red_powerfactory')

app = powerfactory.GetApplication()
app.ClearOutputWindow()


def atr(obj, nombre):
    """Atributo del objeto, o vacío si no existe o falla."""
    if obj is None:
        return ''
    try:
        v = obj.GetAttribute(nombre)
    except Exception:
        return ''
    if isinstance(v, list):
        return v[0] if v else ''
    return '' if v is None else v


def nombre(obj):
    return obj.loc_name if obj is not None else ''


def ruta(obj):
    try:
        return obj.GetFullName(type=0) if obj is not None else ''
    except Exception:
        return ''


def terminal(cubiculo):
    """Barra (ElmTerm) a la que llega un cubículo (StaCubic)."""
    if cubiculo is None:
        return None
    try:
        return cubiculo.cterm
    except Exception:
        return None


def subestacion(term):
    if term is None:
        return ''
    for a in ('cpSubstat', 'cpSite'):
        s = atr(term, a)
        if s:
            return nombre(s)
    return nombre(term.GetParent()) if term.GetParent() is not None else ''


def escribir(archivo, filas):
    if not filas:
        app.PrintPlain(f'{archivo}: 0 filas')
        return
    cols = list(filas[0].keys())
    with open(os.path.join(CARPETA_SALIDA, archivo), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter=';')
        w.writeheader()
        w.writerows(filas)
    app.PrintPlain(f'{archivo}: {len(filas)} filas')


def objetos(patron):
    return app.GetCalcRelevantObjects(patron) or []


os.makedirs(CARPETA_SALIDA, exist_ok=True)

# Barras
barras = []
for t in objetos('*.ElmTerm'):
    barras.append({'barra': nombre(t), 'ruta': ruta(t), 'subestacion': subestacion(t), 'kv_nominal': atr(t, 'uknom'),
                   'fuera_de_servicio': atr(t, 'outserv'), 'tipo_barra': atr(t, 'iUsage')})
escribir('barras.csv', barras)

# Líneas
lineas = []
for e in objetos('*.ElmLne'):
    tp = atr(e, 'typ_id')
    a, b = terminal(atr(e, 'bus1')), terminal(atr(e, 'bus2'))
    lineas.append({'linea': nombre(e), 'ruta': ruta(e), 'barra_a': nombre(a), 'barra_b': nombre(b), 'kv_a': atr(a, 'uknom'), 'kv_b': atr(b, 'uknom'),
                   'largo_km': atr(e, 'dline'), 'circuitos_paralelo': atr(e, 'nlnum'), 'fuera_de_servicio': atr(e, 'outserv'),
                   'R1_ohm': atr(e, 'R1'), 'X1_ohm': atr(e, 'X1'),
                   'tipo': nombre(tp), 'tipo_r_ohm_km': atr(tp, 'rline'), 'tipo_x_ohm_km': atr(tp, 'xline'), 'tipo_kv': atr(tp, 'uline')})
escribir('lineas.csv', lineas)

# Trafos de 2 devanados
tr2 = []
for e in objetos('*.ElmTr2'):
    tp = atr(e, 'typ_id')
    hv, lv = terminal(atr(e, 'bushv')), terminal(atr(e, 'buslv'))
    tr2.append({'trafo': nombre(e), 'ruta': ruta(e), 'barra_at': nombre(hv), 'barra_bt': nombre(lv), 'kv_barra_at': atr(hv, 'uknom'), 'kv_barra_bt': atr(lv, 'uknom'),
                'unidades_paralelo': atr(e, 'ntnum'), 'fuera_de_servicio': atr(e, 'outserv'), 'tap': atr(e, 'nntap'),
                'tipo': nombre(tp), 'mva': atr(tp, 'strn'), 'kv_at': atr(tp, 'utrn_h'), 'kv_bt': atr(tp, 'utrn_l'),
                'uk_pct': atr(tp, 'uktr'), 'pcu_kw': atr(tp, 'pcutr'), 'ukr_pct': atr(tp, 'uktrr')})
escribir('trafos2.csv', tr2)

# Trafos de 3 devanados
tr3 = []
for e in objetos('*.ElmTr3'):
    tp = atr(e, 'typ_id')
    hv, mv, lv = terminal(atr(e, 'bushv')), terminal(atr(e, 'busmv')), terminal(atr(e, 'buslv'))
    tr3.append({'trafo': nombre(e), 'ruta': ruta(e), 'barra_at': nombre(hv), 'barra_mt': nombre(mv), 'barra_bt': nombre(lv),
                'kv_barra_at': atr(hv, 'uknom'), 'kv_barra_mt': atr(mv, 'uknom'), 'kv_barra_bt': atr(lv, 'uknom'),
                'unidades_paralelo': atr(e, 'nt3nm'), 'fuera_de_servicio': atr(e, 'outserv'), 'tipo': nombre(tp),
                'mva_at': atr(tp, 'strn3_h'), 'mva_mt': atr(tp, 'strn3_m'), 'mva_bt': atr(tp, 'strn3_l'),
                'kv_at': atr(tp, 'utrn3_h'), 'kv_mt': atr(tp, 'utrn3_m'), 'kv_bt': atr(tp, 'utrn3_l'),
                'uk_at_mt_pct': atr(tp, 'uktr3_h'), 'uk_mt_bt_pct': atr(tp, 'uktr3_m'), 'uk_bt_at_pct': atr(tp, 'uktr3_l'),
                'pcu_at_mt_kw': atr(tp, 'pcut3_h'), 'pcu_mt_bt_kw': atr(tp, 'pcut3_m'), 'pcu_bt_at_kw': atr(tp, 'pcut3_l')})
escribir('trafos3.csv', tr3)

# Acoplamientos (interruptores entre barras)
acop = []
for e in objetos('*.ElmCoup'):
    a, b = terminal(atr(e, 'bus1')), terminal(atr(e, 'bus2'))
    acop.append({'acoplamiento': nombre(e), 'ruta': ruta(e), 'barra_a': nombre(a), 'barra_b': nombre(b), 'cerrado': atr(e, 'on_off'),
                 'fuera_de_servicio': atr(e, 'outserv'), 'tipo': atr(e, 'aUsage')})
escribir('acoplamientos.csv', acop)

# Interruptores de cubículo (abren un elemento en un extremo)
sw = []
for e in objetos('*.StaSwitch'):
    cub = e.GetParent(); t = terminal(cub)
    try:
        elem = cub.obj_id
    except Exception:
        elem = None
    sw.append({'interruptor': nombre(e), 'barra': nombre(t), 'elemento': nombre(elem), 'clase_elemento': elem.GetClassName() if elem is not None else '',
               'cerrado': atr(e, 'on_off')})
escribir('interruptores.csv', sw)

# Otras impedancias serie (reactores, condensadores serie, impedancias en p.u.)
otras = []
for patron in ('*.ElmSind', '*.ElmScap', '*.ElmZpu'):
    for e in objetos(patron):
        a, b = terminal(atr(e, 'bus1')), terminal(atr(e, 'bus2'))
        otras.append({'elemento': nombre(e), 'clase': e.GetClassName(), 'ruta': ruta(e), 'barra_a': nombre(a), 'barra_b': nombre(b),
                      'fuera_de_servicio': atr(e, 'outserv'), 'kv': atr(e, 'ucn'), 'mva_base': atr(e, 'Sn'),
                      'r_ohm': atr(e, 'rrea'), 'x_ohm': atr(e, 'xrea'), 'r_pu': atr(e, 'r_pu'), 'x_pu': atr(e, 'x_pu'), 'x_cap_ohm': atr(e, 'xcap')})
escribir('otras_impedancias.csv', otras)

# Identificación del modelo
proy = app.GetActiveProject(); caso = app.GetActiveStudyCase()
try:
    esc = app.GetActiveScenario()
except Exception:
    esc = None
with open(os.path.join(CARPETA_SALIDA, 'info.txt'), 'w', encoding='utf-8') as f:
    f.write(f'proyecto: {nombre(proy)}\ncaso de estudio: {nombre(caso)}\nescenario: {nombre(esc)}\n')
    f.write(f'version PowerFactory: {atr(app, "version")}\nexportado: {datetime.datetime.now():%Y-%m-%d %H:%M}\n')
    for n, l in [('barras', barras), ('lineas', lineas), ('trafos2', tr2), ('trafos3', tr3), ('acoplamientos', acop), ('interruptores', sw), ('otras', otras)]:
        f.write(f'{n}: {len(l)}\n')
app.PrintPlain(f'Listo: {CARPETA_SALIDA}')
