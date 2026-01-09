"""
Módulo para cargar datos de líneas eléctricas desde archivos CSV y Excel.
"""

import pandas as pd
import re
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
from rapidfuzz import fuzz

# Ruta base del proyecto
BASE_PATH = Path(__file__).parent.parent

# Mapeo de meses en español a número
MESES = {
    'Ene': 1, 'Feb': 2, 'Mar': 3, 'Abr': 4,
    'May': 5, 'Jun': 6, 'Jul': 7, 'Ago': 8,
    'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dic': 12
}


def convertir_fecha(fecha_str: str) -> Optional[datetime]:
    """
    Convierte fecha del formato 'MesXXX-YYYY' a datetime.

    Args:
        fecha_str: Fecha en formato 'MesNov-2017', 'MesDic-2023', etc.
                   '*' indica sin fecha.

    Returns:
        datetime o None si no tiene fecha válida.

    Ejemplos:
        'MesNov-2017' -> datetime(2017, 11, 1)
        'MesDic-2023' -> datetime(2023, 12, 1)
        '*' -> None
    """
    if pd.isna(fecha_str) or fecha_str == '*':
        return None

    try:
        # Formato: MesXXX-YYYY
        if fecha_str.startswith('Mes') and '-' in fecha_str:
            partes = fecha_str.replace('Mes', '').split('-')
            mes_str = partes[0]
            anio_str = partes[1]

            # Si el año es '*', no hay fecha válida
            if anio_str == '*':
                return None

            mes = MESES.get(mes_str)
            anio = int(anio_str)

            if mes:
                return datetime(anio, mes, 1)
    except (ValueError, IndexError, KeyError):
        pass

    return None


def aplicar_conversion_fechas(df: pd.DataFrame, columnas: list) -> pd.DataFrame:
    """
    Aplica conversión de fechas a las columnas especificadas.

    Args:
        df: DataFrame a modificar
        columnas: Lista de columnas a convertir

    Returns:
        DataFrame con columnas de fecha convertidas
    """
    df = df.copy()
    for col in columnas:
        if col in df.columns:
            df[col] = df[col].apply(convertir_fecha)
    return df


def cargar_lineas_operacion(filepath: Optional[str] = None, convertir_fechas: bool = True) -> pd.DataFrame:
    """
    Carga el archivo CSV de parámetros de operación de líneas.

    Args:
        filepath: Ruta al archivo CSV. Si es None, usa la ruta por defecto.
        convertir_fechas: Si True, convierte fechas a formato datetime.

    Returns:
        DataFrame con los datos de operación de líneas.
    """
    if filepath is None:
        filepath = BASE_PATH / "inputs" / "Actualizacion CNE" / "LinDatParOpe_2024_PNCP.csv"

    df = pd.read_csv(filepath, encoding='latin-1')

    # Convertir columnas numéricas
    cols_numericas = [
        'LinINum', 'LinNIntHis', 'LinPotMaxA->B', 'LinPotMaxB->A',
        'LinPotN-1A->B', 'LinPotN-1B->A', 'LinVolt', 'LinR', 'LinX',
        'LinNTra', 'LinDisEne', 'LinVI', 'LinCOMA', 'LinVidUti'
    ]

    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Convertir columnas booleanas (T/F)
    cols_booleanas = [
        'LinFOpe', 'LinFPrtFlu', 'LinFPrtHis', 'LinFPrtInd', 'LinFCC',
        'LinFMax', 'LinFPri', 'LinFN-1', 'LinFPer', 'LinFPeaCal',
        'LinFTipDef', 'LinFInv'
    ]

    for col in cols_booleanas:
        if col in df.columns:
            df[col] = df[col].map({'T': True, 'F': False})

    # Convertir fechas
    if convertir_fechas:
        df = aplicar_conversion_fechas(df, ['LinFecOpeIni', 'LinFecOpeFin'])

    return df


