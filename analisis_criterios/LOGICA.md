# Mínimo camino eléctrico: lógica del análisis y plan de actualización

Resumen de lo razonado hasta el 2026-11-13. Cada número tiene su fuente en la última columna o al
final; el detalle está en `docs/HANDOFF.md` §4–§4i.

## 1. Problema

| | |
|---|---|
| Qué pide la norma | Numeral 2.2 de los decretos de precio de nudo: la subestación del Sistema de Transmisión Nacional a "mínima distancia eléctrica" del punto de inyección, determinada por el Coordinador. No define X, Z ni niveles de tensión. |
| Qué hace hoy el módulo | Dijkstra sobre la X del ENT, sumando Ω de distintas tensiones sin referir, hasta la barra troncal de 220 kV. |
| Por qué falla | Una línea de 66 kV pesa ~11 veces menos de lo que debe y los trafos parecen enormes. Por eso el camino rodea los trafos (caso La Palma → Candelaria). |

## 2. Metodología propuesta

| Decisión | Elección | Por qué | Alternativas descartadas |
|---|---|---|---|
| Unidad común | **Referir**: X × (220/V)² | Es lo que hace coherente una "distancia eléctrica", igual que por unidad o un flujo DC | Sumar Ω sin referir (hoy; C1 y C2) |
| Hasta dónde se mide | **Hasta la subestación, anulando el trafo que toca la barra troncal** | El 2.2 habla de "subestación". No depende de pareos por nombre | Estricta (solo la barra de 220 kV): 255 barras distintas. Amplia (todos los niveles): 14 barras distintas de la intermedia |
| Magnitud | **X**, con R solo para desempatar diferencias menores al 2 % | Es la convención del flujo DC y es estable | \|Z\|: casi no cambia en Referido (6 barras); con subestación solo da vuelta casi empates (~100 barras) |

Resultado con los datos actuales (1.442 barras):

| Criterio | = PN2604 | Cambian vs hoy | Barra a >100 km de su troncal | MM$/mes movidos |
|---|---|---|---|---|
| Hoy | 1.020 | — | 174 | — |
| **Referido + trafo troncal** | **1.180** | 362 | 86 | 878 |

PN2604 es una referencia, no la verdad.

Fuentes: `datos/comparacion_criterios.xlsx` (script `scripts/referido/comparacion_final.py`).

## 3. Diagnóstico de los datos del ENT

- **Referencia:** tu validación previa ENT ↔ CNE ↔ Infotécnica (`revision/output/homologacion_clasificada.xlsx`,
  con regla del 15 %).
- **Cuánto discrepa:** 668 bloques (circuitos en paralelo agrupados) difieren de las fuentes.
- **Patrón ×3 en 66 trafos:** el ENT da el triple que las fuentes.
  - Verificado con fichas de Infotécnica en 4 casos: L.Almendros, Maule, Charrúa y Concepción.
  - Equivale a usar un tercio de la potencia. No depende del tipo de trafo.
  - **Falta que quien mantiene el ENT lo confirme.**
- **Los demás factores no tienen una causa común:**
  - ×2 y ×½: solo 17 de 68 son unidades en paralelo.
  - ×4: no se explica por referir.
  - 264 trafos y 294 líneas difieren sin un factor fijo.
- **Las fuentes también tienen errores:** pareos malos en la homologación y fichas con datos
  imposibles (por ejemplo, Ochagavía con 336 MVA en un trafo de 13,3 MVA).
- **Indicios, no confirmados:**
  - #287 (numeración del ENT) y #288 (reemplazo de Tap San Joaquín).
  - Tap Pulelfu en S1, cuando sus vecinas están en S2.
  - 4 trafos con X = 0,000378 Ω.

Scripts: `datos_x.py`, `datos_ceros.py`, `x3_conteo.py`.

## 4. Cuánto pesan los datos

- **Corregir todos los datos** cambia 181–231 barras, de las que 84–109 tienen inyección o retiro.
  Es del mismo orden que el cambio de criterio.
- **El orden entre criterios no cambia** con ningún juego de datos, así que el criterio se puede
  decidir ya.
