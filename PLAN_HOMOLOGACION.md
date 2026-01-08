# Plan: Mejorar Homologación de Líneas

## Problema Actual
- El fuzzy matching promedia la similitud de ambas barras: `(sim_a + sim_b) / 2`
- Esto genera falsos positivos cuando una barra matchea bien pero la otra no
- Ejemplo: "PAPOSO-TALTAL" podría matchear con "PAPOSO-CARDONES" si Paposo tiene 100% pero Cardones/Taltal tienen 50%

## Enfoque Propuesto

### 1. Definición de Match Válido
Una línea se define por: **Barra_A + Barra_B + Voltaje**

Para que haya match, se requiere:
- Voltaje EXACTO (o diferencia <= 1 kV para redondeos)
- Barra A debe matchear con >= 80% de similitud
- Barra B debe matchear con >= 80% de similitud
- (También probar invertido: A↔B)

### 2. Estrategia de Matching por Niveles

**Nivel 1 - Match Exacto:**
- Normalizar nombres y buscar coincidencia exacta de ambas barras
- Confianza: 100%

**Nivel 2 - Match por Token:**
- Tokenizar nombres (ej: "ALTO JAHUEL" → ["alto", "jahuel"])
- Si todos los tokens de ENT están en OP (o viceversa), es match
- Confianza: 95%

**Nivel 3 - Match por Fuzzy (estricto):**
- Ambas barras deben tener >= 85% similitud individual
- Confianza: mínimo de ambas similitudes

**Nivel 4 - Match Parcial:**
- Una barra tiene >= 90%, la otra >= 70%
- Confianza: promedio ponderado, marcado como "revisar"

### 3. Normalización Mejorada

```
ENT: "D.ALMAGRO_____220"
  → Quitar voltaje: "D.ALMAGRO"
  → Expandir abreviaturas: "DIEGO DE ALMAGRO" (diccionario)
  → Normalizar: "diego de almagro"

OP: "Diego de Almagro 220"
  → Quitar voltaje: "Diego de Almagro"
  → Normalizar: "diego de almagro"
```

### 4. Diccionario de Equivalencias
Crear mapeo de abreviaturas conocidas:
- "D." → "DIEGO DE"
- "S." → "SAN" o "SANTA"
- "L." → "LOS" o "LAS"
- "C." → "CENTRAL" o "CERRO"
- etc.

### 5. Estructura del Código

```python
def homologar_lineas_v2(df_ent, df_operacion):
    # 1. Pre-procesar y normalizar
    # 2. Agrupar por voltaje
    # 3. Para cada línea ENT:
    #    a. Filtrar OP por voltaje exacto
    #    b. Buscar match exacto
    #    c. Si no hay, buscar match por tokens
    #    d. Si no hay, buscar match fuzzy estricto
    #    e. Reportar nivel de confianza y método usado
```

### 6. Output Esperado
- match_linnom: Nombre de línea OP
- confianza: Porcentaje (mínimo de ambas barras)
- metodo_match: "exacto", "token", "fuzzy", "parcial"
- requiere_revision: True/False
- sim_barra_a: Similitud individual barra A
- sim_barra_b: Similitud individual barra B

## Pasos de Implementación

1. [ ] Crear diccionario de abreviaturas comunes
2. [ ] Mejorar función de normalización con expansión de abreviaturas
3. [ ] Implementar match por niveles (exacto → token → fuzzy)
4. [ ] Requerir que AMBAS barras superen umbral mínimo
5. [ ] Agregar columnas de diagnóstico (similitud individual por barra)
6. [ ] Testear y comparar resultados con versión anterior
