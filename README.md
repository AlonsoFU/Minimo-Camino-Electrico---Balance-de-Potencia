# Balance de Potencia - Mínimo Camino Eléctrico

Sistema para homologar y validar datos de líneas eléctricas y transformadores entre tres fuentes de datos: **ENT**, **CNE** e **Infotécnica**.

## ¿Qué hace este proyecto?

Este proyecto resuelve un problema común en el sector eléctrico chileno: los parámetros técnicos de las líneas y transformadores del sistema eléctrico (como resistencia R y reactancia X) están registrados en **múltiples bases de datos** que no siempre coinciden.

Este sistema:
1. **Carga** los datos de las tres fuentes
2. **Homologa** (empareja) cada elemento entre las distintas bases usando similitud de nombres, tensiones y barras
3. **Compara** los valores de R y X para detectar inconsistencias
4. **Valida** cuáles valores de ENT son correctos y cuáles necesitan corrección

## ¿Qué son las fuentes de datos?

| Fuente | Descripción | Archivo de entrada |
|--------|-------------|---------------------|
| **ENT** | Base de referencia actual del operador (contiene R, X, barras, voltajes) | `Base_ENT.xlsx` |
| **CNE** | Comisión Nacional de Energía - datos oficiales de operación y mantenimiento | `LinDatParOpe.csv`, `LinDatManOpe.csv` |
| **Infotécnica** | Reportes técnicos detallados con parámetros de secciones y transformadores | `secciones.xlsx`, `trafos-2d.xlsx`, `trafos-3d.xlsx` |

## ¿Por qué validar?

Los valores de reactancia (X) en ENT pueden estar **desactualizados o tener errores**. Este sistema compara X_ENT con las otras dos fuentes para:
- Confirmar los valores correctos (CORRECTO)
- Detectar discrepancias significativas (DISCREPA)
- Proponer qué valores cambiar automáticamente y cuáles revisar manualmente

## Flujo General

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FUENTES DE DATOS                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   inputs/Base Ent/              inputs/Actualizacion CNE/    inputs/Actualizacion│
│   └── Base_ENT.xlsx             ├── LinDatParOpe.csv         Infotecnica/       │
│       (base de referencia)      └── LinDatManOpe.csv         ├── secciones.xlsx │
│                                     (operación + mant.)      ├── trafos-2d.xlsx │
│                                                              └── trafos-3d.xlsx │
└────────────┬────────────────────────────┬────────────────────────────┬──────────┘
             │                            │                            │
             ▼                            ▼                            ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              ETAPA 1: CARGA DE DATOS                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   cargar_lineas_ent()         cargar_lineas_operacion()    consolidar_infotecnica│
│   cargar barras, R, X         cargar_lineas_mantenimiento  _completa()          │
│   desde Excel                 filtrar por mes de trabajo   calcular R, X desde  │
│                               aplicar_reemplazo_por_mes()  Z%, Pcu, S, V        │
│                                                                                 │
└────────────┬────────────────────────────┬────────────────────────────┬──────────┘
             │                            │                            │
             ▼                            ▼                            ▼
         df_ent                      df_resultado                  df_infotec
             │                            │                            │
             └──────────────┬─────────────┘                            │
                            ▼                                          │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         ETAPA 2: HOMOLOGACIÓN ENT ↔ CNE                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   homologar_lineas(df_ent, df_resultado)                                        │
│                                                                                 │
│   - Match por nombre usando similitud de texto (fuzz ratio)                     │
│   - Comparación de barras (a↔a, b↔b o invertido a↔b, b↔a)                       │
│   - Asigna confianza: ≥90% alta, 80-89% media, 50-79% revisar, <50% sin match   │
│   - Extrae R_CNE, X_CNE del match encontrado                                    │
│                                                                                 │
└────────────────────────────────────┬────────────────────────────────────────────┘
                                     │
                                     ▼
                               df_homologado
                                     │
                                     ├─────────────────────────────────────────────┐
                                     ▼                                             │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      ETAPA 3: HOMOLOGACIÓN ENT ↔ INFOTÉCNICA                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   homologar_con_infotecnica(df_homologado, df_infotec)                          │