def cargar_lineas_mantenimiento(filepath: Optional[str] = None, convertir_fechas: bool = True) -> pd.DataFrame:
    """
    Carga el archivo CSV de mantenimiento de líneas.

    Args:
        filepath: Ruta al archivo CSV. Si es None, usa la ruta por defecto.
        convertir_fechas: Si True, convierte fechas a formato datetime.

    Returns:
        DataFrame con los datos de mantenimiento de líneas.
    """
    if filepath is None:
        filepath = BASE_PATH / "inputs" / "Mantenimiento CNE" / "LinDatManOpe_2024_PNCP.csv"

    df = pd.read_csv(filepath, encoding='latin-1')

    # Convertir columnas numéricas
    cols_numericas = [
        'LinINum', 'LinIBlo', 'LinPotMaxA->B', 'LinPotMaxB->A',
        'LinPotN-1A->B', 'LinPotN-1B->A', 'LinVolt', 'LinR', 'LinX',
        'LinDisEne', 'LinVI', 'LinCOMA'
    ]

    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Convertir columnas booleanas (T/F)
    cols_booleanas = ['LinFMan', 'LinFManTip', 'LinFOpe', 'LinFMax', 'LinFN-1', 'LinFCC']

    for col in cols_booleanas:
        if col in df.columns:
            df[col] = df[col].map({'T': True, 'F': False})

    # Convertir fechas
    if convertir_fechas:
        df = aplicar_conversion_fechas(df, ['LinFecIni', 'LinFecFin'])

    return df


def cargar_lineas_ent(filepath: Optional[str] = None, sheet_name: str = 'lineas') -> pd.DataFrame:
    """
    Carga la hoja 'lineas' del archivo Excel ENT.

    Args:
        filepath: Ruta al archivo Excel. Si es None, usa la ruta por defecto.
        sheet_name: Nombre de la hoja a cargar.

    Returns:
        DataFrame con los datos de líneas del archivo ENT.
    """
    if filepath is None:
        filepath = BASE_PATH / "inputs" / "Base Ent" / "Ent2026.xlsx"

    # Leer con header en fila 4 (0-indexed)
    df = pd.read_excel(filepath, sheet_name=sheet_name, header=4)

    # Seleccionar solo columnas necesarias
    columnas_utiles = {
        'Nombre A->B': 'nombre',
        'Barra A': 'barra_a',
        'Barra B': 'barra_b',
        'V [kV]': 'voltaje_kv',
        'R [ohm]': 'resistencia_ohm',
        'X [ohm]': 'reactancia_ohm'
    }

    # Filtrar columnas que existen
    columnas_presentes = {k: v for k, v in columnas_utiles.items() if k in df.columns}
    df_limpio = df[list(columnas_presentes.keys())].copy()
    df_limpio.rename(columns=columnas_presentes, inplace=True)

    # Convertir tipos de datos numéricos
    cols_numericas = ['voltaje_kv', 'resistencia_ohm', 'reactancia_ohm']

    for col in cols_numericas:
        if col in df_limpio.columns:
            df_limpio[col] = pd.to_numeric(df_limpio[col], errors='coerce')

    # Eliminar filas completamente vacías
    df_limpio = df_limpio.dropna(how='all')

    return df_limpio


def cargar_lineas_infotecnica(filepath: Optional[str] = None) -> pd.DataFrame:
    """
    Carga el archivo Excel de Infotécnica (reporte secciones-tramos).

    Args:
        filepath: Ruta al archivo Excel. Si es None, usa la ruta por defecto.

    Returns:
        DataFrame con columnas:
        - nombre, nombre_centro_control
        - tension_nominal, longitud
        - R_unitaria, X_unitaria (ohm/km)
        - R_total, X_total (ohm) = R/X_unitaria * longitud
    """
    if filepath is None:
        filepath = BASE_PATH / "inputs" / "Actualizacion Infotecnica" / "reporte_secciones-tramos.xlsx"

    # Leer con header en fila 6 (0-indexed)
    df = pd.read_excel(filepath, sheet_name=0, header=6)

    # Seleccionar columnas requeridas
    columnas_origen = [
        'Nombre',
        'Nombre Centro Control',
        '1.1 Tensión nominal',
        '1.2 Longitud conductor',
        '1.3 Resistencia de secuencia positiva a 20°C (50 Hz)',
        '1.4 Reactancia de Secuencia positiva  X (50Hz)'
    ]

    df_filtrado = df[columnas_origen].copy()

    # Renombrar columnas
    df_filtrado.columns = [
        'nombre',
        'nombre_centro_control',
        'tension_nominal',
        'longitud',
        'R_unitaria',
        'X_unitaria'
    ]

    # Convertir a numérico
    cols_numericas = ['tension_nominal', 'longitud', 'R_unitaria', 'X_unitaria']
    for col in cols_numericas:
        df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce')

    # Calcular R_total y X_total (R/X unitaria * longitud)
    df_filtrado['R_total'] = df_filtrado['R_unitaria'] * df_filtrado['longitud']
    df_filtrado['X_total'] = df_filtrado['X_unitaria'] * df_filtrado['longitud']

    # Eliminar filas vacías
    df_filtrado = df_filtrado.dropna(how='all')

    return df_filtrado


