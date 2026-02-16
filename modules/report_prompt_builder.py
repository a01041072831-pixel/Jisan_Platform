# -*- coding: utf-8 -*-
"""
프롬프트 빌더 모듈 - MD 파일들을 로드하여 Gemini API 시스템 프롬프트로 조립합니다.
참고자료 PDF는 Gemini Vision OCR로 읽고 텍스트 캐시를 저장합니다.
"""
import json
from pathlib import Path

import fitz  # PyMuPDF

PROJECT_ROOT = Path(__file__).parent.parent
PROMPT_DIR = PROJECT_ROOT / "prompts" / "report"
REFERENCE_DIR = PROMPT_DIR / "참고자료"
CACHE_FILE = REFERENCE_DIR / "_cache.json"

# 01~06 순서대로 로드 (00_README.md는 인간용 안내서이므로 제외)
PROMPT_FILES = [
    "01_SYSTEM.md",
    "02_PROCESS.md",
    "03_DOCUMENT_STRUCTURE.md",
    "04_TONE_AND_STYLE.md",
    "05_DATA_PROTOCOL.md",
    "06_CHECKLIST.md",
]


def _extract_pdf_text_pymupdf(pdf_path: Path) -> str:
    """PyMuPDF로 텍스트 추출 시도. 한글 비율이 낮으면 빈 문자열 반환."""
    doc = fitz.open(pdf_path)
    raw = "\n".join(page.get_text() for page in doc)
    doc.close()
    korean_chars = sum(1 for c in raw if '\uac00' <= c <= '\ud7a3')
    if korean_chars > len(raw) * 0.1 and len(raw.strip()) > 100:
        return raw
    return ""


def _extract_pdf_text_gemini(pdf_path: Path) -> str:
    """Gemini에 PDF 파일을 직접 전송하여 텍스트 추출 (1회 API 호출)."""
    from google import genai
    from google.genai import types
    from modules.report_ai_client import get_api_key, DEFAULT_MODEL

    api_key = get_api_key()
    if not api_key:
        return "[API 키 미설정 - OCR 불가]"

    pdf_bytes = pdf_path.read_bytes()
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=[
                types.Content(role="user", parts=[
                    types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                    types.Part.from_text(
                        text="이 PDF 문서의 모든 텍스트를 원문 그대로 추출해주세요. "
                             "추가 설명 없이 문서 내용만 출력하세요."
                    ),
                ])
            ],
        )
        return response.text
    except Exception as e:
        return f"[PDF 텍스트 추출 실패: {e}]"


def _load_cache() -> dict:
    """캐시 파일 로드."""
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_cache(cache: dict):
    """캐시 파일 저장."""
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_reference_pdfs() -> str:
    """참고자료 폴더의 PDF를 읽어 텍스트로 변환. 캐시 사용."""
    if not REFERENCE_DIR.exists():
        return ""

    cache = _load_cache()
    parts = []
    updated = False

    for pdf_path in sorted(REFERENCE_DIR.glob("*.pdf")):
        fname = pdf_path.name
        # 캐시에 있고 파일 수정시간이 같으면 캐시 사용
        mtime = str(pdf_path.stat().st_mtime)
        if fname in cache and cache[fname].get("mtime") == mtime:
            text = cache[fname]["text"]
        else:
            # PyMuPDF 시도 → 실패 시 Gemini Vision OCR
            text = _extract_pdf_text_pymupdf(pdf_path)
            if not text:
                text = _extract_pdf_text_gemini(pdf_path)
            cache[fname] = {"mtime": mtime, "text": text}
            updated = True

        parts.append(f"### 참고자료: {fname}\n\n{text}")

    if updated:
        _save_cache(cache)

    if not parts:
        return ""
    return (
        "# 보고서 작성 참고자료\n\n"
        "아래는 손해사정서 작성 시 참고해야 할 법률, 약관, 판례 자료입니다.\n\n"
        + "\n\n---\n\n".join(parts)
    )


def load_prompt_files() -> str:
    """6개 프롬프트 MD 파일 + 참고자료 PDF를 읽어 하나의 시스템 프롬프트 문자열로 결합합니다."""
    parts = []
    for fname in PROMPT_FILES:
        fpath = PROMPT_DIR / fname
        if fpath.exists():
            parts.append(fpath.read_text(encoding="utf-8"))
        else:
            parts.append(f"[WARNING: {fname} 파일을 찾을 수 없습니다]")
    prompt = "\n\n---\n\n".join(parts)

    # 참고자료 PDF 텍스트 추가
    ref_text = _load_reference_pdfs()
    if ref_text:
        prompt += "\n\n---\n\n" + ref_text

    return prompt


def build_user_message(data: dict, uploaded_texts: list[str] | None = None) -> str:
    """폼 입력값 + 업로드 문서 텍스트를 사용자 메시지 형식으로 구성합니다."""
    lines = ["# 손해사정서 작성 요청\n"]

    # 피보험자 정보
    if data.get("insured_name"):
        lines.append("## 피보험자 인적사항")
        lines.append(f"- 성명: {data.get('insured_name', '정보 미제공')}")
        lines.append(f"- 생년월일: {data.get('insured_birth', '정보 미제공')}")
        lines.append(f"- 주소: {data.get('insured_address', '정보 미제공')}")
        lines.append(f"- 연락처: {data.get('insured_phone', '정보 미제공')}")
        lines.append("")

    # 보험계약사항
    contracts = data.get("contracts", [])
    if contracts:
        lines.append("## 보험계약사항")
        for i, c in enumerate(contracts, 1):
            lines.append(f"### 계약 {i}")
            lines.append(f"- 보험회사: {c.get('company', '정보 미제공')}")
            lines.append(f"- 보험종목: {c.get('product', '정보 미제공')}")
            lines.append(f"- 증권번호: {c.get('policy_no', '정보 미제공')}")
            lines.append(f"- 보험기간: {c.get('period', '정보 미제공')}")
            lines.append(f"- 담보내역: {c.get('coverage', '정보 미제공')}")
            lines.append("")

    # 사고정보
    if data.get("accident_date") or data.get("accident_desc"):
        lines.append("## 사고정보")
        lines.append(f"- 사고일시: {data.get('accident_date', '정보 미제공')}")
        lines.append(f"- 사고장소: {data.get('accident_place', '정보 미제공')}")
        lines.append(f"- 사고경위: {data.get('accident_desc', '정보 미제공')}")
        lines.append("")

    # 추가 입력사항
    if data.get("additional_info"):
        lines.append("## 추가 정보")
        lines.append(data["additional_info"])
        lines.append("")

    # 업로드된 문서 텍스트
    if uploaded_texts:
        lines.append("## 첨부자료 내용")
        for i, text in enumerate(uploaded_texts, 1):
            lines.append(f"### 첨부자료 {i}")
            lines.append(text)
            lines.append("")

    return "\n".join(lines)
