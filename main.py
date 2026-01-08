"""
Script para probar la carga de datos.
"""

from src import cargar_lineas_operacion, cargar_lineas_mantenimiento, cargar_lineas_ent, cruzar_operacion_mantenimiento


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

print("Cruzando operación con mantenimiento...")
df_cruce = cruzar_operacion_mantenimiento(df_operacion, df_mantenimiento)
print(f"OK - {len(df_cruce)} filas")
print(f"Líneas CON mantenimiento: {df_cruce['tiene_mantenimiento'].sum()}")
print(f"Líneas SIN mantenimiento: {(~df_cruce['tiene_mantenimiento']).sum()}")

print("\n" + "-"*50 + "\n")

print("Líneas CON mantenimiento (primeras 10):")
cols = ['LinNom', 'LinFecOpeIni', 'LinFecOpeFin', 'man_LinFecIni', 'man_LinFecFin']
print(df_cruce[df_cruce['tiene_mantenimiento']][cols].head(10))