def cruzar_operacion_mantenimiento(df_operacion: Optional[pd.DataFrame] = None,
                                    df_mantenimiento: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Cruza los datos de operación con los de mantenimiento para detectar
    los mantenimientos programados de cada línea.

    El cruce se hace por el nombre de la línea (LinNom).

    Args:
        df_operacion: DataFrame de operación. Si es None, se carga automáticamente.
        df_mantenimiento: DataFrame de mantenimiento. Si es None, se carga automáticamente.

    Returns:
        DataFrame con las líneas de operación y sus mantenimientos asociados.
        Columnas adicionales con prefijo 'man_' para datos de mantenimiento.
    """
    if df_operacion is None:
        df_operacion = cargar_lineas_operacion()
    if df_mantenimiento is None:
        df_mantenimiento = cargar_lineas_mantenimiento()

    # Renombrar columnas de mantenimiento para evitar conflictos
    cols_man_rename = {col: f'man_{col}' for col in df_mantenimiento.columns if col != 'LinNom'}
    df_man_renamed = df_mantenimiento.rename(columns=cols_man_rename)

    # Hacer el cruce por nombre de línea
    df_cruce = df_operacion.merge(
        df_man_renamed,
        on='LinNom',
        how='left',
        indicator=True
    )

    # Agregar columna para indicar si tiene mantenimiento
    df_cruce['tiene_mantenimiento'] = df_cruce['_merge'] == 'both'
    df_cruce = df_cruce.drop(columns=['_merge'])

    return df_cruce


def obtener_mantenimientos_linea(nombre_linea: str,
                                  df_operacion: Optional[pd.DataFrame] = None,
                                  df_mantenimiento: Optional[pd.DataFrame] = None) -> dict:
    """
    Obtiene los datos de operación y mantenimientos de una línea específica.

    Args:
        nombre_linea: Nombre de la línea a buscar (parcial o completo).
        df_operacion: DataFrame de operación. Si es None, se carga automáticamente.
        df_mantenimiento: DataFrame de mantenimiento. Si es None, se carga automáticamente.

    Returns:
        Diccionario con:
        - 'operacion': DataFrame con datos de operación de la línea
        - 'mantenimientos': DataFrame con mantenimientos de la línea
    """
    if df_operacion is None:
        df_operacion = cargar_lineas_operacion()
    if df_mantenimiento is None:
        df_mantenimiento = cargar_lineas_mantenimiento()

    # Buscar en operación
    mask_op = df_operacion['LinNom'].str.contains(nombre_linea, case=False, na=False)
    lineas_op = df_operacion[mask_op]

    # Buscar en mantenimiento
    mask_man = df_mantenimiento['LinNom'].str.contains(nombre_linea, case=False, na=False)
    lineas_man = df_mantenimiento[mask_man]

    return {
        'operacion': lineas_op,
        'mantenimientos': lineas_man
    }


def aplicar_reemplazo_por_mes(mes_trabajo: str,
                              df_operacion: Optional[pd.DataFrame] = None,
                              df_mantenimiento: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Determina para cada línea si hay un reemplazo de mantenimiento activo
    en el mes especificado.

    Si el mes_trabajo cae dentro del período de mantenimiento (LinFecIni a LinFecFin),
    se usa el valor del mantenimiento. Si no, se usa el valor de operación.

    Reglas de fechas en mantenimiento:
    - LinFecIni = * (NaT): el mantenimiento viene desde siempre
    - LinFecFin = * (NaT): el mantenimiento sigue operativo hasta siempre
    - Ambos = * (NaT): mantenimiento siempre operativo

    Filtros de validez:
    - LinFOpe = F en operación: línea no operativa, se dropea
    - LinFMan = F en mantenimiento: mantenimiento no válido, se ignora

    Args:
        mes_trabajo: Mes a evaluar en formato 'YYYY-MM' (ej: '2025-06').
        df_operacion: DataFrame de operación. Si es None, se carga automáticamente.
        df_mantenimiento: DataFrame de mantenimiento. Si es None, se carga automáticamente.

    Returns:
        DataFrame con columnas adicionales:
        - 'mes_trabajo': El mes evaluado
        - 'hay_reemplazo': True si hay mantenimiento activo en ese mes
        - 'fuente': 'mantenimiento' o 'operacion' según corresponda
    """
    if df_operacion is None:
        df_operacion = cargar_lineas_operacion()
    if df_mantenimiento is None:
        df_mantenimiento = cargar_lineas_mantenimiento()

    # Filtrar líneas de operación donde LinFOpe = True (líneas operativas)
    df_operacion = df_operacion[df_operacion['LinFOpe'] == True].copy()

    # Filtrar mantenimientos donde LinFMan = True (mantenimientos válidos)
    df_mantenimiento = df_mantenimiento[df_mantenimiento['LinFMan'] == True].copy()

    # Convertir mes_trabajo a datetime (primer día del mes)
    fecha_trabajo = pd.to_datetime(mes_trabajo + '-01')

    # Filtrar líneas que aún no existen en el mes de trabajo
    # Si LinFecOpeIni > fecha_trabajo, la línea aún no está operativa
    df_operacion = df_operacion[
        (df_operacion['LinFecOpeIni'].isna()) |  # Sin fecha = existe desde siempre
        (df_operacion['LinFecOpeIni'] <= fecha_trabajo)  # Ya está operativa
    ].copy()

    # Primero hacer el cruce
    df_cruce = cruzar_operacion_mantenimiento(df_operacion, df_mantenimiento)

    # Agregar columna mes_trabajo
    df_cruce['mes_trabajo'] = mes_trabajo

    # Determinar si hay reemplazo activo en ese mes
    # Reglas:
    # - Si LinFecIni es NaT (asterisco): viene desde siempre
    # - Si LinFecFin es NaT (asterisco): sigue hasta siempre
    # - Si ambos son NaT: mantenimiento siempre operativo
    def verificar_reemplazo(row):
        if not row['tiene_mantenimiento']:
            return False

        # Verificar que el mantenimiento sea válido (man_LinFMan = True)
        if 'man_LinFMan' in row and row['man_LinFMan'] == False:
            return False

        fecha_ini = row['man_LinFecIni']
        fecha_fin = row['man_LinFecFin']

        # Si ambas fechas son NaT (asterisco), el mantenimiento está siempre operativo
        if pd.isna(fecha_ini) and pd.isna(fecha_fin):
            return True

        # Verificar si fecha_trabajo está en el rango
        # NaT en inicio = desde siempre, NaT en fin = hasta siempre
        inicio_ok = pd.isna(fecha_ini) or fecha_trabajo >= fecha_ini
        fin_ok = pd.isna(fecha_fin) or fecha_trabajo <= fecha_fin

        return inicio_ok and fin_ok

    df_cruce['hay_reemplazo'] = df_cruce.apply(verificar_reemplazo, axis=1)

    # Agregar columna fuente
    df_cruce['fuente'] = df_cruce['hay_reemplazo'].apply(
        lambda x: 'mantenimiento' if x else 'operacion'
    )

    # Seleccionar solo columnas relevantes
    columnas_finales = [
        'LinNom',                # Nombre de la línea
        'LinR', 'LinX',          # Resistencia y reactancia
        'LinFecOpeIni', 'LinFecOpeFin',  # Fechas operación
        'man_LinFecIni', 'man_LinFecFin',  # Fechas mantenimiento
        'mes_trabajo',           # Mes de trabajo (input)
        'hay_reemplazo',         # Si hay reemplazo activo
        'fuente'                 # Origen de los datos
    ]

    # Filtrar solo columnas que existen
    columnas_presentes = [col for col in columnas_finales if col in df_cruce.columns]
    df_resultado = df_cruce[columnas_presentes].copy()

    return df_resultado


def cargar_todos_los_datos() -> dict:
    """
    Carga todos los DataFrames de datos de líneas.

    Returns:
        Diccionario con los DataFrames:
        - 'operacion': Datos de operación de líneas
        - 'mantenimiento': Datos de mantenimiento de líneas
        - 'ent_lineas': Datos de líneas del archivo ENT
    """
    return {
        'operacion': cargar_lineas_operacion(),
        'mantenimiento': cargar_lineas_mantenimiento(),
        'ent_lineas': cargar_lineas_ent()
    }


def normalizar_barra_ent(barra: str) -> str:
    """
    Normaliza el nombre de una barra del archivo ENT.

    El formato ENT es: NOMBRE_PADDED_VOLTAJE (ej: PAPOSO________220)
    - Elimina el sufijo de voltaje (últimos 2-3 dígitos)
    - Reemplaza guiones bajos y puntos por espacios
    - Convierte a minúsculas

    Args:
        barra: Nombre de la barra del ENT

    Returns:
        Nombre normalizado
    """
    barra = str(barra)
    # Eliminar sufijo de voltaje (últimos 2-3 dígitos precedidos de _)
    barra = re.sub(r'_*(\d{2,3})$', '', barra)
    # Reemplazar caracteres especiales
    barra = barra.replace('_', ' ').replace('.', ' ')
    # Limpiar espacios múltiples y convertir a minúsculas
    return ' '.join(barra.split()).lower().strip()


def normalizar_barra_op(barra: str) -> str:
    """
    Normaliza el nombre de una barra del archivo de operación.

    Extrae el nombre de la barra desde el formato "NOMBRE VOLTAJE CIRCUITO"
    eliminando el sufijo de voltaje al final.

    Args:
        barra: Nombre de la barra del archivo de operación (extraído de LinNom)

    Returns:
        Nombre normalizado
    """
    barra = str(barra)
    # Eliminar sufijo de voltaje
    barra = re.sub(r'\s+\d{2,3}$', '', barra)
    # Reemplazar guiones bajos y puntos por espacios
    barra = barra.replace('_', ' ').replace('.', ' ')
    # Limpiar espacios múltiples y convertir a minúsculas
    return ' '.join(barra.split()).lower().strip()


def extraer_barras_de_linnom(linnom: str) -> Tuple[str, str, Optional[float]]:
    """
    Extrae las barras A y B y el voltaje desde el nombre de línea LinNom.

    El formato de LinNom es: "BARRA_A VOLTAJE->BARRA_B VOLTAJE CIRCUITO"
    Ejemplo: "SUEZ_Los Changos 220->Kapatur 220 I"
             "Los Changos 500->Kimal 500 II"

    Args:
        linnom: Nombre de la línea en formato operación

    Returns:
        Tupla con (barra_a, barra_b, voltaje)
    """
    if pd.isna(linnom):
        return ('', '', None)

    linnom = str(linnom)

    # Separar por "->" (el separador real del archivo de operación)
    partes = linnom.split('->')
    if len(partes) < 2:
        # Intentar con " - " como fallback
        partes = linnom.split(' - ')
        if len(partes) < 2:
            return (linnom, '', None)

    barra_a_raw = partes[0].strip()
    resto = '->'.join(partes[1:]).strip()

    # Extraer voltaje de barra_a (último número de 2-3 dígitos)
    match_volt = re.search(r'\s+(\d{2,3})\s*$', barra_a_raw)
    voltaje = float(match_volt.group(1)) if match_volt else None

    # Limpiar barra_a quitando el voltaje
    barra_a = re.sub(r'\s+\d{2,3}\s*$', '', barra_a_raw)

    # Limpiar barra_b quitando voltaje y circuito (ej: "I", "II", "C1", "C2")
    # Formato: "Kapatur 220 I" -> "Kapatur"
    barra_b = re.sub(r'\s+\d{2,3}\s*[IVX]*\s*$', '', resto)  # Romanos I, II, III, IV, V
    barra_b = re.sub(r'\s+\d{2,3}\s*C?\d*\s*$', '', barra_b)  # C1, C2
    barra_b = re.sub(r'\s+[IVX]+\s*$', '', barra_b)  # Romanos solos al final

    return (barra_a.strip(), barra_b.strip(), voltaje)


def extraer_circuito_ent(nombre: str) -> Optional[int]:
    """
    Extrae el número de circuito del nombre ENT.

    Patrones:
    - '_1de2' -> 1
    - '_2de3' -> 2
    - Sin patrón -> None

    Args:
        nombre: Nombre de la línea ENT

    Returns:
        Número de circuito (1, 2, 3...) o None
    """
    match = re.search(r'_(\d+)de\d+$', str(nombre))
    if match:
        return int(match.group(1))
    return None


def extraer_circuito_op(linnom: str) -> Optional[int]:
    """
    Extrae el número de circuito del nombre de operación.

    Patrones:
    - 'I' -> 1, 'II' -> 2, 'III' -> 3, 'IV' -> 4, 'V' -> 5
    - 'C1' -> 1, 'C2' -> 2

    Args:
        linnom: Nombre de la línea de operación

    Returns:
        Número de circuito (1, 2, 3...) o None
    """
    linnom = str(linnom).strip()

    # Buscar romano al final
    romanos = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6}
    match = re.search(r'\s+([IVX]+)\s*$', linnom)
    if match:
        romano = match.group(1)
        return romanos.get(romano)

    # Buscar C1, C2, etc
    match = re.search(r'\s+C(\d+)\s*$', linnom)
    if match:
        return int(match.group(1))

    return None


