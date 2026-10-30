# Análisis complementario: criterios de mínimo camino eléctrico

Material de apoyo a la minuta (`docs/Minuta_Minimo_Camino_Electrico.docx`). No forma parte del
código ni de los entregables del repo. Vive solo en la rama `claude/relaxed-ptolemy-70ek36`, que no
se mezcla con `main`. Los detalles de método y los números están en `docs/HANDOFF.md`, §3–§4b.

## Nombres de los criterios

| Nombre | Origen | Qué hace |
|---|---|---|
| Hoy (módulo) | — | Dijkstra sobre la X del ENT, sumando Ω de distintas tensiones sin referir |
| «Anular trafos troncales» (C1) | Dueño | X = 0 en los trafos de subestaciones con barra troncal |
| «Anular todos los trafos» (C2) | Dueño | X = 0 en todos los trafos |
| **«Referido»** | Propuesta | Cada Ω × (V_ref / V)², con V_ref = 220 kV y V = columna `V [kV]` del ENT. Equivale a por unidad |
| **«Referido + Subestación»** | Propuesta | «Referido» + C1: se llega a la troncal al tocar cualquier barra de su subestación |

## Conclusiones clave

- **La X está referida al lado de alta, en las tres fuentes.**
  - El ENT y la CNE entregan la X de los trafos referida al lado de alta.
  - Las líneas vienen en Ω de su propia tensión, ~0,4 Ω/km en todas.
  - El método actual suma esos Ω sin referir; tampoco lo hacía el R de 2023 (`CaminoMin_2023.R`).
- **Coincidencia con PN2604 (de 1.442 barras):**

  | Criterio | Coinciden | Diferencias a >100 km |
  |---|---|---|
  | Hoy | 1.020 | 119 |
  | «Referido» | 1.101 | 44 |
  | «Referido + Subestación» | 1.194 | 30 |

- **Plata (solo inyecciones y retiros), «Referido + Subestación» vs PN2604:** 109 barras con
  inyección o retiro, ~488 MM$/mes. El 56 % está en C.Chena→A.Jahuel, Candelaria→A.Jahuel y
  Quillota→Nogales.
- **Datos que conviene validar:**
  - X de los trafos de Itahue, Linares y Los Maquis: el ENT difiere 3–9× de la CNE.
  - Subsistema de Tap Pulelfu: aparece en S1 y debería estar en S2.
  - Errores #287 y #288.
- **Casos borde de «Referido»:**
  - Red de 500 kV (Jadresic, Kallpa, Cumbres).
  - Casi empates (Los Andes, Concepción).
  - Usar |Z| en vez de X: en «Referido» cambian 6 barras; en «Referido + Subestación», 99
    (casi empates en redes urbanas). Detalle en `docs/HANDOFF.md` §4d.

## Contenido

| Carpeta | Qué hay |
|---|---|
| `datos/` | `diferencias_*.csv` (módulo vs PN2604), `analisis_criterios_transformadores_PN2604.xlsx` (C1/C2), `criterios_ev.pkl`, `criterios_v2_por_barra.csv` (asignación con 8 criterios), `criterios_con_resistencia_por_barra.csv` (X vs |Z|) y `precio_por_barra_criterios.xlsx` (Δ precio por barra, PSUF y montos) |
| `figuras/anular_trafos/` | Mapas de 3 paneles hoy / C1 / C2 (Tilcoco, La Reina, Jadresic, Panguipulli, etc.) |
| `figuras/referido/` | Ver la tabla de abajo |
| `scripts/anular_trafos/` | Escenarios C1/C2, flag #287 y mapas |
| `scripts/referido/` | `banco.py` (todos los criterios), métricas, pruebas CNE y \|Z\| (`con_r.py`, `con_r_plata.py`), tablas de plata y figuras |

### Figuras de «Referido»

| Archivo | Para qué sirve |
|---|---|
| `simple_rahue.png` | **El ejemplo más simple**: una línea y un trafo, con el factor (V_ref / V)² |
| `simple_llanquihue.png` | Dos salidas de Llanquihue 66 kV; referir cambia la troncal |
| `concepto_que_es_referir.png` | Qué significa referir (66 / 154 kV, mismo circuito) |
| `concepto_referido.png`, `concepto_referido_subestacion.png` | Las dos propuestas explicadas |
| `concepto_donde_se_separan.png` | Por qué solo algunas barras cambian |
| `didactico_referir_lapalma.png`, `nodos_lapalma.png`, `nodos_linares.png`, `tramos_linares.png`, `con_sin_transformacion_linares.png` | Caminos reales, sin y con referir |
| `tres_criterios_*.png` | Barras donde hoy, «Referido» y «Referido + Subestación» dan troncales distintas |
| `v2_*.png`, `v3_*.png`, `referido_ejemplos_*.png` | Mapas de ejemplos (corrige, cambio nuevo, tercera troncal) |
| `referido_sin_sentido_*.png`, `caso_peq.png` | Casos borde y diferencias con PN2604 |

## Notas para reproducir

- **Fuente de verdad:** el módulo `minimo_camino` de `AlonsoFU/Balance-de-Potencia-Anual` (insumos
  `data/minimo_camino/inputs/2025/pre/`). La asociación de referencia es PN2604 de
  `Balance_2609_def.xlsm`, que no está en el repo.
- **Rutas:** los scripts tienen rutas absolutas al clon del módulo y a un scratchpad. Hay que
  ajustarlas al reproducir; los de `anular_trafos/` todavía apuntan al scratchpad original.
- **Orden de ejecución en `scripts/referido/`:**
  1. `banco.py` genera `banco.pkl`.
  2. `det.py` genera `grafos.pkl`.
  3. Después corren las métricas y las figuras.
