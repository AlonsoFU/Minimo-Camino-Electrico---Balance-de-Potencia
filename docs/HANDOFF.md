# HANDOFF — Minuta y análisis del mínimo camino eléctrico

Rama: `claude/relaxed-ptolemy-70ek36`. Última actualización: 2026-10-30.

## 1. Fuente de verdad (regla del dueño)

- **Todo se basa en el módulo `minimo_camino` del repo `AlonsoFU/Balance-de-Potencia-Anual`.**
  Hay que olvidar el primer repo y los km de Infotécnica. Los km se calculan con las coordenadas
  del módulo (`conversor_coordenadas_Nodos.xlsx`, haversine) y, si faltan, se pone "sin dato".
- Código del cálculo: `src/minimo_camino/domain/minimo_camino.py`.
- Insumos: `data/minimo_camino/inputs/2025/pre/`, que contiene `Ent2026.xlsx`, `Barras_PNCP.xlsx`,
  `Base_Potencia_2601_pre.xlsx` y `conversor_coordenadas_Nodos.xlsx`. La revisión está en
  `data/minimo_camino/revision/2025/pre/revision_subsistemas.csv`.
- Lógica del módulo, confirmada por el dueño:
  - Dijkstra sobre la reactancia X en Ω.
  - Las líneas y trafos en paralelo se combinan con 1/Xeq = Σ1/Xi.
  - Los destinos son solo las 50 barras troncales PNCP (44 S1, 6 S2) del mismo subsistema.
  - Los mantenimientos se filtran a la fecha de corte 2025-12-31.
  - Las barras sin ENT usan un proxy (EXACTO, MISMO_NOMBRE_OTRO_NV, TAP_NOMBRE_BASE, FUZZY ≥ 0.85,
    o el override de revision_subsistemas).
  - En un empate gana la primera alfabéticamente.
- **Asociación de referencia: solo el bloque PN2604 de la hoja 04 de `Balance_2609_def.xlsm`.**
  Ese archivo lo subió el usuario y no está en el repo.

## 2. Dónde está cada cosa

- **`docs/`: solo la minuta.**
  - `Minuta_Minimo_Camino_Electrico.docx`: minuta CEN (6 págs.) con el estilo de `Minuta_Enlight.docx`.
  - `figuras/fig1..fig3*.png`: figuras de la minuta (concepto, caso La Palma y comparación).
  - `scripts/minuta/`: construcción del docx y de las figuras 1–3.
- **`analisis_criterios/`: todo el análisis complementario de criterios.** Se mantiene aparte por
  decisión del dueño (2026-10-30), para no mezclarlo con el repo. Esta rama no se mezcla con main.
  Su `README.md` es el índice:
  - `datos/`: CSV, Excel y `criterios_ev.pkl` (1.445 barras × 46 columnas).
  - `figuras/anular_trafos/`: los mapas `mapa_*.png` de C1/C2.
  - `figuras/referido/`: conceptos, ejemplos y mapas de «Referido».
  - `scripts/anular_trafos/` y `scripts/referido/`.

### Estructura de la minuta

1. **Introducción.** Cita el extracto del numeral 2.2 de los decretos de precio de nudo sin
   nombrar un decreto específico, porque está en todos. Explica el propósito y menciona la
   asociación histórica.
2. **Metodología.** Describe la red, la regla 1/Xeq y cuatro bullets.
   - La Figura 1 es conceptual: dos caminos solo de líneas, de 28 y 35 Ω.
   - Sigue un párrafo "Cabe destacar…" sobre los trafos.
   - Luego viene el párrafo de la asociación manual histórica: 66 kV → 220 kV de la misma
     subestación, sin respaldo en código ni en documentos. En PN2604, 415 de 1.553 difieren, y 71
     de ellas están en la zona de Itahue, donde el cálculo da Candelaria.
3. **Caso de análisis: asignación por rodeo de transformadores de alta reactancia.** Usa La
   Palma 13 kV. Un párrafo corto cierra con "como se ve a continuación", y le siguen la Fig. 2,
   una tabla, la Fig. 3 y los bullets del problema.
   - La tabla compara tres caminos:
     - Ancoa por Linares: 32 km en línea recta, 109,0 km por la red, 287,9 Ω.
     - Itahue por los trafos de Itahue: 58 km en línea recta, por la red sin dato, 206,0 Ω.
     - Candelaria por San Fernando: 199 km en línea recta, por la red sin dato, 150,7 Ω. Es el
       seleccionado.
   - Con Nueva Nirivilo 2026, Itahue baja a 148,1 Ω.
4. **Alternativas.**
   - Publicar el camino.
   - Validar las X de los trafos Linares 154/66 e Itahue 154/66.
   - Formalizar la asociación manual.
   - Agregar un criterio complementario.
   - Comunicar el cambio.

### Reglas de redacción del dueño (respetar al editar la minuta)

- Nada de p.u. ni referencias al código: solo metodología.
- Decir "barra analizada". "Medio de generación de pequeña escala" va solo dentro de la cita. Si
  se habla de inyección, aclarar que es en la barra.
- Sin la sigla STN.
- Sin cantidades como "orden de 1.400 barras".
- Sin supuestos como "en general 220 y 500 kV".
- Nada de "fecha de corte / registro de entradas y salidas"; es un remanente del repo viejo.
- No usar "conservando empates" ni "situación problemática".
- La sección 3 debe ser corta: figura más tabla chica. La figura basta para explicar.
- Candelaria está en **O'Higgins**, no en la RM.

### Reconstruir la minuta

Los scripts esperan sus insumos en el directorio de trabajo:
- `ref/`: el `Minuta_Enlight.docx` del usuario descomprimido. **No está en el repo**; hay que
  pedirlo o descomprimirlo como `ref.docx`.
- `heading_block.xml`.
- `fig/` con las tres figuras.

```bash
cd docs/scripts/minuta
python3 make_figs3.py && python3 make_figs4.py        # fig/fig1..fig3
python3 build_docx2.py                                # reutiliza los helpers de build_docx.py
python <skill docx>/scripts/office/validate.py Minuta_Minimo_Camino_Electrico.docx --original ref.docx
```

Los paraIds deben ser < 0x80000000, o validate.py falla.

## 3. Análisis: módulo vs PN2604

- Resultado general: 1.006 barras iguales, 415 distintas y 132 sin resultado.
- De las 415 distintas, 285 se explican anulando el trafo pegado a la troncal y 299 con todos los
  trafos en 0. Quedan 93 sin explicar:
  - Quillota → A.Melipilla: casi empate por Dichas–A.Melipilla.
  - Atacama → O'Higgins: por la Liqcau nueva.
  - Cautín → Ciruelos: S2 vs S1.
  - Atacama → Laberinto.
- Ninguna barra de PN2604 está fuera de su zona.

## 4. Criterios evaluados (anular X de trafos, contra PN2604)

La X "anulada" se implementa como 1e-6, porque el módulo descarta aristas con X ≤ 0. El script
es `analisis_criterios/scripts/anular_trafos/criterios.py`.

- **Criterio 1:** trafos de subestaciones que tienen una barra troncal PNCP, por prefijo de 14
  caracteres. Son 83 trafos, incluyendo los de 13 kV.
- **Criterio 2:** todos los trafos (657).

Resultados sobre 1.445 barras evaluadas, con el ENT sin corregir:

| | C1 | C2 |
|---|---|---|
| Difieren de PN2604 | 297 | 293 |
| Diferencias del módulo que corrige | 290 | 303 |
| Diferencias nuevas | 179 | 215 |
| >200 km, por metodología | 7 | 10 |
| >200 km, por datos | 13 | 14 |
| Camino por baja tensión | 23 | 53 |
| Margen < 1 Ω | 314 | 388 |