- **Los criterios referidos son más robustos a errores de datos** que el método de hoy.

Script: `datos_x.py`.

## 5. Qué revisar primero

**Prioridad = impacto × probabilidad de error:**
- **Impacto:** barras y MM$/mes que cambian si se corrige el tramo, corrigiendo los circuitos en
  paralelo juntos.
- **Probabilidad:**
  - alta: CNE e Infotécnica coinciden entre sí y el ENT no;
  - media: las fuentes no coinciden entre sí, o hay una sola fuente;
  - baja: el dato coincide con las fuentes.

**Resultado:**

| Grupo | Bloques | Qué hacer |
|---|---|---|
| Discrepan pero no cambian nada solos | 624 | No se revisan uno por uno |
| Decisivos | 44 (38 con plata) | Revisión con ficha, en orden de impacto |
| Top 5 | | 79 % del impacto |
| Top 10 | | 91 % del impacto |

Script: `cadena.py`.

## 6. Efectos en cadena

| Medición | Barras | MM$/mes |
|---|---|---|
| 44 decisivos de a uno (unión) | 243 | — |
| 44 decisivos juntos | 193 | 541 |
| Los 668 juntos | 183 | 395 |

- **9 barras** cambian solo al combinar correcciones, y **59** cambian solas pero vuelven al
  combinar.
- **Ejemplos:** Crucero–Kimal pasa de 16 a 26 barras después de L.Changos–Kimal; Itahue, de 4 a 25
  después de Teno y Maule.
- **Las interacciones son locales:** Kimal, Maule–Itahue–Teno–Linares, Dichas y Santiago oriente.
- **Regla:** el resultado depende solo del **conjunto** de correcciones, no del orden. Nunca se suman
  efectos individuales; siempre se recalcula con todo lo aplicado.
- **Secuencia simulada:** 6 pasos alcanzan el 96 % del impacto final.

Fuente: `datos/secuencia_correcciones.xlsx`.

## 7. Plan de actualización (en rondas)

| # | Paso | Entrada | Regla | Salida |
|---|---|---|---|---|
| 1 | Ranking | Estado actual (ENT + correcciones ya aplicadas) | Impacto × probabilidad, por bloque | Lista ordenada |
| 2 | Agrupar por zona | Lista | Juntar los tramos que afectan las mismas barras o la misma zona | Zonas de la ronda |
| 3 | Revisar | Zonas de mayor impacto | Ficha de Infotécnica, más plausibilidad (Z entre 4 y 15 %, MVA coherente) y, si persiste la duda, consulta al propietario | Valor verificado |
| 4 | Registrar | Valor verificado | Tabla de correcciones: tramo, X anterior, X nueva, fuente, fecha, responsable y motivo. El ENT no se edita a mano | Correcciones |
| 5 | Recalcular | Estado + correcciones | Asignación completa con todo lo aplicado | Nuevo estado y delta (barras, MM$) |
| 6 | ¿Seguir? | Delta de la ronda | Parar si la ronda mueve menos del 1 % de la plata | Siguiente ronda o cierre |
| 7 | Cerrar | Bloques no revisados | Aplicar por regla solo donde CNE ≈ Infotécnica, y recalcular. Lo que cambie se revisa | Asignación final |

**Para cada proceso siguiente**, el mismo ciclo, más:
- bajar Infotécnica y la CNE;
- homologar solo lo nuevo o cambiado;
- correr controles automáticos: X ≈ 0, Ω/km fuera de rango, Z % implícita fuera de 4–15 %, columna V
  incoherente, barras aisladas, subsistema distinto al de las vecinas y diferencia contra
  Infotécnica sobre el umbral.

## 8. Decisiones pendientes del dueño

1. Adoptar «Referido + trafo troncal» con X (o \|Z\|).
2. Fuente oficial para X: se propone Infotécnica.
3. Confirmar el patrón ×3 con quien mantiene el ENT.
4. Decidir sobre #287, #288 y Tap Pulelfu.
5. El umbral de corte de las rondas (se propone 1 % de la plata).
