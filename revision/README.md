# Validación de Reactancia (X) ENT

Este documento describe la estrategia de validación de los valores de reactancia (X) de la base ENT, comparándolos con las fuentes CNE e Infotécnica.

## Objetivo

Identificar si los valores de X_ENT son correctos o presentan discrepancias respecto a las fuentes de referencia (CNE e Infotécnica).

## Columna `revision` (entrada)

La columna `revision` del archivo de homologación indica qué fuentes son confiables:

| Valor | Significado | Cantidad |
|-------|-------------|----------|
| `1` | Ambas fuentes (CNE e Infotec) son confiables | 1410 |
| `CNE` | Solo CNE es confiable | 246 |
| `Infotec` | Solo Infotec es confiable | 195 |
| `0` | Ninguna fuente es confiable | 153 |

**Nota:** Si `revision=1` pero falta `X_Infotec`, se trata como `revision=CNE`. Lo mismo aplica inversamente.

## Categorías de Validación (salida)

### Categorías CORRECTO (X_ENT validado)

| Categoría | Descripción |
|-----------|-------------|
| `CORRECTO` | Ambas fuentes coinciden con X_ENT (diff < 15%) |
| `CORRECTO_PARCIAL_CNE` | Solo CNE disponible/confiable, coincide con X_ENT (diff < 15%) |
| `CORRECTO_PARCIAL_INFOTEC` | Solo Infotec disponible/confiable, coincide con X_ENT (diff < 15%) |

### Categorías DISCREPA (X_ENT con problemas)

| Categoría | Descripción |
|-----------|-------------|
| `DISCREPA_ENT_FUENTES_COINCIDEN` | CNE ≈ Infotec (coinciden entre sí), pero ambas difieren de X_ENT |
| `DISCREPA_FUENTES` | CNE ≠ Infotec (no coinciden entre sí), y ninguna coincide con X_ENT |
| `DISCREPA_PARCIAL_CNE` | Solo CNE disponible/confiable, difiere de X_ENT (diff ≥ 15%) |
| `DISCREPA_PARCIAL_INFOTEC` | Solo Infotec disponible/confiable, difiere de X_ENT (diff ≥ 15%) |

### Sin Referencia

| Categoría | Descripción |
|-----------|-------------|
| `SIN_REFERENCIA` | No hay fuente confiable para comparar (revision=0 o fuente sin valor X) |

## Tabla Resumen (umbral 15%)

| Categoría | Cantidad | % |
|-----------|----------|---|
| `CORRECTO` | 512 | 25.5% |
| `CORRECTO_PARCIAL_CNE` | 341 | 17.0% |
| `CORRECTO_PARCIAL_INFOTEC` | 177 | 8.8% |
| `DISCREPA_ENT_FUENTES_COINCIDEN` | 323 | 16.1% |
| `DISCREPA_FUENTES` | 255 | 12.7% |
| `DISCREPA_PARCIAL_CNE` | 139 | 6.9% |
| `DISCREPA_PARCIAL_INFOTEC` | 92 | 4.6% |
| `SIN_REFERENCIA` | 165 | 8.2% |
| **Total** | **2004** | **100%** |

**Resumen:**
- **Correctos:** 1030 (51.4%) → `CORRECTO` + `CORRECTO_PARCIAL_CNE` + `CORRECTO_PARCIAL_INFOTEC`
- **Discrepan:** 809 (40.4%) → `DISCREPA_ENT_FUENTES_COINCIDEN` + `DISCREPA_FUENTES` + `DISCREPA_PARCIAL_CNE` + `DISCREPA_PARCIAL_INFOTEC`
- **Sin referencia:** 165 (8.2%) → `SIN_REFERENCIA`

## Análisis de Sensibilidad

Variación de resultados según el umbral de tolerancia:

