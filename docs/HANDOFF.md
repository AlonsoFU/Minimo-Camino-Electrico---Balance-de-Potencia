# HANDOFF — Minuta y análisis del mínimo camino eléctrico

Rama: `claude/relaxed-ptolemy-70ek36`. Última actualización: 2026-10-27.

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

## 2. Entregables en `docs/`

| Archivo | Qué es |
|---|---|
| `Minuta_Minimo_Camino_Electrico.docx` | Minuta CEN (6 págs.) con el estilo de `Minuta_Enlight.docx` |
| `figuras/fig1..fig3*.png` | Figuras de la minuta: concepto, caso La Palma y comparación |
| `figuras/mapa_*.png` | Mapas de 3 paneles (hoy / C1 / C2) para el análisis de criterios |
| `diferencias_modulo_vs_PN2604.csv` | Barras donde el módulo ≠ PN2604 |
| `diferencias_PN2604_por_escenario.csv` | Qué escenario de trafos explica cada diferencia |
| `analisis_criterios_transformadores_PN2604.xlsx` | Análisis de criterios con hojas Resumen, Cambios críticos, Grupos C1/C2, Barras (flags #287/#288) y Origen |
| `scripts/minuta/` | Construcción del docx y de las figuras 1–3 |
| `scripts/analisis/` | Escenarios, flag #287 y mapas; `criterios_ev.pkl` es el resultado (1.445 barras × 46 cols) |

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
es `scripts/analisis/criterios.py`.

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

### 4b. Criterios nuevos (2026-10-27, `scripts/analisis/criterios_v2/`, `criterios_v2_por_barra.csv`)

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
- Regla del repo: los pendientes van como issues, Claude no cierra issues y los comentarios
  llevan el footer de Claude Code.

## 6. Pendientes / ofrecidos (sin confirmar por el dueño)

- [ ] Registrar como issue de datos el empate de Illapa por tramos idénticos.
- [ ] Hoja de revisión manual de los cambios críticos agrupados.
- [ ] Probar un tercer criterio: anular solo los trafos de barras de la **misma subestación**
  que la troncal.
- [ ] Agregar a la minuta una sección que compare las alternativas C1/C2.
- [ ] Corregir #287 (el dueño decide).

## 7. Notas operativas

- Los scripts de `scripts/analisis/` tienen rutas absolutas:
  - `/home/user/balance-de-potencia-anual/...` para el clon del repo Balance.
  - Un scratchpad con `up/bal.xlsm` para el Balance_2609_def.
  - Al retomar, ajustar las constantes `INP`, `U`, `OUT` y `S`.
- `criterios_ev.pkl` tiene columnas agregadas por pasos interactivos que no están todas en
  `criterios.py`: impacto, origen y flags 287. Para no recalcular, usarlo directo o la hoja
  Barras del xlsx.
- El impacto económico es indicativo: |Δprecio PN2604 $/kW/mes| × MW abs de la hoja 05
  ('Cons + Perd') × 1000.
- No abrir PR salvo que se pida. El push va a `claude/relaxed-ptolemy-70ek36`.
