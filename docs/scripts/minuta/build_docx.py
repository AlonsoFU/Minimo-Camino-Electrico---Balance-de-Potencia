import re, shutil, os, zipfile, random
from xml.sax.saxutils import escape
from PIL import Image

SRC = "ref"; OUT = "build"
shutil.rmtree(OUT, ignore_errors=True); shutil.copytree(SRC, OUT)
d = open(f"{SRC}/word/document.xml", encoding="utf8").read()

# ---------- pieces from the reference ----------
a = d.find("<w:body>") + len("<w:body>")
b = d.find("</w:sectPr></w:pPr></w:p>") + len("</w:sectPr></w:pPr></w:p>")
cover = d[a:b]
final_sect = re.findall(r"<w:sectPr(?! [^>]*w:type).*?</w:sectPr>", d, re.S)[-1]
heading_block = open("heading_block.xml", encoding="utf8").read()
heading_block = heading_block.replace("<w:lastRenderedPageBreak/>", "")

# new title on the cover
tp = re.search(r'<w:p [^>]*><w:pPr><w:pStyle w:val="Ttulo"/></w:pPr>.*?</w:p>', cover, re.S).group(0)
new_title = ('<w:p><w:pPr><w:pStyle w:val="Ttulo"/></w:pPr><w:r><w:rPr><w:color w:val="585858"/></w:rPr>'
             '<w:t xml:space="preserve">MINUTA SOBRE LA LÓGICA DEL MÍNIMO CAMINO ELÉCTRICO EN EL BALANCE DE POTENCIA DE SUFICIENCIA</w:t></w:r></w:p>')
cover = cover.replace(tp, new_title)

# ---------- helpers ----------
_ids = {"bm": 100, "docpr": 200}
def uid(k): _ids[k] += 1; return _ids[k]
def hexid(): return "%08X" % random.randint(0, 0xFFFFFFFF)

def runs(text):
    """**bold** markup -> runs"""
    out = []
    for i, part in enumerate(re.split(r"\*\*", text)):
        if not part: continue
        rpr = "<w:rPr><w:b/><w:bCs/></w:rPr>" if i % 2 else ""
        out.append(f'<w:r>{rpr}<w:t xml:space="preserve">{escape(part)}</w:t></w:r>')
    return "".join(out)

PPR_BODY = '<w:spacing w:after="200" w:line="276" w:lineRule="auto"/><w:ind w:left="140" w:right="272"/><w:jc w:val="both"/>'
def para(text):
    return f'<w:p><w:pPr><w:pStyle w:val="Textoindependiente"/>{PPR_BODY}</w:pPr>{runs(text)}</w:p>'
def empty():
    return f'<w:p><w:pPr><w:pStyle w:val="Textoindependiente"/><w:spacing w:after="0"/></w:pPr></w:p>'
def _unused():
    return f'<w:p><w:pPr><w:pStyle w:val="Textoindependiente"/>{PPR_BODY}</w:pPr></w:p>'
def bullet(text):
    return ('<w:p><w:pPr><w:pStyle w:val="Textoindependiente"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="15"/></w:numPr>'
            '<w:spacing w:after="100" w:line="276" w:lineRule="auto"/><w:ind w:right="272"/><w:jc w:val="both"/></w:pPr>'
            f'{runs(text)}</w:p>')