| Umbral | CORRECTO | PARCIAL | Total Correctos | % | DISCREPA |
|--------|----------|---------|-----------------|------|----------|
| 5% | 251 | 566 | 817 | 40.8% | 1022 |
| 10% | 404 | 545 | 949 | 47.4% | 890 |
| **15%** | **512** | **518** | **1030** | **51.4%** | **809** |
| 20% | 576 | 509 | 1085 | 54.1% | 754 |
| 25% | 607 | 517 | 1124 | 56.1% | 715 |
| 30% | 643 | 500 | 1143 | 57.0% | 696 |
| 40% | 703 | 506 | 1209 | 60.3% | 630 |
| 50% | 754 | 480 | 1234 | 61.6% | 605 |

## Diagrama de Decisión

```
                                    ┌─────────────────────────┐
                                    │  revision + X disponible │
                                    └────────────┬────────────┘
                                                 │
          ┌──────────────────────────────────────┼──────────────────────────────────────┐
          ▼                                      ▼                                      ▼
     SIN_REFERENCIA                        Solo una fuente                        Ambas fuentes
     (rev=0, o fuente                      disponible                             disponibles
      sin valor X)                              │                                (rev=1 + ambos X)
        (165)                                   │                                      │
                             ┌──────────────────┴──────────────────┐                   │
                             ▼                                      ▼                   ▼
                       Solo CNE                               Solo Infotec      ┌──────────────┐
                             │                                      │           │CNE ≈ Infotec?│
                      ┌──────┴──────┐                        ┌──────┴──────┐    │  (diff<15%)  │
                    <15%          ≥15%                     <15%          ≥15%   └──────┬───────┘
                      │             │                        │             │           │
                      ▼             ▼                        ▼             ▼      ┌────┴────┐
                 CORRECTO      DISCREPA                CORRECTO      DISCREPA    SÍ        NO
                 PARCIAL       PARCIAL                 PARCIAL       PARCIAL      │          │
                  _CNE          _CNE                  _INFOTEC      _INFOTEC      │          │
                  (341)         (139)                  (177)         (92)         ▼          ▼
                                                                           ┌──────────┐    ┌──────────┐
                                                                           │ ¿Ambas   │    │ ¿Alguna  │
                                                                           │  ≈ ENT?  │    │  ≈ ENT?  │
                                                                           └────┬─────┘    └────┬─────┘
                                                                           ┌────┴────┐     ┌────┴────┐
                                                                          SÍ        NO    SÍ        NO
                                                                           │         │     │          │
                                                                           ▼         ▼     ▼          ▼
                                                                       CORRECTO  DISCREPA CORRECTO  DISCREPA
                                                                        (512)    _ENT_    PARCIAL   FUENTES
                                                                                 FUENTES   CNE/      (255)
                                                                                COINCIDEN INFOTEC
                                                                                  (323)
```

## Lógica de Ajuste de Revisión

```python
# Ajustar revision efectiva cuando falta X
if revision == 1 and X_Infotec es NaN → tratar como revision = CNE
if revision == 1 and X_CNE es NaN → tratar como revision = Infotec
if revision == Infotec and X_Infotec es NaN → SIN_REFERENCIA
if revision == CNE and X_CNE es NaN → SIN_REFERENCIA
```

## Interpretación de Resultados

1. **CORRECTO / CORRECTO_PARCIAL_***: X_ENT está validado, no requiere acción.

2. **DISCREPA_ENT_FUENTES_COINCIDEN**: Las fuentes CNE e Infotec coinciden entre sí pero difieren de ENT. **Alta probabilidad de que X_ENT esté incorrecto.**

3. **DISCREPA_FUENTES**: Las fuentes no coinciden entre sí y ninguna coincide con ENT. Requiere revisión manual para determinar el valor correcto.

4. **DISCREPA_PARCIAL_***: Solo hay una fuente y difiere de ENT. Revisar si la fuente es correcta.

5. **SIN_REFERENCIA**: No hay datos para validar. Buscar otras fuentes o mantener X_ENT.

---

# Capítulo 2: Análisis de Magnitud de Cambios

## Objetivo

Para los casos que DISCREPAN, no solo importa el porcentaje de diferencia sino también **la magnitud absoluta del cambio** (ΔX). Un cambio pequeño en magnitud puede ser aceptable aunque el porcentaje sea alto.

