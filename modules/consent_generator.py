# -*- coding: utf-8 -*-
"""
동의서/위임장 PDF 생성 모듈
템플릿 PDF의 Gulim 14pt 플레이스홀더를 찾아 제거하고,
사용자 데이터를 삽입하여 PDF bytes를 반환합니다.
"""
from datetime import date
from pathlib import Path

import fitz  # PyMuPDF

# ── 경로 설정 ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATE_DIR = PROJECT_ROOT / "templates"
TEMPLATE_NAME = "의무기록_동의서위임장.pdf"
FONT_PATH = "C:/Windows/Fonts/malgun.ttf"

# ── 플레이스홀더 → (data dict 키, 폰트 크기) ───────────────
PLACEHOLDER_MAP = {
    "환자이름":       ("patient_name",      12),
    "환자생년월일":   ("patient_birth",     10),
    "환자전화번호":   ("patient_phone",     12),
    "환자의주소":     ("patient_address",   10),
    "신청인이름":     ("applicant_name",    12),
    "신청인생년월일": ("applicant_birth",   10),
    "신청인전화번호": ("applicant_phone",   12),
    "신청인주소":     ("applicant_address", 10),
    "관계":           ("relationship",      12),
}

# ── 날짜 삽입 좌표 (년/월/일 마커의 x0, 공통 y baseline) ───
DATE_COORDS = {
    0: {"year_x": 449.67, "month_x": 482.67, "day_x": 518.67, "y": 681.94},
    1: {"year_x": 415.00, "month_x": 469.00, "day_x": 518.33, "y": 453.27},
}


def _find_placeholder_rects(page, text: str) -> list:
    """Gulim 14pt 폰트의 플레이스홀더 rect 목록을 반환합니다."""
    rects = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                if (span["text"].strip() == text
                        and "Gulim" in span["font"]
                        and abs(span["size"] - 14.0) < 1.0):
                    rects.append(fitz.Rect(span["bbox"]))
    return rects


def _process_page(page, data: dict):
    """한 페이지의 모든 플레이스홀더를 redact → 새 텍스트로 대체합니다."""
    replacements = []

    for placeholder, (field_key, font_size) in PLACEHOLDER_MAP.items():
        value = data.get(field_key, "")
        if not value:
            continue
        rects = _find_placeholder_rects(page, placeholder)
        for rect in rects:
            replacements.append((rect, value, font_size))

    # 1단계: 모든 redact annotation 등록
    for rect, _, _ in replacements:
        page.add_redact_annot(rect, fill=(1, 1, 1))

    # 2단계: 일괄 적용
    if replacements:
        page.apply_redactions()

    # 3단계: 새 텍스트 삽입
    for rect, text, font_size in replacements:
        page.insert_text(
            fitz.Point(rect.x0, rect.y1 - 1),
            text,
            fontname="malgun",
            fontfile=FONT_PATH,
            fontsize=font_size,
            color=(0, 0, 0),
        )


def _text_width(text: str, fontsize: float) -> float:
    """맑은 고딕 폰트 기준 텍스트 너비를 계산합니다."""
    font = fitz.Font(fontfile=FONT_PATH)
    return font.text_length(text, fontsize=fontsize)


def _insert_date_on_page(page, page_idx: int, dt: date):
    """날짜를 페이지 하단의 년/월/일 마커 왼쪽에 삽입합니다."""
    coords = DATE_COORDS.get(page_idx)
    if not coords:
        return

    font_size = 9
    y = coords["y"]

    for text, key in [(str(dt.year), "year_x"), (str(dt.month), "month_x"), (str(dt.day), "day_x")]:
        tw = _text_width(text, font_size)
        page.insert_text(
            fitz.Point(coords[key] - tw - 1, y),
            text,
            fontname="malgun", fontfile=FONT_PATH,
            fontsize=font_size, color=(0, 0, 0),
        )


def create_consent_pdf(
    patient_name: str,
    patient_birth: str,
    patient_address: str,
    patient_phone: str,
    applicant_name: str,
    applicant_phone: str,
    relationship: str,
    applicant_address: str,
    applicant_birth: str = "",
    consent_date: date = None,
) -> bytes:
    """
    동의서/위임장 PDF를 생성하여 bytes로 반환합니다.

    Args:
        patient_name: 환자 성명
        patient_birth: 환자 생년월일/주민번호
        patient_address: 환자 주소
        patient_phone: 환자 연락처
        applicant_name: 신청인(수임인) 성명
        applicant_phone: 신청인 연락처
        relationship: 환자와의 관계
        applicant_address: 신청인 주소/소속
        applicant_birth: 신청인 생년월일 (선택)
        consent_date: 작성일자 (기본값: 오늘)

    Returns:
        생성된 PDF의 bytes 데이터
    """
    template_path = TEMPLATE_DIR / TEMPLATE_NAME
    if not template_path.exists():
        raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {template_path}")

    if consent_date is None:
        consent_date = date.today()

    data = {
        "patient_name":      patient_name,
        "patient_birth":     patient_birth,
        "patient_phone":     patient_phone,
        "patient_address":   patient_address,
        "applicant_name":    applicant_name,
        "applicant_birth":   applicant_birth,
        "applicant_phone":   applicant_phone,
        "applicant_address": applicant_address,
        "relationship":      relationship,
    }

    doc = fitz.open(str(template_path))

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        _process_page(page, data)
        _insert_date_on_page(page, page_idx, consent_date)

    pdf_bytes = doc.tobytes(deflate=True, garbage=4)
    doc.close()

    return pdf_bytes
