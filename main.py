"""
Script principal para pruebas de carga de datos de líneas eléctricas.
"""

from src import (
    cargar_lineas_operacion,
    cargar_lineas_mantenimiento,
    cargar_lineas_ent,
    cargar_todos_los_datos
)


def mostrar_info_dataframe(df, nombre):
    """Muestra información resumida de un DataFrame."""
    print(f"\n{'='*60}")
    print(f" {nombre}")
    print(f"{'='*60}")
    print(f"Filas: {len(df):,} | Columnas: {len(df.columns)}")
    print(f"\nColumnas disponibles:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i:2}. {col}")
    print(f"\nPrimeras 5 filas:")
    print(df.head().to_string())
    print(f"\nEstadísticas de columnas numéricas:")
    print(df.describe().to_string())


def main():
    print("=" * 60)
    print(" PRUEBA DE CARGA DE DATOS - LÍNEAS ELÉCTRICAS")
    print("=" * 60)

    # Cargar datos
    print("\nCargando datos...")

    # 1. Datos de operación
    print("\n[1/3] Cargando datos de operación...")
    df_operacion = cargar_lineas_operacion()
    print(f"      ✓ LinDatParOpe: {len(df_operacion):,} líneas")

    # 2. Datos de mantenimiento
    print("[2/3] Cargando datos de mantenimiento...")
    df_mantenimiento = cargar_lineas_mantenimiento()
    print(f"      ✓ LinDatManOpe: {len(df_mantenimiento):,} registros")

    # 3. Datos ENT
    print("[3/3] Cargando datos ENT (Excel)...")
    df_ent = cargar_lineas_ent()
    print(f"      ✓ Ent2026 (lineas): {len(df_ent):,} líneas")

    # Mostrar información detallada
    mostrar_info_dataframe(df_operacion, "DATOS DE OPERACIÓN (LinDatParOpe)")
    mostrar_info_dataframe(df_mantenimiento, "DATOS DE MANTENIMIENTO (LinDatManOpe)")
    mostrar_info_dataframe(df_ent, "DATOS ENT 2026 (hoja lineas)")

    # Ejemplos de consultas útiles
    print("\n" + "=" * 60)
    print(" EJEMPLOS DE CONSULTAS")
    print("=" * 60)

    # Ejemplo 1: Filtrar líneas por voltaje
    print("\n1. Líneas de 500 kV en operación:")
    lineas_500 = df_operacion[df_operacion['LinVolt'] == 500]
    print(f"   Total: {len(lineas_500)} líneas")
    if len(lineas_500) > 0:
        print(f"   Ejemplo: {lineas_500['LinNom'].iloc[0]}")

    # Ejemplo 2: Líneas en mantenimiento
    print("\n2. Líneas con mantenimiento activo:")
    en_mantenimiento = df_mantenimiento[df_mantenimiento['LinFMan'] == True]
    print(f"   Total: {len(en_mantenimiento)} registros")

    # Ejemplo 3: Estadísticas de voltajes en ENT
    print("\n3. Distribución de voltajes en ENT:")
    if 'voltaje_kv' in df_ent.columns:
        voltajes = df_ent['voltaje_kv'].value_counts().sort_index()
        for v, count in voltajes.items():
            print(f"   {v:6} kV: {count:4} líneas")

    # Ejemplo 4: Líneas por tipo (Trafo/Linea) en ENT
    print("\n4. Tipo de elementos en ENT:")
    if 'tipo' in df_ent.columns:
        tipos = df_ent['tipo'].value_counts()
        for t, count in tipos.items():
            tipo_nombre = "Línea" if t == "L" else "Trafo" if t == "T" else t
            print(f"   {tipo_nombre}: {count} elementos")

    print("\n" + "=" * 60)
    print(" CARGA COMPLETADA EXITOSAMENTE")
    print("=" * 60)

    return df_operacion, df_mantenimiento, df_ent


if __name__ == "__main__":
    df_op, df_man, df_ent = main()