Lecturas clave:

- **Mecanismo.** Anular trafos favorece a las troncales con muchos trafos de menor tensión, como
  Alto Jahuel. Candelaria no tiene ninguno.
- **Dirección.** La mayoría de las diferencias nuevas mueve la barra a una troncal
  *geográficamente más lejana*: 100/179 en C1 y 107/215 en C2.
- **Calidad.** Que coincida con PN2604 **no** prueba que esté bien, porque PN2604 es histórico.
  El dueño cree que los casos críticos se deben ver a mano.
- **Zona.** Criticidad se juzga por zona y distancia, no por precio. La columna "Sector" del ENT
  resultó demasiado granular.

Casos con mapa (hoy / C1 / C2):

- Tilcoco 154: Candelaria 39,1 Ω → A.Jahuel 32,0 → A.Jahuel 17,8.
- La Reina 110: C.Chena 19,8 → C.Navia 13,3 (empate con C.Chena) → A.Jahuel 13,0 por Los
  Almendros.
- Jadresic 220: PN2604 es D.Almagro. El módulo y C1 dan O'Higgins 42,5. C2 da C.Pinto 33,3, en
  **empate exacto** con D.Almagro.
  - El empate se explica porque los tramos D.Almagro–Illapa e Illapa–C.Pinto son idénticos en el
    ENT: 3 circuitos, cada uno con R 3,596604 y X 17,983020.
  - Probablemente es una línea partida en partes iguales, pero no se puede confirmar con los
    datos del módulo.
- Panguipulli 23: Rahue 97,3 → Valdivia 49,2 (= PN2604) → Ciruelos 15,7.
- Casos donde solo un criterio cambia la asignación:
  - San Fernando 66: solo C1 la cambia, a Itahue.
  - Concepción 66: solo C2 la cambia, a Hualpén.
- Santa Elena 13: ambos criterios dan C.Navia, por 0,1 Ω. Las barras de 13–23 kV heredan la
  decisión de su barra de 66/110 kV.

Las coordenadas tienen problemas:
- Algunas están malas u homónimas: S.CODEGUA, CODEGUA_066/110, Los Maquis 66, San Andrés.
- El Ruil aparece en las coordenadas como EL_RUIL_______066, pero en el ENT como RUIL1/RUIL2.
- Los mapas filtran por una caja regional y omiten los nodos sin coordenada.

### 4b. Criterios nuevos (2026-10-27, `analisis_criterios/scripts/referido/`, `analisis_criterios/datos/criterios_v2_por_barra.csv`)

- **Hallazgo de fondo.** El ENT entrega la X de cada línea en Ω a su propia tensión y la de cada
  trafo en Ω referida al lado de alta. Así, el módulo suma Ω de distintas tensiones sin referirlos
  a una base común. Por eso una línea de 66 kV pesa unas 11 veces menos de lo que corresponde
  frente a 220 kV, y el camino largo en baja tensión le gana al trafo. Esa es la causa del rodeo.
- **Nombres acordados con el dueño:**
  - Sus criterios: **«Anular trafos troncales»** (C1) y **«Anular todos los trafos»** (C2).
  - Las propuestas de Claude: **«Referido»** (`P_ref220`) y **«Referido + Subestación»** (`P_C1`).
  - Las figuras `v2_*`/`v3_*` usan estos nombres.
- **Criterios probados:**
  - `P_ref220`: X·(220/V)², equivalente a una base común. El resultado no depende de la tensión
    elegida.
  - `P_C1`: el anterior, más destino = subestación troncal completa.
  - `P_C2`.
  - `C3`: solo los trafos que tocan la barra troncal (≈ C1).
  - Reactancia efectiva de Thevenin, en Ω y referida. Se descarta porque se aleja más de PN2604.
- **Resultados** (sin barras con problema de datos; "dif >100 km" = la troncal elegida está a más
  de 100 km de la de PN2604):

| | actual | C1 | C2 | P_ref220 | P_C1 |
|---|---|---|---|---|---|
| = PN2604 (de 1.442) | 1.020 | 1.145 | 1.149 | 1.101 | 1.194 |
| Nuevas diferencias | — | 165 | 174 | 57 | 88 |
| Dif >100 km | 119 | 63 | 32 | 44 | 30 |
| Barra a >100 km de su troncal (PN2604: 83) | 174 | 103 | 98 | 96 | 80 |

- **Comportamiento por caso:**
  - `P_ref220` resuelve La Palma (Itahue).
  - Teno y Curicó siguen yendo a Candelaria, porque el trafo Itahue 220/154 (48,9 Ω) es más pesado
    que el de Tinguiririca (13,9 Ω).
  - `P_C1` las devuelve a Itahue (76 de 88), pero manda Rancagua a A.Jahuel por su 154 kV. Esa es
    la asimetría a favor de las subestaciones con varias tensiones.

- **La X de los trafos está referida al lado de alta.** Se verificó con el CSV CNE
  `inputs/Actualizacion CNE/LinDatParOpe_2024_PNCP.csv` del repo antiguo:
  - En 1.309 de 1.327 trafos, `LinVolt` es la tensión mayor.
  - Con `LinPotMaxA->B` como potencia nominal, la impedancia mediana da 12,6 % si X está en AT y
    363 % si está en BT. 1.148 trafos caen en el rango 5–20 % en AT, contra 41 en BT.
- **Hallazgo de datos: el ENT tiene X de trafos muy distintas a las de la CNE.**

  | Trafo | ENT (Ω) | CNE (Ω, equivalente en paralelo) |
  |---|---|---|
  | Itahue 154/66 | 85,7 | ~13,1 (tres trafos) |
  | Itahue 220/154 | 48,9 | 15,6 |
  | Linares 154/66 | 164 | ~19 (dos trafos) |
  | Los Maquis 220/110 | 7,3 | 46,4 |

  Con los valores CNE solo en Itahue y Linares, incluso el método **actual** asigna La Palma,
  Curicó, Linares y Teno a Itahue, igual que PN2604. Script: `analisis_criterios/scripts/referido/test_cne.py`.

### 4c. Sesión 2026-10-28/30 (hallazgos adicionales)

- **El R de 2023 tampoco referenciaba.** El usuario subió `CaminoMin_2023.R`:
  - Lee `V [kV]` pero solo usa X (`Xinv = 1/X`, `Xfinal`, Dijkstra de igraph).
  - Nunca hubo p.u. El `Minimo_camino_AFU.R` de 2025 no se recibió.
- **Argumento central de «Referido».**
  - X = V/I. Al pasar por un trafo, V se multiplica por (V_ref/V) e I se divide por lo mismo, así
    que X se multiplica por (V_ref/V)².
  - Es lo que hacen DIgSILENT y PSS/E (por unidad: X_pu = X_ref220 / 484 con base 100 MVA).
  - Da lo mismo a qué tensión se refiera. Solo cambia la escala.
- **Usar |Z| en vez de X:**
  - «Referido» cambia 6 barras.
  - «Referido + Subestación» cambia 99, casi todas casi empates.
  - Se recomienda mantener X (modelo DC).
- **Cambio por criterio (de 1.442 barras):**

  | Criterio | Cambian vs módulo | Difieren de PN2604 (hoy 422) |
  |---|---|---|
  | «Referido» | 244 | 341 |
  | «Referido + Subestación» | 368 | 248 |

  - De los 244 de «Referido»: 138 van hacia PN2604, 57 se alejan y 49 caen en una tercera troncal.
  - Solo 3 cambios se deben a la red de 500 kV: Jadresic, Kallpa y Cumbres.
