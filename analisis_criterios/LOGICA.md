# Mínimo camino eléctrico: resumen

Resultados en `datos/resultados.xlsx`; el detalle está en `docs/HANDOFF.md` §4j.

## Comparación contra lo vigente (PN2604)

La base es PN2604, la asignación vigente. El "módulo actual" es solo lo que calcula hoy el código.

| Método (datos actuales → corregidos) | Barras distintas a PN2604 | Barras que cambian al corregir los datos (mismo método, antes y después) | MM$/mes | Más cerca / más lejos que PN2604 | Barras a >100 km |
|---|---|---|---|---|---|
| PN2604 (vigente) | 0 | — | 0 | — | 83 |
| Actual, sin referir (módulo) | 422 → 524 | 216 | 946 → 1.257 | 56/318 → 62/408 | 174 → 169 |
| Referido, X | 341 → 399 | 168 | 662 → 839 | 98/202 → 105/232 | 96 → 95 |
| Referido, R | 341 → 379 | 183 | 612 → 932 | 100/200 → 103/214 | 93 → 98 |
| Referido + subestación troncal, X | 248–262 → 277–279 | 183 | 488–554 → 632–633 | 59–67/140–146 → 104–106/112 | 80–86 → 83 |
| Referido + subestación troncal, R | 245–257 → 275–279 | 167 | 508–555 → 670–672 | 85–93/132–136 → 104–108/108 | 82–86 → 84 |

Rangos de "subestación troncal": de anular solo el trafo que toca la barra troncal a unir toda la subestación.
Datos corregidos: los 668 tramos al valor sugerido de la validación. Hoja 13 de `datos/resultados.xlsx`.

**Qué decir al presentarla**
- El código actual ya difiere de PN2604 en 422 barras, y casi siempre hacia troncales más lejanas (318).
- Unir la subestación troncal es lo que más acerca el resultado a lo vigente: ~250 barras distintas.
- Corregir los datos con el método actual empeora: la diferencia con PN2604 pasa de 422 a 524 barras.
- Con el método nuevo, corregir los datos cambia ~170–180 barras de su propio resultado, pero la
  diferencia con PN2604 solo sube ~20–30: unas 70 barras pasan a coincidir con PN2604 y unas 95 dejan de
  coincidir.
- **Conclusión:** el método nuevo hace al resultado más estable frente a la corrección de datos. Igual hay
  que corregirlos.
- X o R da casi lo mismo dentro de cada variante.
- PN2604 se calculó con los datos viejos, así que perder algo de coincidencia al corregir es esperable.
- **MM$/mes** = Σ |Δ precio| × MW de inyección más retiro, sobre las barras distintas a PN2604. Se separa en lo que sube y lo que
  baja (hoja 14). El código actual sube +708 / −238 (neto +470); el método nuevo con datos corregidos, ~+280 / −372
  (neto −75 a −112).
- **Distancia:** "más lejos que PN2604" se cuenta solo entre las barras distintas. En el total de barras, la distancia
  promedio a la troncal es 50 km con PN2604, 63 con el código actual y ~53–54 con el método nuevo con datos corregidos.

## Problema
- La norma (2.2 de los decretos) pide la subestación a "mínima distancia eléctrica", sin decir cómo
  se calcula.
- Hoy se suman Ω de distintas tensiones sin referir, y los caminos rodean los trafos.

## Metodología (pendiente)
- Base común: referir a 220 kV y medir hasta la subestación.
- Falta decidir:
  - si se anula solo el trafo que toca la barra troncal o todos los de la subestación;
  - si se usa X o |Z|.
- Con R cambian ~100 casi empates, y la R difiere de las fuentes en el 53 % de los tramos.

## Datos del ENT
- 668 tramos difieren de la CNE o de Infotécnica.
- 66 trafos dan el triple que las fuentes; falta que lo confirme quien mantiene el ENT.
- Corregir los datos cambia ~180–230 barras. Con el método propuesto, la mayoría quedan más cerca de
  su troncal.

## Qué revisar
- Solo 44 tramos cambian el resultado; los 10 primeros cubren el 91 % del impacto.
- Por tramo se mira si el cambio tiene sentido: si la barra queda más cerca o más lejos de su
  troncal, y si gana o pierde coincidencia con PN2604.
- Vecinos: además de los decisivos hay que revisar los vecinos que interactúan con ellos (más de 1 MM$/mes).
  Total a revisar: 76–98 tramos según el criterio (`datos/registro_pruebas.sqlite.gz`).

## Por qué solo 44 afectan (demostración)
- **Prueba directa sobre todos:** los 668 tramos se corrigieron uno a uno y se recalculó la troncal de las
  1.442 barras. 624 no cambian ninguna barra; 44 sí (`cadena.py`, hoja 3).
- **Mecanismo:** una barra cambia solo si la corrección altera el orden entre su troncal y la siguiente.
  - 13 de los 44 están en la parte del camino que diferencia a la troncal ganadora de la segunda, y su
    corrección supera ese margen.
  - 22 abren un camino nuevo más corto al bajar su X.
  - 9 desvían el camino al subir su X.

  El resto está en tramos comunes a ambos caminos, fuera de los caminos, o su corrección es menor que el
  margen (`embudo.py`).
- **Combinaciones:** al juntar tramos solo se agregan vecinos en la zona central y en Kimal.
- **Límite:** vale para los datos y el método actuales; tras cada ronda se vuelve a probar.
- **Afectar no es estar malo:** que un tramo difiera sale de la validación; que esté malo se demuestra
  con la ficha.

## Reglas
- Corregir circuitos en paralelo juntos y zonas completas, nunca a medias.
- Siempre recalcular con todo lo corregido; no sumar efectos individuales.
- Si una corrección aleja barras, revisar la ficha antes de aplicarla, aunque las fuentes coincidan
  (L.Changos–Kimal).
- No revisar los trafos que el criterio anula.

## Plan en rondas
1. Ordenar por impacto.
2. Revisar con ficha (decisivos, más la zona completa en central y Kimal).
3. Registrar la corrección.
4. Recalcular.
5. Repetir hasta que una ronda mueva menos del 1 % de la plata.
6. Aplicar el resto por regla y recalcular.

## Decisiones tuyas
- Metodología.
- Fuente oficial para X.
- Confirmar el ×3.
- #287, #288 y Tap Pulelfu.
