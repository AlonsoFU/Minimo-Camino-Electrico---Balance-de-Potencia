"""
Script para analizar TODAS las abreviaciones presentes en los datos reales
y generar un diccionario seguro sin ambigüedades.

Estrategia:
1. Extraer todos los nombres únicos de las 3 fuentes (ENT, CNE, Infotécnica)
2. Identificar patrones de abreviación (palabras con punto, palabras cortas)
3. Validar que no haya colisiones (ej: D.ALMAGRO → DIEGO vs DAVID)
4. Solo agregar expansiones 100% seguras
5. Reportar casos ambiguos para revisión manual
"""

import pandas as pd
import re
from collections import defaultdict, Counter
from pathlib import Path

# Importar funciones de carga
from src.data_loader import (
    cargar_lineas_ent,
    cargar_lineas_operacion,
    cargar_lineas_infotecnica
)

def extraer_tokens_barra(nombre):
    """
    Extrae tokens (palabras) de un nombre de barra.
    Retorna tokens en mayúsculas, limpiando números y símbolos.
    """
    if pd.isna(nombre):
        return []

    nombre = str(nombre).upper()
    # Eliminar voltajes (números de 2-3 dígitos al final)
    nombre = re.sub(r'\s*\d{2,3}\s*$', '', nombre)
    nombre = re.sub(r'_*\d{2,3}\s*$', '', nombre)
    # Eliminar circuitos (I, II, C1, C2, etc)
    nombre = re.sub(r'\s+[IVX]+\s*$', '', nombre)
    nombre = re.sub(r'\s+C\d+\s*$', '', nombre, flags=re.IGNORECASE)
    # Reemplazar separadores por espacios
    nombre = nombre.replace('_', ' ').replace('->', ' ').replace('–', ' ').replace('-', ' ')

    # Extraer palabras (incluyendo las que tienen punto)
    tokens = nombre.split()
    return [t.strip() for t in tokens if len(t.strip()) > 0]


def es_abreviacion(token):
    """
    Detecta si un token es una abreviación.

    Criterios:
    - Termina en punto: "S.", "STA.", "D.ALMAGRO"
    - Es muy corta (1-2 letras) sin punto pero antes de palabra larga
    """
    return '.' in token or (len(token) <= 2 and token.isalpha())


def normalizar_token(token):
    """Normaliza un token quitando puntos y espacios."""
    return token.replace('.', '').replace(' ', '').strip()


print("="*80)
print("ANÁLISIS EXHAUSTIVO DE ABREVIACIONES EN DATOS REALES")
print("="*80)

# 1. CARGAR TODOS LOS DATOS
print("\n[1/6] Cargando datos de las 3 fuentes...")
print("-"*80)

df_ent = cargar_lineas_ent()
df_cne = cargar_lineas_operacion()
df_infotec = cargar_lineas_infotecnica()

print(f"✓ ENT:        {len(df_ent):,} líneas")
print(f"✓ CNE:        {len(df_cne):,} líneas")
print(f"✓ Infotécnica: {len(df_infotec):,} líneas")

# 2. EXTRAER TODOS LOS NOMBRES DE BARRAS
print("\n[2/6] Extrayendo nombres de barras únicos...")
print("-"*80)

nombres_unicos = set()

# De ENT
for col in ['barra_a', 'barra_b']:
    if col in df_ent.columns:
        nombres_unicos.update(df_ent[col].dropna().unique())

# De CNE (extraer de LinNom)
if 'LinNom' in df_cne.columns:
    for linnom in df_cne['LinNom'].dropna().unique():
        # Separar por "->"
        partes = str(linnom).split('->')
        for parte in partes:
            # Extraer nombre de barra (sin voltaje ni circuito)
            barra = re.sub(r'\s+\d{2,3}\s*[IVX]*\s*$', '', parte.strip())
            barra = re.sub(r'\s+\d{2,3}\s*C?\d*\s*$', '', barra)
            if barra:
                nombres_unicos.add(barra.strip())

# De Infotécnica
if 'nombre' in df_infotec.columns:
    for nombre in df_infotec['nombre'].dropna().unique():
        # Formato: "BARRA A - BARRA B VVVkV C#"
        match = re.match(r'(.+?)\s*[-–]\s*(.+?)\s+\d{2,3}KV', str(nombre), re.IGNORECASE)
        if match:
            nombres_unicos.add(match.group(1).strip())
            nombres_unicos.add(match.group(2).strip())

print(f"✓ Total de nombres únicos de barras: {len(nombres_unicos):,}")

# 3. EXTRAER TODOS LOS TOKENS
print("\n[3/6] Extrayendo y analizando tokens (palabras)...")
print("-"*80)

todos_tokens = []
for nombre in nombres_unicos:
    tokens = extraer_tokens_barra(nombre)
    todos_tokens.extend(tokens)

# Contar frecuencia de tokens
frecuencia_tokens = Counter(todos_tokens)
print(f"✓ Total de tokens: {len(todos_tokens):,}")
print(f"✓ Tokens únicos: {len(frecuencia_tokens):,}")

# 4. IDENTIFICAR POSIBLES ABREVIACIONES
print("\n[4/6] Identificando posibles abreviaciones...")
print("-"*80)

