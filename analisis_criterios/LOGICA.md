# Mínimo camino eléctrico: resumen

Estado al 2026-11-20. El detalle está en `docs/HANDOFF.md` §4k–§4l.

## 1. El problema

- La norma (numeral 2.2 de los decretos de precio de nudo) pide asociar cada barra a la subestación a "mínima
  distancia eléctrica", sin decir cómo se calcula.
- Hoy se suman Ω de distintas tensiones sin referir, y los caminos rodean los trafos.
- El código actual ya difiere de la asignación vigente (PN2604) en 422 barras, casi siempre hacia troncales más
  lejanas.
- Además, 668 tramos del ENT tienen una X distinta a la de CNE o Infotécnica.

## 2. Tabla clave: métodos contra PN2604

| Método (datos actuales → corregidos) | Barras distintas a PN2604 | Barras que cambian al corregir los datos (mismo método) | MM$/mes | Más cerca / más lejos que PN2604 | Barras a >100 km |
|---|---|---|---|---|---|
| PN2604 (vigente) | 0 | — | 0 | — | 83 |
| Actual, sin referir | 422 → 524 | 216 | 946 → 1.257 | 56/318 → 62/408 | 174 → 169 |
| Referido, X | 341 → 399 | 168 | 662 → 839 | 98/202 → 105/232 | 96 → 95 |
| Referido, R | 341 → 379 | 183 | 612 → 932 | 100/200 → 103/214 | 93 → 98 |
| **Referido + subestación troncal, X** | 248–262 → 277–279 | 183 | 488–554 → 632–633 | 59–67/140–146 → 104–106/112 | 80–86 → 83 |
| Referido + subestación troncal, R | 245–257 → 275–279 | 167 | 508–555 → 670–672 | 85–93/132–136 → 104–108/108 | 82–86 → 84 |

- Rango de "subestación troncal": de anular solo el trafo que toca la barra troncal a anular toda la subestación.
- MM$/mes = Σ |Δ precio| × MW de inyección y retiro de las barras distintas a PN2604.
- "Más cerca / más lejos" se cuenta solo entre las barras distintas a PN2604.

**Qué decir:**
- Referir y unir la subestación troncal es lo que más acerca el resultado a lo vigente: unas 250 barras distintas,
  contra 422 del código actual.
- Con el método actual, corregir los datos aleja el resultado de PN2604 (+102 barras). Con el método nuevo, apenas
  lo mueve (+20 a 30): el método nuevo es más estable frente a los datos.
- X o R da casi lo mismo. Con R hay que confirmar un dato más por tramo, y es menos confiable: la R de CNE e
  Infotécnica coincide en solo 18 de los 48 imprescindibles.
- PN2604 se calculó con datos viejos, así que perder algo de coincidencia al corregir es esperable.

## 3. Tabla clave: qué mueve corregir cada zona

Método nuevo, antes contra después de corregir. Rango de las 4 variantes. Las filas que juntan varias zonas suman
sus efectos (las zonas son independientes entre sí).

| Etapa | Zona | Tramos | Barras que cambian | Más cerca | Más lejos | MM$/mes | Lectura |
|---|---|---|---|---|---|---|---|
| 1 | Ventanas | 2 | 37 | 33 | 1 | 87 | Acerca |
| 2 | Maule–Itahue–Teno–Linares | 13 | 8–10 | 8–10 | 0 | 6–62 | Acerca mucho |
| 3 | Santiago oriente | 8 | 19–43 | 0–1 | 19–24 | 139–144 | Aleja: revisar bien |
| 3 | Mulchén | 4 | 4 | 0 | 4 | 36 | Aleja; solo con los 4 juntos |
| 4 | Aconcagua (Calera–S.Rafael) | 20 | 14 | 3–13 | 1–9 | 6–22 | Con X aleja, con R acerca |
| 4 | Melipilla, Atacama, Dichas 220, Fopaco y Turibe | 26 | 20–22 | 13–20 | 0–3 | 19–57 | Acerca; con R pesa Fopaco (aleja 3 barras) |
| 5 | Kimal | 19 | 17 | 1 | 2 | 34 | Casi neutro |
| 6 | El Laurel, Codegua e independientes chicos | 24 | 20–65 | 7–44 | 5–8 | 5–11 | Poca plata |
| | **Lista completa** | 116 | 162–187 | 79–114 | 39–42 | 342–422 | Acerca |

## 4. Qué corregir del ENT

- **De 668 a 48.** De los 668 tramos que difieren, 116 mueven alguna barra. De esos, 48 son imprescindibles:
  corregir solo esos da el mismo resultado que corregir los 116, y ninguno sobra.
- **27 grupos.** Un tramo corregido fuera de su grupo puede dar un efecto falso (Maule 154/66 solo deja 21 barras
  en una troncal equivocada). Cada grupo corregido completo da su efecto real, en cualquier orden.
- **Plata por etapa:** después de las etapas 1–3 (13 imprescindibles) ya está el 70–83 % de la plata; después de
  la 5, el 97–99 %.
- **Confianza del valor sugerido:** de los 48, 19 alta, 19 media y 10 baja.
- **No corregir solo los de confianza alta:** deja grupos a medias y sesga el resultado hacia alejar, porque lo que
  acerca suele tener confianza media o baja.

## 5. Recomendación

1. Método: referido + subestación troncal, **con X**. R da casi lo mismo y pide el doble de datos dudosos.
2. Fichas para los 48 imprescindibles, empezando por lo que más pesa y lo menos seguro: Ventanas, Santiago
   oriente, Maule, Mulchén (aleja) y Kimal.
3. Aplicar solo grupos completos con ficha. Si la ficha confirma el valor del ENT, ese tramo no se cambia.
4. Recalcular después de cada etapa. Los 68 restantes y los 552 que no mueven nada se corrigen por regla al final.

## 6. Pendientes

- **Decisiones del dueño:**
  - variante (trafo troncal o toda la subestación; X o R);
  - fuente oficial de X;
  - confirmar el patrón ×3 de los trafos;
  - casos #287, #288 y Tap Pulelfu.
- **Minuta por completar** (`docs/Minuta_Minimo_Camino_Electrico.docx`): agregar la metodología propuesta, la
  revisión de datos y la recomendación sobre X o R (#308).
- **PowerFactory como fuente de datos** en vez del ENT (#307).
- **Tramos a revisar por etapa** (#306) y **casos raros** (#305).

## 7. Archivos

- `datos/listado_tramos.xlsx`: el listado para revisar (Etapas, Grupos, Tramos y Resto). El detalle está en
  `listado_tramos_respaldo.xlsx`.
- `datos/resultados.xlsx`: hoja 13 (métodos contra PN2604), hoja 14 (plata y distancia) y hoja 16 (zonas).
- `datos/registro_pruebas.sqlite.gz`: las pruebas auditables.
- `presentacion/`: la presentación de 10 láminas.
