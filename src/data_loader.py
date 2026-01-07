"""
Módulo para cargar datos de líneas eléctricas desde archivos CSV y Excel.
"""

import pandas as pd
from pathlib import Path
from typing import Optional

# Ruta base del proyecto
BASE_PATH = Path(__file__).parent.parent


def cargar_lineas_operacion(filepath: Optional[str] = None) -> pd.DataFrame:
    """
    Carga el archivo CSV de parámetros de operación de líneas.

    Args:
        filepath: Ruta al archivo CSV. Si es None, usa la ruta por defecto.

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

    return df


def cargar_lineas_mantenimiento(filepath: Optional[str] = None) -> pd.DataFrame:
    """
    Carga el archivo CSV de mantenimiento de líneas.

    Args:
        filepath: Ruta al archivo CSV. Si es None, usa la ruta por defecto.

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
