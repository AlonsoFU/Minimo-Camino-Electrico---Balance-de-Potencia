"""
Script para probar la carga de datos y reemplazos por mes.
"""

import sys
import re
from src import (
    cargar_lineas_operacion,
    cargar_lineas_mantenimiento,
    cargar_lineas_ent,
    aplicar_reemplazo_por_mes,
    homologar_lineas,
    resumen_homologacion
)


def validar_mes(mes: str) -> bool:
    """Valida que el mes tenga formato YYYY-MM."""
    patron = r'^\d{4}-(0[1-9]|1[0-2])$'
    return bool(re.match(patron, mes))


def main():
    # Cargar datos
    print("Cargando datos de operación...")
    df_operacion = cargar_lineas_operacion()
    print(f"OK - {len(df_operacion)} filas")
    print(df_operacion.head())

    print("\n" + "-"*50 + "\n")

    print("Cargando datos de mantenimiento...")
    df_mantenimiento = cargar_lineas_mantenimiento()
    print(f"OK - {len(df_mantenimiento)} filas")
    print(df_mantenimiento.head())

    print("\n" + "-"*50 + "\n")

    print("Cargando datos ENT (Excel)...")
    df_ent = cargar_lineas_ent()
    print(f"OK - {len(df_ent)} filas")
    print(df_ent.head())

    print("\n" + "="*50 + "\n")

    # Homologación ENT vs Operación
    print("Homologando líneas ENT con Operación...")
    df_homologado = homologar_lineas(df_ent, df_operacion)

    resumen = resumen_homologacion(df_homologado)
    print(f"\n--- RESUMEN HOMOLOGACIÓN ---")
    print(f"Total líneas ENT: {resumen['total_lineas']}")
    print(f"Con match (>=50%): {resumen['con_match']} ({resumen['porcentaje_match']}%)")
    print(f"Sin match: {resumen['sin_match']}")
    print(f"Confianza >=90%: {resumen['confianza_90_100']}")
    print(f"Confianza 70-89%: {resumen['confianza_70_89']}")
    print(f"Confianza 50-69%: {resumen['confianza_50_69']}")
    print(f"Matches invertidos: {resumen['invertidos']}")

    print("\nPrimeras 10 líneas homologadas:")
    print(df_homologado[['nombre', 'match_linnom', 'confianza']].head(10).to_string())

    print("\n" + "="*50 + "\n")

    # Obtener mes de trabajo
    if len(sys.argv) > 1:
        mes_trabajo = sys.argv[1]
    else:
        mes_trabajo = input("Ingresa el mes de trabajo (YYYY-MM, ej: 2025-06): ").strip()

    # Validar formato
    if not mes_trabajo or not validar_mes(mes_trabajo):
        print(f"Error: Formato de mes inválido '{mes_trabajo}'")
        print("Debe ser YYYY-MM, ejemplo: 2025-06")
        return None

    print(f"\nAplicando reemplazos para el mes: {mes_trabajo}")
    df_resultado = aplicar_reemplazo_por_mes(mes_trabajo, df_operacion, df_mantenimiento)

    print(f"OK - {len(df_resultado)} filas procesadas")
    print(f"Líneas CON reemplazo activo: {df_resultado['hay_reemplazo'].sum()}")
    print(f"Líneas SIN reemplazo: {(~df_resultado['hay_reemplazo']).sum()}")

    print("\n" + "-"*50 + "\n")

    print(f"Columnas del resultado: {df_resultado.columns.tolist()}")
    print("\nPrimeras 15 filas:")
    print(df_resultado.head(15).to_string())

    print("\n" + "-"*50 + "\n")

    print("Líneas CON reemplazo activo (primeras 10):")
    print(df_resultado[df_resultado['hay_reemplazo']].head(10).to_string())

    return df_resultado


if __name__ == "__main__":
    df = main()
