"""
Análisis específico para nombres geográficos con abreviaciones.

Estrategia:
1. Buscar nombres que empiecen con "L.", "D.", "S." (posibles Los, Diego, San)
2. Buscar sus versiones completas en los datos
3. Validar que sean el mismo lugar
4. Solo agregar si NO hay ambigüedad
"""

import pandas as pd
import re
from collections import defaultdict
from src.data_loader import (
    cargar_lineas_ent,
    cargar_lineas_operacion,
    cargar_lineas_infotecnica
)

def extraer_nombres_barras_limpios():
    """Extrae todos los nombres de barras limpios (sin voltaje, circuitos, etc.)"""
    nombres = set()

    # ENT
    df_ent = cargar_lineas_ent()
    for col in ['barra_a', 'barra_b']:
        if col in df_ent.columns:
            for barra in df_ent[col].dropna().unique():
                # Limpiar voltaje y símbolos
                barra_limpia = re.sub(r'_*\d{2,3}$', '', str(barra))
                barra_limpia = barra_limpia.replace('_', ' ').strip()
                if barra_limpia:
                    nombres.add(barra_limpia.upper())

    # CNE
    df_cne = cargar_lineas_operacion()
    if 'LinNom' in df_cne.columns:
        for linnom in df_cne['LinNom'].dropna().unique():
            partes = str(linnom).split('->')
            for parte in partes:
                # Extraer barra sin voltaje ni circuito
                barra = re.sub(r'\s+\d{2,3}\s*[IVX]*\s*$', '', parte.strip())
                barra = re.sub(r'\s+\d{2,3}\s*C?\d*\s*$', '', barra)
                if barra:
                    nombres.add(barra.upper())

    # Infotécnica
    df_infotec = cargar_lineas_infotecnica()
    if 'nombre' in df_infotec.columns:
        for nombre in df_infotec['nombre'].dropna().unique():
            match = re.match(r'(.+?)\s*[-–]\s*(.+?)\s+\d{2,3}KV', str(nombre), re.IGNORECASE)
            if match:
                nombres.add(match.group(1).strip().upper())
                nombres.add(match.group(2).strip().upper())

    return sorted(nombres)

print("="*80)
print("ANÁLISIS DE ABREVIACIONES EN NOMBRES GEOGRÁFICOS")
print("="*80)

nombres = extraer_nombres_barras_limpios()
print(f"\nTotal de nombres únicos: {len(nombres):,}\n")

# Buscar patrones específicos
patrones = {
    'D.': {'descripcion': 'DIEGO / DON / DESIERTO', 'candidatos': []},
    'L.': {'descripcion': 'LOS / LAS / LA', 'candidatos': []},
    'S.': {'descripcion': 'SAN / SANTA', 'candidatos': []},
    'STA.': {'descripcion': 'SANTA', 'candidatos': []},
    'PTO.': {'descripcion': 'PUERTO', 'candidatos': []},
    'C.': {'descripcion': 'CENTRAL / CERRO / CHILE', 'candidatos': []},
}

# Buscar nombres con estos patrones
for nombre in nombres:
    for patron in patrones.keys():
        if patron in nombre:
            patrones[patron]['candidatos'].append(nombre)

# Analizar cada patrón
for patron, data in patrones.items():
    print(f"\n{'='*80}")
    print(f"PATRÓN: '{patron}' (posiblemente: {data['descripcion']})")
    print(f"{'='*80}")

    candidatos = data['candidatos']
    print(f"Total de nombres con '{patron}': {len(candidatos)}")

    if len(candidatos) == 0:
        print("  ✗ No se encontraron nombres con este patrón")
        continue

    # Mostrar primeros 30
    print(f"\nPrimeros {min(30, len(candidatos))} ejemplos:")
    for i, nombre in enumerate(candidatos[:30], 1):
        print(f"  {i:2}. {nombre}")

    if len(candidatos) > 30:
        print(f"  ... y {len(candidatos) - 30} más")

    # Buscar posibles expansiones
    print(f"\nBuscando versiones expandidas...")

    expansiones_encontradas = defaultdict(list)

    for candidato in candidatos:
        # Extraer la parte después del patrón
        if patron in candidato:
            partes = candidato.split(patron, 1)
            if len(partes) == 2:
                sufijo = partes[1].strip()

                # Buscar nombres que terminen igual pero sin abreviación
                posibles_expansiones = {
                    'D.': ['DIEGO', 'DON', 'DESIERTO'],
                    'L.': ['LOS', 'LAS', 'LA'],
                    'S.': ['SAN', 'SANTA'],
                    'STA.': ['SANTA'],
                    'PTO.': ['PUERTO'],
                    'C.': ['CENTRAL', 'CERRO', 'CHILE', 'CASA']
                }

                for expansion in posibles_expansiones.get(patron, []):
                    # Buscar si existe "EXPANSION + sufijo"
                    nombre_expandido = f"{expansion} {sufijo}"
                    if nombre_expandido in nombres:
                        expansiones_encontradas[candidato].append(nombre_expandido)

    # Mostrar resultados
    if expansiones_encontradas:
        print(f"\n  ✓ Encontradas {len(expansiones_encontradas)} expansiones:")
        for abrev, expansiones in sorted(expansiones_encontradas.items())[:20]:
            if len(expansiones) == 1:
                print(f"    ✓ {abrev:40} → {expansiones[0]:40} [SEGURO]")
            else:
                print(f"    ⚠ {abrev:40} → {', '.join(expansiones)} [AMBIGUO]")

        if len(expansiones_encontradas) > 20:
            print(f"    ... y {len(expansiones_encontradas) - 20} más")
    else:
        print("  ✗ No se encontraron versiones expandidas en los datos")

# Análisis especial para "D.ALMAGRO"
print(f"\n{'='*80}")
print("ANÁLISIS ESPECÍFICO: D.ALMAGRO")
print(f"{'='*80}")

dalmagro_variantes = [n for n in nombres if 'ALMAGRO' in n]
print(f"Variantes de ALMAGRO encontradas: {len(dalmagro_variantes)}")
for var in sorted(dalmagro_variantes):
    print(f"  - {var}")

# Análisis especial para "L.CHANGOS"
print(f"\n{'='*80}")
print("ANÁLISIS ESPECÍFICO: CHANGOS")
print(f"{'='*80}")

changos_variantes = [n for n in nombres if 'CHANGOS' in n]
print(f"Variantes de CHANGOS encontradas: {len(changos_variantes)}")
for var in sorted(changos_variantes):
    print(f"  - {var}")

print("\n" + "="*80)
print("CONCLUSIÓN Y RECOMENDACIÓN")
print("="*80)
print("""
Basado en el análisis de datos reales:

1. Si NO existe la versión expandida en los datos → NO agregar al diccionario
2. Si existen múltiples expansiones posibles → NO agregar (ambiguo)
3. Solo agregar si:
   - Existe la versión expandida en los datos
   - Es la ÚNICA expansión posible
   - Aparece con frecuencia significativa

RECOMENDACIÓN: Usar un diccionario MÍNIMO con solo casos comprobados,
o mejor aún, NO usar diccionario y confiar en el algoritmo de similitud
fuzzy que ya maneja bien estas variaciones.
""")
print("="*80)
