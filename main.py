"""
Script para probar la carga de datos y reemplazos por mes.
"""

import sys
from src import (
    cargar_lineas_operacion,
    cargar_lineas_mantenimiento,
    cargar_lineas_ent,
    aplicar_reemplazo_por_mes
)


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

    # Obtener mes de trabajo
    if len(sys.argv) > 1:
        # Si se pasa como argumento: python main.py 2025-06
        mes_trabajo = sys.argv[1]
    else:
        # Si no, pedir por terminal
        mes_trabajo = input("Ingresa el mes de trabajo (YYYY-MM): ")

    print(f"\nAplicando reemplazos para el mes: {mes_trabajo}")
    df_resultado = aplicar_reemplazo_por_mes(mes_trabajo, df_operacion, df_mantenimiento)

    print(f"OK - {len(df_resultado)} filas procesadas")
    print(f"Líneas CON reemplazo activo: {df_resultado['hay_reemplazo'].sum()}")
    print(f"Líneas SIN reemplazo: {(~df_resultado['hay_reemplazo']).sum()}")

    print("\n" + "-"*50 + "\n")

    print("Líneas CON reemplazo activo (primeras 15):")
    cols = ['LinNom', 'mes_trabajo', 'hay_reemplazo', 'fuente', 'man_LinFecIni', 'man_LinFecFin']
    print(df_resultado[df_resultado['hay_reemplazo']][cols].head(15).to_string())

    return df_resultado


if __name__ == "__main__":
    df = main()