- **Plata** (`analisis_criterios/datos/precio_por_barra_criterios.xlsx`).
  - Método: Δ precio PN2604 × MW de inyección/retiro (Gx/Bfact de la hoja 05). Excluye las filas Tx.
    El dueño pidió considerar solo inyecciones y retiros.
  - «Referido + Subestación» vs PN2604:
    - 109 barras con inyección o retiro, ~488 MM$/mes. Equivale al 0,26 % de lo valorizado.
    - Neto: inyecciones +31 y retiros −68 MM$/mes.
    - 140 barras suben de precio (61 con MW) y 107 bajan (48 con MW).
  - Los tres cambios que concentran el 56 %:
    - C.Chena→A.Jahuel (95).
    - Candelaria→A.Jahuel (93).
    - Quillota→Nogales (86).
  - Hojas "Ref+Sub PSUF …": PSUF = la barra tiene filas Tx, misma definición que `mb_dim_barra`.
- **Los 5 casos que "empeoran" frente a PN2604 no los causa el criterio:**
  - PEQ 220: cuelga eléctricamente de Lagunas.
  - Capricornio: está eléctricamente más cerca de Laberinto.
  - Quinta: el dato de los trafos de Itahue.
  - Tap Pulelfu: error de subsistema. Base_Potencia la pone en S1, y sus vecinas Capullo y Copihues
    están en S2.
  - Todos dan lo mismo con el módulo actual.
- **Figuras didácticas** (en `analisis_criterios/figuras/referido/`):
  - `simple_rahue.png`: Llanquihue 66 → Rahue, una línea y un trafo, con el factor (V_ref/V)².
  - `simple_llanquihue.png`.
  - `nodos_lapalma.png`.
- **Organización.** El dueño decidió guardar el análisis aparte en `analisis_criterios/` (con
  README índice), no en `docs/`. La rama no se mezcla con main.

### 4d. Criterios con resistencia (|Z| en vez de X), 2026-10-30

Scripts `analisis_criterios/scripts/referido/con_r.py` y `con_r_plata.py`; tabla por barra en
`analisis_criterios/datos/criterios_con_resistencia_por_barra.csv`.

- **Supuestos:**
  - Peso por tramo = |Z| = √(R² + X²). R y X se refieren con el mismo (220/V)².
  - Paralelos en complejo (1/Zeq = Σ 1/Zi). Hacerlo sobre los módulos da exactamente lo mismo.
  - En serie se suman los |Z| de cada tramo, porque Dijkstra necesita pesos sumables. Es una cota
    superior de |ΣR + jΣX|.
  - R tal como viene en el ENT: 3 líneas y 4 trafos con R = 0. No se corrige por temperatura.
  - En «Referido + Subestación» se anulan R y X de los trafos C1.
  - El resto sin cambios: mantenimientos, proxy, desempate alfabético, solo inyección y retiro a
    precio PN2604.
- **Resultados (1.442 barras):**

  | Criterio | = PN2604 | Cambian vs hoy | MM$/mes vs hoy |
  |---|---|---|---|
  | Hoy (X) | 1.020 | — | — |
  | «Referido» X | 1.101 | 244 | 610 |
  | «Referido» \|Z\| | 1.101 | 248 | 660 |
  | «Referido + Subestación» X | 1.194 | 368 | 932 |
  | «Referido + Subestación» \|Z\| | 1.197 | 396 | 961 |

- **X → |Z| en «Referido»:** cambian 6 barras.
  - Curicó y Curicó2 pasan de Candelaria a Itahue, que coincide con PN2604.
  - E.Sauce va de P.Azúcar a L.Vilos.
  - C.Huichahue va de Valdivia a Ciruelos.
  - Impacto: ~50 MM$/mes.
- **X → |Z| en «Referido + Subestación»:** cambian 99 barras, ~45 MM$/mes.
  - Son casi empates: margen menor al 5 % en 76 de ellas.
  - Se concentran en redes urbanas de 110/66 kV:
    - Lagunillas → Hualpén: 34 barras.
    - C.Navia → C.Chena: 31.
    - L.Maquis → Nogales: 17.
  - Entre esos pares los precios son muy parecidos (~10 $/kW/mes), salvo L.Maquis/Nogales y Andes.
  - Con PN2604 coinciden 49 con |Z| y 46 con X: no mejora.
- **Por qué R mueve más en «Referido + Subestación»** (`por_que_r.py`, `por_que_r2.py`):
  - En «Referido», el trafo hacia la troncal separa a las candidatas (C.Navia 24,3 Ω y C.Chena 6,4 Ω
    a 220 kV). Los casi empates comparten casi todo el camino y difieren en un tramo de 220 kV con el
    mismo R/X, así que R escala igual las dos rutas. Solo 1 de 760 casi empates (<5 %) tiene R/X
    distinto entre rutas.
  - En «Referido + Subestación», ese trafo vale 0. Las rutas se separan antes, en la red de 110/66 kV,
    con líneas de R/X distinto, y R penaliza la más resistiva. Pasa en 24 de 685 casi empates.
  - La X del camino que está en trafos (R/X ~0,02) baja de 62 % a 28 %; el R/X del camino sube de
    0,18 a 0,24.
  - Ejemplo La Reina 13 kV: desde Ochagavía, a C.Navia por Metro–Renca (X 8,5 Ω, R 2,7 Ω) o a
    C.Chena por Lo Espejo (X 8,9 Ω, R 1,8 Ω). Gana C.Navia con X por 0,3 % y C.Chena con |Z|.
- **Qué cuenta como "subestación"** (`subest_niveles.py`). El 2.2 de los decretos dice "subestación
  del STN" sin precisar niveles de tensión. En «Referido + Subestación» se anulan 83 trafos: 60
  tocan directo la barra troncal (220/x, 500/220) y 23 son internos de niveles menores (110/66,
  154/66, 66/13). El pareo por nombre arrastra casos dudosos: Hualpén 154–Petropower 66 y
  PPeuco 110–Polpaico 23. La variante intermedia, que anula solo los 60 trafos que tocan la troncal,
  da 1.180 = PN2604 y 362 cambios vs hoy. Difiere de «Referido + Subestación» en solo 14 barras y
  de «Referido» en 255.
- **Sensibilidad a la suma en serie:** usando el |ΣZ| exacto del camino, «Referido» queda en 1.103
  y «Referido + Subestación» baja a 1.171. Esto muestra que este último es sensible donde hay casi
  empates.

### 4e. Comparación consolidada (2026-11-11)

El archivo `analisis_criterios/datos/comparacion_criterios.xlsx` (script `comparacion_final.py`)
compara 9 criterios: Hoy, C1, C2, y Referido / Referido + trafo troncal / Referido + Subestación,
cada uno con X y con |Z|.

| Criterio | = PN2604 | Cambian vs hoy | Barra→troncal >100 km | MM$/mes movidos |
|---|---|---|---|---|
| Hoy | 1.020 | — | 174 | — |
| Referido + trafo troncal, X | 1.180 | 362 | 86 | 878 |
| Referido + Subestación, X | 1.194 | 368 | 80 | 932 |

El numeral 2.2 de los decretos dice "mínima distancia eléctrica" hasta la "subestación", determinada
por el Coordinador. No define X ni Z ni qué niveles de tensión cuentan. Recomendación vigente:
referir, medir hasta la subestación con la lectura intermedia y usar X, con R solo para desempatar
diferencias menores al 2 %. X o |Z| es una elección del dueño.

