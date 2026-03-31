"""
infrastructure/pdf_generator.py
Genera reportes PDF con ReportLab.
Equivale a PdfGenerator.java del proyecto original.
"""

import io
from functools import lru_cache
from pathlib import Path
from datetime import datetime
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


BRAND_COLOR = colors.HexColor("#D90416")
BRAND_COLOR_DARK = colors.HexColor("#B00312")
HEADER_COLOR = colors.HexColor("#181818")
MUTED_COLOR = colors.HexColor("#73727A")
SURFACE_COLOR = colors.HexColor("#FFFFFF")
SURFACE_SOFT = colors.HexColor("#FCFBFC")
ACCENT_SOFT = colors.HexColor("#FFF2F4")
LINE_COLOR = colors.HexColor("#E8E6EB")
LINE_SOFT = colors.HexColor("#F1EFF4")
ALT_ROW = colors.HexColor("#FCFBFC")
LOGO_PATH = Path(__file__).resolve().parents[1] / "interfaces" / "static" / "img" / "logobongusto.png"


def _build_table(headers: list[str], rows: list[list], total_width: float, col_widths=None) -> Table:
    styles = getSampleStyleSheet()
    header_cell_style = ParagraphStyle(
        "BonGustoTableHeaderCell",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=9.2,
        leading=11,
        textColor=colors.white,
        alignment=TA_CENTER,
        wordWrap="CJK",
    )
    body_cell_style = ParagraphStyle(
        "BonGustoTableBodyCell",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.4,
        leading=10.5,
        textColor=HEADER_COLOR,
        alignment=TA_LEFT,
        wordWrap="CJK",
    )

    normalized_rows = rows if rows else [["Sin datos"] + [""] * (len(headers) - 1)]
    table_data = [
        [Paragraph(str(cell), header_cell_style) for cell in headers]
    ] + [
        [Paragraph(str(cell if cell is not None else "-"), body_cell_style) for cell in row]
        for row in normalized_rows
    ]
    if col_widths is None:
        col_width = total_width / max(len(headers), 1)
        col_widths = [col_width] * len(headers)

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BRAND_COLOR),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 9),
                ("TOPPADDING", (0, 0), (-1, 0), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [SURFACE_COLOR, ALT_ROW]),
                ("ALIGN", (0, 1), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
                ("TOPPADDING", (0, 1), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.6, LINE_COLOR),
                ("LINEBELOW", (0, 0), (-1, 0), 1.2, BRAND_COLOR_DARK),
                ("BOX", (0, 0), (-1, -1), 0.7, LINE_COLOR),
            ]
        )
    )
    return table


def _build_section_card(heading: str, paragraph: str | None, total_width: float, heading_style, body_style) -> Table:
    card_rows = [[Paragraph(heading, heading_style)]]
    if paragraph:
        card_rows.append([Paragraph(paragraph, body_style)])

    card = Table(card_rows, colWidths=[total_width])
    card.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), ACCENT_SOFT),
                ("BOX", (0, 0), (-1, -1), 0.7, LINE_COLOR),
                ("LINEBEFORE", (0, 0), (0, -1), 3, BRAND_COLOR),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    return card


@lru_cache(maxsize=1)
def _get_clean_logo_bytes() -> bytes | None:
    if not LOGO_PATH.exists():
        return None

    image = PILImage.open(LOGO_PATH).convert("RGBA")
    cleaned = []
    for r, g, b, a in image.getdata():
        if a == 0:
            cleaned.append((r, g, b, a))
            continue
        if r < 22 and g < 22 and b < 22:
            cleaned.append((r, g, b, 0))
        else:
            cleaned.append((r, g, b, a))

    image.putdata(cleaned)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _build_report_header(total_width: float, styles) -> Table:
    title_style = ParagraphStyle(
        "BonGustoHeaderTitle",
        parent=styles["Heading1"],
        textColor=BRAND_COLOR,
        fontSize=18,
        leading=22,
        spaceAfter=0,
        alignment=TA_LEFT,
    )
    subtitle_style = ParagraphStyle(
        "BonGustoHeaderSubtitle",
        parent=styles["BodyText"],
        textColor=MUTED_COLOR,
        fontSize=9.2,
        leading=12,
        spaceAfter=0,
        alignment=TA_LEFT,
    )
    meta_style = ParagraphStyle(
        "BonGustoHeaderMeta",
        parent=styles["BodyText"],
        textColor=MUTED_COLOR,
        fontSize=8.2,
        leading=10,
        spaceAfter=0,
        alignment=TA_LEFT,
    )

    logo_size = 1.8 * cm
    logo_cell = ""
    logo_bytes = _get_clean_logo_bytes()
    if logo_bytes:
        logo = RLImage(io.BytesIO(logo_bytes), width=logo_size, height=logo_size)
        logo_cell = logo

    fecha_impresion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    copy = [
        Paragraph("BonGusto", title_style),
        Spacer(1, 0.06 * cm),
        Paragraph(f"Fecha y hora de impresión: {fecha_impresion}", meta_style),
    ]

    header = Table([[logo_cell, copy]], colWidths=[2.3 * cm, total_width - (2.3 * cm)])
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return header


