exec(open('build_docx.py').read().split("# ---------- content ----------")[0])
cover = cover.replace("MINUTA SOBRE LA LÓGICA DEL MÍNIMO CAMINO ELÉCTRICO EN EL BALANCE DE POTENCIA DE SUFICIENCIA",
                      "MINUTA SOBRE LA METODOLOGÍA DE MÍNIMO CAMINO ELÉCTRICO PARA MEDIOS DE GENERACIÓN DE PEQUEÑA ESCALA")
def quote(text):
    return ('<w:p><w:pPr><w:pStyle w:val="Textoindependiente"/><w:spacing w:after="200" w:line="276" w:lineRule="auto"/><w:ind w:left="700" w:right="700"/><w:jc w:val="both"/></w:pPr>'
            f'<w:r><w:rPr><w:i/><w:iCs/></w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>')
body = []; P = body.append

P(heading("INTRODUCCIÓN"))
P(para("Los decretos de precios de nudo establecen que las inyecciones de los medios de generación de pequeña escala se valorizan al precio de nudo de la subestación del Sistema de Transmisión Nacional más cercana, y que dicha subestación se determina mediante el criterio de mínima distancia eléctrica, también denominado mínimo camino eléctrico, cuya aplicación corresponde al Coordinador."))
P(para("Como fuente de la metodología descrita en esta minuta se utiliza el siguiente extracto, contenido en el numeral 2.2 de los decretos de precios de nudo:"))
P(quote("“2.2 Precio de Nudo aplicables a las Inyecciones de Medios de generación de pequeña escala. Tanto el precio de nudo de energía como el precio de nudo de potencia aplicables a las inyecciones efectuadas por los medios de generación de pequeña escala a que se refiere el artículo segundo transitorio del decreto Nº 88/2019, del Ministerio de Energía, corresponderán al precio de nudo de la subestación del Sistema de Transmisión Nacional más cercana. A estos efectos, la subestación del Sistema de Transmisión Nacional más cercana corresponderá a la que se encuentre a la mínima distancia eléctrica entre el punto de inyección y la subestación respectiva del Sistema de Transmisión Nacional, determinada por el Coordinador.”"))
P(para("La presente minuta describe brevemente la lógica de la metodología de mínimo camino eléctrico y expone, mediante un caso específico, un efecto no deseado de su aplicación: la asignación de una barra troncal alejada de la barra analizada porque el camino directo, de menor longitud, contiene un transformador de alta reactancia que la metodología prefiere rodear. Asimismo, se describe la práctica histórica de asociación manual de barras que se ha aplicado para evitar este efecto."))
P(empty())

P(heading("METODOLOGÍA DEL MÍNIMO CAMINO ELÉCTRICO"))
P(para("La metodología representa el sistema de transmisión como una red en la que las barras corresponden a nodos y las líneas y transformadores a tramos que las conectan. Cada tramo se caracteriza por sus barras extremas, su tensión nominal y su reactancia X, expresada en ohm, de acuerdo con los parámetros de la base de instalaciones que utiliza el Coordinador para el Balance de Potencia. Los tramos paralelos entre las mismas dos barras, sean circuitos de una línea o unidades de transformación, se combinan en un único tramo de reactancia equivalente (1/Xeq = Σ 1/Xi)."))
P(para("La “distancia” que considera el decreto no es la longitud geográfica que separa la barra analizada de la subestación, sino su distancia eléctrica, representada por la reactancia de los tramos que las vinculan. De este modo, la distancia eléctrica de un camino entre dos barras corresponde a la suma de las reactancias de los tramos que lo componen, y el mínimo camino eléctrico entre la barra analizada y una subestación es aquel que minimiza dicha suma entre todas las rutas posibles de la red."))
P(para("En consecuencia, la determinación de la barra troncal más cercana a una barra analizada se efectúa de la siguiente forma:"))
P(bullet("Se identifica la barra analizada en la red y el subsistema al que pertenece."))
P(bullet("Se identifican las barras troncales de precio de nudo, que son los destinos candidatos a ser asignados."))
P(bullet("Para cada barra troncal del mismo subsistema se determina el camino de mínima reactancia acumulada desde la barra analizada."))
P(bullet("Se asigna la barra troncal cuya distancia eléctrica resulta menor, y su precio de nudo se aplica a las inyecciones de la barra analizada."))
P(para("La Figura 1 ilustra el criterio con un ejemplo conceptual: aunque la barra analizada está vinculada a dos barras troncales, se asigna la barra A, por cuanto la suma de reactancias del camino que conduce a ella es menor."))
P(image("fig/fig1_concepto.png", 5.4))
P(caption("Figura 1. Criterio de mínima distancia eléctrica: la barra troncal asignada es la de menor suma de reactancias."))
P(para("Cabe destacar que, como la reactancia de una línea es proporcional a su longitud, en una red compuesta solo por líneas la distancia eléctrica y la longitud del camino suelen coincidir. Sin embargo, los transformadores tienen longitud nula y una reactancia que puede equivaler a decenas o cientos de kilómetros de línea, por lo que un camino directo que atraviese un transformador de alta reactancia puede resultar eléctricamente más largo que un rodeo de muchos kilómetros por la red."))
P(para("Para evitar este efecto, históricamente en el proceso se ha asociado de forma manual la barra de 66 kV a la barra de 220 kV de la misma subestación, de modo que el cálculo no considere el transformador que las une y la barra quede asignada a la barra troncal de su propio emplazamiento. Esta asociación no tiene respaldo en el cálculo ni en un criterio documentado: se basa únicamente en la práctica histórica del proceso, y por tanto no es verificable ni se aplica necesariamente de manera uniforme a todos los casos equivalentes. En la fijación vigente PN2604, 415 de las 1.553 barras asociadas tienen una barra troncal distinta de la que entrega el cálculo; 71 de ellas corresponden a la red de 66 kV de la zona de Itahue, asociada a Itahue 220 kV mientras el cálculo entrega Candelaria 220 kV."))
P(empty())