### 4f. Calidad de los datos del ENT (2026-11-11)

Scripts `datos_x.py` y `datos_ceros.py`. Referencia: `revision/homologacion_infotecnica_CNE_peajes.xlsx`,
usando la columna `revision` (1 o CNE → X_CNE; Infotec → X_Infotec; 0 → sin referencia).

- **Cobertura:** 1.839 de 2.004 filas tienen referencia válida; 1.688 de los 1.831 tramos
  operativos.
- **Discrepancias (|X_ref/X_ENT − 1|):**
  - Líneas (1.216): 571 bajo 5 %, 250 entre 5 y 20 %, 97 entre 20 y 50 %, 298 sobre 50 %.
  - Trafos (623): 146 bajo 5 %, 48 entre 5 y 20 %, 74 entre 20 y 50 %, 355 sobre 50 %.
  - Hay patrones sistemáticos en trafos: 89 con razón ≈ 1/3 y 39 con ≈ 2. Puede ser cómo se
    representan unidades en paralelo o la base MVA, no necesariamente errores.
- **Errores claros:**
  - 4 trafos 66/13 con X = 0,000378 Ω (placeholder): La Unión, Picarte y Puerto Varas (2). La CNE
    da entre 15 y 33 Ω.
  - Ancoa–Colbún 220 con X = 0,00726 Ω: a verificar.
  - Los tramos con 0,0042 Ω son conexiones o taps, plausibles.
- **La homologación también tiene pareos malos:** Melipeuco ↔ El Peñón, Lo Aguirre ↔ Alto Jahuel,
  Chocalán. Por eso el reemplazo automático es una sensibilidad, no una corrección.
- **Impacto de reemplazar X del ENT por la referencia (barras que cambian solo por datos):**

  | Criterio | Reemplazo si \|dif\| ≥ 20 % (777 tramos) | Reemplazo total (1.688) | = PN2604 (ENT → total) |
  |---|---|---|---|
  | Hoy | 412 | 366 | 1.020 → 1.106 |
  | Referido | 270 | 219 | 1.101 → 1.124 |
  | Referido + trafo troncal | 231 | 181 | 1.180 → 1.177 |
  | Referido + Subestación | 233 | 183 | 1.194 → 1.177 |

  Los datos mueven tantas barras como el criterio, pero el orden entre criterios se mantiene. Los
  criterios referidos son menos sensibles a los datos que el de hoy.

### 4g. Tramos decisivos (2026-11-11)

Archivo `analisis_criterios/datos/tramos_decisivos.xlsx`, con scripts `decisivos.py` y
`decisivos_xlsx.py`.

- **Método:** se reutiliza la validación previa del dueño (`revision/output/homologacion_clasificada.xlsx`).
  A cada tramo DISCREPA se le asigna su valor sugerido, uno a la vez, y se recalcula la troncal de
  las 1.442 barras. El cálculo usa Dijkstra desde las 50 troncales y reproduce 1.442/1.442.
- **Resultados:**
  - Referido + trafo troncal: 727 tramos probados, 47 decisivos (39 con plata), 227 barras
    afectadas.
  - Hoy: 765 tramos probados, 51 decisivos, 368 barras afectadas.
  - Los principales con «Referido + trafo troncal»:
    - L.Almendros 220/110: 144 MM$/mes.
    - Ventanas 220/110: 87.
    - Teno 154/66: 60.
    - Crucero–Kimal: 34.
    - Maule 154/66: 30.
- **Patrón:** varios trafos tienen en el ENT una X ≈ 3 veces la de las fuentes (L.Almendros,
  Maule, Codegua, Charrúa, Concepción). Hay que aclarar si es base MVA o banco de unidades.
- Los trafos de las troncales (A.Jahuel, Itahue 220/154, Charrúa, Concepción) son decisivos hoy,
  pero dejan de importar con el criterio porque quedan anulados.
- **Patrón ×3 verificado con las fichas de Infotécnica** (`inputs/Actualizacion Infotecnica/reporte_transformadores-2d/3d.xlsx`).
  X = Z % · V² / S_base:
  - L.Almendros: 10,57 % a 400 MVA y 220 kV da 12,8 Ω (ENT 38,0).
  - Maule N°1: 8,39 % a 36 MVA y 154 kV da 55,3 Ω (ENT 165,7).
  - Charrúa JT1: 8,01 % a 300 MVA da 13,5 Ω (ENT 40,8).
  - Concepción JT7: 5,94 % a 201 MVA da 15,0 Ω (ENT 43,8).

  El ENT equivale a usar S/3 (o un error de (√3)²). No depende del tipo de trafo (aparece en T,
  BA y A, de 2 y 3 devanados), así que es un error de carga, no de representación: las fuentes
  están bien. Codegua no calza (ENT/Infotécnica = 4,0); revisar aparte.
- **Otros factores, revisados con fichas:** no responden a una sola causa.
  - ×2 y ×½: solo 17 de 68 son filas de unidades en paralelo. Varios "×2" contra el valor sugerido
    son en realidad ×3 contra la ficha (Alto del Carmen, Florida, La Dehesa).
  - ×4: no es por referir. En 110/13 o 66/13 ese factor sería 25 a 71; contra la ficha da ×4,1 a
    ×5,8.
  - Las fichas también tienen errores: Ochagavía con S = 336 MVA en un trafo de 13,3 MVA, y
    Polpaico 500/220.

  Conclusión: no se puede corregir por grupo en automático. Los decisivos se revisan caso a caso
  con la ficha, más una prueba de plausibilidad: Z entre 4 y 15 % y S consistente con el nombre.
- **Pendiente:** verificar a mano los decisivos, corregirlos y volver a correr (paso 6).

### 4h. Trafos sensibles en caminos con retiro (2026-11-13)

Archivo `analisis_criterios/datos/trafos_sensibles_retiros.xlsx` (script `retiros_trafos.py`).
Usa «Referido + trafo troncal» y las 527 barras con retiro (12.043 MW). Para cada barra calcula
el cambio de X que da vuelta su troncal: margen / X de cada trafo no compartido entre el camino
ganador y el camino a la 2ª troncal.

- Solo 11 trafos están en la parte de los caminos que decide; 7 la dan vuelta con ≤20 %.
- Datos dudosos y sensibles:
  - Ventanas 220/110: ENT = ⅓ de las fuentes. Con +200 % da vuelta 16 barras, 77 MM$/mes.
  - L.Almendros 220/110: ENT = 3×. Basta −4 %.
  - Melipilla 110/66: ENT = 4,9×.
- Sensibles pero con datos validados:
  - Esmeralda / Liqcau: el sector también está afectado por #287.
  - R.Aconcagua.
  - Nueva Guindo / Coronel: 17 barras, poca plata.
- Conteo ×3 (`x3_conteo.py`): 66 trafos; 8 tocan la troncal (anulados); quedan 58; 10 decisivos.

- **Ampliado a barras con inyección o retiro y a todos los tramos** (`ivr_*.py`, archivo
  `tramos_sensibles_iny_ret.xlsx`): 700 barras, 22.705 MW.
  - En las partes de los caminos que deciden hay 158 tramos: 11 trafos y 147 líneas. 47 dan
    vuelta alguna barra con un cambio ≤20 %.
  - Corregir los DISCREPA al valor sugerido cambia algo en 12 tramos. Los principales:
    - L.Changos–Kimal 500 (2 circuitos, ENT 2,9×): 4 barras, 218 MM$/mes.
    - Ventanas 220/110: 87.
    - Crucero–Kimal 220: 34.
    - L.Almendros: 10.
  - L.Changos–Kimal no apareció en la prueba uno a uno (§4g), porque ahí se corrigió un circuito a
    la vez. Los circuitos en paralelo hay que corregirlos juntos.

