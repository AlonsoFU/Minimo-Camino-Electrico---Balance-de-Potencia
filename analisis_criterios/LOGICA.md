# Mínimo camino eléctrico: lógica y plan

Resultados en `datos/resultados.xlsx`.

## Problema
- La norma (2.2 de los decretos) pide la subestación a "mínima distancia eléctrica". No dice cómo
  se calcula.
- Hoy se suman Ω de distintas tensiones sin referir, y los caminos rodean los trafos (La Palma →
  Candelaria).

## Metodología propuesta
- Referir todo a 220 kV.
- Medir hasta la subestación: se anula el trafo que toca la barra troncal.
- Usar X; R solo para desempatar.
- Resultado: coincidencia con PN2604 de 1.020 a 1.180; barras a más de 100 km de su troncal, de 174
  a 86.

## Datos del ENT
- 668 tramos difieren de la CNE o de Infotécnica.
- 66 trafos dan el triple que las fuentes (confirmado con fichas en 4); falta que lo confirme quien
  mantiene el ENT.
- Corregir los datos cambia ~180–230 barras. El orden entre criterios no cambia.

## Efecto geográfico de corregir los datos
- Con el método de hoy, corregir los datos aleja barras de su troncal: se acercan 56 y se alejan 146.
- Con el método propuesto, las acerca: se acercan 122 y se alejan 44.
- Ejemplos: Teno, Rauquén y Aguas Claras pasan de Candelaria (~110 km) a Itahue (~35 km).

## Qué revisar primero
- Solo 44 tramos cambian el resultado; los otros 624 no.
- Los 10 primeros cubren el 91 % del impacto.

## Efectos en cadena
- Corregir dos tramos juntos puede dar distinto que corregirlos por separado.
- Ocurre solo entre tramos de la misma zona.
- Regla: siempre recalcular con todo lo ya corregido.

## Plan en rondas
1. Ordenar los tramos por impacto.
2. Agruparlos por zona.
3. Revisar con la ficha.
4. Registrar la corrección.
5. Recalcular.
6. Repetir hasta que una ronda mueva menos del 1 % de la plata.
7. Aplicar el resto por regla y recalcular una última vez.

## Decisiones tuyas
- Criterio.
- Fuente oficial para X.
- Confirmar el ×3.
- #287, #288 y Tap Pulelfu.