def calcular_similitud_barras(barra_ent: str, barra_op: str) -> float:
    """
    Calcula la similitud entre dos nombres de barras.

    Usa múltiples estrategias:
    1. Comparación sin espacios (para nombres concatenados como TAPTALTAL1 vs Tap Taltal 1)
    2. Token sort ratio (para reordenamientos)
    3. Bonus si uno contiene al otro

    Args:
        barra_ent: Nombre de barra del ENT (ya normalizado con espacios)
        barra_op: Nombre de barra de operación (ya normalizado con espacios)

    Returns:
        Porcentaje de similitud (0-100)
    """
    # Versión sin espacios para comparar nombres concatenados
    ent_sin_espacios = barra_ent.replace(' ', '')
    op_sin_espacios = barra_op.replace(' ', '')

    # Estrategia 1: Comparación directa sin espacios
    score_sin_espacios = fuzz.ratio(ent_sin_espacios, op_sin_espacios)

    # Estrategia 2: Token sort (con espacios)
    score_token = fuzz.token_sort_ratio(barra_ent, barra_op)

    # Estrategia 3: Si uno contiene al otro, bonus
    if ent_sin_espacios in op_sin_espacios or op_sin_espacios in ent_sin_espacios:
        score_sin_espacios = max(score_sin_espacios, 90)

    return max(score_sin_espacios, score_token)


