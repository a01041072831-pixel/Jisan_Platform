# -*- coding: utf-8 -*-
"""
Gemini AI 클라이언트 모듈 - Google Gemini API를 사용하여 손해사정 보고서를 생성합니다.
"""
import base64
from typing import Generator

import fitz  # PyMuPDF
import streamlit as st
from google import genai
from google.genai import types

# 기본 모델 설정
DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_MAX_TOKENS = 65536


_DEFAULT_KEY = "AIzaSyCkvNThgiJ3_2avUGozZUqTSWYHPTCOLEA"


def get_api_key() -> str | None:
    """API 키를 로드합니다. secrets.toml 우선, 없으면 기본 키 사용."""
    try:
        return st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        return _DEFAULT_KEY


def get_client(api_key: str | None = None) -> genai.Client:
    """Gemini API 클라이언트를 생성합니다."""
    key = api_key or get_api_key()
    if not key:
        raise ValueError("Gemini API 키가 설정되지 않았습니다.")
    return genai.Client(api_key=key)


def send_message(
    system_prompt: str,
    messages: list[dict],
    api_key: str | None = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    stream: bool = True,
) -> Generator[str, None, None] | str:
    """Gemini API로 메시지를 전송합니다.

    Args:
        system_prompt: 시스템 프롬프트 (MD 파일 통합본)
        messages: 대화 히스토리 [{"role": "user"|"model", "content": "..."}]
        api_key: API 키 (None이면 secrets에서 로드)
        model: 사용할 모델명
        max_tokens: 최대 토큰 수
        stream: 스트리밍 여부

    Returns:
        스트리밍 시 Generator[str], 아닐 시 str
    """
    client = get_client(api_key)

    # 대화 히스토리를 Gemini 형식으로 변환
    contents = []
    for msg in messages:
        role = msg["role"]
        # Gemini는 "user"와 "model" 역할만 사용
        if role == "assistant":
            role = "model"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])],
            )
        )

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        max_output_tokens=max_tokens,
        temperature=0.3,
    )

    if stream:
        # 제너레이터 안에서 클라이언트를 직접 사용하여 닫힘 방지
        def _stream_generator():
            c = genai.Client(api_key=api_key or get_api_key())
            response_stream = c.models.generate_content_stream(
                model=model,
                contents=contents,
                config=config,
            )
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        return _stream_generator()
    else:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )
        return response.text


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """PDF에서 텍스트를 추출합니다. PyMuPDF 실패 시 Gemini에 PDF 직접 전송 (1회 호출)."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # 먼저 PyMuPDF로 텍스트 추출 시도
    raw_texts = []
    for page in doc:
        raw_texts.append(page.get_text())
    raw = "\n".join(raw_texts)
    doc.close()

    # 한글이 충분히 포함되어 있으면 PyMuPDF 결과 사용
    korean_chars = sum(1 for c in raw if '\uac00' <= c <= '\ud7a3')
    if korean_chars > len(raw) * 0.1 and len(raw.strip()) > 100:
        return raw

    # 한글 추출 실패 → Gemini에 PDF 파일 직접 전송 (1회 API 호출)
    try:
        client = genai.Client(api_key=get_api_key())
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