P(heading("CASO DE ANÁLISIS: ASIGNACIÓN POR RODEO DE TRANSFORMADORES DE ALTA REACTANCIA"))
P(para("El efecto descrito se observa en la barra La Palma 13 kV, en la comuna de San Javier, Región del Maule. La barra troncal más cercana es Ancoa 220 kV, a unos 32 km en línea recta y a 109 km de recorrido por la red de Linares, Yerbas Buenas y Maule, y la siguiente es Itahue 220 kV, a unos 58 km en línea recta. Sin embargo, ambos caminos pasan por transformadores de alta reactancia: Linares 154/66 kV, de 164,2 ohm, e Itahue 154/66 kV, de 85,7 ohm equivalente, valores comparables a cientos de kilómetros de línea de 66 kV. Por ello, el mínimo camino eléctrico los rodea por la red de 66 kV hasta San Fernando y termina asignando Candelaria 220 kV, en la Región de O’Higgins, como se ve a continuación:"))
P(image("fig/fig2_caso_lapalma.png", 6.9))
P(caption("Figura 2. Caminos desde la barra La Palma 13 kV: caminos descartados por Linares hacia Ancoa y por los transformadores de Itahue (segmentados) y camino de mínima distancia eléctrica por San Fernando hasta Candelaria 220 kV (continuo). Reactancias equivalentes con paralelos combinados; longitudes por la red donde la base de coordenadas lo permite."))
P(table(["Camino", "Línea recta [km]", "Por la red [km]", "X [ohm]", "Resultado"],
        [["A Ancoa 220 kV por Linares, el más corto en kilómetros", "32", "109,0", "287,9", "Descartado"],
         ["A Itahue 220 kV por los transformadores de Itahue", "58", "sin dato", "206,0", "Descartado"],
         ["A Candelaria 220 kV por San Fernando y Tinguiririca", "199", "sin dato", "150,7", "Seleccionado"]],
        [4300, 1300, 1300, 1100, 1300]))
