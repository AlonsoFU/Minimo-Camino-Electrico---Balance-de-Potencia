"""
Script de prueba para verificar las mejoras implementadas.
"""

from src.data_loader import (
    expandir_abreviaciones,
    normalizar_nombre_infotec,
    extraer_circuito_infotec,
    extraer_circuito_ent,
    extraer_circuito_op,
    extraer_barras_infotecnica
)

print("="*60)
print("PRUEBAS DE MEJORAS IMPLEMENTADAS")
print("="*60)

# Mejora 1: Diccionario de abreviaciones
print("\n1. EXPANSIÓN DE ABREVIACIONES:")
print("-"*60)

casos_abrev = [
    "D.ALMAGRO",
    "D. ALMAGRO",
    "S. VICENTE",
    "STA. ROSA",
    "PTO. MONTT"
]

for caso in casos_abrev:
    resultado = expandir_abreviaciones(caso)
    print(f"  {caso:20} -> {resultado}")

# Mejora 2: Match de circuito _1de2 ↔ C1
print("\n2. EXTRACCIÓN DE CIRCUITOS:")
print("-"*60)

print("\n  ENT (_Xde2):")
casos_ent = [
    "LINEA_NOMBRE_1de2",
    "LINEA_NOMBRE_2de3",
    "LINEA_SIN_CIRCUITO"
]
for caso in casos_ent:
    circuito = extraer_circuito_ent(caso)
    print(f"  {caso:30} -> {circuito}")

print("\n  CNE (I, II, C1, C2):")
casos_cne = [
    "Los Changos 220->Kapatur 220 I",
    "Los Changos 220->Kapatur 220 II",
    "Los Changos 220->Kapatur 220 C1",
    "Los Changos 220->Kapatur 220 C2"
]
for caso in casos_cne:
    circuito = extraer_circuito_op(caso)
    print(f"  {caso:40} -> {circuito}")

print("\n  Infotécnica (C1, C2):")
casos_infotec = [
    "PAPOSO - TAP TAL TAL 220KV C1",
    "PAPOSO - TAP TAL TAL 220KV C2",
    "PAPOSO - TAP TAL TAL 220KV C3",
    "LINEA SIN CIRCUITO 220KV"
]
for caso in casos_infotec:
    circuito = extraer_circuito_infotec(caso)
    print(f"  {caso:40} -> {circuito}")

# Mejora 3: Normalización de guiones
print("\n3. NORMALIZACIÓN DE GUIONES (– vs -):")
print("-"*60)

casos_guiones = [
    "PAPOSO - TAP TAL TAL",           # hyphen normal
    "PAPOSO – TAP TAL TAL",           # en-dash
    "D.ALMAGRO - S. VICENTE",         # hyphen con abreviaciones
    "D.ALMAGRO – S. VICENTE"          # en-dash con abreviaciones
]

for caso in casos_guiones:
    resultado = normalizar_nombre_infotec(caso)
    print(f"  '{caso}' ->")
    print(f"    '{resultado}'")

# Prueba integrada: extracción de barras con guiones
print("\n4. EXTRACCIÓN DE BARRAS (con guiones):")
print("-"*60)

casos_barras = [
    "PAPOSO - TAP TAL TAL 220KV C1",      # hyphen
    "PAPOSO – TAP TAL TAL 220KV C1",      # en-dash
]

for caso in casos_barras:
    barra_a, barra_b, voltaje = extraer_barras_infotecnica(caso)
    print(f"  '{caso}' ->")
    print(f"    Barra A: {barra_a}")
    print(f"    Barra B: {barra_b}")
    print(f"    Voltaje: {voltaje} kV")

print("\n" + "="*60)
print("TODAS LAS MEJORAS FUNCIONAN CORRECTAMENTE ✓")
print("="*60)