def heading(text):
    h = heading_block
    h = h.replace(">INTRODUCCIÓN<", f">{escape(text)}<")
    h = re.sub(r'w:name="_bookmark0"', f'w:name="_bookmark{uid("bm")}"', h)
    h = re.sub(r'w:name="_Toc132959049"', f'w:name="_Toc{uid("bm")}9049"', h)
    h = h.replace('<w:bookmarkStart w:id="1"', f'<w:bookmarkStart w:id="{uid("bm")}"').replace('<w:bookmarkEnd w:id="1"', f'<w:bookmarkEnd w:id="{_ids["bm"]}"')
    h = h.replace('<w:bookmarkStart w:id="2"', f'<w:bookmarkStart w:id="{uid("bm")}"').replace('<w:bookmarkEnd w:id="2"', f'<w:bookmarkEnd w:id="{_ids["bm"]}"')
    h = h.replace('<wp:docPr id="66"', f'<wp:docPr id="{uid("docpr")}"').replace('<wps:cNvPr id="67"', f'<wps:cNvPr id="{uid("docpr")}"')
    h = re.sub(r'wp14:anchorId="[0-9A-F]+"', f'wp14:anchorId="{hexid()}"', h)
    h = re.sub(r'w14:anchorId="[0-9A-F]+"', f'w14:anchorId="{hexid()}"', h)
    h = re.sub(r'w14:paraId="[0-9A-F]+"', lambda m: f'w14:paraId="{"%08X" % random.randint(0, 0x7FFFFFFF)}"', h)
    return h + '<w:p><w:pPr><w:pStyle w:val="Textoindependiente"/><w:spacing w:before="0" w:after="0"/><w:rPr><w:sz w:val="14"/></w:rPr></w:pPr></w:p>'
def caption(text):
    return ('<w:p><w:pPr><w:pStyle w:val="Textoindependiente"/><w:spacing w:before="60" w:after="200"/><w:jc w:val="center"/></w:pPr>'
            f'<w:r><w:rPr><w:i/><w:iCs/><w:color w:val="585858"/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>')

rels_add = []; img_n = [0]
def image(path, width_in=6.3):
    img_n[0] += 1; n = img_n[0]
    w, h = Image.open(path).size
    cx = int(width_in * 914400); cy = int(cx * h / w)
    name = f"image_fig{n}.png"
    shutil.copy(path, f"{OUT}/word/media/{name}")
    rid = f"rIdFig{n}"
    rels_add.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{name}"/>')
    did = uid("docpr")
    return ('<w:p><w:pPr><w:pStyle w:val="Textoindependiente"/><w:spacing w:before="120"/><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:noProof/></w:rPr>'
            f'<w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
            f'<wp:docPr id="{did}" name="{name}"/><wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="{did}" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
            '</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')

def table(headers, rows, widths):
    total = sum(widths)
    ind = (10198 - total) // 2
    B = '<w:tcBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:left w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:right w:val="single" w:sz="4" w:space="0" w:color="auto"/></w:tcBorders>'
    def cell(text, w, head=False, bold=False):
        shade = '<w:shd w:val="clear" w:color="auto" w:fill="DCEBF0"/>' if head else ''
        rpr = '<w:rPr>' + ('<w:b/><w:bCs/>' if (head or bold) else '') + '<w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr>'
        return (f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{B}{shade}<w:vAlign w:val="center"/></w:tcPr>'
                f'<w:p><w:pPr><w:spacing w:before="40" w:after="40"/><w:jc w:val="center"/>{rpr}</w:pPr><w:r>{rpr}<w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p></w:tc>')
    x = (f'<w:tbl><w:tblPr><w:tblW w:w="{total}" w:type="dxa"/><w:tblInd w:w="{ind}" w:type="dxa"/>'
         '<w:tblCellMar><w:left w:w="70" w:type="dxa"/><w:right w:w="70" w:type="dxa"/></w:tblCellMar><w:tblLook w:val="04A0"/></w:tblPr>'
         '<w:tblGrid>' + "".join(f'<w:gridCol w:w="{w}"/>' for w in widths) + '</w:tblGrid>')
    x += '<w:tr><w:trPr><w:trHeight w:val="300"/></w:trPr>' + "".join(cell(h, w, head=True) for h, w in zip(headers, widths)) + '</w:tr>'
    for r in rows:
        bold = r[-1] in ("Seleccionado",)
        x += '<w:tr><w:trPr><w:trHeight w:val="300"/></w:trPr>' + "".join(cell(c, w, bold=bold) for c, w in zip(r, widths)) + '</w:tr>'
    return x + '</w:tbl>'

