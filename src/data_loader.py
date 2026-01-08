"""
Módulo para cargar datos de líneas eléctricas desde archivos CSV y Excel.
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from datetime import datetime

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
        filepath = BASE_PATH / "inputs" / "Actualizacion" / "LinDatParOpe_2024_PNCP.csv"

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
        filepath = BASE_PATH / "inputs" / "Mantenimiento" / "LinDatManOpe_2024_PNCP.csv"

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

    # Seleccionar y renombrar columnas útiles
    columnas_utiles = {
        'Barra A': 'barra_a',
        'Barra B': 'barra_b',
        'Sector A': 'sector_a',
        'Sector B': 'sector_b',
        'Tension A': 'tension_a',
        'Tension B': 'tension_b',
        'Trafo o Linea': 'tipo',  # L=Linea, T=Trafo
        'Nº': 'numero',
        'Nombre A->B': 'nombre',
        'V [kV]': 'voltaje_kv',
        'R [ohm]': 'resistencia_ohm',
        'X [ohm]': 'reactancia_ohm',
        'Operativa': 'operativa',
        'Tronc': 'troncal',
        'Zona': 'zona',
        'dir': 'direccion',
        'Area': 'area'
    }

    # Filtrar columnas que existen
    columnas_presentes = {k: v for k, v in columnas_utiles.items() if k in df.columns}
    df_limpio = df[list(columnas_presentes.keys())].copy()
    df_limpio.rename(columns=columnas_presentes, inplace=True)

    # Convertir tipos de datos
    cols_numericas = ['tension_a', 'tension_b', 'numero', 'voltaje_kv',
                      'resistencia_ohm', 'reactancia_ohm', 'operativa',
                      'troncal', 'zona', 'direccion', 'area']

    for col in cols_numericas:
        if col in df_limpio.columns:
            df_limpio[col] = pd.to_numeric(df_limpio[col], errors='coerce')

    # Eliminar filas completamente vacías
    df_limpio = df_limpio.dropna(how='all')

    return df_limpio


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

    return df_cruce


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
