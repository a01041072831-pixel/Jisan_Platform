# -*- coding: utf-8 -*-
"""
PDF 생성 모듈 - 템플릿 PDF의 마커를 제거하고 사용자 데이터를 삽입합니다.
tkinter 의존성 없이 독립적으로 동작하며, PDF bytes를 반환합니다.
"""
import json
from pathlib import Path

import fitz  # PyMuPDF

# ── 경로 설정 ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
TEMPLATE_DIR = PROJECT_ROOT / "templates"
FONT_PATH = "C:/Windows/Fonts/malgun.ttf"

# ── 배경색 (원본 PDF 살색 배경) ─────────────────────────────
BG_COLOR = (0.984, 0.961, 0.906)  # RGB(251, 245, 231)

# ── 필드 좌표 맵핑 ──────────────────────────────────────────
# 각 항목: (page_index, marker_bbox, insert_x, insert_y)
FIELD_MAP = {
    # Page 0 (손해사정업무위임장)
    "사고당사자_p0": (0, (143.5, 112.5, 213.5, 123.5), 163.5, 124.0),
    "작성날짜_p0":   (0, (428.5, 607.6, 484.5, 618.6), 448.5, 619.0),
    "위임인_p0":     (0, (197.0, 640.6, 248.3, 651.6), 217.0, 652.0),
    "관계_p0":       (0, (459.0, 638.0, 487.0, 649.0), 459.0, 650.0),
    "주민번호_p0":   (0, (198.0, 667.1, 254.0, 678.1), 218.0, 679.0),
    "연락처_p0":     (0, (425.5, 667.1, 467.5, 678.1), 445.5, 679.0),

    # Page 1 (손해사정보수약정서)
    "사고당사자_p1": (1, (165.5, 173.0, 235.5, 184.0), 185.5, 185.0),
    "보수율_p1":     (1, (257.5, 466.1, 299.5, 477.1), 277.5, 478.0),
    "보수율2_p1":    (1, (358.5, 468.6, 408.5, 479.6), 378.5, 480.0),

    # Page 2 (특약사항)
    "작성날짜_p2":   (2, (415.0, 295.1, 471.0, 306.1), 435.0, 307.0),
    "위임인_p2":     (2, (199.0, 328.0, 241.0, 339.0), 219.0, 340.0),
    "관계_p2":       (2, (459.5, 329.1, 487.5, 340.1), 459.5, 341.0),
    "주민번호_p2":   (2, (201.0, 360.6, 257.0, 371.6), 221.0, 372.0),
    "연락처_p2":     (2, (426.0, 361.1, 468.0, 372.1), 446.0, 373.0),
    "주소_p2":       (2, (202.5, 391.6, 230.5, 402.6), 222.5, 403.0),

    # Page 3 (개인정보동의서)
    "위임인_p3":     (3, (207.5, 672.1, 249.5, 683.1), 227.5, 684.0),
    "관계_p3":       (3, (486.0, 671.6, 514.0, 682.6), 486.0, 683.0),
}

# 사용자 입력 필드 → FIELD_MAP 키 맵핑
INPUT_TO_FIELDS = {
    "사고당사자": ["사고당사자_p0", "사고당사자_p1"],
    "작성날짜":   ["작성날짜_p0", "작성날짜_p2"],
    "위임인":     ["위임인_p0", "위임인_p2", "위임인_p3"],
    "관계":       ["관계_p0", "관계_p2", "관계_p3"],
    "주민번호":   ["주민번호_p0", "주민번호_p2"],
    "연락처":     ["연락처_p0", "연락처_p2"],
    "보수율":     ["보수율_p1"],
    "보수율2":    ["보수율2_p1"],
    "주소":       ["주소_p2"],
}


def load_coords(config_name: str) -> dict:
    """config 폴더에서 좌표 JSON을 로드합니다."""
    config_path = CONFIG_DIR / config_name
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_contract_pdf(
    사고당사자: str,
    위임인: str,
    주민번호: str,
    연락처: str,
    주소: str,
    관계: str = "",
    보수율: str = "",
    보수율한글: str = "",
    작성날짜: str = "",
) -> bytes:
    """
    계약서 템플릿 PDF에서 마커를 제거하고 사용자 데이터를 삽입하여
    완성된 PDF를 bytes로 반환합니다.

    Returns:
        생성된 PDF의 bytes 데이터
    """
    template_path = TEMPLATE_DIR / "지산법인 계약서 2026.pdf"
    if not Path(template_path).exists():
        raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {template_path}")

    data = {
        "사고당사자": 사고당사자,
        "위임인": 위임인,
        "주민번호": 주민번호,
        "연락처": 연락처,
        "주소": 주소,
        "관계": 관계,
        "보수율": 보수율,
        "보수율2": 보수율한글,
        "작성날짜": 작성날짜,
    }

    doc = fitz.open(template_path)

    # Step 1: 모든 Gulim 마커에 대해 redaction annotation 추가
    for field_key, (page_idx, bbox, _, _) in FIELD_MAP.items():
        page = doc[page_idx]
        rect = fitz.Rect(bbox)
        annot = page.add_redact_annot(rect)
        annot.set_colors(fill=BG_COLOR)

    # Step 2: redaction 적용 (마커 텍스트 제거)
    for page in doc:
        page.apply_redactions()

    # Step 3: 각 페이지에 폰트 등록
    font_name = "malgun"
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        page.insert_font(fontname=font_name, fontfile=FONT_PATH)

    # Step 4: 사용자 데이터 삽입
    for input_field, field_keys in INPUT_TO_FIELDS.items():
        value = data.get(input_field, "")
        if not value:
            continue
        for field_key in field_keys:
            page_idx, _, ins_x, ins_y = FIELD_MAP[field_key]
            page = doc[page_idx]
            page.insert_text(
                point=fitz.Point(ins_x, ins_y),
                text=value,
                fontname=font_name,
                fontsize=10,
                color=(0, 0, 0),
            )

    # Step 5: 폰트 서브셋 및 bytes 반환
    doc.subset_fonts()
    pdf_bytes = doc.tobytes(deflate=True, garbage=4)
    doc.close()

    return pdf_bytes