## Sub-categorías por Magnitud

Se define la magnitud del cambio como: `ΔX = |X_ENT - X_sugerido|`

| Magnitud | Rango ΔX | Descripción |
|----------|----------|-------------|
| `CAMBIO_BAJO` | < 5 | Cambio menor, fácil de aceptar |
| `CAMBIO_MEDIO` | 5 - 50 | Cambio moderado, revisar |
| `CAMBIO_ALTO` | ≥ 50 | Cambio significativo, requiere análisis |

## Distribución por Categoría y Magnitud

| Categoría | CAMBIO_BAJO | CAMBIO_MEDIO | CAMBIO_ALTO | Total |
|-----------|-------------|--------------|-------------|-------|
| `DISCREPA_ENT_FUENTES_COINCIDEN` | 112 | 103 | 108 | 323 |
| `DISCREPA_PARCIAL_CNE` | 40 | 57 | 42 | 139 |
| `DISCREPA_PARCIAL_INFOTEC` | 39 | 34 | 19 | 92 |
| `DISCREPA_FUENTES` | 64 | 146 | 45 | 255 |
| **Total** | **255** | **340** | **214** | **809** |

## Análisis por Categoría

### DISCREPA_ENT_FUENTES_COINCIDEN (323 casos)

Las fuentes CNE e Infotec coinciden entre sí → **alta confianza para cambiar**.

- **Valor sugerido:** Promedio de X_CNE y X_Infotec
- **Prioridad de cambio:**
  - `CAMBIO_BAJO` (112): ✅ Cambiar sin problema
  - `CAMBIO_MEDIO` (103): ⚠️ Revisar antes de cambiar
  - `CAMBIO_ALTO` (108): 🔍 Analizar caso por caso

### DISCREPA_PARCIAL_CNE (139 casos)

Solo CNE disponible/confiable, difiere de ENT.

- **Valor sugerido:** X_CNE
- **Prioridad de cambio:**
  - `CAMBIO_BAJO` (40): ✅ Cambiar
  - `CAMBIO_MEDIO` (57): ⚠️ Revisar
  - `CAMBIO_ALTO` (42): 🔍 Analizar

### DISCREPA_PARCIAL_INFOTEC (92 casos)

Solo Infotec disponible/confiable, difiere de ENT.

- **Valor sugerido:** X_Infotec
- **Prioridad de cambio:**
  - `CAMBIO_BAJO` (39): ✅ Cambiar
  - `CAMBIO_MEDIO` (34): ⚠️ Revisar
  - `CAMBIO_ALTO` (19): 🔍 Analizar

### DISCREPA_FUENTES (255 casos)

CNE e Infotec no coinciden entre sí, ninguna coincide con ENT → **requiere decisión manual**.

**¿Cuál fuente está más cerca de ENT?**

| Fuente más cercana | Cantidad |
|--------------------|----------|
| CNE | 142 (56%) |
| Infotec | 113 (44%) |

- **Valor sugerido:** La fuente más cercana a ENT
- **Columna adicional:** `fuente_cercana` indica cuál usar
- **Prioridad de cambio:**
  - `CAMBIO_BAJO` (64): ⚠️ Revisar cuál fuente es correcta
  - `CAMBIO_MEDIO` (146): ⚠️ Revisar con cuidado
  - `CAMBIO_ALTO` (45): 🔍 Análisis detallado requerido

## Resumen de Prioridades

| Prioridad | Criterio | Casos | Acción |
|-----------|----------|-------|--------|
| 🟢 Alta | FUENTES_COINCIDEN + CAMBIO_BAJO | 112 | Cambiar directamente |
| 🟢 Alta | PARCIAL_* + CAMBIO_BAJO | 79 | Cambiar directamente |
| 🟡 Media | FUENTES_COINCIDEN + CAMBIO_MEDIO | 103 | Revisar y cambiar |
| 🟡 Media | PARCIAL_* + CAMBIO_MEDIO | 91 | Revisar y cambiar |
| 🟠 Baja | DISCREPA_FUENTES + CAMBIO_BAJO/MEDIO | 210 | Decidir cuál fuente usar |
| 🔴 Manual | Cualquier CAMBIO_ALTO | 214 | Análisis caso por caso |