### 4i. Efectos en cadena de las correcciones (2026-11-13)

Script `cadena.py`; secuencia en `analisis_criterios/datos/secuencia_correcciones.xlsx`. Usa
«Referido + trafo troncal» y 668 bloques DISCREPA, con los paralelos corregidos juntos.

- **De a uno:** 44 bloques decisivos, 243 barras (unión).
- **Juntos:**
  - Los 44 decisivos: 193 barras, 541 MM$/mes. 9 barras cambian solo al combinar y 59 se
    cancelan.
  - Los 668 bloques: 183 barras, 395 MM$. Los no decisivos combinados también mueven el resultado.
- **Secuencia que recalcula en cada paso:**
  - 6 pasos dan 521 de 541 MM$.
  - Hay interacciones: Crucero–Kimal pasa de 16 a 26 barras después de L.Changos–Kimal; Itahue, de
    4 a 25 después de Teno y Maule; Linares, de 14 a 4.
  - Las interacciones son locales, por zona: Kimal, Maule–Itahue–Teno–Linares, Dichas, Santiago
    oriente.
- **Regla:** no sumar efectos individuales. El resultado depende solo del conjunto aplicado, no del
  orden. Revisar por zona en rondas, recalcular el ranking tras cada ronda y cerrar aplicando el
  resto por regla, con un recálculo final.

### 4j. Plan de revisión de datos: calidad, combinaciones y zonas (2026-11-14/17)

Punteo para presentar: `analisis_criterios/LOGICA.md`. Resultados: `analisis_criterios/datos/resultados.xlsx`
(hojas 1–7) y `resultados_refsub_z.xlsx`. Todo es **simulación sobre una copia**: el ENT no se toca.

- **Objetivo:** saber qué datos conviene verificar y corregir antes de cambiar el ENT, sin revisar
  los 668 tramos que discrepan.
- **Método base:** se corrige un tramo (o un bloque de paralelos) al valor sugerido de la validación
  previa del dueño, se recalcula la troncal de las 1.442 barras y se cuentan las barras y la plata
  que cambian. Los efectos individuales nunca se suman; siempre se recalcula con todo lo aplicado.
- **Tramos decisivos por criterio** (`dec_criterios.py`, `dec_criterios_geo.py`):

  | Criterio | Decisivos | Mejoran / empeoran (geografía, ±5 km) |
  |---|---|---|
  | Hoy (X) | 35 | 12 / 21 |
  | Ref + trafo troncal (X) | 44 | 27 / 13 |
  | Ref + trafo troncal (\|Z\|) | 48 | 21 / 21 |
  | Ref + misma subestación (X) | 40 | 23 / 13 |
  | Ref + misma subestación (\|Z\|) | 43 | 20 / 17 |

- **Calidad del cambio** (`calidad_tramo.py`, `geo_tramo.py`): se mide si la barra queda más cerca o
  más lejos y si gana o pierde coincidencia con PN2604. Con «Ref + trafo troncal» y X:
  - cambiar: 12 tramos, 202 MM$/mes;
  - revisar ficha: 11 tramos, 71;
  - no cambiar sin ficha: 11 tramos, 392;
  - sin señal: 10 tramos, 36.
- **No decisivos que pasan a decisivos** (`nodec_post.py`): 3 después de aplicar los 12; 7 (318 MM$)
  después de aplicar los 44.
- **«Ref + misma subestación» con |Z|, completo** (`ref_sub_z.py`):
  - 43 decisivos (14 cambiar, 9 revisar, 14 no cambiar, 6 sin señal);
  - juntos: 182 barras y 528 MM$;
  - **validación de R:** difiere en 1.064 de 1.996 tramos (53 %); en 205 la X coincide y la R no.
- **Por qué X es más estable que |Z|:** la R decide ~100 casi empates (<5 %); el resultado depende
  de cómo se suma la R en serie (1.197 contra 1.171); la R está menos validada. La metodología
  queda pendiente: decide el dueño.
- **Combinaciones de no decisivos** (`grupos.py`, `grupos2.py`, `grupos_robusto.py`):
  - Prueba por grupos: tramos ordenados de norte a sur en grupos de 40; los grupos que cambian algo
    se parten hasta aislar la combinación (ddmin); al final se prueba todo junto.
  - Se repitió con 4 agrupaciones (latitud, troncal más cercana, dos al azar): coinciden salvo en
    Mulchén.
- **Prueba exhaustiva por zona** (`zonas_exh.py`; entorno de 2 saltos, todas las combinaciones de
  hasta 4 tramos, ~10.700 recálculos):

  | Zona | Zona completa (MM$/mes) | Peor parcial (MM$/mes) |
  |---|---|---|
  | Kimal | 34 | 227 (solo L.Changos–Kimal) |
  | Mulchén | 36 | 270 |
  | Las Vegas, Calera, Chiloé, Puerto Varas | ≤ 6 | ≤ 6 |

  **Regla:** cada zona se corrige completa, nunca a medias.
- **Casos ilustrados:**
  - `analisis_criterios/figuras/datos/busqueda_combinaciones.png`.
  - `caso_lchangos_kimal.png`: las fuentes coinciden en que el ENT está mal (106,8 contra
    36,9 Ω), pero corregir solo ese tramo deja 10 barras más lejos (227 MM$). Es el caso borde de
    500 kV.
- **Definición de zona** (`zonas_def.py`): un tramo decisivo o de combinación, más los tramos que
  difieren a ≤2 conexiones; las zonas que comparten tramos se juntan. Resultado: 16 zonas, 244 tramos
  (44 decisivos y 200 vecinos). La más grande (83 tramos, red central) hay que partirla. De los 200
  vecinos, solo ~15 tienen interacción probada.
- **Registro auditable (2026-11-17):** se repitieron todas las pruebas para 4 criterios (trafo troncal y
  misma subestación, cada uno con X y |Z|), guardando cada recálculo en
  `analisis_criterios/datos/registro_pruebas.sqlite.gz` (52.446 pruebas; ver `REGISTRO_PRUEBAS.md`;
  scripts `registro.py` y `post_registro.py`).

  | Criterio | Decisivos | Vecinos con interacción > 1 MM$/mes | Total a revisar |
  |---|---|---|---|
  | Trafo troncal, X | 44 | 50 | 94 |
  | Trafo troncal, \|Z\| | 48 | 50 | 98 |
  | Misma subestación, X | 40 | 36 | 76 |
  | Misma subestación, \|Z\| | 43 | 51 | 94 |

  - Las listas de X y de |Z| comparten 83 de 94–98 tramos (trafo troncal) y 67 de 76–94 (misma
    subestación). Unión de los 4 criterios: 112 tramos; 66 están en los cuatro.
  - **Corrección:** antes se dijo que solo pesaban 22 vecinos (zona central y Kimal). Ese conteo
    miraba solo esas dos zonas. Contando todas, con interacción mayor a 1 MM$/mes, son ~50.
- **Comparación final contra la base actual** (`final_vs_base*.py`, hoja 11). La base es el método actual
  con el ENT; el final, el método nuevo con los datos corregidos.
  - El final difiere de la base en 506 barras y ~1.240–1.285 MM$/mes.
  - El método solo explica 362–396 barras; los datos agregan ~110–145 más.
  - Corrigiendo solo la lista a revisar (76–98 tramos) se reproduce el final en 489–494 de esas 506
    barras.
  - La coincidencia con PN2604 baja de ~1.190 a ~1.165 al corregir los datos (PN2604 se hizo con los
    datos viejos).