tokens_con_punto = [t for t in frecuencia_tokens.keys() if '.' in t]
tokens_cortos = [t for t in frecuencia_tokens.keys() if len(normalizar_token(t)) <= 3 and t.isalpha()]

print(f"\n  Tokens con punto (posibles abreviaciones): {len(tokens_con_punto)}")
if tokens_con_punto:
    print("  Ejemplos:", sorted(tokens_con_punto)[:20])

print(f"\n  Tokens muy cortos (1-3 letras): {len(tokens_cortos)}")
tokens_cortos_freq = [(t, frecuencia_tokens[t]) for t in tokens_cortos]
tokens_cortos_freq.sort(key=lambda x: x[1], reverse=True)
if tokens_cortos_freq:
    print("  Más frecuentes:", tokens_cortos_freq[:20])

# 5. BUSCAR EXPANSIONES CANDIDATAS
print("\n[5/6] Buscando expansiones para abreviaciones...")
print("-"*80)

candidatos_expansion = defaultdict(set)

# Para cada token con punto, buscar versiones sin punto
for token_abrev in tokens_con_punto:
    token_norm = normalizar_token(token_abrev)

    # Buscar tokens que empiecen con las mismas letras
    for token_completo in frecuencia_tokens.keys():
        token_completo_norm = normalizar_token(token_completo)

        # Criterios de match:
        # 1. El token completo debe empezar con el abreviado
        # 2. El token completo debe ser más largo
        # 3. No debe tener punto (es la versión expandida)
        if (token_completo_norm.startswith(token_norm) and
            len(token_completo_norm) > len(token_norm) and
            '.' not in token_completo):
            candidatos_expansion[token_abrev].add(token_completo)

# Mostrar resultados
print(f"\n  Abreviaciones con candidatos a expansión: {len(candidatos_expansion)}")
print("\n  Análisis de ambigüedades:")
print("  " + "="*76)

expansion_segura = {}
expansion_ambigua = {}
sin_expansion = []

for abrev, expansiones in sorted(candidatos_expansion.items()):
    if len(expansiones) == 0:
        sin_expansion.append(abrev)
    elif len(expansiones) == 1:
        expansion_segura[abrev] = list(expansiones)[0]
        print(f"  ✓ {abrev:20} → {list(expansiones)[0]:30} [SEGURO]")
    else:
        expansion_ambigua[abrev] = expansiones
        print(f"  ⚠ {abrev:20} → {', '.join(sorted(expansiones)[:3])}... [AMBIGUO - {len(expansiones)} opciones]")

# Casos sin expansión encontrada
for abrev in sorted(tokens_con_punto):
    if abrev not in candidatos_expansion or len(candidatos_expansion[abrev]) == 0:
        print(f"  ✗ {abrev:20} → (sin expansión encontrada)")

# 6. GENERAR DICCIONARIO SEGURO
print("\n[6/6] Generando diccionario de abreviaciones SEGURO...")
print("-"*80)

diccionario_seguro = {}

# Solo agregar expansiones seguras (sin ambigüedad)
for abrev, expansion in expansion_segura.items():
    # Normalizar: agregar con y sin punto, con y sin espacio
    base = normalizar_token(abrev)
    diccionario_seguro[abrev] = expansion
    diccionario_seguro[abrev.replace('.', '')] = expansion
    if ' ' in abrev:
        diccionario_seguro[abrev.replace(' ', '')] = expansion

print(f"\n  Total de expansiones SEGURAS: {len(expansion_segura)}")
print(f"  Total de expansiones AMBIGUAS (no incluidas): {len(expansion_ambigua)}")
print(f"  Total de entradas en diccionario final: {len(diccionario_seguro)}")

# Mostrar diccionario generado
print("\n" + "="*80)
print("DICCIONARIO PYTHON GENERADO (solo expansiones seguras):")
print("="*80)
print("\nABREVIACIONES = {")
for abrev, expansion in sorted(diccionario_seguro.items()):
    print(f"    '{abrev}': '{expansion}',")
print("}")

# Guardar reporte de ambigüedades
print("\n" + "="*80)
print("REPORTE DE CASOS AMBIGUOS (requieren revisión manual):")
print("="*80)
if expansion_ambigua:
    for abrev, expansiones in sorted(expansion_ambigua.items()):
        print(f"\n  {abrev}:")
        for exp in sorted(expansiones):
            freq = frecuencia_tokens.get(exp, 0)
            print(f"    - {exp} (frecuencia: {freq})")
else:
    print("\n  ✓ No se encontraron casos ambiguos")

# Estadísticas finales
print("\n" + "="*80)
print("ESTADÍSTICAS FINALES:")
print("="*80)
print(f"  Total de barras analizadas:           {len(nombres_unicos):,}")
print(f"  Total de tokens únicos:                {len(frecuencia_tokens):,}")
print(f"  Tokens con punto (abreviaciones):      {len(tokens_con_punto):,}")
print(f"  Expansiones seguras encontradas:       {len(expansion_segura):,}")
print(f"  Expansiones ambiguas (no usar):        {len(expansion_ambigua):,}")
print(f"  Tamaño del diccionario generado:       {len(diccionario_seguro):,}")
print("="*80)

print("\n✓ Análisis completado. Revisa los casos ambiguos antes de usar el diccionario.")
