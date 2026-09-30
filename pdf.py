"""Armado del PDF con la estructura del informe del centro (ReportLab)."""
import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (HRFlowable, Image, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

from datos import tiempos_tabla
from grafico import ALTO_MM, ANCHO_MM, crear_grafico

AZUL = colors.HexColor("#1E9BC9")
AZUL_BARRA = colors.HexColor("#3CC0DF")
GRIS = colors.HexColor("#555555")
GRIS_CLARO = colors.HexColor("#DDDDDD")
OSCURO = colors.HexColor("#333333")

MARGEN_X = 22 * mm


def _estilo(nombre, **kw):
    base = dict(fontName="Helvetica", fontSize=8, leading=10, textColor=OSCURO)
    base.update(kw)
    return ParagraphStyle(nombre, **base)


ST_DIRECCION = _estilo("dir", fontSize=6.3, leading=7.6, textColor=GRIS)
ST_PACIENTE = _estilo("pac", fontSize=9.5, leading=13)
ST_FECHA = _estilo("fecha", fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=GRIS)
ST_TITULO = _estilo("tit", fontSize=10, leading=15, textColor=AZUL)
ST_SEDE = _estilo("sede", fontName="Helvetica-Bold", fontSize=9.5, leading=13, textColor=GRIS, spaceBefore=3)
ST_TEXTO = _estilo("txt", fontSize=7.6, leading=10.6)
ST_FIRMA = _estilo("firma", fontSize=9.5, leading=13, alignment=TA_CENTER, textColor=GRIS)
ST_LEYENDA = _estilo("ley", fontSize=6.3, leading=7.8, textColor=GRIS)
ST_CELDA = _estilo("cel", fontSize=7.6, leading=9.5)
ST_CELDA_ENC = _estilo("celenc", fontName="Helvetica-Bold", fontSize=7.6, leading=9.5)


def _sub(texto):
    """Escapa el texto y pone H2 / CH4 con subíndice real (sin caracteres unicode)."""
    t = escape(str(texto))
    t = re.sub(r"\bCH4\b", "CH<sub>4</sub>", t)
    t = re.sub(r"\bH2\b", "H<sub>2</sub>", t)
    return t


def _num(v):
    if v is None:
        return ""
    return str(int(v)) if float(v) == int(v) else f"{v:g}"


def _ruta(base_dir, nombre):
    if not nombre:
        return None
    p = Path(nombre)
    if not p.is_absolute():
        p = Path(base_dir) / p
    return p if p.exists() else None


def _encabezado(cfg, base_dir):
    centro = cfg["centro"]
    logo = _ruta(base_dir, centro.get("logo"))
    if logo:
        marca = Image(str(logo), width=38 * mm, height=12 * mm, kind="proportional")
        marca.hAlign = "LEFT"
    else:  # marcador de texto si no hay archivo de logo
        marca = Paragraph(
            f'<font color="#6EC1E4" size="30">{escape(centro["nombre"][:3])}</font>'
            f'<font color="#3B9CC9" size="30">{escape(centro["nombre"][3:])}</font>',
            _estilo("logo", fontSize=30, leading=32))
    direccion = Paragraph("<br/>".join(escape(l) for l in centro["lineas_encabezado"]),
                          ST_DIRECCION)
    t = Table([[marca], [direccion]], colWidths=[100 * mm], hAlign="LEFT")
    t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                           ("TOPPADDING", (0, 0), (-1, -1), 0),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
    return t


def _datos_paciente(reg):
    def fila(etiqueta, valor):
        return Paragraph(f"{etiqueta}: <b>{escape(valor)}</b>" if valor
                         else f"{etiqueta}:", ST_PACIENTE)
    edad = f"{reg['edad']} años" if reg["edad"] else ""
    t = Table(
        [[fila("Paciente", reg["nombre"]), fila("DNI", reg["dni"])],
         [fila("Cobertura", reg["cobertura"]), fila("Edad", edad)],
         [fila("N°", reg["nro_afiliado"]), ""]],
        colWidths=[100 * mm, 66 * mm], hAlign="LEFT")
    t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                           ("TOPPADDING", (0, 0), (-1, -1), 0),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    return t


def _tabla_y_grafico(reg, cfg):
    filas = [[Paragraph("TIEMPO", ST_CELDA_ENC), Paragraph("H<sub>2</sub>", ST_CELDA_ENC),
              Paragraph("CH<sub>4</sub>", ST_CELDA_ENC)]]
    for t in tiempos_tabla(cfg):
        filas.append([f"{t:02d}", _num(reg["h2"].get(t)), _num(reg["ch4"].get(t))])
    tabla = Table(filas, colWidths=[15 * mm, 9 * mm, 10 * mm], rowHeights=13.2)
    tabla.setStyle(TableStyle([
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 7.6),
        ("TEXTCOLOR", (0, 1), (-1, -1), GRIS),
        ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    grafico = Image(crear_grafico(reg, cfg), width=ANCHO_MM * mm, height=ALTO_MM * mm)
    conjunto = Table([[tabla, grafico]], colWidths=[36 * mm, 130 * mm], hAlign="LEFT")
    conjunto.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                  ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                  ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                  ("TOPPADDING", (0, 0), (-1, -1), 0)]))
    return conjunto