- **Base = PN2604** (pedido del dueño, 2026-11-18): las comparaciones finales se hacen contra la asignación
  vigente, no contra el módulo (hoja 13, `vs_pn2.py`).

  | Escenario | Distintas a PN2604 | MM$/mes | Más cerca / más lejos que PN2604 |
  |---|---|---|---|
  | Módulo actual | 422 | 946 | 56 / 318 |
  | Método actual + datos corregidos | 524 | 1.257 | 62 / 408 |
  | Nuevo + datos actuales | 245–262 | 488–555 | 59–93 / 132–146 |
  | Nuevo + datos corregidos | 275–279 | 632–672 | 104–108 / 108–112 |

- **Escala de la plata:** el total valorizado (inyección y retiro a precio de su troncal) es
  ~190.000 MM$/mes. Corregir los 44 mueve ~540 (0,3 %) y el cambio de método ~880 (0,5 %).
- **Hueco cerrado** (`hueco.py`, 13.170 recálculos; hojas 8–9 de `resultados.xlsx`). En las zonas de
  ≤20 tramos se probaron todas las combinaciones de 2–4 tramos con al menos un decisivo; en las grandes,
  cada decisivo con cada vecino más ddmin. Comparación de decisivos solos (juntos) contra la zona
  completa, en MM$/mes:
  - Zona central (83 tramos, incluye Mulchén): 236 → 272 (+36).
  - Kimal: 200 → 34 (los vecinos anulan L.Changos–Kimal).
  - El Salto: 10 → 0.
  - El Laurel: 3 → 0.
  - Calera / Las Vegas: 13 → 16.
  - En las otras 11 zonas los vecinos no cambian nada.

  Conclusión: los vecinos pesan de verdad solo en la zona central y en Kimal; en las demás basta con
  los decisivos.

### 4k. Estado al cierre de la sesión 2026-11-19 (para retomar)

**Archivos clave** (todos en `analisis_criterios/`):
- `LOGICA.md`: resumen en punteo. Empieza con la **tabla comparativa contra PN2604** y el punteo "Qué decir al
  presentarla", que el dueño pidió conservar.
- `datos/listado_tramos.xlsx`: **listado final de los 116 tramos a corregir** (rehecho y verificado el 2026-11-19,
  ver §4l; lo genera `scripts/referido/listado_excel2.py`). Hojas:
  - Leeme: definiciones, en una línea cada una.
  - **Etapas**: el plan. Por etapa: tramos, líneas y trafos, imprescindibles, grupos, MM$/mes, plata acumulada y
    barras distintas a PN2604.
  - **Revisión**: una fila por tramo, ordenada por etapa, zona y grupo, en 4 bloques:
    - Identificación.
    - Por qué importa: imprescindible, crítico/vecino, solo o en grupo, con quién se corrige, efecto del grupo y
      de la zona.
    - Datos: X y R de ENT, CNE e Infotécnica, X sugerida y su fuente, razón ENT/sugerida, nombres en las fuentes,
      **confianza del valor sugerido** (alta/media/baja) y su motivo.
    - Para llenar con la ficha (columnas amarillas).
  - Zonas, Zonas por variante, Avance por etapa, Verificación y Detalle (efecto de cada tramo solo).
- `datos/resultados.xlsx`, hojas 1–16. Las más usadas:
  - 13: todos los escenarios contra PN2604.
  - 14: plata que sube y que baja, y distancia promedio.
  - 15: % por zona.
  - 16: barras más cerca o más lejos por zona, con el resto, la lista completa y los 668.