# ---------- content ----------
body = []
P = body.append

P(heading("INTRODUCCIÓN"))
P(para("En el marco del Balance de Potencia de Suficiencia, la potencia de suficiencia de cada central debe asociarse a los retiros del sistema a través de las instalaciones de transmisión que los vinculan. Para ello, la metodología utiliza el criterio de mínimo camino eléctrico, que define, para cada par inyección–retiro, la ruta de la red por la cual se considera que transita la potencia."))
P(para("El repositorio “Mínimo Camino Eléctrico – Balance de Potencia” contiene el código que construye y valida la base de datos de impedancias sobre la cual se calcula dicho camino. En particular, el código homologa las líneas y transformadores de la base ENT con las fuentes CNE e Infotécnica, y clasifica la calidad de los valores de reactancia (X) de cada tramo."))
P(para("La presente minuta describe brevemente la lógica del mínimo camino eléctrico a partir del código disponible y expone, mediante un caso simplificado, una situación problemática de la metodología: la selección de un camino eléctricamente más corto a pesar de existir un camino geográficamente más corto."))
P(empty())

P(heading("LÓGICA DEL MÍNIMO CAMINO ELÉCTRICO A PARTIR DEL CÓDIGO"))
P(para("El código representa el sistema de transmisión como una red en la que las barras corresponden a nodos y las líneas y transformadores a tramos que las conectan. Cada tramo de la hoja “lineas” de la base ENT se describe por su Barra A, Barra B, tensión nominal V [kV], resistencia R [ohm] y reactancia X [ohm]. Los circuitos paralelos se tratan como tramos independientes (sufijos _1de2 y _2de2) y los transformadores se identifican por el cambio de tensión entre sus barras."))
P(para("La “distancia” que utiliza la metodología no es la longitud geográfica del tramo, sino su distancia eléctrica, representada por la reactancia X. De este modo, la distancia eléctrica de un camino entre dos barras corresponde a la suma de las reactancias de los tramos que lo componen, y el mínimo camino eléctrico es aquel que minimiza dicha suma entre todas las rutas posibles de la red. Dado que los valores se expresan en ohm a distintos niveles de tensión, para comparar caminos que atraviesan transformadores las reactancias deben referirse a una base común en por unidad (X_pu = X_ohm × S_base / V²)."))
P(para("El flujo del código se compone de las siguientes etapas:"))
P(bullet("**Carga de datos:** se cargan las líneas de la base ENT (Ent2026.xlsx), las líneas de operación y de mantenimiento de la CNE (LinDatParOpe y LinDatManOpe) y los reportes de Infotécnica (secciones y tramos, transformadores de dos y de tres devanados)."))
P(bullet("**Reemplazo por mes de trabajo:** para el mes analizado (formato AAAA-MM) se reemplazan los valores R y X de operación por los valores de mantenimiento vigentes, de manera que la red refleje la configuración efectiva del período."))
P(bullet("**Homologación ENT–CNE:** cada línea ENT se compara con las líneas CNE exigiendo coincidencia de tensión y similitud de los nombres de las barras A y B, probando también el orden invertido. La confianza del match se clasifica como alta (≥ 90 %), media (80 a 89 %), a revisar (50 a 79 %) o sin match (< 50 %)."))
P(bullet("**Homologación ENT–Infotécnica:** se repite el proceso contra Infotécnica, con desempate por número de circuito. Para líneas, R y X se obtienen como el producto de los valores unitarios (ohm/km) por la longitud; para transformadores, a partir de la impedancia porcentual Z %, las pérdidas en el cobre y la potencia y tensión nominales."))
P(bullet("**Validación de X_ENT:** con las tres fuentes homologadas, cada tramo se clasifica como CORRECTO o DISCREPA según si la diferencia porcentual entre X_ENT y las fuentes de referencia supera un umbral de 15 %, y se decide CAMBIAR o REVISAR según si la magnitud del cambio supera 50 ohm."))
P(para("El resultado de la validación sobre la base ENT se resume a continuación:"))
P(table(["Resultado de la validación", "Tramos", "%"],
        [["Correctos (X_ENT coincide con las fuentes)", "1.022", "51,0 %"],
         ["Discrepan (diferencia ≥ 15 %)", "817", "40,8 %"],
         ["Sin referencia", "165", "8,2 %"],
         ["Total", "2.004", "100 %"]], [5000, 1300, 1300]))
