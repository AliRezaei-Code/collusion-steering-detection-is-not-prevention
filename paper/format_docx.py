"""Build the official Apart-template DOCX from the Markdown draft.

The title/author/abstract block comes from
``reference/templates/apart-submission-template.docx``. Pandoc supplies the
body and math; this script replaces its title block, drops the optional Author
Contributions section, and applies the template's serif typography.

Input:  collusion_steering_draft.docx   (pandoc output; keeps OMML math)
Output: collusion_steering_draft_formatted.docx

Run:
    uv run --with python-docx python format_docx.py
"""

from __future__ import annotations

import copy
from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

SRC = "collusion_steering_draft.docx"
DST = "collusion_steering_draft_formatted.docx"
ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT.parents[1] / "reference" / "templates" / "apart-submission-template.docx"
FONT = "Old Standard TT"
TITLE = (
    "Detection Is Not Prevention: A Behavioral and Activation-Level Study "
    "of Collusion Steering in Multi-Agent LLMs"
)
AUTHOR = "Ali Rezaei"
AFFILIATION = "York University, Department of EECS"

GRAY = RGBColor(0x59, 0x59, 0x59)
PALE_BLUE = "F2F5FA"
BORDER = "BFBFBF"


def set_run_font(run, name: str, size: float | None = None, bold=None, italic=None, color=None):
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs"):
        rfonts.set(qn(attr), name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def set_style_font(style, name: str, size: float, bold=None, italic=None, color=None):
    style.font.name = name
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs"):
        rfonts.set(qn(attr), name)
    style.font.size = Pt(size)
    if bold is not None:
        style.font.bold = bold
    if italic is not None:
        style.font.italic = italic
    if color is not None:
        style.font.color.rgb = color


def shade_cell(cell, fill: str):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def _clear_cell(cell):
    tc = cell._tc
    for child in list(tc):
        if child.tag != qn("w:tcPr"):
            tc.remove(child)


def _add_cell_para(cell, text, size, *, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.CENTER):
    p = cell.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(text)
    set_run_font(r, FONT, size, bold=bold, italic=italic)
    return p


def fill_template_title_table(abstract: str):
    """Return the official template title table, filled for a solo author."""
    template = Document(str(TEMPLATE))
    table = template.tables[0]
    title_cell = table.rows[0].cells[0]
    title_para = next(
        (p for p in title_cell.paragraphs if p.text.strip() == "PROJECT TITLE"),
        title_cell.paragraphs[1],
    )
    for run in list(title_para.runs)[1:]:
        run._element.getparent().remove(run._element)
    if title_para.runs:
        title_para.runs[0].text = TITLE
        title_para.runs[0].font.superscript = False
        set_run_font(title_para.runs[0], FONT, 20, bold=True)
    else:
        set_run_font(title_para.add_run(TITLE), FONT, 20, bold=True)

    cell = table.rows[1].cells[0]
    _clear_cell(cell)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    _add_cell_para(cell, AUTHOR, 12)
    _add_cell_para(cell, AFFILIATION, 11)
    p = cell.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(6)
    set_run_font(p.add_run("Abstract"), FONT, 14, bold=True)
    p = cell.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    set_run_font(p.add_run(abstract), FONT, 10.5, italic=True)

    if len(template.tables) > 1:
        el = template.tables[1]._element
        el.getparent().remove(el)
    return table


def set_table_borders(table, color: str = BORDER, sz: str = "4"):
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), sz)
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)
    tbl_pr.append(borders)


def set_cell_margins(table, top=60, bottom=60, left=90, right=90):
    tbl_pr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for edge, value in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:w"), str(value))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tbl_pr.append(mar)


def repeat_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    tr_pr.append(header)


def no_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    cant = OxmlElement("w:cantSplit")
    tr_pr.append(cant)


def add_page_field(paragraph):
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)


def add_left_border_and_shade(paragraph, color="8EAADB", fill=PALE_BLUE):
    p_pr = paragraph._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), "18")
    left.set(qn("w:space"), "8")
    left.set(qn("w:color"), color)
    borders.append(left)
    p_pr.append(borders)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    p_pr.append(shd)


