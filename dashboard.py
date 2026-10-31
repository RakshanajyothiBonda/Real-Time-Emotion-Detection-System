"""MoodLens - Emotion Analytics Dashboard."""

import csv
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "emotion_log.csv"

BG = "#F4F7FB"
PANEL = "#FFFFFF"
INK = "#172033"
MUTED = "#667085"
ACCENT = "#4F46E5"
BORDER = "#E5EAF2"

EMOTION_COLORS = {
    "Happy": "#16A36A",
    "Sad": "#3B82F6",
    "Angry": "#EF4444",
    "Fear": "#8B5CF6",
    "Surprise": "#F59E0B",
    "Neutral": "#64748B",
    "Disgust": "#0D9488",
    "Uncertain Expression": "#D97706",
}


def load_rows():
    if not LOG_FILE.exists():
        return []

    with LOG_FILE.open("r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def emotion_color(emotion):
    return EMOTION_COLORS.get(emotion, ACCENT)


def generate_pdf_report(rows):
    """Generate a professional MoodLens PDF analytics report."""

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import (
            getSampleStyleSheet,
            ParagraphStyle
        )
        from reportlab.lib.units import mm

        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            KeepTogether
        )

        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.charts.piecharts import Pie
        from reportlab.graphics.charts.barcharts import VerticalBarChart
        from reportlab.graphics.charts.linecharts import HorizontalLineChart

    except ImportError:
        messagebox.showerror(
            "PDF Library Missing",
            "ReportLab is not installed.\n"
            "Run: python -m pip install reportlab"
        )
        return

    # --------------------------------------------------
    # REPORT SETTINGS
    # --------------------------------------------------

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    default_name = (
        f"MoodLens_Professional_Report_{timestamp}.pdf"
    )

    output_path = filedialog.asksaveasfilename(
        title="Export MoodLens Analytics Report",
        defaultextension=".pdf",
        initialfile=default_name,
        filetypes=[("PDF Files", "*.pdf")]
    )

    if not output_path:
        return

    # --------------------------------------------------
    # COLORS
    # --------------------------------------------------

    NAVY = colors.HexColor("#172033")
    PURPLE = colors.HexColor("#4F46E5")
    LIGHT_BG = colors.HexColor("#F4F7FB")
    MUTED = colors.HexColor("#667085")
    BORDER = colors.HexColor("#E5EAF2")

    chart_colors = [
        colors.HexColor("#16A36A"),
        colors.HexColor("#3B82F6"),
        colors.HexColor("#EF4444"),
        colors.HexColor("#8B5CF6"),
        colors.HexColor("#F59E0B"),
        colors.HexColor("#64748B"),
        colors.HexColor("#0D9488"),
        colors.HexColor("#D97706")
    ]

    # --------------------------------------------------
    # PROCESS EMOTION DATA
    # --------------------------------------------------

    counts = {}
    confidence_values = []

    for row in rows:

        emotion = (
            row.get("Emotion") or ""
        ).strip().title()

        if emotion:
            counts[emotion] = (
                counts.get(emotion, 0) + 1
            )

        try:
            confidence = float(
                row.get("Confidence", "")
            )

            if 0 <= confidence <= 100:
                confidence_values.append(confidence)

        except (ValueError, TypeError):
            pass

    total_records = len(rows)

    emotion_types = len(counts)

    most_frequent = (
        max(counts, key=counts.get)
        if counts else "—"
    )

    average_confidence = (
        sum(confidence_values) / len(confidence_values)
        if confidence_values else None
    )

    average_text = (
        f"{average_confidence:.2f}%"
        if average_confidence is not None
        else "Not available"
    )

    sorted_emotions = sorted(
        counts.items(),
        key=lambda item: item[1],
        reverse=True
    )

    # --------------------------------------------------
    # PDF DOCUMENT
    # --------------------------------------------------

    document = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "MoodLensTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=23,
        leading=28,
        textColor=colors.white,
        alignment=0,
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        "MoodLensSubtitle",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#DCE2FF"),
        leading=13
    )

    section_style = ParagraphStyle(
        "MoodLensSection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=NAVY,
        spaceBefore=8,
        spaceAfter=10
    )

    small_style = ParagraphStyle(
        "MoodLensSmall",
        parent=styles["Normal"],
        fontSize=8,
        leading=12,
        textColor=MUTED
    )

    story = []

    # --------------------------------------------------
    # BRANDED HEADER
    # --------------------------------------------------

    header_content = [
        Paragraph("MOODLENS", title_style),

        Paragraph(
            "REAL-TIME EMOTION DETECTION SYSTEM",
            subtitle_style
        ),

        Spacer(1, 8),

        Paragraph(
            "EMOTION ANALYTICS REPORT",
            ParagraphStyle(
                "ReportLabel",
                parent=subtitle_style,
                fontName="Helvetica-Bold",
                fontSize=10
            )
        )
    ]

    header = Table(
        [[header_content]],
        colWidths=[178 * mm]
    )

    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("BOX", (0, 0), (-1, -1), 0, NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 18),
        ("RIGHTPADDING", (0, 0), (-1, -1), 18),
        ("TOPPADDING", (0, 0), (-1, -1), 17),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 17)
    ]))

    story.append(header)
    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            f"Generated on: "
            f"{datetime.now().strftime('%d %B %Y, %I:%M %p')}",
            small_style
        )
    )

    story.append(Spacer(1, 15))

    # --------------------------------------------------
    # SUMMARY STATISTICS
    # --------------------------------------------------

    story.append(
        Paragraph("PROJECT SUMMARY", section_style)
    )

    summary_items = [
        ("TOTAL RECORDS", f"{total_records:,}"),
        ("EMOTION TYPES", str(emotion_types)),
        ("MOST FREQUENT", most_frequent),
        ("AVERAGE CONFIDENCE", average_text)
    ]

    summary_cells = []

    for label, value in summary_items:

        cell_content = [
            Paragraph(
                label,
                ParagraphStyle(
                    "CardLabel",
                    fontName="Helvetica-Bold",
                    fontSize=7,
                    textColor=MUTED
                )
            ),

            Spacer(1, 7),

            Paragraph(
                str(value),
                ParagraphStyle(
                    "CardValue",
                    fontName="Helvetica-Bold",
                    fontSize=13,
                    textColor=NAVY
                )
            )
        ]

        summary_cells.append(cell_content)

    summary_table = Table(
        [summary_cells],
        colWidths=[44.5 * mm] * 4
    )

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.6, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12)
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 17))

    # --------------------------------------------------
    # EMOTION DISTRIBUTION TABLE
    # --------------------------------------------------

    story.append(
        Paragraph("EMOTION DISTRIBUTION", section_style)
    )

    distribution_data = [
        ["EMOTION", "RECORDS", "PERCENTAGE"]
    ]

    for emotion, count in sorted_emotions:

        percentage = (
            count / total_records * 100
            if total_records else 0
        )

        distribution_data.append([
            emotion,
            str(count),
            f"{percentage:.1f}%"
        ])

    if not sorted_emotions:
        distribution_data.append([
            "No records",
            "0",
            "0.0%"
        ])

    distribution_table = Table(
        distribution_data,
        colWidths=[
            75 * mm,
            45 * mm,
            58 * mm
        ],
        repeatRows=1
    )

    distribution_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, LIGHT_BG]),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 8)
    ]))

    story.append(distribution_table)
    story.append(Spacer(1, 17))

    # --------------------------------------------------
    # PIE CHART AND BAR CHART
    # --------------------------------------------------

    if sorted_emotions:

        story.append(
            Paragraph("VISUAL EMOTION ANALYSIS", section_style)
        )

        # PIE CHART
        pie_drawing = Drawing(235, 175)

        pie = Pie()
        pie.x = 48
        pie.y = 20
        pie.width = 130
        pie.height = 130

        pie.data = [
            count for emotion, count in sorted_emotions
        ]

        pie.labels = [
            f"{emotion} ({count})"
            for emotion, count in sorted_emotions
        ]

        pie.slices.strokeWidth = 0.5
        pie.slices.strokeColor = colors.white

        for index in range(len(sorted_emotions)):
            pie.slices[index].fillColor = (
                chart_colors[index % len(chart_colors)]
            )

        pie_drawing.add(pie)

        # BAR CHART
        bar_drawing = Drawing(250, 175)

        bar_chart = VerticalBarChart()

        bar_chart.x = 35
        bar_chart.y = 30
        bar_chart.width = 190
        bar_chart.height = 110

        bar_chart.data = [[
            count for emotion, count in sorted_emotions
        ]]

        bar_chart.categoryAxis.categoryNames = [
            emotion[:9]
            for emotion, count in sorted_emotions
        ]

        bar_chart.categoryAxis.labels.fontSize = 7
        bar_chart.categoryAxis.labels.angle = 25

        bar_chart.valueAxis.valueMin = 0

        maximum = max(
            count for emotion, count in sorted_emotions
        )

        bar_chart.valueAxis.valueMax = max(5, maximum * 1.2)

        bar_chart.valueAxis.valueStep = max(
            1,
            (int(bar_chart.valueAxis.valueMax) // 5) or 1
        )

        bar_chart.bars[0].fillColor = PURPLE
        bar_chart.bars[0].strokeColor = PURPLE

        bar_drawing.add(bar_chart)

        chart_table = Table(
            [[pie_drawing, bar_drawing]],
            colWidths=[89 * mm, 89 * mm]
        )

        chart_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("BACKGROUND", (0, 0), (-1, -1), colors.white)
        ]))

        story.append(chart_table)
        story.append(Spacer(1, 15))

    # --------------------------------------------------
    # CONFIDENCE TREND CHART
    # --------------------------------------------------

    if confidence_values:

        story.append(
            Paragraph("CONFIDENCE TREND", section_style)
        )

        recent_confidence = confidence_values[-20:]

        line_drawing = Drawing(480, 155)

        line_chart = HorizontalLineChart()

        line_chart.x = 42
        line_chart.y = 35
        line_chart.width = 405
        line_chart.height = 90

        line_chart.data = [
            tuple(recent_confidence)
        ]

        line_chart.categoryAxis.categoryNames = [
            str(index + 1)
            for index in range(len(recent_confidence))
        ]

        line_chart.categoryAxis.labels.fontSize = 7

        line_chart.valueAxis.valueMin = 0
        line_chart.valueAxis.valueMax = 100
        line_chart.valueAxis.valueStep = 20

        line_chart.lines[0].strokeColor = PURPLE
        line_chart.lines[0].strokeWidth = 2

        line_drawing.add(line_chart)

        story.append(line_drawing)
        story.append(Spacer(1, 15))

    # --------------------------------------------------
    # RECENT EMOTION RECORDS
    # --------------------------------------------------

    story.append(
        Paragraph("RECENT DETECTION RECORDS", section_style)
    )

    recent_data = [
        ["RECORD", "EMOTION", "CONFIDENCE"]
    ]

    start_index = max(1, total_records - 14)

    for index, row in enumerate(
        rows[-15:],
        start=start_index
    ):

        emotion = (
            row.get("Emotion") or "Unknown"
        ).strip()

        confidence = (
            row.get("Confidence") or "—"
        ).strip()

        recent_data.append([
            str(index),
            emotion,
            confidence
        ])

    if len(recent_data) == 1:
        recent_data.append([
            "—",
            "No records available",
            "—"
        ])

    recent_table = Table(
        recent_data,
        colWidths=[
            35 * mm,
            85 * mm,
            58 * mm
        ],
        repeatRows=1
    )

    recent_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, LIGHT_BG]),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 7)
    ]))

    story.append(recent_table)
    story.append(Spacer(1, 18))

    # --------------------------------------------------
    # REPORT DISCLAIMER
    # --------------------------------------------------

    story.append(
        Paragraph(
            "<b>Important Note:</b> MoodLens uses AI-based facial "
            "expression analysis to estimate emotions. These results "
            "are predictions and should not be treated as a medical "
            "diagnosis or a definitive measurement of a person's feelings.",
            small_style
        )
    )

    # --------------------------------------------------
    # PAGE FOOTER
    # --------------------------------------------------

    def add_page_footer(canvas, doc):

        canvas.saveState()

        canvas.setStrokeColor(BORDER)
        canvas.line(
            16 * mm,
            12 * mm,
            A4[0] - 16 * mm,
            12 * mm
        )

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)

        canvas.drawString(
            16 * mm,
            8 * mm,
            "MoodLens | Emotion Analytics"
        )

        canvas.drawRightString(
            A4[0] - 16 * mm,
            8 * mm,
            f"Page {doc.page}"
        )

        canvas.restoreState()

    # --------------------------------------------------
    # GENERATE PDF
    # --------------------------------------------------

    try:

        document.build(
            story,
            onFirstPage=add_page_footer,
            onLaterPages=add_page_footer
        )

        messagebox.showinfo(
            "Report Generated Successfully",
            "Your professional MoodLens PDF report "
            f"has been saved successfully:\n\n{output_path}"
        )

    except Exception as exc:

        messagebox.showerror(
            "PDF Generation Error",
            f"Could not generate the PDF report:\n\n{exc}"
        )