P(empty())
P(para("El producto de estas etapas es una base de reactancias validada, que constituye el insumo del grafo sobre el cual se determina el mínimo camino eléctrico. Cabe señalar que el algoritmo de búsqueda del camino propiamente tal no forma parte del código del repositorio, cuyo alcance termina en la validación de X, según se muestra en la Figura 1."))
P(image("fig/fig1_flujo.png", 5.9))
P(caption("Figura 1. Etapas del código y su relación con el cálculo del mínimo camino eléctrico."))

P(heading("CASO PROBLEMÁTICO: CAMINO ELÉCTRICAMENTE CORTO VERSUS CAMINO GEOGRÁFICAMENTE CORTO"))
P(para("La reactancia por kilómetro de una línea es relativamente similar entre niveles de tensión (del orden de 0,3 a 0,4 ohm/km); sin embargo, al referirla a una base común, la reactancia en por unidad disminuye con el cuadrado de la tensión. Así, un kilómetro de línea de 500 kV resulta, eléctricamente, cerca de cinco veces más corto que un kilómetro de línea de 220 kV. Esta propiedad es la que origina que la metodología pueda seleccionar rutas que, en distancia, resultan contraintuitivas."))
P(para("Para ilustrarlo se considera el caso simplificado de la Figura 2. Una central inyecta en la barra G de 220 kV y el retiro se ubica en la barra C, también de 220 kV. Existen dos caminos posibles:"))
P(bullet("**Camino 1:** línea directa G–C en 220 kV, de 70 km y X = 28,0 ohm (0,40 ohm/km), equivalente a 0,0579 pu en base 100 MVA."))
P(bullet("**Camino 2:** transformador 220/500 kV en G (750 MVA y 12 %, equivalente a 0,016 pu), línea de 500 kV G’–C’ de 150 km y X = 49,5 ohm (0,33 ohm/km, equivalente a 0,0198 pu) y transformador 500/220 kV en C (0,016 pu). Distancia eléctrica total: 0,0518 pu."))
P(image("fig/fig2_red.png", 5.9))
P(caption("Figura 2. Red simplificada: camino geográficamente más corto (línea segmentada) y camino eléctricamente más corto (línea continua)."))
P(table(["Camino", "Longitud [km]", "X líneas [ohm]", "X total [pu]", "Resultado"],
        [["Camino 1 (directo 220 kV)", "70", "28,0", "0,0579", "Descartado"],
         ["Camino 2 (vía 500 kV)", "150", "49,5 + trafos", "0,0518", "Seleccionado"]], [3000, 1500, 1600, 1500, 1600]))
