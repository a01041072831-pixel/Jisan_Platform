"""
지산 통합 자동화 플랫폼 - 메인 대시보드
"""
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="지산 통합 자동화 플랫폼",
    page_icon="🏠",
    layout="wide",
)

st.title("🏠 지산 통합 자동화 플랫폼")
st.markdown("---")
st.markdown(
    """
    ### 좌측 메뉴에서 원하는 기능을 선택하세요

    | 메뉴 | 설명 |
    |------|------|
    | 📝 계약서 작성 | 손해사정 업무 위임 계약서 자동 생성 |
    | ✅ 동의서·위임장 | 개인정보 동의서, 위임장 자동 생성 |
    | 📊 손해사정 보고서(압박골절_개인보험) | 손해사정 보고서 자동 생성 |
    | 💰 숨은보험금 찾기 | 미청구 보험금 조회 |
    """
)
