"""
지산 통합 자동화 플랫폼 - 메인 대시보드
- 사이드바: 브랜드 + 카테고리별 메뉴 + 확장 메뉴(비활성) + 하단 푸터
- 메인 영역: 3개 카드(통계/최근생성/바로가기) + 시스템 상태 바
"""
import streamlit as st
from datetime import datetime
from pathlib import Path

# ── 경로 설정 ──────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
TEMPLATE_DIR = BASE_DIR / "templates"
FONT_PATH = BASE_DIR / "assets" / "fonts" / "malgun.ttf"

st.set_page_config(
    page_title="지산 통합 자동화 플랫폼",
    page_icon="🏠",
    layout="wide",
)


# ── 유틸리티 함수 ──────────────────────────────────────────

def count_generated_pdfs():
    """output 폴더의 PDF 파일을 날짜별로 집계한다."""
    result = {"today": 0, "month": 0, "total": 0}
    if not OUTPUT_DIR.is_dir():
        return result

    now = datetime.now()
    today_date = now.date()
    current_month = (now.year, now.month)

    for filepath in OUTPUT_DIR.iterdir():
        if not filepath.suffix.upper() == ".PDF":
            continue
        result["total"] += 1
        try:
            ctime = datetime.fromtimestamp(filepath.stat().st_ctime)
            if ctime.date() == today_date:
                result["today"] += 1
            if (ctime.year, ctime.month) == current_month:
                result["month"] += 1
        except OSError:
            pass
    return result


def get_recent_pdfs(n=3):
    """output 폴더에서 최근 생성된 PDF n개를 반환한다.
    반환: [(파일명, 생성시간 문자열), ...] 리스트
    """
    if not OUTPUT_DIR.is_dir():
        return []

    pdf_files = []
    for filepath in OUTPUT_DIR.iterdir():
        if filepath.suffix.upper() == ".PDF":
            try:
                ctime = filepath.stat().st_ctime
                pdf_files.append((filepath.name, ctime))
            except OSError:
                pass

    # 생성시간 내림차순 정렬 후 상위 n개
    pdf_files.sort(key=lambda x: x[1], reverse=True)
    result = []
    for name, ctime in pdf_files[:n]:
        time_str = datetime.fromtimestamp(ctime).strftime("%m/%d %H:%M")
        result.append((name, time_str))
    return result


def check_system_status():
    """시스템 핵심 리소스 존재 여부를 확인한다.
    반환: {"templates": bool, "font": bool, "output_dir": bool}
    """
    # 템플릿 폴더 내 PDF 파일 존재 여부
    templates_ok = False
    if TEMPLATE_DIR.is_dir():
        templates_ok = any(f.suffix.upper() == ".PDF" for f in TEMPLATE_DIR.iterdir())

    return {
        "templates": templates_ok,
        "font": FONT_PATH.exists(),
        "output_dir": OUTPUT_DIR.is_dir(),
    }