**Total cambios recomendados con alta confianza:** 191 casos (CAMBIO_BAJO en categorías con fuente clara)

## Columnas de Salida Adicionales (Capítulo 2)

| Columna | Descripción |
|---------|-------------|
| `valor_sugerido` | Valor de X recomendado según la fuente confiable |
| `delta_X` | Magnitud del cambio: \|X_ENT - valor_sugerido\| |
| `magnitud` | Clasificación: CAMBIO_BAJO / CAMBIO_MEDIO / CAMBIO_ALTO |
| `fuente_cercana` | Para DISCREPA_FUENTES: cuál fuente (CNE/Infotec) está más cerca |

---

# Anexo: Cálculo de Reactancias Infotécnica

## Líneas de Transmisión

Los valores de R y X para líneas se obtienen del archivo `reporte_secciones-tramos.xlsx`:

```
R_total = R_unitaria × longitud
X_total = X_unitaria × longitud
```

Donde:
- `R_unitaria`: Resistencia de secuencia positiva a 20°C (Ω/km)
- `X_unitaria`: Reactancia de secuencia positiva (Ω/km)
- `longitud`: Longitud del conductor (km)

**Nota:** Cuando hay tramos repetidos (mismo nombre), los valores R y X se **suman**.

## Transformadores 2D (Dos Devanados)

Los valores se calculan a partir del archivo `reporte_transformadores-2d.xlsx` usando las siguientes fórmulas:

```
1. R% = (Pcu_kW × 100) / (S_MVA × 1000)
2. X% = √(Z%² - R%²)
3. Z_base = V_kV² / S_MVA
4. R_Ω = (R% / 100) × Z_base
5. X_Ω = (X% / 100) × Z_base
```

Donde:
- `S_MVA`: Capacidad nominal AT (MVA) - columna "2.1 Capacidad nominal AT"
- `V_kV`: Tensión nominal AT (kV) - columna "2.7 Tensión nominal AT (f-f) el equipo"
- `Z%`: Impedancia de secuencia positiva tap central - columna "2.8 Impedancia de secuencia positiva tap central Z"
- `Pcu_kW`: Pérdidas en el cobre (kW) - columna "2.16 Pérdidas en el cobre de la prueba de cortocircuito Tap central"

## Transformadores 3D (Tres Devanados)

Para transformadores de 3 devanados se usan los valores del devanado **AT-MT** del archivo `reporte_transformadores-3d.xlsx`:

```
1. R% = (Pcu_kW_AT-MT × 100) / (S_base × 1000)
2. X% = √(Z%_AT-MT² - R%²)
3. Z_base = V_kV_AT² / S_base
4. R_Ω = (R% / 100) × Z_base
5. X_Ω = (X% / 100) × Z_base
```

Donde:
- `S_base`: Potencia base AT-MT (MVA) - columna "3.25 Potencia base utilizada para calcular las Pérdidas bajo carga y Pérdidas en el cobre AT-MT"
  - Si no está disponible, se usa "3.1 Capacidad nominal AT"
- `V_kV_AT`: Tensión nominal AT (kV) - columna "3.7 Tensión nominal AT (f-f) del equipo"
- `Z%_AT-MT`: Impedancia AT-MT tap central - columna "3.8 Impedancia secuencia positiva AT-MT tap central Z"
- `Pcu_kW_AT-MT`: Pérdidas en cobre AT-MT (kW) - columna "3.16 Pérdidas en el cobre AT-MT tap central"

## Casos sin R/X calculado

Cuando no se puede calcular R/X, se indica el motivo en la columna `motivo_sin_rx`:
- "Falta S_MVA (Capacidad nominal)"
- "Falta V_kV (Tensión nominal)"
- "Falta Z% (Impedancia)"
- "Falta Pcu_kW (Pérdidas en cobre)"
- "Z%² < R%² (error en datos)"