def _bloque(etiqueta, texto):
    return Paragraph(f"<b>{etiqueta}:</b> {_sub(texto)}" if texto
                     else f"<b>{etiqueta}:</b>", ST_TEXTO)


def _linea():
    return HRFlowable(width="100%", thickness=0.6, color=GRIS_CLARO,
                      spaceBefore=4, spaceAfter=6)


def generar_pdf(reg, cfg, ruta_salida, base_dir="."):
    est, prof = cfg["estudio"], cfg["profesional"]

    def decorar(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(AZUL_BARRA)
        canvas.rect(MARGEN_X, A4[1] - 11 * mm, 65 * mm, 2 * mm, stroke=0, fill=1)
        leyenda = Paragraph(escape(cfg["centro"]["leyenda"]), ST_LEYENDA)
        w, h = leyenda.wrap(A4[0] - 2 * MARGEN_X, 30 * mm)
        leyenda.drawOn(canvas, MARGEN_X, 14 * mm)
        canvas.restoreState()

    doc = SimpleDocTemplate(str(ruta_salida), pagesize=A4,
                            leftMargin=MARGEN_X, rightMargin=MARGEN_X,
                            topMargin=17 * mm, bottomMargin=30 * mm,
                            title=f"Informe {est['titulo']} - {reg['nombre']}",
                            author=cfg["centro"]["nombre"])

    story = [
        _encabezado(cfg, base_dir), _linea(),
        _datos_paciente(reg), _linea(),
        Paragraph(f"Fecha de estudio: {escape(reg['fecha_estudio'])} - "
                  f"COBERTURA: {escape(reg['cobertura'])}", ST_FECHA),
        Paragraph(escape(est["titulo"]), ST_TITULO),
        Paragraph(_sub(est["gases"]), ST_TITULO),
        Paragraph(f"Sede: {escape(reg['sede'])}", ST_SEDE),
        Spacer(1, 3 * mm),
        _tabla_y_grafico(reg, cfg),
        Spacer(1, 4 * mm),
        _bloque("Estímulo", reg["estimulo"]),
        _bloque("Dieta previa", reg["dieta_previa"]),
        _bloque("Procedimiento", est["procedimiento"]),
        _bloque("Causa", reg["causa"]),
        _bloque("Criterio", est["criterio"]),
        _bloque("Conclusión", reg["conclusion"]),
        _bloque("Comentarios", reg["comentarios"]),
        Spacer(1, 10 * mm),
    ]

    firma = _ruta(base_dir, prof.get("firma_imagen"))
    if firma:
        img = Image(str(firma), width=35 * mm, height=14 * mm, kind="proportional")
        img.hAlign = "CENTER"
        story.append(img)
    else:
        story.append(Spacer(1, 12 * mm))
    story.append(Paragraph(escape(prof["nombre"]), ST_FIRMA))
    story.append(Paragraph(escape(f"{prof['cargo']} - {prof['matricula']}"), ST_FIRMA))

    doc.build(story, onFirstPage=decorar, onLaterPages=decorar)
    return ruta_salida
