"""
Script para probar la carga de datos.
"""

from src import cargar_lineas_operacion, cargar_lineas_mantenimiento, cargar_lineas_ent


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