│                                                                                 │
│   - Match por nombre, tensión y barras                                          │
│   - Desempate por circuito cuando hay múltiples candidatos                      │
│   - Extrae R_Infotec, X_Infotec del match encontrado                            │
│                                                                                 │
└────────────────────────────────────┬────────────────────────────────────────────┘
                                     │
                                     ▼
                                 df_final
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              ETAPA 4: EXPORTACIÓN                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   outputs/                                                                      │
│   ├── homologacion_YYYY-MM.csv        (resultado principal)                     │
│   ├── infotecnica_consolidada.csv     (líneas + trafos)                         │
│   ├── infotecnica_lineas.csv                                                    │
│   ├── infotecnica_transformadores_2d.csv                                        │
│   └── infotecnica_transformadores_3d.csv                                        │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Uso

El script principal `main.py` procesa los datos de un mes específico, aplicando reemplazos por mantenimiento y generando los archivos de salida.

```bash
# Opción 1: Con mes como argumento (formato YYYY-MM)
python main.py 2025-06

# Opción 2: Modo interactivo (solicita el mes)
python main.py
```

**¿Por qué el mes?** Las bases de datos reflejan el estado del sistema eléctrico en un momento dado. Un elemento puede tener un "reemplazo por mantenimiento" activo que cambia sus parámetros durante ciertos meses.

## Estructura del Proyecto

```
.
├── main.py                     # Script principal
├── src/
│   ├── __init__.py
│   ├── data_loader.py          # Funciones de carga y homologación
│   └── cargar_transformadores_infotec.py  # Carga de transformadores
├── inputs/
│   ├── Base Ent/               # Datos ENT (Excel)
│   ├── Actualizacion CNE/      # Datos CNE operación/mantenimiento
│   ├── Actualizacion Infotecnica/  # Reportes Infotécnica
│   └── Mantenimiento CNE/
├── outputs/                    # Archivos generados
└── revision/                   # Validación de X_ENT
    ├── README.md               # Documentación de validación
    ├── input/                  # Archivo de homologación con columna revision
    └── output/                 # Archivo clasificado con categorías
```

## Carpeta `revision/`

Contiene el análisis de validación de los valores de reactancia (X) de ENT comparados con CNE e Infotécnica. Aquí es donde se **decide qué valores X_ENT están correctos, cuáles cambiar y cuáles revisar manualmente**.

**Ver `revision/README.md` para la documentación completa con gráficos, análisis de sensibilidad de umbrales y conclusiones.**

### Flujo de Validación

```
revision/input/homologacion_*.xlsx          revision/output/homologacion_clasificada.xlsx
┌────────────────────────────┐              ┌────────────────────────────────────────────┐
│ Columnas de entrada:       │              │ Columnas agregadas:                        │
│ - revision (1/CNE/Infotec/0)│    ───►     │ - accion_propuesta                         │
│ - X_ENT, X_CNE, X_Infotec  │              │   (MANTENER/CAMBIAR/REVISAR/SIN_VALIDAR)   │
│ - diff_X_CNE_%, diff_X_... │              │ - clasificacion_validacion                 │
│                            │              │   (CORRECTO/DISCREPA_*/SIN_REFERENCIA)     │
│ La columna `revision`      │              │ - valor_sugerido (X recomendado)           │
│ indica qué fuente es       │              │ - delta_X (|X_ENT - valor_sugerido|)       │
│ confiable para validar     │              │ - fuente_valor_sugerido                    │
└────────────────────────────┘              └────────────────────────────────────────────┘
```

### Resultado del Análisis (umbral 15% y 50 Ω)

| Acción | Casos | % | Significado |
|--------|-------|---|-------------|
| **MANTENER** | 1,022 | 51.0% | X_ENT validado, no requiere cambio |
| **CAMBIAR** | 604 | 30.1% | Diferencia significativa pero cambio <50Ω: aplicar automáticamente |
| **REVISAR** | 213 | 10.6% | Diferencia grande (≥50Ω): revisar manualmente |
| **SIN_VALIDAR** | 165 | 8.2% | No hay fuente confiable para validar |

### Categorías de Validación

