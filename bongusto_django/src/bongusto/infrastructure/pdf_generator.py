"""
infrastructure/pdf_generator.py
Aquí se arma toda la lógica para sacar reportes PDF con ReportLab.
Sería como el generador de PDF del proyecto.
"""

import io
import re
from functools import lru_cache
from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation
from collections import Counter
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.widgets.markers import makeMarker


# Colores principales que se usan en los reportes
# Esto ayuda a mantener el estilo visual de BonGusto
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
CHART_FILL = colors.HexColor("#FDE0E4")
CHART_GRID = colors.HexColor("#E7E1E8")
CHART_PANEL = colors.HexColor("#FFF9F4")
CHART_LINE = colors.HexColor("#E07A5F")
CHART_DOT = colors.HexColor("#81B29A")
CHART_BAR_COLORS = [
    colors.HexColor("#E9C46A"),
    colors.HexColor("#81B29A"),
    colors.HexColor("#F4A261"),
    colors.HexColor("#A8DADC"),
    colors.HexColor("#CDB4DB"),
    colors.HexColor("#F28482"),
]

# Rutas candidatas del logo para que aparezca en todos los PDF
LOGO_CANDIDATES = [
    Path(__file__).resolve().parents[1] / "modules" / "shared" / "static" / "img" / "logobongusto.png",
    Path(__file__).resolve().parents[1] / "interfaces" / "static" / "img" / "logobongusto.png",
]


def _build_table(headers: list[str], rows: list[list], total_width: float, col_widths=None) -> Table:
    # Carga estilos base de ReportLab
    styles = getSampleStyleSheet()

    # Estilo de los encabezados
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

    # Estilo del contenido normal de la tabla
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

    # Si no hay filas, deja una fila básica para que no quede vacía
    normalized_rows = rows if rows else [["Sin datos"] + [""] * (len(headers) - 1)]

    # Aquí se arma toda la data de la tabla
    table_data = [
        [Paragraph(str(cell), header_cell_style) for cell in headers]
    ] + [
        [Paragraph(str(cell if cell is not None else "-"), body_cell_style) for cell in row]
        for row in normalized_rows
    ]

    # Si no mandan anchos personalizados, reparte todo parejo
    if col_widths is None:
        col_width = total_width / max(len(headers), 1)
        col_widths = [col_width] * len(headers)

    # Crea la tabla
    # repeatRows=1 hace que el encabezado se repita si pasa de página
    table = Table(table_data, colWidths=col_widths, repeatRows=1)

    # Estilos visuales de la tabla
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
    # Arma una tarjeta para mostrar el título de una sección
    # y si existe, también un pequeño texto
    card_rows = [[Paragraph(heading, heading_style)]]
    if paragraph:
        card_rows.append([Paragraph(paragraph, body_style)])

    # Crea la tarjeta
    card = Table(card_rows, colWidths=[total_width])

    # Estilo visual de la tarjeta
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


def _clean_label(value, fallback: str = "Sin dato") -> str:
    text = str(value if value not in (None, "") else fallback).strip()
    if not text:
        text = fallback
    return re.sub(r"\s+", " ", text)


def _compact_label(value, max_chars: int = 16) -> str:
    text = _clean_label(value)
    if len(text) <= max_chars:
        return text
    return f"{text[: max_chars - 1]}..."


def _is_empty_cell(value) -> bool:
    text = str(value if value is not None else "").strip()
    return text in {"", "-", "Sin datos", "Sin registros"}


def _coerce_number(value) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value if value is not None else "").strip()
    if not text or text == "-":
        return None

    cleaned = text.replace("%", "").replace("$", "").replace(",", "").strip()
    cleaned = re.sub(r"[^0-9.\-]+", "", cleaned)
    if not cleaned or cleaned in {"-", ".", "-.", ".-"}:
        return None

    try:
        return float(Decimal(cleaned))
    except (InvalidOperation, ValueError):
        return None


def _looks_temporal(headers: list[str], labels: list[str]) -> bool:
    temporal_tokens = ("mes", "fecha", "hora", "dia", "semana", "periodo", "calendario")
    header_text = " ".join(str(header).lower() for header in headers[:2])
    if any(token in header_text for token in temporal_tokens):
        return True

    sample = " ".join(label.lower() for label in labels[:4])
    return any(token in sample for token in ("202", "/", ":", "ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"))