def main():
    doc = Document(SRC)

    # Page setup: US Letter, 1-inch margins.
    sec = doc.sections[0]
    sec.page_width = Inches(8.5)
    sec.page_height = Inches(11)
    sec.left_margin = Inches(0.85)
    sec.right_margin = Inches(0.85)
    sec.top_margin = Inches(0.8)
    sec.bottom_margin = Inches(0.8)
    sec.header_distance = Inches(0.5)
    sec.footer_distance = Inches(0.5)

    # Base styles.
    set_style_font(doc.styles["Body Text"], FONT, 9.8, color=RGBColor(0x1A, 0x1A, 0x1A))
    doc.styles["Body Text"].paragraph_format.line_spacing = 1.03
    doc.styles["Body Text"].paragraph_format.space_after = Pt(3)
    doc.styles["Body Text"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    set_style_font(doc.styles["First Paragraph"], FONT, 9.8, color=RGBColor(0x1A, 0x1A, 0x1A))
    doc.styles["First Paragraph"].paragraph_format.line_spacing = 1.03
    doc.styles["First Paragraph"].paragraph_format.space_after = Pt(3)
    doc.styles["First Paragraph"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    set_style_font(doc.styles["Compact"], FONT, 10)
    doc.styles["Compact"].paragraph_format.space_after = Pt(2)
    doc.styles["Compact"].paragraph_format.line_spacing = 1.05

    set_style_font(doc.styles["Block Text"], FONT, 9.5, italic=True, color=GRAY)
    doc.styles["Block Text"].paragraph_format.space_before = Pt(4)
    doc.styles["Block Text"].paragraph_format.space_after = Pt(8)
    doc.styles["Block Text"].paragraph_format.left_indent = Inches(0.05)

    set_style_font(doc.styles["Heading 1"], FONT, 18, bold=True, color=RGBColor(0,0,0))
    doc.styles["Heading 1"].paragraph_format.space_before = Pt(0)
    doc.styles["Heading 1"].paragraph_format.space_after = Pt(6)

    set_style_font(doc.styles["Heading 2"], FONT, 13.5, bold=True, color=RGBColor(0,0,0))
    doc.styles["Heading 2"].paragraph_format.space_before = Pt(14)
    doc.styles["Heading 2"].paragraph_format.space_after = Pt(4)
    doc.styles["Heading 2"].paragraph_format.keep_with_next = True

    set_style_font(doc.styles["Heading 3"], FONT, 11, bold=True, italic=True, color=RGBColor(0,0,0))
    doc.styles["Heading 3"].paragraph_format.space_before = Pt(10)
    doc.styles["Heading 3"].paragraph_format.space_after = Pt(3)
    doc.styles["Heading 3"].paragraph_format.keep_with_next = True

    if "Source Code" in doc.styles:
        set_style_font(doc.styles["Source Code"], "Consolas", 9, color=RGBColor(0x33, 0x33, 0x33))

    # Inline code. Pandoc tags every `backticked` span with the "Verbatim Char"
    # character style, whose default is 11 pt against a 9.5 pt body: the code
    # shouted louder than the sentences carrying it. Match the code blocks at
    # 9 pt so inline identifiers read as identifiers, not as headings.
    if "Verbatim Char" in doc.styles:
        set_style_font(doc.styles["Verbatim Char"], "Consolas", 9, color=RGBColor(0x33, 0x33, 0x33))

    # Page numbers. The rebuilt document drops the template's footer, so the
    # PDF had no page numbers at all. Add a centred PAGE field to every section.
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    for section in doc.sections:
        footer = section.footer
        footer.is_linked_to_previous = False
        para = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        para.alignment = 1  # centre
        if not para.text.strip():
            run = para.add_run()
            fld_begin = OxmlElement("w:fldChar"); fld_begin.set(qn("w:fldCharType"), "begin")
            instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = " PAGE "
            fld_end = OxmlElement("w:fldChar"); fld_end.set(qn("w:fldCharType"), "end")
            run._r.append(fld_begin); run._r.append(instr); run._r.append(fld_end)
            run.font.size = Pt(9)
            run.font.name = FONT

    # Capture the title table and abstract paragraph before restructuring.
    title_para = doc.paragraphs[0]
    old_title_table = doc.tables[0]
    abstract_para = doc.paragraphs[1]
    abstract_text = abstract_para.text
    if abstract_text.startswith("Abstract. "):
        abstract_text = abstract_text[len("Abstract. "):]

    # Use the official template's title table (black serif title, rules,
    # solo-author block, centered Abstract) instead of a custom box.
    title_table = fill_template_title_table(abstract_text)

    # Move the template title table to the very start of the body, then remove
    # pandoc's title heading, metadata table, and abstract paragraph.
    body = doc.element.body
    body.insert(0, copy.deepcopy(title_table._tbl))
    old_title_table._element.getparent().remove(old_title_table._element)
    abstract_para._element.getparent().remove(abstract_para._element)
    title_para._element.getparent().remove(title_para._element)

    # Remove the empty paragraph pandoc leaves after the new table, if present.
    first = body[0]
    # (The table itself is first; the old abstract paragraph is gone.)

    # Format content tables.
    for ti, table in enumerate(doc.tables[1:]):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = True
        first_header = table.rows[0].cells[0].text.strip() if table.rows else ""
        if len(table.columns) == 5 and first_header == "Condition":
            table.autofit = False
            widths = [
                Inches(2.0),
                Inches(0.35),
                Inches(1.35),
                Inches(1.35),
                Inches(1.35),
            ]
            for i, w in enumerate(widths):
                table.columns[i].width = w
            for row in table.rows:
                for i, w in enumerate(widths):
                    row.cells[i].width = w
        set_table_borders(table, color=BORDER, sz="4")
        set_cell_margins(table, top=30, bottom=30, left=70, right=70)
        for ri, row in enumerate(table.rows):
            no_split(row)
            if ri == 0:
                repeat_header(row)
            for cell in row.cells:
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                if ri == 0:
                    shade_cell(cell, "E8E8E8")
                for p in cell.paragraphs:
                    p.paragraph_format.space_after = Pt(0)
                    for run in p.runs:
                        run.font.size = Pt(9)
                    p.paragraph_format.line_spacing = 1.0
                    for r in p.runs:
                        set_run_font(
                            r,
                            FONT,
                            8.5,
                            bold=True if ri == 0 else None,
                            color=RGBColor(0,0,0),
                        )

    # Block quotes: left rule + pale fill.
    for p in doc.paragraphs:
        if p.style.name == "Block Text":
            add_left_border_and_shade(p)

    # Keep the reference list off the body's last page so the Word rendering
    # matches the canonical PDF (body ends p.8, references start p.9).
    for p in doc.paragraphs:
        if p.text.strip() == "References" and p.style.name.startswith("Heading"):
            p.paragraph_format.page_break_before = True
            break

    # Core properties.
    doc.core_properties.title = (
        "Detection Is Not Prevention: A Behavioral and Activation-Level "
        "Study of Collusion Steering in Multi-Agent LLMs"
    )
    doc.core_properties.author = "Ali Rezaei"
    doc.core_properties.subject = "Collusion steering"

    doc.save(DST)
    print(f"wrote {DST}")


if __name__ == "__main__":
    main()