def homologar_lineas(df_ent: Optional[pd.DataFrame] = None,
                     df_operacion: Optional[pd.DataFrame] = None,
                     umbral_confianza: float = 50.0) -> pd.DataFrame:
    """
    Homologa las líneas del archivo ENT con las líneas de operación.

    Busca el mejor match para cada línea ENT comparando:
    1. Voltaje debe coincidir (o ser cercano)
    2. Similitud de nombres de barras (A y B) - usa MÍNIMO de ambas

    También prueba el match invertido (A->B vs B->A) y usa el mejor.

    IMPORTANTE: df_operacion puede ser el resultado de aplicar_reemplazo_por_mes()
    (ya filtrado por mes de trabajo y con valores R/X correctos).

    Args:
        df_ent: DataFrame de líneas ENT. Si es None, se carga automáticamente.
        df_operacion: DataFrame de operación (puede ser df_resultado filtrado).
                      Si es None, se carga automáticamente.
        umbral_confianza: Porcentaje mínimo de confianza para considerar match (default 50%)

    Returns:
        DataFrame con las líneas ENT más columnas adicionales:
        - 'match_linnom': Nombre de línea operación que matchea
        - 'confianza': Porcentaje de confianza (MÍNIMO de ambas barras)
        - 'sim_barra_a', 'sim_barra_b': Similitud individual de cada barra
        - 'match_invertido': True si el match fue con barras invertidas
        - 'requiere_revision': True si confianza entre 50-80%
    """
    if df_ent is None:
        df_ent = cargar_lineas_ent()
    if df_operacion is None:
        df_operacion = cargar_lineas_operacion()
        # Solo filtrar si es df crudo (tiene columna LinFOpe)
        if 'LinFOpe' in df_operacion.columns:
            df_operacion = df_operacion[df_operacion['LinFOpe'] == True].copy()

    # Pre-procesar líneas de operación
    lineas_op_info = []
    for _, row in df_operacion.iterrows():
        linnom = row.get('LinNom')
        if pd.isna(linnom):
            continue
        barra_a, barra_b, voltaje = extraer_barras_de_linnom(linnom)
        circuito_op = extraer_circuito_op(linnom)
        lineas_op_info.append({
            'linnom': linnom,
            'barra_a': normalizar_barra_op(barra_a),
            'barra_b': normalizar_barra_op(barra_b),
            'voltaje': voltaje,
            'circuito': circuito_op,
            'linr': row.get('LinR'),
            'linx': row.get('LinX'),
            'hay_reemplazo': row.get('hay_reemplazo'),
            'fuente': row.get('fuente')
        })

    # Procesar cada línea ENT
    resultados = []

    for idx, row_ent in df_ent.iterrows():
        barra_a_ent = normalizar_barra_ent(row_ent['barra_a'])
        barra_b_ent = normalizar_barra_ent(row_ent['barra_b'])
        voltaje_ent = row_ent['voltaje_kv']
        circuito_ent = extraer_circuito_ent(row_ent['nombre'])

        mejor_match = None
        mejor_confianza = 0
        mejor_sim_a = 0
        mejor_sim_b = 0
        match_invertido = False
        circuito_coincide = None

        for info_op in lineas_op_info:
            # Filtrar por voltaje (debe coincidir exactamente o muy cercano)
            if pd.notna(voltaje_ent) and pd.notna(info_op['voltaje']):
                if abs(voltaje_ent - info_op['voltaje']) > 5:  # Más estricto: 5kV
                    continue

            # Verificar circuito: si ambos tienen, deben coincidir
            circuito_op = info_op['circuito']
            if circuito_ent is not None and circuito_op is not None:
                if circuito_ent != circuito_op:
                    continue  # No matchear si circuitos son diferentes

            # Calcular similitud normal (A-A, B-B)
            sim_a = calcular_similitud_barras(barra_a_ent, info_op['barra_a'])
            sim_b = calcular_similitud_barras(barra_b_ent, info_op['barra_b'])
            # Usar MÍNIMO: ambas barras deben matchear bien
            confianza_normal = min(sim_a, sim_b)

            # Calcular similitud invertida (A-B, B-A)
            sim_a_inv = calcular_similitud_barras(barra_a_ent, info_op['barra_b'])
            sim_b_inv = calcular_similitud_barras(barra_b_ent, info_op['barra_a'])
            confianza_invertida = min(sim_a_inv, sim_b_inv)

            # Usar la mejor de las dos
            if confianza_normal >= confianza_invertida:
                confianza = confianza_normal
                sims = (sim_a, sim_b)
                invertido = False
            else:
                confianza = confianza_invertida
                sims = (sim_a_inv, sim_b_inv)
                invertido = True

            if confianza > mejor_confianza:
                mejor_confianza = confianza
                mejor_sim_a, mejor_sim_b = sims
                circuito_coincide = (circuito_ent == circuito_op) if (circuito_ent and circuito_op) else None
                mejor_match = info_op
                match_invertido = invertido

        # Determinar si requiere revisión
        requiere_revision = umbral_confianza <= mejor_confianza < 80

        # Agregar resultado (ordenado para fácil comparación)
        resultado = {
            # Identificación ENT
            'nombre': row_ent['nombre'],
            'match_linnom': mejor_match['linnom'] if mejor_match and mejor_confianza >= umbral_confianza else None,
            # Confianza
            'confianza': round(mejor_confianza, 1),
            'sim_barra_a': round(mejor_sim_a, 1),
            'sim_barra_b': round(mejor_sim_b, 1),
            'match_invertido': match_invertido if mejor_match and mejor_confianza >= umbral_confianza else None,
            'requiere_revision': requiere_revision,
            # Circuitos
            'circuito_ent': circuito_ent,
            'circuito_op': mejor_match['circuito'] if mejor_match and mejor_confianza >= umbral_confianza else None,
            # Barras ENT
            'barra_a': row_ent['barra_a'],
            'barra_b': row_ent['barra_b'],
            'voltaje_kv': voltaje_ent,
            # Valores R/X de ENT
            'R_ent': row_ent['resistencia_ohm'],
            'X_ent': row_ent['reactancia_ohm'],
            # Valores R/X de Operación (match)
            'R_op': mejor_match['linr'] if mejor_match and mejor_confianza >= umbral_confianza else None,
            'X_op': mejor_match['linx'] if mejor_match and mejor_confianza >= umbral_confianza else None,
            # Info de reemplazo
            'hay_reemplazo': mejor_match.get('hay_reemplazo') if mejor_match and mejor_confianza >= umbral_confianza else None,
            'fuente': mejor_match.get('fuente') if mejor_match and mejor_confianza >= umbral_confianza else None
        }
        resultados.append(resultado)

    return pd.DataFrame(resultados)