| Categoría | Descripción |
|-----------|-------------|
| `CORRECTO` | Ambas fuentes coinciden con X_ENT (diff < 15%) |
| `CORRECTO_PARCIAL_CNE` | Solo CNE disponible, coincide con X_ENT |
| `CORRECTO_PARCIAL_INFOTEC` | Solo Infotec disponible, coincide con X_ENT |
| `DISCREPA_ENT_FUENTES_COINCIDEN` | CNE ≈ Infotec pero difieren de X_ENT |
| `DISCREPA_FUENTES` | CNE ≠ Infotec, ninguna coincide con X_ENT |
| `DISCREPA_PARCIAL_CNE` | Solo CNE disponible, difiere de X_ENT |
| `DISCREPA_PARCIAL_INFOTEC` | Solo Infotec disponible, difiere de X_ENT |
| `SIN_REFERENCIA` | No hay fuente confiable para comparar |

Ver `revision/README.md` para documentación detallada de umbrales y análisis.

## Columnas Principales del Output

| Columna | Descripción |
|---------|-------------|
| `nombre_ENT` | Nombre de la línea/trafo en base ENT |
| `nombre_CNE` | Nombre homologado desde CNE |
| `nombre_Infotec` | Nombre homologado desde Infotécnica |
| `R_ENT`, `X_ENT` | Resistencia y reactancia de ENT |
| `R_CNE`, `X_CNE` | Resistencia y reactancia de CNE |
| `R_Infotec`, `X_Infotec` | Resistencia y reactancia de Infotécnica |
| `conf_CNE` | Confianza del match con CNE (%) |
| `conf_Infotec` | Confianza del match con Infotécnica (%) |
| `hay_reemplazo` | Si la línea tiene reemplazo activo en el mes |

## Requisitos

- Python 3.8+
- pandas
- openpyxl
- fuzzywuzzy (o rapidfuzz)
- matplotlib (solo para generar gráficos de validación)

## ¿Cómo empezar? (Guía rápida para nuevos usuarios)

1. **Instalar dependencias:**
   ```bash
   pip install pandas openpyxl rapidfuzz matplotlib
   ```

2. **Ubicar los archivos de entrada** en `inputs/`:
   - `Base Ent/Base_ENT.xlsx` (base de referencia)
   - `Actualizacion CNE/` (datos CNE)
   - `Actualizacion Infotecnica/` (reportes Infotécnica)

3. **Ejecutar la homologación** para un mes específico:
   ```bash
   python main.py 2025-06
   ```
   Esto genera `outputs/homologacion_YYYY-MM.csv` con los datos homologados de las tres fuentes.

4. **Analizar la validación de reactancias:**
   - El archivo clasificado está en `revision/output/homologacion_clasificada.xlsx`
   - Ver `revision/README.md` para análisis completo con gráficos

5. **Regenerar gráficos** (opcional):
   ```bash
   python revision/generar_graficos.py
   ```

---

## Anexo: Cálculo de R/X desde Infotécnica

### Líneas de Transmisión

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

### Transformadores 2D (Dos Devanados)

Los valores se calculan a partir del archivo `reporte_transformadores-2d.xlsx`:

```
1. R% = (Pcu_kW × 100) / (S_MVA × 1000)
2. X% = √(Z%² - R%²)
3. Z_base = V_kV² / S_MVA
4. R_Ω = (R% / 100) × Z_base
5. X_Ω = (X% / 100) × Z_base
```

Donde:
- `S_MVA`: Capacidad nominal AT (MVA)
- `V_kV`: Tensión nominal AT (kV)
- `Z%`: Impedancia de secuencia positiva tap central
- `Pcu_kW`: Pérdidas en el cobre (kW)

### Transformadores 3D (Tres Devanados)

Para transformadores de 3 devanados se usan los valores del devanado **AT-MT**:

```
1. R% = (Pcu_kW_AT-MT × 100) / (S_base × 1000)
2. X% = √(Z%_AT-MT² - R%²)
3. Z_base = V_kV_AT² / S_base
4. R_Ω = (R% / 100) × Z_base
5. X_Ω = (X% / 100) × Z_base
```

