"""
Script para probar la carga de datos y reemplazos por mes.
"""

import sys
import re
from pathlib import Path
from src import (
    cargar_lineas_operacion,
    cargar_lineas_mantenimiento,
    cargar_lineas_ent,
    cargar_lineas_infotecnica,
    aplicar_reemplazo_por_mes,
    homologar_lineas,
    resumen_homologacion
)

# Ruta de outputs
OUTPUT_PATH = Path(__file__).parent / "outputs"


def validar_mes(mes: str) -> bool:
    """Valida que el mes tenga formato YYYY-MM."""
    patron = r'^\d{4}-(0[1-9]|1[0-2])$'
    return bool(re.match(patron, mes))


def main():
    # 1. Obtener mes de trabajo PRIMERO
    print("="*50)
    print("BALANCE DE POTENCIA - MÍNIMO CAMINO ELÉCTRICO")
    print("="*50 + "\n")

    if len(sys.argv) > 1:
        mes_trabajo = sys.argv[1]
    else:
        mes_trabajo = input("Ingresa el mes de trabajo (YYYY-MM, ej: 2025-06): ").strip()

    if not mes_trabajo or not validar_mes(mes_trabajo):
        print(f"Error: Formato de mes inválido '{mes_trabajo}'")
        print("Debe ser YYYY-MM, ejemplo: 2025-06")
        return None

    print(f"\nMes de trabajo: {mes_trabajo}\n")

    # 2. Cargar datos base
    print("-"*50)
    print("CARGA DE DATOS")
    print("-"*50 + "\n")

    print("Cargando datos de operación...")
    df_operacion = cargar_lineas_operacion()
    print(f"OK - {len(df_operacion)} filas totales")

    print("Cargando datos de mantenimiento...")
    df_mantenimiento = cargar_lineas_mantenimiento()
    print(f"OK - {len(df_mantenimiento)} filas totales")

    print("Cargando datos ENT (Excel)...")
    df_ent = cargar_lineas_ent()
    print(f"OK - {len(df_ent)} filas totales")

    print("Cargando datos Infotécnica (R/X por tramo)...")
    df_infotec = cargar_lineas_infotecnica()
    print(f"OK - {len(df_infotec)} filas totales\n")

    # 3. Aplicar filtros por mes de trabajo
    print("-"*50)
    print(f"FILTRADO POR MES: {mes_trabajo}")
    print("-"*50 + "\n")

    df_resultado = aplicar_reemplazo_por_mes(mes_trabajo, df_operacion, df_mantenimiento)

    print(f"Líneas operativas en {mes_trabajo}: {len(df_resultado)}")
    print(f"  - CON reemplazo activo: {df_resultado['hay_reemplazo'].sum()}")
    print(f"  - SIN reemplazo: {(~df_resultado['hay_reemplazo']).sum()}\n")

    # 4. Homologación ENT vs Operación (con df filtrado)
    print("-"*50)
    print("HOMOLOGACIÓN ENT vs OPERACIÓN")
    print("-"*50 + "\n")

    print("Homologando líneas ENT con líneas de operación filtradas...")
    df_homologado = homologar_lineas(df_ent, df_resultado)

    resumen = resumen_homologacion(df_homologado)
    print(f"\n--- RESUMEN HOMOLOGACIÓN ---")
    print(f"Total líneas ENT: {resumen['total_lineas']}")
    print(f"Con match (>=50%): {resumen['con_match']} ({resumen['porcentaje_match']}%)")
    print(f"Sin match (<50%): {resumen['sin_match']}")
    print(f"  Confianza >=90%: {resumen['confianza_90_100']}")
    print(f"  Confianza 80-89%: {resumen['confianza_80_89']}")
    print(f"  Confianza 50-79% (revisar): {resumen['confianza_50_79']}")
    print(f"Requieren revisión: {resumen['requiere_revision']}")
    print(f"Matches invertidos: {resumen['invertidos']}")

    # 5. Mostrar ejemplos
    print("\n" + "-"*50)
    print("EJEMPLOS DE HOMOLOGACIÓN")
    print("-"*50 + "\n")

    print("Primeras 10 líneas con match:")
    cols_mostrar = ['nombre', 'match_linnom', 'confianza', 'sim_barra_a', 'sim_barra_b']
    df_con_match = df_homologado[df_homologado['match_linnom'].notna()]
    print(df_con_match[cols_mostrar].head(10).to_string())

    print("\nComparación R/X (primeras 5 con match):")
    cols_rx = ['nombre', 'match_linnom', 'R_ent', 'R_op', 'X_ent', 'X_op']
    print(df_con_match[cols_rx].head(5).to_string())

    print("\nLíneas que REQUIEREN REVISIÓN (confianza 50-80%):")
    df_revisar = df_homologado[df_homologado['requiere_revision'] == True]
    if len(df_revisar) > 0:
        print(df_revisar[cols_mostrar].head(10).to_string())
    else:
        print("  (ninguna)")

    print("\nLíneas SIN match (<50%):")
    df_sin_match = df_homologado[df_homologado['match_linnom'].isna()]
    if len(df_sin_match) > 0:
        print(df_sin_match[['nombre', 'barra_a', 'barra_b', 'confianza']].head(10).to_string())
    else:
        print("  (ninguna)")

    # 6. Datos Infotécnica
    print("\n" + "-"*50)
    print("DATOS INFOTÉCNICA (R/X por tramo)")
    print("-"*50 + "\n")

    print(f"Total tramos: {len(df_infotec)}")
    print(f"Columnas: {df_infotec.columns.tolist()}\n")

    print("Primeras 10 filas:")
    cols_infotec = ['nombre', 'nombre_centro_control', 'tension_nominal', 'longitud', 'R_total', 'X_total']
    print(df_infotec[cols_infotec].head(10).to_string())

    print("\nResumen por tensión nominal:")
    resumen_tension = df_infotec.groupby('tension_nominal').agg({
        'nombre': 'count',
        'longitud': 'sum',
        'R_total': 'mean',
        'X_total': 'mean'
    }).rename(columns={'nombre': 'cantidad'}).round(3)
    print(resumen_tension.to_string())

    # 7. Exportar a CSV
    print("\n" + "-"*50)
    print("EXPORTACIÓN")
    print("-"*50 + "\n")

    OUTPUT_PATH.mkdir(exist_ok=True)

    # Exportar homologación
    archivo_homolog = OUTPUT_PATH / f"homologacion_{mes_trabajo}.csv"
    df_homologado.to_csv(archivo_homolog, index=False, sep=',', encoding='utf-8')
    print(f"Homologación: {archivo_homolog} ({len(df_homologado)} filas)")

    # Exportar infotécnica
    archivo_infotec = OUTPUT_PATH / "infotecnica.csv"
    df_infotec.to_csv(archivo_infotec, index=False, sep=',', encoding='utf-8')
    print(f"Infotécnica: {archivo_infotec} ({len(df_infotec)} filas)")

    return {
        'homologado': df_homologado,
        'infotecnica': df_infotec
    }


if __name__ == "__main__":
    df = main()
