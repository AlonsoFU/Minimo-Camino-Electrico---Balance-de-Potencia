"""
Funciones para cargar y procesar transformadores de Infotécnica (2D y 3D)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional

BASE_PATH = Path(__file__).parent.parent


def calcular_rx_transformador(
    S_MVA: float,
    V_kV: float,
    Z_percent: float,
    Pcu_kW: float
) -> Tuple[Optional[float], Optional[float], str]:
    """
    Calcula R y X de un transformador en ohmios.

    Fórmulas:
    1. R% = (Pcu_kW × 100) / (S_MVA × 1000)
    2. X% = √(Z%² - R%²)
    3. Z_base = V_kV² / S_MVA
    4. R_Ω = (R% / 100) × Z_base
    5. X_Ω = (X% / 100) × Z_base

    Args:
        S_MVA: Potencia nominal o base (MVA)
        V_kV: Tensión nominal (kV)
        Z_percent: Impedancia de secuencia positiva (%)
        Pcu_kW: Pérdidas en el cobre (kW)

    Returns:
        Tupla (R_ohm, X_ohm, motivo_error)
        motivo_error es None si el cálculo fue exitoso
    """
    # Validar que tengamos valores válidos
    if pd.isna(S_MVA):
        return (None, None, "Falta S_MVA (Capacidad nominal)")
    if pd.isna(V_kV):
        return (None, None, "Falta V_kV (Tensión nominal)")
    if pd.isna(Z_percent):
        return (None, None, "Falta Z% (Impedancia)")
    if pd.isna(Pcu_kW):
        return (None, None, "Falta Pcu_kW (Pérdidas en cobre)")

    if S_MVA <= 0:
        return (None, None, "S_MVA <= 0 (inválido)")
    if V_kV <= 0:
        return (None, None, "V_kV <= 0 (inválido)")

    # Paso 1: Calcular R%
    R_percent = (Pcu_kW * 100) / (S_MVA * 1000)

    # Paso 2: Calcular X%
    # X% = √(Z%² - R%²)
    if Z_percent**2 < R_percent**2:
        # Físicamente imposible, probablemente error en datos
        return (None, None, f"Z%² < R%² (Z={Z_percent:.2f}%, R={R_percent:.2f}%)")

    X_percent = np.sqrt(Z_percent**2 - R_percent**2)

    # Paso 3: Calcular impedancia base
    Z_base = V_kV**2 / S_MVA

    # Paso 4: Convertir a ohmios
    R_ohm = (R_percent / 100) * Z_base
    X_ohm = (X_percent / 100) * Z_base

    return (R_ohm, X_ohm, None)


def cargar_transformadores_2d(filepath: Optional[str] = None) -> pd.DataFrame:
    """
    Carga transformadores 2D de Infotécnica y calcula R/X.

    Returns:
        DataFrame con columnas:
        - nombre: Nombre del transformador
        - nombre_centro_control: Centro de control
        - tension_nominal_at: Tensión AT (kV)
        - tension_nominal_bt: Tensión BT (kV)
        - capacidad_nominal: Capacidad nominal (MVA)
        - R_total: Resistencia en ohm
        - X_total: Reactancia en ohm
        - tipo_instalacion: 'trafo_2d'
    """
    if filepath is None:
        filepath = BASE_PATH / "inputs" / "Actualizacion Infotecnica" / "reporte_transformadores-2d.xlsx"

    # Leer con header en fila 6
    df = pd.read_excel(filepath, sheet_name=0, header=6)

    # Columnas necesarias
    columnas_necesarias = {
        'Nombre': 'nombre',
        'Nombre Centro Control': 'nombre_centro_control',
        '2.1 Capacidad nominal AT': 'capacidad_nominal_mva',
        '2.7 Tensión nominal AT (f-f) el equipo': 'tension_nominal_at',
        '2.7 Tensión nominal BT (f-f) del equipo': 'tension_nominal_bt',
        '2.8 Impedancia de secuencia positiva tap central Z': 'z_percent',
        '2.16 Pérdidas en el cobre de la prueba de cortocircuito Tap central': 'pcu_kw'
    }

    # Filtrar columnas que existen
    columnas_presentes = {k: v for k, v in columnas_necesarias.items() if k in df.columns}
    df_limpio = df[list(columnas_presentes.keys())].copy()
    df_limpio.rename(columns=columnas_presentes, inplace=True)

    # Convertir tipos numéricos
    cols_numericas = ['capacidad_nominal_mva', 'tension_nominal_at', 'tension_nominal_bt',
                      'z_percent', 'pcu_kw']
    for col in cols_numericas:
        if col in df_limpio.columns:
            df_limpio[col] = pd.to_numeric(df_limpio[col], errors='coerce')

    # Calcular R y X para cada transformador
    resultados = []

    for idx, row in df_limpio.iterrows():
        S_MVA = row.get('capacidad_nominal_mva')
        V_kV = row.get('tension_nominal_at')
        Z_percent = row.get('z_percent')
        Pcu_kW = row.get('pcu_kw')

        R_ohm, X_ohm, motivo_error = calcular_rx_transformador(S_MVA, V_kV, Z_percent, Pcu_kW)

        resultados.append({
            'nombre': row.get('nombre'),
            'nombre_centro_control': row.get('nombre_centro_control'),
            'tension_nominal': V_kV,  # Usar AT como tensión nominal
            'tension_nominal_at': V_kV,
            'tension_nominal_bt': row.get('tension_nominal_bt'),
            'capacidad_nominal': S_MVA,
            # Parámetros de cálculo
            'S_MVA': S_MVA,
            'V_kV': V_kV,
            'Z_percent': Z_percent,
            'Pcu_kW': Pcu_kW,
            # Resultados
            'R_total': R_ohm,
            'X_total': X_ohm,
            'motivo_sin_rx': motivo_error,
            'tipo_instalacion': 'trafo_2d'
        })

    return pd.DataFrame(resultados)


def cargar_transformadores_3d(filepath: Optional[str] = None) -> pd.DataFrame:
    """
    Carga transformadores 3D de Infotécnica y calcula R/X.

    Para transformadores 3D se calculan los valores para el devanado AT-MT.

    Returns:
        DataFrame con columnas similares a transformadores 2D
    """
    if filepath is None:
        filepath = BASE_PATH / "inputs" / "Actualizacion Infotecnica" / "reporte_transformadores-3d.xlsx"

    # Leer con header en fila 6
    df = pd.read_excel(filepath, sheet_name=0, header=6)

    # Columnas necesarias para AT-MT
    columnas_necesarias = {
        'Nombre': 'nombre',
        'Nombre Centro Control': 'nombre_centro_control',
        '3.1 Capacidad nominal AT': 'capacidad_nominal_at',
        '3.1 Capacidad nominal MT': 'capacidad_nominal_mt',
        '3.7 Tensión nominal AT (f-f) del equipo': 'tension_nominal_at',
        '3.7 Tensión nominal MT (f-f) del equipo': 'tension_nominal_mt',
        '3.7 Tensión nominal BT (f-f) del equipo': 'tension_nominal_bt',
        '3.8 Impedancia secuencia positiva AT-MT tap central Z': 'z_percent_at_mt',
        '3.16 Pérdidas en el cobre AT-MT  tap central': 'pcu_kw_at_mt',
        '3.25 Potencia base utilizada para calcular las Pérdidas bajo carga y Pérdidas en el cobre AT-MT': 'potencia_base_at_mt'
    }

    # Filtrar columnas que existen
    columnas_presentes = {k: v for k, v in columnas_necesarias.items() if k in df.columns}
    df_limpio = df[list(columnas_presentes.keys())].copy()
    df_limpio.rename(columns=columnas_presentes, inplace=True)

    # Convertir tipos numéricos
    cols_numericas = ['capacidad_nominal_at', 'capacidad_nominal_mt',
                      'tension_nominal_at', 'tension_nominal_mt', 'tension_nominal_bt',
                      'z_percent_at_mt', 'pcu_kw_at_mt', 'potencia_base_at_mt']
    for col in cols_numericas:
        if col in df_limpio.columns:
            df_limpio[col] = pd.to_numeric(df_limpio[col], errors='coerce')

    # Calcular R y X para cada transformador (AT-MT)
    resultados = []

    for idx, row in df_limpio.iterrows():
        # Usar potencia base si está disponible, sino usar capacidad nominal AT
        S_MVA = row.get('potencia_base_at_mt')
        if pd.isna(S_MVA):
            S_MVA = row.get('capacidad_nominal_at')

        V_kV = row.get('tension_nominal_at')
        Z_percent = row.get('z_percent_at_mt')
        Pcu_kW = row.get('pcu_kw_at_mt')

        R_ohm, X_ohm, motivo_error = calcular_rx_transformador(S_MVA, V_kV, Z_percent, Pcu_kW)

        resultados.append({
            'nombre': row.get('nombre'),
            'nombre_centro_control': row.get('nombre_centro_control'),
            'tension_nominal': V_kV,  # Usar AT como tensión nominal
            'tension_nominal_at': V_kV,
            'tension_nominal_mt': row.get('tension_nominal_mt'),
            'tension_nominal_bt': row.get('tension_nominal_bt'),
            'capacidad_nominal': S_MVA,
            # Parámetros de cálculo (AT-MT)
            'S_MVA': S_MVA,
            'V_kV': V_kV,
            'Z_percent': Z_percent,
            'Pcu_kW': Pcu_kW,
            # Resultados
            'R_total': R_ohm,
            'X_total': X_ohm,
            'motivo_sin_rx': motivo_error,
            'tipo_instalacion': 'trafo_3d'
        })

    return pd.DataFrame(resultados)


def consolidar_infotecnica_completa(
    filepath_lineas: Optional[str] = None,
    filepath_trafo_2d: Optional[str] = None,
    filepath_trafo_3d: Optional[str] = None
) -> pd.DataFrame:
    """
    Consolida todas las instalaciones de Infotécnica: líneas, trafos 2D y trafos 3D.

    Returns:
        DataFrame consolidado con columna 'tipo_instalacion' que puede ser:
        - 'linea': Líneas de transmisión
        - 'trafo_2d': Transformadores 2 devanados
        - 'trafo_3d': Transformadores 3 devanados
    """
    # Cargar líneas existentes
    if filepath_lineas is None:
        filepath_lineas = BASE_PATH / "inputs" / "Actualizacion Infotecnica" / "reporte_secciones-tramos.xlsx"

    df_lineas = pd.read_excel(filepath_lineas, sheet_name=0, header=6)

    # Procesar líneas
    df_lineas_procesado = df_lineas[[
        'Nombre Tramo',  # Usar Nombre Tramo en lugar de Nombre
        'Nombre Centro Control',
        '1.1 Tensión nominal',
        '1.2 Longitud conductor',
        '1.3 Resistencia de secuencia positiva a 20°C (50 Hz)',
        '1.4 Reactancia de Secuencia positiva  X (50Hz)'
    ]].copy()

    df_lineas_procesado.columns = [
        'nombre',  # Ahora es Nombre Tramo
        'nombre_centro_control',
        'tension_nominal',
        'longitud',
        'R_unitaria',
        'X_unitaria'
    ]

    # Convertir numéricos
    for col in ['tension_nominal', 'longitud', 'R_unitaria', 'X_unitaria']:
        df_lineas_procesado[col] = pd.to_numeric(df_lineas_procesado[col], errors='coerce')

    # Calcular R y X totales ANTES de agrupar
    df_lineas_procesado['R_total'] = df_lineas_procesado['R_unitaria'] * df_lineas_procesado['longitud']
    df_lineas_procesado['X_total'] = df_lineas_procesado['X_unitaria'] * df_lineas_procesado['longitud']

    # AGRUPAR por Nombre Tramo y SUMAR los valores R y X
    # Cuando hay tramos repetidos (ej: CARDONES - REFUGIO 110KV C1), se suman
    df_lineas_agrupado = df_lineas_procesado.groupby('nombre', dropna=False).agg({
        'nombre_centro_control': 'first',  # Tomar el primero
        'tension_nominal': 'first',  # Debería ser la misma para todos
        'longitud': 'sum',  # Sumar longitudes
        'R_unitaria': 'mean',  # Promedio (para referencia)
        'X_unitaria': 'mean',  # Promedio (para referencia)
        'R_total': 'sum',  # SUMAR R totales
        'X_total': 'sum'   # SUMAR X totales
    }).reset_index()

    # Agregar motivo si falta R/X
    def obtener_motivo_linea(row):
        if pd.notna(row['R_total']):
            return None
        if pd.isna(row['R_unitaria']):
            return "Falta R_unitaria"
        if pd.isna(row['X_unitaria']):
            return "Falta X_unitaria"
        if pd.isna(row['longitud']):
            return "Falta longitud"
        return "Datos incompletos"

    df_lineas_agrupado['motivo_sin_rx'] = df_lineas_agrupado.apply(obtener_motivo_linea, axis=1)
    df_lineas_agrupado['tipo_instalacion'] = 'linea'

    # Cargar transformadores
    print("Cargando transformadores 2D...")
    df_trafo_2d = cargar_transformadores_2d(filepath_trafo_2d)
    print(f"  Transformadores 2D cargados: {len(df_trafo_2d)}")

    print("Cargando transformadores 3D...")
    df_trafo_3d = cargar_transformadores_3d(filepath_trafo_3d)
    print(f"  Transformadores 3D cargados: {len(df_trafo_3d)}")

    # Guardar archivos CSV separados por tipo
    OUTPUT_PATH = BASE_PATH / "outputs"
    OUTPUT_PATH.mkdir(exist_ok=True)

    # Eliminar filas sin nombre antes de guardar
    df_lineas_limpio = df_lineas_agrupado[df_lineas_agrupado['nombre'].notna()].copy()
    df_trafo_2d_limpio = df_trafo_2d[df_trafo_2d['nombre'].notna()].copy()
    df_trafo_3d_limpio = df_trafo_3d[df_trafo_3d['nombre'].notna()].copy()

    # Guardar CSVs separados
    archivo_lineas = OUTPUT_PATH / "infotecnica_lineas.csv"
    df_lineas_limpio.to_csv(archivo_lineas, index=False, encoding='utf-8')
    print(f"\n  ✓ Guardado: {archivo_lineas}")

    archivo_trafo_2d = OUTPUT_PATH / "infotecnica_transformadores_2d.csv"
    df_trafo_2d_limpio.to_csv(archivo_trafo_2d, index=False, encoding='utf-8')
    print(f"  ✓ Guardado: {archivo_trafo_2d}")

    archivo_trafo_3d = OUTPUT_PATH / "infotecnica_transformadores_3d.csv"
    df_trafo_3d_limpio.to_csv(archivo_trafo_3d, index=False, encoding='utf-8')
    print(f"  ✓ Guardado: {archivo_trafo_3d}")

    # Combinar todos los DataFrames para retornar (mantener compatibilidad)
    # Asegurar que tengan las mismas columnas básicas
    columnas_comunes = ['nombre', 'nombre_centro_control', 'tension_nominal',
                        'R_total', 'X_total', 'motivo_sin_rx', 'tipo_instalacion']

    df_lineas_final = df_lineas_limpio[columnas_comunes].copy()
    df_trafo_2d_final = df_trafo_2d_limpio[columnas_comunes].copy()
    df_trafo_3d_final = df_trafo_3d_limpio[columnas_comunes].copy()

    # Concatenar
    df_consolidado = pd.concat([
        df_lineas_final,
        df_trafo_2d_final,
        df_trafo_3d_final
    ], ignore_index=True)

    return df_consolidado


if __name__ == "__main__":
    # Prueba
    df = consolidar_infotecnica_completa()
    print(f"\nTotal instalaciones: {len(df)}")
    print(f"  - Líneas: {(df['tipo_instalacion'] == 'linea').sum()}")
    print(f"  - Transformadores 2D: {(df['tipo_instalacion'] == 'trafo_2d').sum()}")
    print(f"  - Transformadores 3D: {(df['tipo_instalacion'] == 'trafo_3d').sum()}")

    # Guardar
    output_path = BASE_PATH / "outputs" / "infotecnica_consolidada.csv"
    output_path.parent.mkdir(exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"\nArchivo guardado: {output_path}")