def _extract_numeric_series(headers: list[str], rows: list[list]) -> tuple[list[str], list[float], str | None]:
    best_labels: list[str] = []
    best_values: list[float] = []
    best_metric = None
    best_score = -1

    if not headers or not rows:
        return best_labels, best_values, best_metric

    for column_index, metric_name in enumerate(headers[1:], start=1):
        labels = []
        values = []

        for row_index, row in enumerate(rows):
            if column_index >= len(row):
                continue
            number = _coerce_number(row[column_index])
            if number is None:
                continue

            label_source = row[0] if row else f"Fila {row_index + 1}"
            labels.append(_compact_label(label_source))
            values.append(number)

        if len(values) > best_score:
            best_score = len(values)
            best_labels = labels
            best_values = values
            best_metric = str(metric_name)

    return best_labels, best_values, best_metric


def _extract_frequency_series(headers: list[str], rows: list[list]) -> tuple[list[str], list[float], str | None]:
    if not rows:
        return [], [], None

    best_labels: list[str] = []
    best_values: list[float] = []
    best_metric = None
    best_score = -1

    for column_index, header in enumerate(headers or ["Categoria"]):
        values = []
        for row in rows:
            if column_index >= len(row):
                continue
            if _is_empty_cell(row[column_index]):
                continue
            values.append(_clean_label(row[column_index]))

        counts = Counter(values)
        if not counts:
            continue

        top = counts.most_common(6)
        if len(top) > best_score:
            best_score = len(top)
            best_labels = [_compact_label(label) for label, _ in top]
            best_values = [float(total) for _, total in top]
            best_metric = f"Frecuencia por {header}"

    return best_labels, best_values, best_metric


def _extract_column_density(headers: list[str], rows: list[list]) -> tuple[list[str], list[float], str | None]:
    if not headers or not rows:
        return [], [], None

    labels = []
    values = []
    for column_index, header in enumerate(headers[:6]):
        total = 0
        for row in rows:
            if column_index < len(row) and not _is_empty_cell(row[column_index]):
                total += 1
        labels.append(_compact_label(header))
        values.append(float(total))

    return labels, values, "Cobertura por columna"


def _build_auto_chart(headers: list[str], rows: list[list], total_width: float) -> Drawing | None:
    if not headers or rows is None:
        return None

    labels, values, metric_name = _extract_numeric_series(headers, rows)
    chart_kind = "bar"

    if not values:
        labels, values, metric_name = _extract_frequency_series(headers, rows)

    if not values:
        labels, values, metric_name = _extract_column_density(headers, rows)

    if not values:
        return None

    labels = labels[:6]
    values = values[:6]
    if len(labels) != len(values) or not values:
        return None

    if _looks_temporal(headers, labels) and len(values) >= 2:
        chart_kind = "line"

    width = total_width
    height = 4.8 * cm
    drawing = Drawing(width, height)
    drawing.add(Rect(0, 0, width, height, rx=8, ry=8, fillColor=CHART_PANEL, strokeColor=LINE_COLOR, strokeWidth=0.8))
    drawing.add(String(12, height - 14, "Vista grafica de la seccion", fontName="Helvetica-Bold", fontSize=9, fillColor=HEADER_COLOR))
    drawing.add(String(12, height - 27, _compact_label(metric_name or "Resumen visual", 42), fontName="Helvetica", fontSize=8, fillColor=MUTED_COLOR))

    max_value = max(values) if values else 0
    min_value = min(values) if values else 0
    value_max = max_value * 1.2 if max_value > 0 else 1
    value_min = min(0, min_value)

    if chart_kind == "line":
        chart = HorizontalLineChart()
        chart.x = 42
        chart.y = 20
        chart.width = width - 62
        chart.height = height - 56
        chart.data = [values]
        chart.joinedLines = 1
        chart.lines[0].strokeColor = CHART_LINE
        chart.lines[0].strokeWidth = 2.4
        chart.lines[0].symbol = makeMarker("FilledCircle")
        chart.lines[0].symbol.size = 5
        chart.lines[0].symbol.fillColor = CHART_DOT
        chart.lines[0].symbol.strokeColor = colors.white
        chart.categoryAxis.categoryNames = labels
        chart.categoryAxis.labels.boxAnchor = "n"
        chart.categoryAxis.labels.angle = 20
        chart.categoryAxis.labels.fontName = "Helvetica"
        chart.categoryAxis.labels.fontSize = 7
        chart.valueAxis.valueMin = value_min
        chart.valueAxis.valueMax = value_max
        chart.valueAxis.labels.fontName = "Helvetica"
        chart.valueAxis.labels.fontSize = 7
        chart.valueAxis.visibleGrid = True
        chart.valueAxis.gridStrokeColor = CHART_GRID
        drawing.add(chart)
        return drawing

    chart = VerticalBarChart()
    chart.x = 42
    chart.y = 20
    chart.width = width - 62
    chart.height = height - 56
    chart.data = [values]
    chart.strokeColor = LINE_COLOR
    chart.valueAxis.valueMin = value_min
    chart.valueAxis.valueMax = value_max
    chart.valueAxis.visibleGrid = True
    chart.valueAxis.gridStrokeColor = CHART_GRID
    chart.valueAxis.labels.fontName = "Helvetica"
    chart.valueAxis.labels.fontSize = 7
    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.boxAnchor = "n"
    chart.categoryAxis.labels.angle = 20 if any(len(label) > 8 for label in labels) else 0
    chart.categoryAxis.labels.fontName = "Helvetica"
    chart.categoryAxis.labels.fontSize = 7
    chart.bars[0].fillColor = CHART_FILL
    chart.bars[0].strokeColor = colors.HexColor("#B08968")
    chart.bars[0].strokeWidth = 0.8
    for bar_index, _ in enumerate(values):
        chart.bars[(0, bar_index)].fillColor = CHART_BAR_COLORS[bar_index % len(CHART_BAR_COLORS)]
        chart.bars[(0, bar_index)].strokeColor = colors.white
        chart.bars[(0, bar_index)].strokeWidth = 0.6
    drawing.add(chart)
    return drawing