- `datos/registro_pruebas.sqlite.gz` (+ `REGISTRO_PRUEBAS.md`): las 52.446 pruebas, auditables.
- `datos/lista_revision.xlsx`: los 112 tramos por variante.
- `presentacion/`: fuentes de la presentación (10 láminas; artifact
  https://claude.ai/artifact/4UsMzNCY3a8ZAVxcdhhHSY, privado).

**Base de todo:** PN2604, la asignación vigente. Método nuevo = Referido (referir a 220 kV) + subestación troncal,
en 4 variantes: TT (anula solo el trafo que toca la barra troncal) o MS (toda la subestación), con X o |Z|. La
metodología final la decide el dueño. Los datos corregidos son el valor sugerido de su validación
(`revision/output/homologacion_clasificada.xlsx`).

**Tabla comparativa clave (contra PN2604; datos actuales → corregidos):**

| Método | Distintas a PN2604 | Barras que cambian al corregir (mismo método) | MM$/mes | Más cerca / más lejos que PN2604 | >100 km |
|---|---|---|---|---|---|
| PN2604 | 0 | — | 0 | — | 83 |
| Actual, sin referir | 422 → 524 | 216 | 946 → 1.257 | 56/318 → 62/408 | 174 → 169 |
| Referido, X | 341 → 399 | 168 | 662 → 839 | 98/202 → 105/232 | 96 → 95 |
| Referido, R | 341 → 379 | 183 | 612 → 932 | 100/200 → 103/214 | 93 → 98 |
| Ref + subestación, X | 248–262 → 277–279 | 183 | 488–554 → 632–633 | 59–67/140–146 → 104–106/112 | 80–86 → 83 |
| Ref + subestación, R | 245–257 → 275–279 | 167 | 508–555 → 670–672 | 85–93/132–136 → 104–108/108 | 82–86 → 84 |

**Segunda tabla clave: qué pasa al corregir cada zona** (método nuevo, antes contra después; rango de las 4
variantes; zonas definitivas de §4l; hoja Zonas del listado y hoja 16 de `resultados.xlsx`):

| Ronda | Qué se corrige | Tramos | Barras que cambian | Más cerca | Más lejos | Δ km promedio | MM$/mes | Lectura |
|---|---|---|---|---|---|---|---|---|
| 1 | Ventanas | 2 | 37 | 33 | 1 | −14 | 87 | Acerca |
| 2 | Maule–Itahue–Teno–Linares | 13 | 8–10 | 8–10 | 0 | −56 a −49 | 6–62 | Acerca mucho |
| 3 | Santiago oriente | 8 | 19–43 | 0–1 | 19–24 | +9 a +19 | 139–144 | Aleja |
| 3 | Mulchén | 4 | 4 | 0 | 4 | +53 | 36 | Aleja; solo con los 4 juntos |
| 4 | Aconcagua (Calera–S.Rafael) | 20 | 14 | 3–13 | 1–9 | −45 a +33 | 6–22 | Con X aleja, con R acerca |
| 4 | Melipilla–Isla de Maipo | 13 | 6–11 | 4–11 | 0 | −42 a −24 | 4 | Acerca, poca plata |
| 4 | Atacama (Cardones–Maitencillo–D.Almagro) | 9 | 5 | 3 | 0 | −32 | 5 | Acerca, poca plata |
| 4 | Dichas 220 | 2 | 1 | 1 | 0 | −38 | 0 | Sin plata |
| 4 | Fopaco (independiente) | 1 | 0–3 | 0 | 0–3 | +416 | 0–39 | Solo con R; caso raro (#305) |
| 4 | Turibe–Esmeralda (independiente) | 1 | 5 | 5 | 0 | −45 | 9 | Acerca |
| 5 | Kimal | 19 | 17 | 1 | 2 | +4 | 34 | Casi neutro |
| 6 | El Laurel 220 | 2 | 0–11 | 0–4 | 0–3 | −5 | 0–3 | Solo con X |
| 6 | Codegua 66 | 2 | 1 | 0 | 1 | +32 | 0 | Sin plata |
| 6 | Independientes chicos | 20 | 19–53 | 7–40 | 4 | −16 a −13 | 4–8 | Acerca, poca plata |
| | Lista completa | 116 | 162–187 | 79–114 | 39–42 | −10 a −4 | 342–422 | Acerca |
| | Todos (668) | 668 | 167–183 | 84–113 | 39–40 | −10 a −4 | 341–426 | Casi igual que la lista |

**El dueño marcó estas dos tablas como las más importantes.**

**Próxima sesión:**
1. Leer este §4k y `analisis_criterios/LOGICA.md`.
2. Esperar las decisiones del dueño: variante de la metodología (TT/MS, X/|Z|), fuente oficial de X,
   confirmación del ×3, y #287/#288/Tap Pulelfu.
3. Con fichas verificadas por el dueño: aplicar la ronda 1 (Ventanas, luego Maule), recalcular y repetir las
   pruebas con `registro.py`.
4. Si se elige |Z|: validar la R de los tramos del listado.

**Acotaciones acordadas:**
- MM$/mes es absoluto (Σ |Δ precio| × MW). Contra PN2604, el código actual da +708 / −238 (neto +470); el método
  nuevo con datos corregidos, ~+280 / −372 (neto −75 a −112).
- "Más cerca / más lejos" solo cuenta las barras distintas a PN2604. En promedio total: PN2604 50 km, código actual
  63, método nuevo corregido ~53–54.
- El método nuevo hace al resultado más estable frente a la corrección de datos: +20–30 barras contra PN2604, en vez
  de +102 con el método actual. Igual hay que corregir.
- Casos raros (>100 km nuevos): 20, casi todos explicados (#287, #288, Tap Pulelfu, Mulchén, Fopaco, 500 kV,
  Juncal) → #305.
- Las correcciones parciales son peligrosas: se corrige cada zona completa. Kimal corregida completa mueve poco
  (34 MM$, 18 tramos); nunca corregir solo L.Changos–Kimal.

**Orden de revisión vigente** (listado_tramos.xlsx; #306):
1. Ventanas.
2. Maule–Itahue–Teno–Linares, con S.Fernando 154/66.
3. Santiago oriente (con Renca–Altamirano) y Mulchén. Alejan barras: revisar bien.
4. Aconcagua (Calera C. 62 con Tap S.Rafael–Totoralillo y S.Rafael 110/13), Melipilla–Isla de Maipo, Atacama,
   Dichas 220, Fopaco y Turibe–Esmeralda.
5. Kimal, completa.
6. El Laurel 220, Codegua 66 e independientes chicos.

En total son 57 críticos, 55 vecinos y 4 combinados (Mulchén).

### 4l. Verificación del listado (2026-11-19)

Scripts en `scripts/referido/`: `listado_verif.py`, `listado_pares.py`, `listado_final.py` y `listado_excel.py`.
Parten del listado anterior, guardado como `listado_v1.xlsx` en el directorio de trabajo. Todo se hizo en las 4
variantes.

- **Zonas redefinidas por interacción.**
  - Se probaron los 820 pares de unidades del listado (grupo previo, Mulchén o tramo suelto).
  - Dos unidades interactúan si corregirlas juntas no da lo mismo que corregirlas por separado. Umbral: 1 MM$/mes.
  - Fusiones resultantes:
    - S.Fernando 154/66 → Maule (hasta 21 MM$/mes con TT-R).
    - Renca–Altamirano → Santiago oriente (32 MM$/mes con R).
    - Tap S.Rafael–Totoralillo y S.Rafael 110/13 → Calera C. 62, que pasa a llamarse Aconcagua (11 MM$/mes cada
      uno).
  - El antiguo "Resto de los comunes" eran 3 grupos que no interactúan entre sí, más Turibe–Esmeralda suelto. Se
    separaron en Melipilla–Isla de Maipo, Atacama y Dichas 220.
- **Independencia entre zonas.** Cada zona da el mismo efecto corregida sola que dentro de la lista completa. Única
  excepción: Ventanas, que difiere en 6 barras y 0,3 MM$/mes.
- **Redundancia, no interacción.** Coronel–Tap Loma Colorada, Concepción 154/66, A. de Ribera 154/66 y Talcahuano
  154/66 mueven las mismas barras a la misma troncal. Cualquiera de ellos basta, y juntos no se contradicen.
- **La lista basta.** La lista completa difiere de corregir los 668 tramos en solo 5–14 barras y 2–4 MM$/mes.
- **Si se omite un tramo:** 49 de los 116 cambian el resultado final.
- **Rondas.** Después de la ronda 5 (92 tramos) falta solo un 1–3 % de la plata (4–10 MM$/mes).
  - Las rondas 1–2 acercan a PN2604: las barras distintas bajan de 245–262 a 218–225.
  - La ronda 3 (Santiago oriente y Mulchén) aleja: sube a 241–268. Al final quedan 276–285.
- **Imprescindibles: 48 tramos** (37 críticos, 8 vecinos y 3 de Mulchén). Columna en la hoja Revisión.
  - Con solo estos corregidos se obtiene el mismo resultado que con los 116, en las 4 variantes (0 barras
    distintas).
  - Ninguno se puede quitar sin cambiar el resultado (`nuc1.py` y una segunda pasada en `nuc2.py`, que sacó
    Cardones–Algarrobal y C.Calera1 62–Calera C. 62).
  - También funciona zona por zona y etapa por etapa (`nucleo_zonas2.py`). Única diferencia: Codegua 66, 1 barra y
    0,1 MM$/mes.
  - El conjunto no es único.
  - En Kimal son 6 de 19: L.Changos–Kimal, Crucero–Kimal, Kimal–Crucero Sal Aux, Kimal–Encuentro, Nueva
    Chuqui–Chuquicamata y Kimal 500/220.
  - En Mulchén son 3 de 4 (sobra Los Notros–Charrúa).
- **Grupos: un crítico solo puede dar un efecto falso.** "Crítico" solo dice que mueve alguna barra por sí solo.
  - Ejemplos: Maule 154/66 solo deja 21 barras en una troncal equivocada, y Linares 154/66 solo, 12 (con TT).
    Ambos necesitan a Itahue 154/66.
  - Los imprescindibles de cada zona se agrupan (`grupos_min2.py` y `grupos_min3.py`; se probaron todas las
    combinaciones en las 4 variantes) de modo que:
    - cada grupo corregido solo da exactamente su parte del resultado final, sin barras en troncal equivocada;
    - cualquier combinación de grupos da la suma de sus efectos.
  - Resultado (columnas Grupo, Se corrige junto con y Efecto):
    - Maule: 2 grupos (Teno 154/66 + Quinta–Teno 66; Maule + Linares + Itahue 154/66).
    - Aconcagua: 3 grupos.
    - Atacama: 2 grupos.
    - Santiago oriente, Mulchén, Melipilla, Kimal y El Laurel: 1 grupo cada una.
  - Efecto por tramo:
    - 16 con efecto propio;
    - 2 casi propio (Dichas 220/66 y L.Verde 110/66, que dejan 3 barras mal por menos de 1 MM$/mes);
    - 30 que necesitan a su grupo;
    - 68 que no cambian el resultado final.
- **Solo los críticos de cada zona** (`solo_criticos.py`):
  - Dan lo mismo que la zona completa en Ventanas, Maule, Santiago oriente, Dichas, El Laurel y Codegua.
  - Difieren poco en Aconcagua, Melipilla y Atacama (1–2 barras, 3–6 MM$/mes).
  - En Kimal difieren 11 barras y 167 MM$/mes.
  - En Mulchén ningún tramo es crítico.
- **"Zona completa" significa revisar todos los tramos de la zona con ficha antes de recalcular, no cambiarlos
  todos.** Se corrige lo que la ficha confirme como malo.
- **Etapas** (`etapas.py`; plata acumulada = % del cambio total ya hecho, en el orden de revisión, no Pareto):

  | Etapa | Qué | Tramos | Líneas / trafos | Imprescindibles (de 48) | MM$/mes | Plata acumulada | Distintas a PN2604 (hoy 245–262) |
  |---|---|---|---|---|---|---|---|
  | 1 | Ventanas | 2 | 1 / 1 | 1 | 87 | 21–26 % | 210–227 |
  | 2 | Maule | 13 | 6 / 7 | 5 | 6–62 | 24–37 % | 218–225 |
  | 3 | Santiago oriente y Mulchén | 12 | 8 / 4 | 7 | 175–180 | 70–83 % | 241–268 |
  | 4 | Aconcagua, Fopaco, Turibe, Melipilla, Atacama y Dichas | 46 | 24 / 22 | 16 | 24–80 | 87–91 % | 241–261 |
  | 5 | Kimal | 19 | 17 / 2 | 6 | 34 | 97–99 % | 258–278 |
  | 6 | El Laurel, Codegua e independientes chicos | 24 | 11 / 13 | 13 | 4–10 | 100 % | 276–285 |
- **Confianza del valor sugerido** (columna de la hoja Revisión):
  - Una fuente es válida si existe, su pareo de nombres es bueno (80 o más) y su valor no es casi nulo.
  - Alta: las dos fuentes son válidas y coinciden (hasta 20 %).
  - Media: difieren hasta 2 veces, o hay una sola fuente válida.
  - Baja: difieren más de 2 veces, o la sugerida usa una fuente no válida.
  - De los 48 imprescindibles: 19 alta, 19 media y 10 baja. 6 de los 10 de confianza baja están en la etapa 4.
  - Casos a mirar primero:
    - Fopaco: la X sugerida es 0, viene de Infotécnica con pareo dudoso (CNE da 3,59 Ω).
    - Sant Solar–Ppeuco, L.Vegas–Sant Solar, C.Calera1 110/62, Turibe–Esmeralda, A.Jahuel–Tap Sta Marta y
      L.Verde 110/66: la sugerida usa una fuente con pareo dudoso.
    - Teno 154/66, El Salto–San Cristóbal y S.Rafael 110/13: CNE e Infotécnica difieren más de 2 veces.
- **Correcciones al listado anterior:**
  - Mulchén decía "se puede corregir solo"; se corrige con los 4 juntos.
  - La columna MM$ "solo" quedó en Detalle, porque engaña: L.Changos–Kimal solo da 227 MM$/mes y Kimal
    completa, 34.
  - La hoja 16 de `resultados.xlsx` se reemplazó por las zonas definitivas.

## 5. Issues en `AlonsoFU/Balance-de-Potencia-Anual`

- **#287: numeración del ENT.**
  - Causa: Mejillones 13 kV se insertó en el N° 1394 y no se renumeraron las líneas Nº 1949–1988,
    que son 24 líneas con números tipeados en Q:R.
  - Efecto en la topología: el nodo 1394 queda fusionado (Mejillones 13 / Recinto 23) y el 1406
    queda aislado.
  - Evidencia: los extremos por número quedan a 200–1.533 km entre sí; por nombre, a 0–17 km.
  - 9 barras afectadas:
    - Sin resultado: GUARDIAMARINA_023, LIQCAU_110, RECINTO_013, RECINTO_033 y SENORAZA_066.
    - Con distancias malas: FUENTECILLA_066, GUARDIAMARINA_013, LIQCAU1_220 y SENORAZA_220.
  - PN2604 no está afectado. En los criterios hay 5 barras extra que pasan por el nodo 1394; los
    cambios colaterales reales son Ciruelitos 33 (C2) y Mejillones 13 (C1).
  - El golden `Minima Distancia Eléctrica_2026.csv` contiene este error.
  - **El dueño evalúa la corrección; no corregirla por cuenta propia.**
- **#288: proxy de Tap San Joaquín.** El proxy elige mal; San Andrés 154 queda como segundo
  candidato.
- **#305: casos raros** (troncal a >100 km) que quedan con la metodología referida: 20 barras, con su causa (#287, #288,
  Tap Pulelfu, Mulchén, Fopaco, 500 kV, Juncal).
- **#306: tramos críticos** del ENT con orden de mérito por zona: Kimal, Santiago oriente, Ventanas,
  Maule–Itahue–Teno–Linares, Mulchén, resto; más reglas de corrección.
- Regla del repo: los pendientes van como issues, Claude no cierra issues y los comentarios
  llevan el footer de Claude Code.

## 6. Pendientes / ofrecidos (sin confirmar por el dueño)

- [ ] Ranking por zona completa (no por tramo) y lista de fichas a revisar.
- [ ] Validar la R de los tramos decisivos (necesario si se usa |Z|).
- [ ] Regla para la red de 500 kV (caso L.Changos–Kimal).
- [ ] Decisiones del dueño: metodología, fuente oficial de X, confirmar ×3 con quien mantiene el
  ENT, #287/#288/Tap Pulelfu.

- [ ] Registrar como issue de datos el empate de Illapa por tramos idénticos.
- [ ] Hoja de revisión manual de los cambios críticos agrupados.
- [ ] Probar un tercer criterio: anular solo los trafos de barras de la **misma subestación**
  que la troncal.
- [ ] Agregar a la minuta una sección que compare las alternativas C1/C2.
- [ ] Corregir #287 (el dueño decide).
- [ ] Probar un desempate geográfico cuando la diferencia eléctrica sea < 2 %. Resolvería Los Andes,
  Juncal y Concepción.
- [ ] Comparación completa de las X de trafos ENT vs CNE/Infotécnica en todo el sistema.
- [ ] Confirmar si las filas Tx (PSUF) se valorizan a precio de nudo. Si se valorizan, el monto
  sube de ~488 a ~2.370 MM$/mes.
- [ ] Posibles issues de datos:
  - Subsistema de Tap Pulelfu (S1 → S2).
  - X de los trafos de Itahue, Linares y Los Maquis.
- [ ] Incorporar «Referido» a la minuta como alternativa metodológica. Ya hay un texto propuesto en
  la conversación: el modelo DC más las reactancias referidas a una tensión común.

## 7. Notas operativas

- Los scripts de `analisis_criterios/scripts/` tienen rutas absolutas:
  - `/home/user/balance-de-potencia-anual/...` para el clon del repo Balance.
  - Un scratchpad con `up/bal.xlsm` para el Balance_2609_def.
  - Al retomar, ajustar las constantes `INP`, `U`, `OUT` y `S`.
- `criterios_ev.pkl` tiene columnas agregadas por pasos interactivos que no están todas en
  `criterios.py`: impacto, origen y flags 287. Para no recalcular, usarlo directo o la hoja
  Barras del xlsx.
- El impacto económico es indicativo: |Δprecio PN2604 $/kW/mes| × MW abs de la hoja 05
  ('Cons + Perd') × 1000.
- No abrir PR salvo que se pida. El push va a `claude/relaxed-ptolemy-70ek36`.