def _build_report_footer(total_width: float, styles) -> Paragraph:
    footer_style = ParagraphStyle(
        "BonGustoFooter",
        parent=styles["BodyText"],
        textColor=MUTED_COLOR,
        fontSize=8.2,
        leading=10,
        alignment=TA_CENTER,
    )
    year = datetime.now().year
    return Paragraph(f"Copyright © {year} BonGusto. Todos los derechos reservados.", footer_style)


def crear_pdf(titulo: str, headers: list[str], rows: list[list]) -> bytes:
    """
    Genera un PDF con tabla de datos.

    :param titulo: Título del reporte.
    :param headers: Lista de encabezados de columna.
    :param rows:    Lista de filas (cada fila es lista de strings).
    :return:        Bytes del PDF generado.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "BonGustoTitle",
        parent=styles["Title"],
        textColor=BRAND_COLOR,
        fontSize=17,
        spaceAfter=8,
        alignment=TA_CENTER,
    )

    total_width = landscape(A4)[0] - 3 * cm
    elements = []
    elements.append(_build_report_header(total_width, styles))
    elements.append(Spacer(1, 0.35 * cm))
    elements.append(Paragraph(titulo, title_style))
    elements.append(Spacer(1, 0.45 * cm))

    table = _build_table(headers, rows, total_width)
    elements.append(table)
    elements.append(Spacer(1, 0.35 * cm))
    elements.append(_build_report_footer(total_width, styles))

    doc.build(elements)
    return buffer.getvalue()


def crear_pdf_compuesto(titulo: str, bloques: list[dict]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "BonGustoCompositeTitle",
        parent=styles["Title"],
        textColor=BRAND_COLOR,
        fontSize=17,
        spaceAfter=8,
        alignment=TA_CENTER,
    )
    section_style = ParagraphStyle(
        "BonGustoSectionTitle",
        parent=styles["Heading2"],
        textColor=HEADER_COLOR,
        fontSize=11.5,
        spaceBefore=0,
        spaceAfter=0,
        alignment=TA_LEFT,
    )
    body_style = ParagraphStyle(
        "BonGustoBody",
        parent=styles["BodyText"],
        textColor=MUTED_COLOR,
        fontSize=8.6,
        leading=12,
        spaceAfter=0,
        alignment=TA_LEFT,
    )

    total_width = landscape(A4)[0] - 3 * cm
    elements = [
        _build_report_header(total_width, styles),
        Spacer(1, 0.35 * cm),
        Paragraph(titulo, title_style),
        Spacer(1, 0.3 * cm),
    ]

    for index, bloque in enumerate(bloques):
        block_elements = []
        heading = bloque.get("heading")
        paragraph = bloque.get("paragraph")
        if heading:
            block_elements.append(_build_section_card(heading, paragraph, total_width, section_style, body_style))
            block_elements.append(Spacer(1, 0.14 * cm))
        headers = bloque.get("headers")
        rows = bloque.get("rows")
        if headers:
            table = _build_table(headers, rows or [], total_width, bloque.get("col_widths"))
            block_elements.append(table)
        if block_elements:
            if index == 0:
                elements.extend(block_elements)
            else:
                elements.append(KeepTogether(block_elements))
        elements.append(Spacer(1, 0.3 * cm))

    elements.append(Spacer(1, 0.15 * cm))
    elements.append(_build_report_footer(total_width, styles))

    doc.build(elements)
    return buffer.getvalue()
