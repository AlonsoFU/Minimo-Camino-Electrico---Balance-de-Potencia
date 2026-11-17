# Mínimo camino eléctrico: resumen

Resultados en `datos/resultados.xlsx`; el detalle está en `docs/HANDOFF.md` §4j.

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
- Vecinos: solo pesan en la zona central y en Kimal; ahí se revisa la zona completa.

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
