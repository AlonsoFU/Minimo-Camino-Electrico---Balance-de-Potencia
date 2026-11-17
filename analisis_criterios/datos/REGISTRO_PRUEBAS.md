# Registro de pruebas (`registro_pruebas.sqlite.gz`)

Cada recálculo hecho para decidir qué datos del ENT revisar queda registrado: 52.446 pruebas en 4
criterios. Para usarlo: `gunzip -k registro_pruebas.sqlite.gz` y abrirlo con cualquier lector
SQLite (DB Browser, DBeaver, Python, Excel vía ODBC).

Lo genera `scripts/referido/registro.py <tt_x|tt_z|sub_x|sub_z>`; el análisis posterior está en
`post_registro.py`.

## Tablas

| Tabla | Qué tiene |
|---|---|
| `pruebas` | Una fila por prueba: criterio, etapa, detalle (qué agrupación, zona o paso), tramos corregidos, barras que cambian, MM$/mes, si se tomó de caché, segundos y fecha |
| `cambios` | Una fila por barra que cambió en una prueba: troncal base, troncal nueva y MW de inyección más retiro |
| `etapas` | Estado, inicio, fin y resumen JSON de cada etapa por criterio |
| `resumen` | Totales por criterio y la lista a revisar |
| `lista_a_revisar` | Tramos a revisar por criterio: decisivos, más los vecinos con interacción mayor a 1 MM$/mes |

## Etapas

1. **Individual:** cada tramo que difiere se corrige solo, con el valor sugerido de la validación
   (`revision/output/homologacion_clasificada.xlsx`).
2. **Conjuntos:** los decisivos juntos y todos juntos.
3. **Grupos:** combinaciones de no decisivos, con 4 agrupaciones (latitud, troncal más cercana y dos
   al azar). Cada grupo que cambia algo se parte hasta aislar la combinación mínima (ddmin).
4. **Zonas:** decisivo más sus vecinos que difieren (a 2 conexiones).
   - Zonas de 20 tramos o menos: todas las combinaciones de 2 a 4 tramos con al menos un decisivo.
   - Zonas más grandes: todos los pares decisivo más vecino, y luego ddmin.

## Consultas de ejemplo

```sql
-- cuántas pruebas por criterio y etapa
SELECT criterio, etapa, COUNT(*) FROM pruebas GROUP BY 1, 2;
-- qué pasa al corregir un tramo
SELECT * FROM pruebas WHERE tramos = 'L.CHANGOS_____500->KIMAL_________500';
-- qué barras cambian en esa prueba
SELECT c.* FROM cambios c JOIN pruebas p ON p.id = c.prueba_id
 WHERE p.tramos = 'L.CHANGOS_____500->KIMAL_________500' AND p.desde_cache = 0;
```