@lru_cache(maxsize=1)
def _get_clean_logo_bytes() -> bytes | None:
    logo_path = next((path for path in LOGO_CANDIDATES if path.exists()), None)

    # Si no existe el logo, no devuelve nada
    if logo_path is None:
        return None

    # Abre el logo y lo pasa a RGBA para trabajar transparencia
    image = PILImage.open(logo_path).convert("RGBA")
    cleaned = []

    # Recorre los píxeles para limpiar zonas muy oscuras
    # así el logo se ve mejor en el PDF
    for r, g, b, a in image.getdata():
        if a == 0:
            cleaned.append((r, g, b, a))
            continue
        if r < 22 and g < 22 and b < 22:
            cleaned.append((r, g, b, 0))
        else:
            cleaned.append((r, g, b, a))

    # Reemplaza los píxeles por la versión limpia
    image.putdata(cleaned)

    # Guarda el resultado en memoria y lo devuelve en bytes
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _build_report_header(total_width: float, styles) -> Table:
    # Estilo del título principal del encabezado
    title_style = ParagraphStyle(
        "BonGustoHeaderTitle",
        parent=styles["Heading1"],
        textColor=BRAND_COLOR,
        fontSize=18,
        leading=22,
        spaceAfter=0,
        alignment=TA_LEFT,
    )

    # Estilo para texto secundario
    subtitle_style = ParagraphStyle(
        "BonGustoHeaderSubtitle",
        parent=styles["BodyText"],
        textColor=MUTED_COLOR,
        fontSize=9.2,
        leading=12,
        spaceAfter=0,
        alignment=TA_LEFT,
    )

    # Estilo para datos pequeños como la fecha
    meta_style = ParagraphStyle(
        "BonGustoHeaderMeta",
        parent=styles["BodyText"],
        textColor=MUTED_COLOR,
        fontSize=8.2,
        leading=10,
        spaceAfter=0,
        alignment=TA_LEFT,
    )

    # Tamaño del logo en el encabezado
    logo_size = 1.8 * cm
    logo_cell = ""

    # Intenta cargar el logo ya limpio
    logo_bytes = _get_clean_logo_bytes()
    if logo_bytes:
        logo = RLImage(io.BytesIO(logo_bytes), width=logo_size, height=logo_size)
        logo_cell = logo

    # Fecha y hora en la que se genera el PDF
    fecha_impresion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Texto que va al lado del logo
    copy = [
        Paragraph("BonGusto", title_style),
        Spacer(1, 0.06 * cm),
        Paragraph(f"Fecha y hora de impresión: {fecha_impresion}", meta_style),
    ]

    # Encabezado con logo a la izquierda y texto a la derecha
    header = Table([[logo_cell, copy]], colWidths=[2.3 * cm, total_width - (2.3 * cm)])

    # Ajustes visuales del encabezado
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
    # Estilo del pie de página
    footer_style = ParagraphStyle(
        "BonGustoFooter",
        parent=styles["BodyText"],
        textColor=MUTED_COLOR,
        fontSize=8.2,
        leading=10,
        alignment=TA_CENTER,
    )

    # Toma el año actual
    year = datetime.now().year

    # Devuelve el texto del footer
    return Paragraph(f"Copyright © {year} BonGusto. Todos los derechos reservados.", footer_style)


