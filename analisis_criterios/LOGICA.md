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

## Calidad del cambio por tramo
- Por tramo no solo se mide cuánto cambia, también si el cambio tiene sentido: si la barra queda
  más cerca o más lejos de su troncal, y si gana o pierde coincidencia con PN2604.
- De los 44 tramos decisivos: 21 mejoran, 13 empeoran, 6 son mixtos y 4 no se pueden evaluar.
- Los que empeoran concentran la mayor parte de la plata (L.Changos–Kimal, L.Almendros): se
  revisan primero y con más cuidado.
- A veces la geografía y PN2604 no coinciden (Maule, A.Melipilla–Dichas): ahí decide la ficha.

## Qué revisar primero
- Solo 44 tramos cambian el resultado; los otros 624 no.
- Los 10 primeros cubren el 91 % del impacto.

## Efectos en cadena
- Corregir dos tramos juntos puede dar distinto que corregirlos por separado.
- Ocurre solo entre tramos de la misma zona.
- Regla: siempre recalcular con todo lo ya corregido.

## Combinaciones (prueba por grupos)
- Se probaron los 624 tramos no decisivos agrupados por zona, partiendo cada grupo que cambiaba
  algo hasta aislar la combinación responsable (~390 recálculos).
- Se encontraron 6 combinaciones de 2–3 tramos que solo cambian algo juntas: 15 barras, ~41 MM$/mes.
- Solo una pesa: Los Notros–Mulchén–Santa Clara–Charrúa (36 MM$/mes), que lleva Mulchén, Los Olmos y
  Picoltué a Cautín (más lejos).

## Consideraciones estándar (aplican siempre)
- **Referir:** toda reactancia (y R, si se usa) se lleva a 220 kV con (220/V)²; V es la columna V del
  ENT, que en los trafos es el lado de alta.
- **X o |Z|:**
  - |Z| es lo más completo físicamente.
  - Con R cambian ~100 barras casi empatadas (diferencias menores al 5 %); la R decide esos empates.
  - El resultado depende de cómo se suma la R en serie: 1.197 contra 1.171 coincidencias con PN2604.
  - La R difiere de las fuentes en el 53 % de los tramos, contra ~41 % en la X. Si se usa |Z|, hay
    que validar la R igual que la X.
- **Paralelos:** se combinan como 1/Z = Σ 1/Zi, y se corrigen en bloque. Corregir un solo circuito
  subestima el efecto (L.Changos–Kimal).
- **Trafos anulados:** los que el criterio deja en 0 no se revisan; su dato no importa.
- **Probar todos, revisar solo los decisivos** (los que cambian alguna troncal). Es una foto del
  estado actual: tras cada ronda se vuelve a probar todo.
- **Nunca sumar efectos individuales:** el resultado depende del conjunto de correcciones, no del
  orden. Siempre se recalcula con todo lo aplicado.
- **Si el cambio tiene sentido:** queda más cerca o más lejos de su troncal (±5 km) y gana o pierde
  coincidencia con PN2604. Si las dos señales se contradicen, decide la ficha.
- **Las fuentes también fallan:** hay pareos malos en la homologación y fichas imposibles. Que las
  fuentes coincidan no basta si el cambio empeora la asignación (L.Changos–Kimal).
- **Red de 500 kV:** al referir se acorta ×0,19 y puede atraer barras lejanas; se revisa como caso
  borde.
- **Combinaciones:** se buscan por grupos, no probando todos los pares. Las zonas son tramos ordenados
  de norte a sur en grupos de 40; al final se prueba todo junto, para captar combinaciones entre zonas.
- **Robustez de la búsqueda:** se repitió con 4 agrupaciones (latitud, troncal más cercana y dos al azar).
  Coinciden en las combinaciones chicas; solo difieren en la zona de Mulchén. Ahí se probaron todas las
  combinaciones de hasta 4 de sus 10 tramos:
  - corrigiendo 3 tramos sin Los Notros–Mulchén: 12 barras, 270 MM$/mes;
  - corrigiendo la zona completa: 4 barras, 36 MM$/mes.

  Regla: donde aparece una combinación, probar exhaustivamente esa zona y corregirla completa, nunca a
  medias.
- **Prueba exhaustiva en las 6 zonas con combinaciones** (entorno de 2 saltos, ~10.700 recálculos):
  - Las Vegas, Calera, Chiloé y Puerto Varas: efecto chico (≤6 MM$/mes), corregidas completas o por partes.
  - Kimal: corregir solo L.Changos–Kimal mueve 227 MM$/mes; corregir la zona completa, 34.
  - Mulchén: corregir 3 tramos mueve 270 MM$/mes; la zona completa, 36.

  Esto confirma la regla de corregir cada zona completa.
- Se revisan líneas y trafos por igual.

Figuras: `figuras/datos/busqueda_combinaciones.png` (cómo se buscan las combinaciones) y
`figuras/datos/caso_lchangos_kimal.png` (un tramo que mueve mucho).

## Zonas
- Zona: un tramo decisivo o de combinación, más los tramos que difieren a ≤2 conexiones; las que
  comparten tramos se juntan.
- Resultado: 16 zonas, 244 tramos (44 decisivos y 200 vecinos). Solo ~15 vecinos tienen
  interacción probada.
- Probado decisivo + vecinos en las 16 zonas (13.170 recálculos): los vecinos solo pesan en la zona
  central (+36 MM$/mes) y en Kimal (anulan 166 MM$/mes); en el resto basta con los decisivos.

## Plan en rondas
1. Ordenar los tramos por impacto.
2. Agruparlos por zona.
3. Revisar con la ficha.
4. Registrar la corrección.
5. Recalcular.
6. Repetir hasta que una ronda mueva menos del 1 % de la plata.
7. Aplicar el resto por regla y recalcular una última vez.

## Decisiones tuyas
- Metodología (pendiente).
- Fuente oficial para X.
- Confirmar el ×3.
- #287, #288 y Tap Pulelfu.