# ── CSS 스타일 ─────────────────────────────────────────────
st.markdown("""
<style>
    /* ══════════════════════════════════════════════════════
       전체 배경: 딥 네이비 + 미세 그리드 패턴
       ══════════════════════════════════════════════════════ */
    .stApp {
        background: #0F172A !important;
        background-image:
            radial-gradient(circle at 15% 20%, rgba(59,130,246,0.08) 0%, transparent 50%),
            radial-gradient(circle at 85% 80%, rgba(139,92,246,0.06) 0%, transparent 50%),
            linear-gradient(rgba(148,163,184,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(148,163,184,0.03) 1px, transparent 1px) !important;
        background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px !important;
    }

    /* 내부 컨테이너 투명 */
    .stApp > div,
    .stMainBlockContainer,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: transparent !important;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1040px !important;
        background: transparent !important;
    }

    /* ══════════════════════════════════════════════════════
       사이드바
       ══════════════════════════════════════════════════════ */
    section[data-testid="stSidebar"] {
        background: #1E293B !important;
        border-right: 1px solid rgba(148,163,184,0.1) !important;
        padding-top: 0rem !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
        padding: 0.5rem 1.2rem 0 1.2rem !important;
    }

    /* 사이드바 네비게이션 링크 */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
        padding-top: 0rem !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li {
        margin: 0.15rem 0.6rem !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
        display: flex !important;
        align-items: center !important;
        padding: 0.65rem 1rem !important;
        border-radius: 10px !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: #CBD5E1 !important;
        border: 1px solid transparent !important;
        transition: all 0.2s ease !important;
        text-decoration: none !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
        background: rgba(96,165,250,0.1) !important;
        border-color: rgba(96,165,250,0.2) !important;
        color: #F1F5F9 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: rgba(96,165,250,0.15) !important;
        border-color: rgba(96,165,250,0.3) !important;
        color: #60A5FA !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a span {
        font-size: 0.9rem !important;
        letter-spacing: 0.2px !important;
    }

    /* 사이드바 내 커스텀 섹션 스타일 */
    .sidebar-brand {
        padding: 1.2rem 0.2rem 0.2rem 0.2rem;
        margin-bottom: 0.2rem;
    }
    .sidebar-brand-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #F1F5F9;
        margin: 0;
        letter-spacing: -0.3px;
    }
    .sidebar-brand-sub {
        font-size: 0.7rem;
        color: #64748B;
        margin: 0.15rem 0 0 0;
        letter-spacing: 0.5px;
    }
    .sidebar-divider {
        height: 1px;
        background: rgba(148,163,184,0.12);
        margin: 0.6rem 0;
    }
    .sidebar-section-label {
        font-size: 0.7rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        padding: 0.3rem 0.2rem 0.4rem 0.2rem;
        margin: 0;
    }

    /* 확장 메뉴 (비활성) */
    .sidebar-menu-disabled {
        display: flex;
        align-items: center;
        padding: 0.55rem 1rem;
        border-radius: 10px;
        font-size: 0.85rem;
        font-weight: 500;
        color: #475569;
        margin: 0.1rem 0;
        cursor: default;
        user-select: none;
    }
    .sidebar-menu-disabled .menu-icon {
        margin-right: 0.5rem;
        font-size: 0.9rem;
        opacity: 0.5;
    }
    .sidebar-coming-soon {
        font-size: 0.6rem;
        color: #475569;
        background: rgba(71,85,105,0.2);
        border-radius: 4px;
        padding: 0.1rem 0.4rem;
        margin-left: auto;
    }

    /* 사이드바 하단 푸터 (고정) */
    .sidebar-footer {
        position: fixed;
        bottom: 0;
        width: inherit;
        max-width: inherit;
        background: #1E293B;
        border-top: 1px solid rgba(148,163,184,0.1);
        padding: 0.8rem 1.4rem 1rem 1.4rem;
        font-size: 0.68rem;
        color: #475569;
        line-height: 1.6;
        z-index: 999;
    }
    .sidebar-footer a {
        color: #64748B;
        text-decoration: none;
        transition: color 0.2s;
    }
    .sidebar-footer a:hover {
        color: #94A3B8;
    }
    .sidebar-footer-version {
        color: #3B5578;
        margin-top: 0.2rem;
    }

    /* ══════════════════════════════════════════════════════
       메인 영역 - 타이틀
       ══════════════════════════════════════════════════════ */
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #F1F5F9;
        margin: 0;
        letter-spacing: -0.3px;
    }
    .main-subtitle {
        font-size: 0.95rem;
        color: #64748B;
        margin: 0.3rem 0 1.5rem 0;
        font-weight: 400;
    }

    /* ══════════════════════════════════════════════════════
       대시보드 카드 공통 (글래스모피즘)
       ══════════════════════════════════════════════════════ */
    .dash-card {
        background: rgba(30,41,59,0.7);
        border: 1px solid rgba(148,163,184,0.1);
        border-radius: 14px;
        backdrop-filter: blur(10px);
        overflow: hidden;
        height: 300px;
        transition: all 0.3s ease;
    }
    .dash-card:hover {
        border-color: rgba(148,163,184,0.2);
        box-shadow: 0 8px 25px rgba(0,0,0,0.25);
    }

    /* 카드 헤더 바 */
    .dash-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 1.4rem;
        border-bottom: 1px solid rgba(148,163,184,0.08);
    }
    .dash-card-header-title {
        font-size: 1rem;
        font-weight: 700;
        color: #CBD5E1;
        margin: 0;
    }
    .dash-card-header-sub {
        font-size: 0.8rem;
        font-weight: 500;
        color: #64748B;
        margin: 0;
    }

    /* 카드 본문 */
    .dash-card-body {
        padding: 1.2rem 1.4rem 1.4rem 1.4rem;
    }

    /* ── 통계 카드 내부 아이템 ── */
    .stat-item {
        display: flex;
        align-items: center;
        padding: 0.75rem 0;
    }
    .stat-item + .stat-item {
        border-top: 1px solid rgba(148,163,184,0.06);
    }
    .stat-icon {
        font-size: 1.15rem;
        margin-right: 0.8rem;
        width: 24px;
        text-align: center;
    }
    .stat-label {
        font-size: 0.95rem;
        color: #94A3B8;
        flex: 1;
    }
    .stat-value {
        font-size: 1.3rem;
        font-weight: 800;
        margin: 0;
    }
    .stat-value.blue { color: #60A5FA; }
    .stat-value.green { color: #34D399; }
    .stat-value.purple { color: #A78BFA; }
    .stat-unit {
        font-size: 0.85rem;
        font-weight: 400;
        opacity: 0.7;
        margin-left: 2px;
    }

    /* ── 최근 생성 카드 아이템 ── */
    .recent-item {
        display: flex;
        align-items: center;
        padding: 0.75rem 0;
    }
    .recent-item + .recent-item {
        border-top: 1px solid rgba(148,163,184,0.06);
    }
    .recent-icon {
        font-size: 1rem;
        margin-right: 0.8rem;
        color: #475569;
    }
    .recent-name {
        font-size: 0.92rem;
        color: #CBD5E1;
        flex: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 180px;
    }
    .recent-time {
        font-size: 0.8rem;
        color: #64748B;
        margin-left: 0.5rem;
        white-space: nowrap;
    }
    .recent-empty {
        font-size: 0.95rem;
        color: #475569;
        padding: 1.5rem 0;
        text-align: center;
    }

    /* ── 바로가기 카드 아이템 ── */
    .shortcut-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.7rem 0.2rem;
        border-radius: 8px;
        transition: background 0.2s;
        cursor: default;
    }
    .shortcut-item + .shortcut-item {
        border-top: 1px solid rgba(148,163,184,0.06);
    }
    .shortcut-label {
        font-size: 0.92rem;
        color: #CBD5E1;
        font-weight: 600;
    }
    .shortcut-arrow {
        font-size: 0.9rem;
        color: #475569;
    }
    .shortcut-item.disabled .shortcut-label {
        color: #475569;
    }
    .shortcut-item.disabled .shortcut-arrow {
        color: #334155;
    }

    /* page_link 스타일 (바로가기 카드 내부) */
    [data-testid="stPageLink"] {
        background: transparent !important;
        border: none !important;
        padding: 0.25rem 0 !important;
        margin: 0 !important;
    }
    [data-testid="stPageLink"] p {
        color: #CBD5E1 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    [data-testid="stPageLink"]:hover p {
        color: #60A5FA !important;
    }

    /* 바로가기 카드: 세 번째 컬럼 자체를 카드처럼 스타일링 */
    .col-shortcut > div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background: rgba(30,41,59,0.7) !important;
        border: 1px solid rgba(148,163,184,0.1) !important;
        border-radius: 14px !important;
        backdrop-filter: blur(10px) !important;
        padding: 1rem 1.4rem 1.4rem 1.4rem !important;
        height: 300px !important;
        transition: all 0.3s ease !important;
    }
    .col-shortcut > div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
        border-color: rgba(148,163,184,0.2) !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.25) !important;
    }
    .col-shortcut .shortcut-header {
        font-size: 1rem;
        font-weight: 700;
        color: #CBD5E1;
        margin: 0 0 0.6rem 0;
        padding-bottom: 0.7rem;
        border-bottom: 1px solid rgba(148,163,184,0.08);
    }

    /* ══════════════════════════════════════════════════════
       시스템 상태 바
       ══════════════════════════════════════════════════════ */
    .status-bar-wrapper {
        margin-top: 4rem;
        display: flex;
        justify-content: center;
    }
    .status-bar {
        background: rgba(30,41,59,0.5);
        border: 1px solid rgba(148,163,184,0.08);
        border-radius: 20px;
        padding: 0.5rem 1.5rem;
        display: inline-flex;
        align-items: center;
        gap: 0.6rem;
        backdrop-filter: blur(10px);
    }
    .status-bar-title {
        font-size: 0.72rem;
        font-weight: 700;
        color: #64748B;
        margin: 0;
    }
    .status-bar-sep {
        width: 1px;
        height: 12px;
        background: rgba(148,163,184,0.15);
    }
    .status-bar-items {
        font-size: 0.7rem;
        color: #475569;
        margin: 0;
    }
    .status-bar-items span {
        margin: 0 0.2rem;
    }
    .status-indicator {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        font-size: 0.7rem;
        font-weight: 600;
    }
    .status-indicator.ok { color: #34D399; }
    .status-indicator.error { color: #F87171; }

    /* ══════════════════════════════════════════════════════
       Streamlit 기본 UI 숨기기
       ══════════════════════════════════════════════════════ */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="stBaseButton-header"] {
        color: #94A3B8 !important;
    }
    button[data-testid="stSidebarCollapseButton"]:hover,
    button[data-testid="stBaseButton-header"]:hover {
        color: #60A5FA !important;
    }
    hr {
        border-color: rgba(148,163,184,0.1) !important;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 사이드바 구성
# ══════════════════════════════════════════════════════════════

# ── 브랜드 + "업무" 섹션 라벨 (자동 nav 위에 표시) ──
st.sidebar.markdown("""
<div class="sidebar-brand">
    <p class="sidebar-brand-title">(주)지산손해사정</p>
    <p class="sidebar-brand-sub">INSURANCE AUTOMATION PLATFORM</p>
</div>
<div class="sidebar-divider"></div>
<p class="sidebar-section-label">업무</p>
""", unsafe_allow_html=True)

# (Streamlit 자동 nav가 여기에 자동으로 렌더링됨 — pages/ 폴더 기반)

# ── 확장 메뉴 (비활성 상태, 향후 기능) + 푸터 ──
st.sidebar.markdown("""
<div class="sidebar-divider"></div>
<p class="sidebar-section-label">운영 <span style="font-size:0.6rem; font-weight:400; color:#475569;">(예정)</span></p>
<div class="sidebar-menu-disabled">
    <span class="menu-icon">📈</span> 통계 · 분석
    <span class="sidebar-coming-soon">SOON</span>
</div>
<div class="sidebar-menu-disabled">
    <span class="menu-icon">👥</span> 고객 관리
    <span class="sidebar-coming-soon">SOON</span>
</div>
<div class="sidebar-divider"></div>
<p class="sidebar-section-label">설정</p>
<div class="sidebar-menu-disabled">
    <span class="menu-icon">⚙️</span> 환경설정
    <span class="sidebar-coming-soon">SOON</span>
</div>

<div class="sidebar-footer">
    <div>
        <a href="#">이용약관</a>
        <span style="margin: 0 0.3rem;">|</span>
        <a href="#">개인정보처리지침</a>
    </div>
    <div class="sidebar-footer-version">v1.0-beta &nbsp;·&nbsp; by 최효승</div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 메인 영역
# ══════════════════════════════════════════════════════════════

# ── 타이틀 + 날짜/시간 ──
now = datetime.now()
date_str = now.strftime("%Y년 %m월 %d일 %A").replace(
    "Monday", "월요일").replace("Tuesday", "화요일").replace(
    "Wednesday", "수요일").replace("Thursday", "목요일").replace(
    "Friday", "금요일").replace("Saturday", "토요일").replace(
    "Sunday", "일요일")
time_str = now.strftime("%H:%M")

st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:flex-end;">
    <div>
        <p class="main-title">대시보드</p>
        <p class="main-subtitle">업무 현황을 한눈에 확인하세요.</p>
    </div>
    <div style="text-align:right; padding-bottom:0.3rem;">
        <p style="margin:0; font-size:0.85rem; color:#64748B;">{date_str}</p>
        <p style="margin:0; font-size:1.6rem; font-weight:800; color:#CBD5E1; letter-spacing:-0.5px;">{time_str}</p>
    </div>
</div>
""", unsafe_allow_html=True)


# ── 데이터 수집 ──
stats = count_generated_pdfs()
recent_pdfs = get_recent_pdfs(n=3)
sys_status = check_system_status()


# ── 3개 카드 (가로 나란히) ──────────────────────────────────
card_col1, card_col2, card_col3 = st.columns(3, gap="medium")

# --- 카드 1: 통계 ---
with card_col1:
    st.markdown(f"""
    <div class="dash-card">
        <div class="dash-card-header">
            <p class="dash-card-header-title">통계</p>
            <p class="dash-card-header-sub">이번 주</p>
        </div>
        <div class="dash-card-body">
            <div class="stat-item">
                <span class="stat-icon">📊</span>
                <span class="stat-label">오늘</span>
                <span class="stat-value blue">{stats['today']}<span class="stat-unit">건</span></span>
            </div>
            <div class="stat-item">
                <span class="stat-icon">📅</span>
                <span class="stat-label">이번 달</span>
                <span class="stat-value green">{stats['month']}<span class="stat-unit">건</span></span>
            </div>
            <div class="stat-item">
                <span class="stat-icon">📁</span>
                <span class="stat-label">전체</span>
                <span class="stat-value purple">{stats['total']}<span class="stat-unit">건</span></span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 카드 2: 최근 생성 ---
with card_col2:
    # 최근 PDF 리스트 HTML 생성
    if recent_pdfs:
        recent_html = ""
        for name, time_str in recent_pdfs:
            recent_html += f"""
            <div class="recent-item">
                <span class="recent-icon">📄</span>
                <span class="recent-name" title="{name}">{name}</span>
                <span class="recent-time">{time_str}</span>
            </div>"""
    else:
        recent_html = '<div class="recent-empty">생성된 파일이 없습니다.</div>'

    st.markdown(f"""
    <div class="dash-card">
        <div class="dash-card-header">
            <p class="dash-card-header-title">최근 생성</p>
            <p class="dash-card-header-sub">PDF</p>
        </div>
        <div class="dash-card-body">
            {recent_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 카드 3: 업무 바로가기 ---
# 컬럼 자체에 카드 스타일 적용 (st.container 없이)
with card_col3:
    st.markdown('<div class="col-shortcut">', unsafe_allow_html=True)

    # 카드 헤더
    st.markdown('<p class="shortcut-header">업무 바로가기</p>', unsafe_allow_html=True)

    # 활성 메뉴: st.page_link로 실제 페이지 이동
    st.page_link("pages/1_📝_계약서_작성.py", label="📝 계약서 작성 →")
    st.page_link("pages/2_✅_동의서_위임장.py", label="✅ 동의서 · 위임장 →")
    st.page_link(
        "pages/3_📊_손해사정_보고서(압박골절_개인보험).py",
        label="📊 손해사정 보고서 →",
    )

    # 비활성 메뉴
    st.markdown("""
    <div class="shortcut-item disabled" style="padding-top: 0.4rem;">
        <span class="shortcut-label">💰 숨은보험금 찾기 (준비 중)</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ── 시스템 상태 바 ─────────────────────────────────────────
all_ok = all(sys_status.values())
status_icon = "🟢" if all_ok else "🔴"
status_text = "정상" if all_ok else "점검 필요"
status_cls = "ok" if all_ok else "error"

# 개별 항목 상태 텍스트
template_count = 0
if TEMPLATE_DIR.is_dir():
    template_count = sum(1 for f in TEMPLATE_DIR.iterdir() if f.suffix.upper() == ".PDF")
font_name = "malgun.ttf" if sys_status["font"] else "없음"
output_status = "output" if sys_status["output_dir"] else "없음"

st.markdown(f"""
<div class="status-bar-wrapper">
    <div class="status-bar">
        <p class="status-bar-title">시스템 상태</p>
        <div class="status-bar-sep"></div>
        <p class="status-bar-items">
            템플릿 {template_count}개
            <span>·</span>
            폰트 {font_name}
            <span>·</span>
            출력 {output_status}
        </p>
        <div class="status-bar-sep"></div>
        <div class="status-indicator {status_cls}">
            {status_icon} {status_text}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
