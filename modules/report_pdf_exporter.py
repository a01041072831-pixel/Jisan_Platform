# -*- coding: utf-8 -*-
"""
PDF 변환 모듈 - fpdf2로 마크다운을 PDF로 변환합니다.
한글 폰트(malgun.ttf)를 사용하며 표, 제목, 인용문 등을 지원합니다.
"""
import re
from pathlib import Path

from fpdf import FPDF

PROJECT_ROOT = Path(__file__).parent.parent
FONT_PATH = str(PROJECT_ROOT / "assets" / "fonts" / "malgun.ttf")


class ReportPDF(FPDF):
    """손해사정서용 PDF 클래스"""

    def __init__(self):
        super().__init__()
        self.add_font("malgun", "", FONT_PATH)
        self.add_font("malgun", "B", FONT_PATH)
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(20, 20, 20)

    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("malgun", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"- {self.page_no()} -", align="C")
        self.set_text_color(0, 0, 0)


def _clean_bold(text: str) -> str:
    """마크다운 bold(**...**) 제거"""
    return re.sub(r"\*\*(.+?)\*\*", r"\1", text)


def _clean_inline(text: str) -> str:
    """마크다운 인라인 서식 제거"""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    return text.strip()


def markdown_to_pdf(md_text: str) -> bytes:
    """마크다운 텍스트를 PDF bytes로 변환합니다."""
    # HTML 태그 정리
    text = re.sub(r"<div[^>]*>\s*</div>", "", md_text)
    text = re.sub(r"<div[^>]*>", "", text)
    text = re.sub(r"</div>", "", text)
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"<hr[^>]*>", "---PAGE_BREAK---", text)

    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_font("malgun", "", 11)

    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # 빈 줄
        if not line.strip():
            pdf.ln(3)
            i += 1
            continue

        # 페이지 넘김
        if "PAGE_BREAK" in line or "page-break" in line.lower():
            pdf.add_page()
            i += 1
            continue

        # 구분선
        if line.strip() in ("---", "***", "___"):
            pdf.ln(2)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(20, pdf.get_y(), 190, pdf.get_y())
            pdf.ln(4)
            i += 1
            continue

        # 제목 H1
        if line.startswith("# "):
            title = _clean_inline(line[2:])
            pdf.ln(4)
            pdf.set_font("malgun", "B", 16)
            pdf.multi_cell(0, 9, title)
            pdf.set_font("malgun", "", 11)
            pdf.ln(2)
            i += 1
            continue

        # 제목 H2
        if line.startswith("## "):
            title = _clean_inline(line[3:])
            pdf.ln(3)
            pdf.set_font("malgun", "B", 13)
            pdf.multi_cell(0, 8, title)
            pdf.set_font("malgun", "", 11)
            pdf.ln(1)
            i += 1
            continue

        # 제목 H3
        if line.startswith("### "):
            title = _clean_inline(line[4:])
            pdf.ln(2)
            pdf.set_font("malgun", "B", 11)
            pdf.multi_cell(0, 7, title)
            pdf.set_font("malgun", "", 11)
            pdf.ln(1)
            i += 1
            continue

        # 인용문
        if line.startswith("> "):
            pdf.set_text_color(80, 80, 80)
            pdf.set_x(25)
            pdf.multi_cell(165, 6, _clean_inline(line[2:]))
            pdf.set_text_color(0, 0, 0)
            i += 1
            continue

        # 리스트 항목
        if re.match(r"^[-*]\s", line.strip()):
            item = _clean_inline(line.strip()[2:])
            pdf.cell(8, 6, "  -")
            pdf.multi_cell(0, 6, item)
            i += 1
            continue

        # 번호 리스트
        m = re.match(r"^(\d+)\.\s(.+)", line.strip())
        if m:
            num, item = m.group(1), _clean_inline(m.group(2))
            pdf.cell(10, 6, f"  {num}.")
            pdf.multi_cell(0, 6, item)
            i += 1
            continue

        # 테이블
        if line.strip().startswith("|"):
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row_text = lines[i].strip()
                cells = [c.strip() for c in row_text.split("|")[1:-1]]
                # 구분선 행 건너뛰기
                if cells and not all(set(c) <= set("-: ") for c in cells):
                    table_rows.append(cells)
                i += 1

            if table_rows:
                num_cols = max(len(r) for r in table_rows)
                col_w = 170 / num_cols
                pdf.set_font("malgun", "", 9)

                for row_idx, row in enumerate(table_rows):
                    for col_idx in range(num_cols):
                        cell_text = _clean_inline(row[col_idx]) if col_idx < len(row) else ""
                        if row_idx == 0:
                            pdf.set_font("malgun", "B", 9)
                            pdf.set_fill_color(240, 240, 240)
                            pdf.cell(col_w, 7, cell_text, border=1, fill=True)
                            pdf.set_font("malgun", "", 9)
                        else:
                            pdf.cell(col_w, 7, cell_text, border=1)
                    pdf.ln()

                pdf.set_font("malgun", "", 11)
                pdf.ln(2)
            continue

        # 일반 텍스트
        clean = _clean_inline(line)
        if clean:
            pdf.multi_cell(0, 6, clean)
        i += 1

    return bytes(pdf.output())