def create_card(parent, title, value):
    card = tk.Frame(parent, bg="#F7F8FC", padx=16, pady=14)
    card.pack(side="left", fill="both", expand=True, padx=5)

    tk.Label(
        card,
        text=title,
        bg="#F7F8FC",
        fg=MUTED,
        font=("Segoe UI", 8, "bold")
    ).pack(anchor="w")

    tk.Label(
        card,
        text=value,
        bg="#F7F8FC",
        fg=INK,
        font=("Segoe UI", 17, "bold")
    ).pack(anchor="w", pady=(7, 0))


def create_section(parent, title):
    section = tk.Frame(
        parent,
        bg=PANEL,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    section.pack(fill="both", expand=True, padx=22, pady=(0, 14))

    tk.Label(
        section,
        text=title,
        bg=PANEL,
        fg=INK,
        font=("Segoe UI", 12, "bold")
    ).pack(anchor="w", padx=18, pady=(14, 8))

    return section


def draw_emotion_history(canvas, rows):
    canvas.delete("all")

    width = max(canvas.winfo_width(), 500)
    height = max(canvas.winfo_height(), 180)
    recent = rows[-20:]

    emotions = [
        "Happy", "Sad", "Angry", "Fear",
        "Surprise", "Neutral", "Disgust",
        "Uncertain Expression"
    ]

    left = 145
    right = width - 25
    top = 15
    bottom = height - 15
    row_height = (bottom - top) / len(emotions)

    for index, emotion in enumerate(emotions):
        y = top + index * row_height + row_height / 2

        canvas.create_text(
            left - 12, y,
            text=emotion,
            anchor="e",
            fill=MUTED,
            font=("Segoe UI", 8)
        )
        canvas.create_line(left, y, right, y, fill="#EEF0F6")

    if not recent:
        canvas.create_text(
            width / 2, height / 2,
            text="No emotion history available yet.",
            fill=MUTED,
            font=("Segoe UI", 10)
        )
        return

    step = (right - left) / max(1, len(recent) - 1)

    for index, record in enumerate(recent):
        emotion = (record.get("Emotion") or "").strip().title()
        if emotion not in emotions:
            continue

        emotion_index = emotions.index(emotion)
        x = left + index * step
        y = top + emotion_index * row_height + row_height / 2
        color = emotion_color(emotion)

        canvas.create_oval(
            x - 5, y - 5, x + 5, y + 5,
            fill=color,
            outline=color
        )

    canvas.create_text(
        left, height - 3,
        text="Older detections",
        anchor="sw",
        fill=MUTED,
        font=("Segoe UI", 8)
    )
    canvas.create_text(
        right, height - 3,
        text="Latest detection",
        anchor="se",
        fill=MUTED,
        font=("Segoe UI", 8)
    )


def draw_confidence_chart(canvas, rows):
    canvas.delete("all")

    width = max(canvas.winfo_width(), 500)
    height = max(canvas.winfo_height(), 180)
    recent = rows[-20:]

    left = 48
    right = width - 25
    top = 15
    bottom = height - 35
    chart_height = bottom - top

    for percentage in range(0, 101, 20):
        y = bottom - (percentage / 100) * chart_height
        canvas.create_line(left, y, right, y, fill="#E9EDF5")
        canvas.create_text(
            left - 10, y,
            text=str(percentage),
            anchor="e",
            fill=MUTED,
            font=("Segoe UI", 8)
        )

    if not recent:
        canvas.create_text(
            width / 2, height / 2,
            text="No confidence data available yet.",
            fill=MUTED,
            font=("Segoe UI", 10)
        )
        return

    values = []
    for record in recent:
        try:
            value = float(record.get("Confidence", 0))
            values.append(max(0, min(100, value)))
        except (ValueError, TypeError):
            values.append(None)

    if not any(value is not None for value in values):
        canvas.create_text(
            width / 2, height / 2,
            text="No valid confidence values found.",
            fill=MUTED
        )
        return

    step = (right - left) / max(1, len(values) - 1)
    previous = None

    for index, value in enumerate(values):
        if value is None:
            previous = None
            continue

        x = left + index * step
        y = bottom - (value / 100) * chart_height

        if previous is not None:
            canvas.create_line(
                previous[0], previous[1], x, y,
                fill=ACCENT,
                width=2
            )

        canvas.create_oval(
            x - 4, y - 4, x + 4, y + 4,
            fill=ACCENT,
            outline=ACCENT
        )
        previous = (x, y)

    canvas.create_text(
        left, height - 8,
        text="Older detections",
        anchor="sw",
        fill=MUTED,
        font=("Segoe UI", 8)
    )
    canvas.create_text(
        right, height - 8,
        text="Latest detection",
        anchor="se",
        fill=MUTED,
        font=("Segoe UI", 8)
    )


def main():
    root = tk.Tk()
    root.title("MoodLens | Emotion Analytics")
    root.geometry("1000x900")
    root.minsize(800, 700)
    root.configure(bg=BG)

    # Header
    header_frame = tk.Frame(root, bg=BG)
    header_frame.pack(fill="x", padx=28, pady=(22, 3))

    tk.Label(
        header_frame,
        text="Emotion analytics",
        bg=BG,
        fg=INK,
        font=("Segoe UI", 23, "bold")
    ).pack(side="left")

    tk.Label(
        header_frame,
        text="[LIVE]",
        bg=BG,
        fg="#16A34A",
        font=("Segoe UI", 9, "bold")
    ).pack(side="left", padx=15)

    # Subtitle
    tk.Label(
        root,
        text="Explore emotion history and confidence trends from saved sessions.",
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 10)
    ).pack(anchor="w", padx=28, pady=(0, 14))

    # Main panel with vertical scrolling
    body_outer = tk.Frame(
        root,
        bg=PANEL,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    body_outer.pack(
        fill="both",
        expand=True,
        padx=28,
        pady=(0, 14)
    )

    scroll_canvas = tk.Canvas(
        body_outer,
        bg=PANEL,
        highlightthickness=0
    )
    scrollbar = tk.Scrollbar(
        body_outer,
        orient="vertical",
        command=scroll_canvas.yview
    )
    scroll_canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    scroll_canvas.pack(side="left", fill="both", expand=True)

    body = tk.Frame(scroll_canvas, bg=PANEL)
    body_window = scroll_canvas.create_window(
        (0, 0),
        window=body,
        anchor="nw"
    )

    def update_scroll_region(event):
        scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

    body.bind("<Configure>", update_scroll_region)
    scroll_canvas.bind(
        "<Configure>",
        lambda event: scroll_canvas.itemconfigure(
            body_window,
            width=event.width
        )
    )

    # Analytics content container
    analytics_content = tk.Frame(body, bg=PANEL)
    analytics_content.pack(fill="both", expand=True)

    rows = []
    history_canvas = None
    confidence_canvas = None

    def refresh_analytics():
        nonlocal rows, history_canvas, confidence_canvas

        try:
            rows = load_rows()
        except (OSError, csv.Error) as exc:
            messagebox.showerror("Could not read log", str(exc))
            return

        for widget in analytics_content.winfo_children():
            widget.destroy()

        counts = {}
        for row in rows:
            emotion = (row.get("Emotion") or "").strip().title()
            if emotion:
                counts[emotion] = counts.get(emotion, 0) + 1

        # Summary cards
        summary = tk.Frame(analytics_content, bg=PANEL)
        summary.pack(fill="x", padx=17, pady=16)

        create_card(summary, "TOTAL RECORDS", f"{len(rows):,}")
        create_card(summary, "EMOTION TYPES", str(len(counts)))
        create_card(
            summary,
            "MOST FREQUENT",
            max(counts, key=counts.get) if counts else "—"
        )

        # Emotion distribution
        distribution = create_section(
            analytics_content,
            "Emotion distribution"
        )
        distribution_content = tk.Frame(distribution, bg=PANEL)
        distribution_content.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(0, 14)
        )

        if not counts:
            tk.Label(
                distribution_content,
                text="No emotion data yet. Start a webcam session to build your report.",
                bg=PANEL,
                fg=MUTED,
                font=("Segoe UI", 9)
            ).pack(anchor="w", pady=8)
        else:
            max_count = max(counts.values()) or 1

            for emotion, count in sorted(
                counts.items(),
                key=lambda item: item[1],
                reverse=True
            ):
                line = tk.Frame(distribution_content, bg=PANEL)
                line.pack(fill="x", pady=3)

                tk.Label(
                    line,
                    text=emotion,
                    width=18,
                    anchor="w",
                    bg=PANEL,
                    fg=INK,
                    font=("Segoe UI", 9, "bold")
                ).pack(side="left")

                track = tk.Frame(line, bg="#EEF0F8", height=13)
                track.pack(
                    side="left",
                    fill="x",
                    expand=True,
                    padx=10
                )
                track.pack_propagate(False)

                bar_width = max(4, int(300 * count / max_count))
                tk.Frame(
                    track,
                    bg=emotion_color(emotion),
                    width=bar_width,
                    height=13
                ).pack(side="left", fill="y")

                tk.Label(
                    line,
                    text=f"{count} ({count / max(1, len(rows)):.0%})",
                    width=12,
                    anchor="e",
                    bg=PANEL,
                    fg=MUTED,
                    font=("Segoe UI", 9)
                ).pack(side="right")

        # Emotion history chart
        history_section = create_section(
            analytics_content,
            "Recent emotion history"
        )
        history_canvas = tk.Canvas(
            history_section,
            height=190,
            bg=PANEL,
            highlightthickness=0
        )
        history_canvas.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 10)
        )

        # Confidence trend chart
        confidence_section = create_section(
            analytics_content,
            "Confidence trend (%)"
        )
        confidence_canvas = tk.Canvas(
            confidence_section,
            height=190,
            bg=PANEL,
            highlightthickness=0
        )
        confidence_canvas.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 10)
        )

        def refresh_charts(event=None):
            draw_emotion_history(history_canvas, rows)
            draw_confidence_chart(confidence_canvas, rows)

        root.after(150, refresh_charts)
        history_canvas.bind("<Configure>", refresh_charts)
        confidence_canvas.bind("<Configure>", refresh_charts)

    # Refresh button in the header
    refresh_button = tk.Button(
        header_frame,
        text="Refresh Analytics",
        command=refresh_analytics,
        bg=ACCENT,
        fg="white",
        activebackground=ACCENT,
        activeforeground="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        cursor="hand2",
        padx=16,
        pady=8
    )
    refresh_button.pack(side="right", padx=5, pady=3)

    # Export current analytics as a PDF report
    report_button = tk.Button(
        header_frame,
        text="Download PDF Report",
        command=lambda: generate_pdf_report(rows),
        bg="#172033",
        fg="white",
        activebackground="#273449",
        activeforeground="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        cursor="hand2",
        padx=16,
        pady=8
    )
    report_button.pack(side="right", padx=5, pady=3)

    # Load analytics when dashboard opens
    refresh_analytics()

    # Footer
    tk.Label(
        root,
        text=(
            "Charts use saved CSV records. "
            "Emotion recognition is an AI estimate, not a diagnosis."
        ),
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 9)
    ).pack(anchor="w", padx=28, pady=(0, 12))

    root.mainloop()


if __name__ == "__main__":
    main()