P(empty())
P(para("Como se observa, el camino 2 recorre más del doble de distancia geográfica (150 km frente a 70 km) y, sin embargo, resulta aproximadamente un 10 % más corto en términos eléctricos, por lo que es el camino que selecciona la metodología (Figura 3). En consecuencia, la potencia de suficiencia de la central queda asociada a las instalaciones de 500 kV y a los transformadores, y no a la línea de 220 kV que la vincula directamente con el consumo."))
P(image("fig/fig3_comparacion.png", 5.9))
P(caption("Figura 3. Comparación de ambos caminos en distancia geográfica y en distancia eléctrica."))
P(para("Lo anterior genera dos tipos de problemas:"))
P(bullet("**Resultados contraintuitivos para los coordinados:** las asignaciones de potencia, y los pagos asociados, recaen sobre instalaciones alejadas geográficamente del punto de inyección y de retiro, lo que dificulta su explicación y motiva observaciones y discrepancias en el proceso."))
P(bullet("**Alta sensibilidad a los datos de reactancia:** la diferencia entre ambos caminos es pequeña, por lo que un error moderado en X_ENT puede cambiar el camino seleccionado. En el ejemplo, bastaría que la reactancia de la línea directa estuviera sobreestimada en 10,5 % para que el camino 1 pasara a ser el mínimo (Figura 4). Dicho error se encuentra dentro de la tolerancia de 15 % que utiliza el proceso de validación, es decir, un tramo clasificado como CORRECTO puede igualmente alterar el resultado."))
P(image("fig/fig4_sensibilidad.png", 5.7))
P(caption("Figura 4. Sensibilidad del camino seleccionado al error en la reactancia de la línea directa."))
P(para("Dado que el 40,8 % de los tramos de la base ENT presenta discrepancias de reactancia respecto de CNE e Infotécnica, este tipo de cambios de camino no corresponde a un caso teórico, sino a una fuente concreta de diferencias entre versiones del Balance y de discrepancias por parte de los coordinados."))
P(empty())

P(heading("ALTERNATIVAS"))
P(para("Con el objeto de reducir el impacto de la situación descrita, se identifican las siguientes alternativas, no excluyentes entre sí:"))
P(bullet("Completar la validación de X_ENT con las fuentes CNE e Infotécnica antes del cálculo del camino, priorizando los tramos clasificados como DISCREPA cuya magnitud supere 50 ohm, así como los tramos de 500 kV y los transformadores, por ser los que concentran el efecto descrito."))
P(bullet("Reportar, junto con el camino seleccionado, el camino alternativo más cercano y la diferencia de distancia eléctrica entre ambos, de forma de identificar los casos sensibles en los que una variación inferior al 15 % en X cambiaría el resultado."))
P(bullet("Evaluar explícitamente en la metodología el tratamiento de los caminos cuya diferencia de distancia eléctrica sea inferior a la tolerancia de los datos, por ejemplo mediante un criterio de desempate documentado, de modo que el resultado no dependa de errores de la base."))
P(bullet("Documentar y comunicar a los coordinados el criterio de distancia eléctrica y el efecto del nivel de tensión, a fin de anticipar las observaciones por caminos aparentemente alejados de la ubicación geográfica de las instalaciones."))

newdoc = d[:a] + cover + "".join(body) + final_sect + "</w:body></w:document>"
open(f"{OUT}/word/document.xml", "w", encoding="utf8").write(newdoc)

# rels + content types
r = open(f"{OUT}/word/_rels/document.xml.rels", encoding="utf8").read()
r = r.replace("</Relationships>", "".join(rels_add) + "</Relationships>")
open(f"{OUT}/word/_rels/document.xml.rels", "w", encoding="utf8").write(r)
ct = open(f"{OUT}/[Content_Types].xml", encoding="utf8").read()
if 'Extension="png"' not in ct:
    ct = ct.replace('<Default Extension="jpeg"', '<Default Extension="png" ContentType="image/png"/><Default Extension="jpeg"')
open(f"{OUT}/[Content_Types].xml", "w", encoding="utf8").write(ct)
# core title
cp = f"{OUT}/docProps/core.xml"
if os.path.exists(cp):
    c = open(cp, encoding="utf8").read()
    c = re.sub(r"<dc:title>.*?</dc:title>", "<dc:title>Minuta mínimo camino eléctrico</dc:title>", c)
    open(cp, "w", encoding="utf8").write(c)

out = "Minuta_Minimo_Camino_Electrico.docx"
if os.path.exists(out): os.remove(out)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    # [Content_Types].xml first
    z.write(f"{OUT}/[Content_Types].xml", "[Content_Types].xml")
    for root, _, files in os.walk(OUT):
        for f in files:
            p = os.path.join(root, f); arc = os.path.relpath(p, OUT)
            if arc == "[Content_Types].xml": continue
            z.write(p, arc)
print("built", out)