def crear_pdf(titulo: str, headers: list[str], rows: list[list]) -> bytes:
    """
    Genera un PDF simple con una sola tabla.

    :param titulo: título del reporte
    :param headers: encabezados de la tabla
    :param rows: filas de la tabla
    :return: bytes del PDF
    """
    # Buffer en memoria donde se arma el archivo
    buffer = io.BytesIO()

    # Configura el documento PDF en horizontal
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    # Carga estilos base
    styles = getSampleStyleSheet()

    # Estilo del título del reporte
    title_style = ParagraphStyle(
        "BonGustoTitle",
        parent=styles["Title"],
        textColor=BRAND_COLOR,
        fontSize=17,
        spaceAfter=8,
        alignment=TA_CENTER,
    )

    # Calcula el ancho disponible
    total_width = landscape(A4)[0] - 3 * cm

    # Lista de elementos que van dentro del PDF
    elements = []
    elements.append(_build_report_header(total_width, styles))
    elements.append(Spacer(1, 0.35 * cm))
    elements.append(Paragraph(titulo, title_style))
    elements.append(Spacer(1, 0.45 * cm))

    # Agrega la tabla principal
    table = _build_table(headers, rows, total_width)
    elements.append(table)
    elements.append(Spacer(1, 0.35 * cm))

    # Agrega el pie de página
    elements.append(_build_report_footer(total_width, styles))

    # Construye el PDF
    doc.build(elements)

    # Devuelve el archivo en bytes
    return buffer.getvalue()


def crear_pdf_compuesto(titulo: str, bloques: list[dict]) -> bytes:
    # Este genera un PDF más completo por secciones
    # Sirve cuando el reporte trae varias tablas o bloques

    buffer = io.BytesIO()

    # Configuración del documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    # Carga estilos base
    styles = getSampleStyleSheet()

    # Estilo del título principal
    title_style = ParagraphStyle(
        "BonGustoCompositeTitle",
        parent=styles["Title"],
        textColor=BRAND_COLOR,
        fontSize=17,
        spaceAfter=8,
        alignment=TA_CENTER,
    )

    # Estilo del título de cada sección
    section_style = ParagraphStyle(
        "BonGustoSectionTitle",
        parent=styles["Heading2"],
        textColor=HEADER_COLOR,
        fontSize=11.5,
        spaceBefore=0,
        spaceAfter=0,
        alignment=TA_LEFT,
    )

    # Estilo del texto normal dentro de una sección
    body_style = ParagraphStyle(
        "BonGustoBody",
        parent=styles["BodyText"],
        textColor=MUTED_COLOR,
        fontSize=8.6,
        leading=12,
        spaceAfter=0,
        alignment=TA_LEFT,
    )

    # Ancho total disponible
    total_width = landscape(A4)[0] - 3 * cm

    # Elementos iniciales del documento
    elements = [
        _build_report_header(total_width, styles),
        Spacer(1, 0.35 * cm),
        Paragraph(titulo, title_style),
        Spacer(1, 0.3 * cm),
    ]

    # Recorre todos los bloques del reporte
    for index, bloque in enumerate(bloques):
        intro_elements = []

        # Toma título y párrafo del bloque
        heading = bloque.get("heading")
        paragraph = bloque.get("paragraph")

        # Si tiene título, crea la tarjeta de sección
        if heading:
            intro_elements.append(_build_section_card(heading, paragraph, total_width, section_style, body_style))
            intro_elements.append(Spacer(1, 0.14 * cm))

        # Toma headers y filas
        headers = bloque.get("headers")
        rows = bloque.get("rows")

        chart = _build_auto_chart(headers or [], rows or [], total_width)
        if chart:
            intro_elements.append(chart)
            intro_elements.append(Spacer(1, 0.16 * cm))

        # Si hay headers, arma la tabla de ese bloque
        if headers:
            table = _build_table(headers, rows or [], total_width, bloque.get("col_widths"))

        # Si el bloque tiene contenido, se agrega al PDF
        # KeepTogether ayuda a que no se parta feo entre páginas
        if intro_elements:
            if index == 0:
                elements.extend(intro_elements)
            else:
                elements.append(KeepTogether(intro_elements))

        if headers:
            elements.append(table)

        # Espacio entre bloques
        elements.append(Spacer(1, 0.3 * cm))

    # Espacio final antes del footer
    elements.append(Spacer(1, 0.15 * cm))

    # Agrega el pie de página
    elements.append(_build_report_footer(total_width, styles))

    # Construye el PDF completo
    doc.build(elements)

    # Devuelve el archivo en bytes
    return buffer.getvalue()