P(empty())
P(para("La barra asignada es Candelaria 220 kV, a unos 199 km en línea recta y 150,7 ohm, y no Ancoa 220 kV ni Itahue 220 kV, que se encuentran a una fracción de esa distancia pero cuyos caminos pasan por un transformador de alta reactancia (Figura 3). Incluso el mejor camino eléctrico hacia Ancoa, que sigue la misma ruta hasta Puente Negro y continúa por Colbún, suma 156,6 ohm, levemente más que Candelaria. En la fijación vigente PN2604, la barra La Palma 13 kV se encuentra asociada a Itahue 220 kV, de modo que la asociación aplicada en el proceso no corresponde al resultado del cálculo. La longitud por la red de los caminos que pasan por la línea La Palma – El Ruil no está disponible, porque la barra El Ruil no cuenta con coordenadas en la base de coordenadas del cálculo."))
P(image("fig/fig3_comparacion_lapalma.png", 5.6))
P(caption("Figura 3. Distancia en línea recta y distancia eléctrica desde La Palma 13 kV hacia las barras troncales Ancoa, Itahue y Candelaria 220 kV."))
P(para("Lo anterior genera los siguientes problemas en la aplicación de la metodología:"))
P(bullet("**Resultados contraintuitivos para los coordinados:** la barra analizada se ubica a unos 32 km de la subestación Ancoa y, pese a ello, se le asigna una barra a unos 199 km, en otra región, cuyo precio de nudo es distinto. Esta situación es difícil de explicar y motiva observaciones y discrepancias en los procesos de valorización."))
P(bullet("**Dependencia de un único parámetro:** la asignación queda determinada por la reactancia registrada para un solo tramo, el transformador de Linares o el de Itahue. Un valor elevado, sea por las características reales de las unidades o por un error en la base de instalaciones, basta para que el camino más corto quede descartado, incluso después de combinar en paralelo las unidades existentes."))
P(bullet("**Inestabilidad del resultado en el tiempo:** la corrección del parámetro, el reemplazo del transformador o la entrada en operación de una nueva instalación pueden cambiar la barra asignada de un período a otro. En este mismo caso, la entrada en operación de la subestación Nueva Nirivilo, con su transformador 220/66 kV de 67,9 ohm y las líneas de 220 kV hacia Mataquito e Itahue, hace que la barra más cercana pase a ser Itahue 220 kV, con 148,1 ohm, y Candelaria deje de ser la asignada, con el consiguiente cambio del precio de nudo aplicado a las inyecciones."))
P(bullet("**Asociación manual sin respaldo:** en casos equivalentes se ha evitado este efecto asociando manualmente la barra de 66 kV a la barra de 220 kV de la misma subestación, según se describió en la sección anterior. Como esa asociación se basa solo en la práctica histórica, existen casos en que la barra asignada no corresponde al resultado del cálculo, como el de La Palma y el resto de la zona de Itahue en la fijación PN2604, y casos en que sí corresponde a pesar de ser contraintuitivo, lo que dificulta la trazabilidad del proceso y puede generar desconfianza en los coordinados."))
P(empty())

P(heading("ALTERNATIVAS"))
P(para("Con el objeto de reducir el impacto del efecto descrito, se identifican las siguientes alternativas, no excluyentes entre sí:"))
P(bullet("Publicar, junto con la barra troncal asignada a cada barra analizada, el camino eléctrico considerado y la distancia eléctrica a las barras troncales candidatas más próximas, de modo que los coordinados puedan verificar el resultado y anticipar las observaciones."))
P(bullet("Validar los valores de reactancia de los transformadores de la base de instalaciones, en particular los de alta reactancia, como Linares 154/66 kV e Itahue 154/66 kV, por ser estos los parámetros que determinan la asignación."))
P(bullet("Formalizar y documentar el criterio con que históricamente se asocia manualmente la barra de 66 kV a la barra de 220 kV de la misma subestación, de modo que la regla sea explícita, forme parte del cálculo, se aplique de manera uniforme a todos los casos equivalentes y pueda ser verificada por los coordinados, en lugar de depender de ajustes caso a caso."))
P(bullet("Evaluar la incorporación de un criterio complementario para los casos en que el camino seleccionado rodee un camino directo de longitud notoriamente menor, por ejemplo privilegiando la barra troncal más cercana en distancia cuando la diferencia de distancia eléctrica respecto del camino seleccionado se explique únicamente por un transformador."))
P(bullet("Documentar y comunicar a los coordinados el criterio de distancia eléctrica y su diferencia con la distancia geográfica, a fin de reducir las discrepancias originadas en la interpretación del concepto de subestación más cercana."))

newdoc = d[:a] + cover + "".join(body) + final_sect + "</w:body></w:document>"
open(f"{OUT}/word/document.xml", "w", encoding="utf8").write(newdoc)
r = open(f"{OUT}/word/_rels/document.xml.rels", encoding="utf8").read()
r = r.replace("</Relationships>", "".join(rels_add) + "</Relationships>")
open(f"{OUT}/word/_rels/document.xml.rels", "w", encoding="utf8").write(r)
ct = open(f"{OUT}/[Content_Types].xml", encoding="utf8").read()
if 'Extension="png"' not in ct:
    ct = ct.replace('<Default Extension="jpeg"', '<Default Extension="png" ContentType="image/png"/><Default Extension="jpeg"')
open(f"{OUT}/[Content_Types].xml", "w", encoding="utf8").write(ct)
cp = f"{OUT}/docProps/core.xml"
if os.path.exists(cp):
    c = open(cp, encoding="utf8").read()
    c = re.sub(r"<dc:title>.*?</dc:title>", "<dc:title>Minuta mínimo camino eléctrico PMGD</dc:title>", c)
    open(cp, "w", encoding="utf8").write(c)
out = "Minuta_Minimo_Camino_Electrico.docx"
if os.path.exists(out): os.remove(out)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(f"{OUT}/[Content_Types].xml", "[Content_Types].xml")
    for root, _, files in os.walk(OUT):
        for f in files:
            p = os.path.join(root, f); arc = os.path.relpath(p, OUT)
            if arc == "[Content_Types].xml": continue
            z.write(p, arc)
print("built", out)