def resumen_homologacion(df_homologado: pd.DataFrame) -> dict:
    """
    Genera un resumen estadístico de la homologación.

    Args:
        df_homologado: DataFrame resultado de homologar_lineas()

    Returns:
        Diccionario con estadísticas de la homologación
    """
    total = len(df_homologado)
    con_match = df_homologado['match_linnom'].notna().sum()
    sin_match = total - con_match

    # Distribución por rangos de confianza
    conf_90_100 = ((df_homologado['confianza'] >= 90) & df_homologado['match_linnom'].notna()).sum()
    conf_80_89 = ((df_homologado['confianza'] >= 80) & (df_homologado['confianza'] < 90) & df_homologado['match_linnom'].notna()).sum()
    conf_50_79 = ((df_homologado['confianza'] >= 50) & (df_homologado['confianza'] < 80) & df_homologado['match_linnom'].notna()).sum()
    conf_bajo_50 = (df_homologado['confianza'] < 50).sum()

    # Contar los que requieren revisión
    requiere_revision = df_homologado['requiere_revision'].sum() if 'requiere_revision' in df_homologado.columns else 0

    return {
        'total_lineas': total,
        'con_match': con_match,
        'sin_match': sin_match,
        'porcentaje_match': round(con_match / total * 100, 1) if total > 0 else 0,
        'confianza_90_100': conf_90_100,
        'confianza_80_89': conf_80_89,
        'confianza_50_79': conf_50_79,
        'confianza_bajo_50': conf_bajo_50,
        'requiere_revision': requiere_revision,
        'invertidos': df_homologado['match_invertido'].sum() if 'match_invertido' in df_homologado.columns else 0
    }


if __name__ == "__main__":
    # Ejemplo de uso
    print("Cargando datos de líneas eléctricas...")

    print("\n1. Datos de Operación (LinDatParOpe):")
    df_op = cargar_lineas_operacion()
    print(f"   Shape: {df_op.shape}")
    print(f"   Columnas: {df_op.columns.tolist()}")

    print("\n2. Datos de Mantenimiento (LinDatManOpe):")
    df_man = cargar_lineas_mantenimiento()
    print(f"   Shape: {df_man.shape}")
    print(f"   Columnas: {df_man.columns.tolist()}")

    print("\n3. Datos ENT (hoja lineas):")
    df_ent = cargar_lineas_ent()
    print(f"   Shape: {df_ent.shape}")
    print(f"   Columnas: {df_ent.columns.tolist()}")
