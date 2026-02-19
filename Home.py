"""
지산 통합 자동화 플랫폼 - 메인 대시보드
- 다크 테마 모던 랜딩페이지 스타일
- 통계 카드 + 메뉴 카드 + 그라디언트 배경
"""
import streamlit as st
from datetime import datetime
from pathlib import Path

# ── 경로 설정 ──────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"

st.set_page_config(
    page_title="지산 통합 자동화 플랫폼",
    page_icon="🏠",
    layout="wide",
)


# ── 통계 집계 함수 ─────────────────────────────────────────
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


# ── CSS 스타일 (다크 모던 랜딩페이지) ──────────────────────
st.markdown("""
<style>
    /* ── 전체 배경: 딥 네이비 + 미세한 그리드 패턴 ── */
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
        max-width: 960px !important;
        background: transparent !important;
    }

    /* ── 사이드바 스타일 ── */
    section[data-testid="stSidebar"] {
        background: #1E293B !important;
        border-right: 1px solid rgba(148,163,184,0.1) !important;
        padding-top: 1rem !important;
    }

    /* 사이드바 로고/타이틀 영역 */
    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
        padding: 1rem 1.2rem 0.8rem 1.2rem !important;
    }

    /* 사이드바 네비게이션 링크 스타일 */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
        padding-top: 0.5rem !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li {
        margin: 0.2rem 0.6rem !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
        display: flex !important;
        align-items: center !important;
        padding: 0.75rem 1rem !important;
        border-radius: 10px !important;
        font-size: 0.95rem !important;
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
        font-size: 0.95rem !important;
        letter-spacing: 0.2px !important;
    }

    /* ── 헤더 영역 ── */
    .hero-section {
        text-align: center;
        padding: 3rem 1rem 2rem 1rem;
        position: relative;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(59,130,246,0.15);
        color: #60A5FA;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.3rem 0.9rem;
        border-radius: 20px;
        border: 1px solid rgba(59,130,246,0.25);
        margin-bottom: 1rem;
        letter-spacing: 0.5px;
    }
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 0%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0.3rem 0;
        line-height: 1.2;
    }
    .hero-sub {
        font-size: 1.1rem;
        color: #64748B;
        margin-top: 0.5rem;
        font-weight: 400;
    }

    /* ── 구분선 ── */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(148,163,184,0.2), transparent);
        margin: 1.5rem 0;
    }

    /* ── 통계 카드 ── */
    .stat-card {
        background: rgba(30,41,59,0.8);
        border: 1px solid rgba(148,163,184,0.1);
        border-radius: 16px;
        padding: 1.4rem 1.5rem;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .stat-card:hover {
        border-color: rgba(148,163,184,0.25);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    .stat-label {
        font-size: 0.8rem;
        color: #64748B;
        margin-bottom: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    .stat-value {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
    }
    .stat-blue .stat-value { color: #60A5FA; }
    .stat-green .stat-value { color: #34D399; }
    .stat-purple .stat-value { color: #A78BFA; }
    .stat-unit {
        font-size: 0.9rem;
        font-weight: 400;
        opacity: 0.7;
    }

    /* ── 섹션 라벨 ── */
    .section-label {
        font-size: 0.85rem;
        font-weight: 700;
        color: #64748B;
        margin: 2rem 0 1rem 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* ── 메뉴 카드 (글래스모피즘) ── */
    .menu-card {
        background: rgba(30,41,59,0.6);
        border: 1px solid rgba(148,163,184,0.1);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        margin-bottom: 0.5rem;
    }
    .menu-card:hover {
        background: rgba(30,41,59,0.9);
        border-color: rgba(96,165,250,0.4);
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.4), 0 0 20px rgba(59,130,246,0.08);
    }
    .menu-card.disabled {
        opacity: 0.4;
    }
    .menu-card.disabled:hover {
        background: rgba(30,41,59,0.6);
        border-color: rgba(148,163,184,0.1);
        transform: none;
        box-shadow: none;
    }

    /* 카드 아이콘 */
    .card-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        font-weight: 800;
        color: white;
        margin-bottom: 0.8rem;
    }

    /* 카드 텍스트 */
    .card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #E2E8F0;
        margin-bottom: 0.3rem;
    }
    .card-desc {
        font-size: 0.85rem;
        color: #64748B;
        margin: 0;
    }
    .card-arrow {
        color: #475569;
        font-size: 1.1rem;
        margin-top: 0.6rem;
        transition: color 0.2s;
    }
    .menu-card:hover .card-arrow {
        color: #60A5FA;
    }

    /* ── 푸터 ── */
    .dashboard-footer {
        text-align: center;
        color: #475569;
        font-size: 0.75rem;
        padding-top: 2rem;
        border-top: 1px solid rgba(148,163,184,0.1);
        margin-top: 3rem;
        letter-spacing: 0.3px;
    }

    /* ── Streamlit 기본 UI 숨기기 (사이드바 토글 버튼은 유지) ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* 헤더 배경만 투명 처리, 사이드바 토글 버튼은 보이게 */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    /* 사이드바 토글 버튼 스타일 */
    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="stBaseButton-header"] {
        color: #94A3B8 !important;
    }
    button[data-testid="stSidebarCollapseButton"]:hover,
    button[data-testid="stBaseButton-header"]:hover {
        color: #60A5FA !important;
    }

    /* Streamlit divider 투명 처리 */
    hr {
        border-color: rgba(148,163,184,0.1) !important;
    }

    /* page_link 스타일 */
    [data-testid="stPageLink"] {
        background: transparent !important;
        border: none !important;
    }
    [data-testid="stPageLink"] p {
        color: #60A5FA !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
    }
    [data-testid="stPageLink"]:hover p {
        color: #93C5FD !important;
    }
</style>
""", unsafe_allow_html=True)


# ── 헤더 영역 ──────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
    <div class="hero-badge">INSURANCE AUTOMATION PLATFORM</div>
    <div class="hero-title">(주)지산손해사정</div>
    <div class="hero-sub">업무 자동화 플랫폼</div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── 통계 카드 영역 ─────────────────────────────────────────
stats = count_generated_pdfs()

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.markdown(f"""
    <div class="stat-card stat-blue">
        <p class="stat-label">Today</p>
        <p class="stat-value">{stats['today']}<span class="stat-unit">건</span></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card stat-green">
        <p class="stat-label">This Month</p>
        <p class="stat-value">{stats['month']}<span class="stat-unit">건</span></p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card stat-purple">
        <p class="stat-label">Total</p>
        <p class="stat-value">{stats['total']}<span class="stat-unit">건</span></p>
    </div>
    """, unsafe_allow_html=True)


# ── 업무 선택 메뉴 ─────────────────────────────────────────
st.markdown('<p class="section-label">업무 선택</p>', unsafe_allow_html=True)

# 메뉴 카드 설정: (아이콘약어, 그라디언트색, 제목, 설명, 페이지파일, 활성여부)
MENU_ITEMS = [
    ("계", "linear-gradient(135deg, #2563EB, #3B82F6)", "계약서 작성",
     "위임장 + 약정서 자동 생성", "pages/1_📝_계약서_작성.py", True),
    ("동", "linear-gradient(135deg, #059669, #10B981)", "동의서 · 위임장",
     "개인정보 동의서, 위임장 생성", "pages/2_✅_동의서_위임장.py", True),
    ("보", "linear-gradient(135deg, #D97706, #F59E0B)", "손해사정 보고서",
     "AI 기반 보고서 자동 작성", "pages/3_📊_손해사정_보고서(압박골절_개인보험).py", True),
    ("찾", "linear-gradient(135deg, #7C3AED, #8B5CF6)", "숨은보험금 찾기",
     "(준비 중)", "pages/4_💰_숨은보험금_찾기.py", False),
]

# 2x2 그리드 배치
row1_col1, row1_col2 = st.columns(2, gap="medium")
row2_col1, row2_col2 = st.columns(2, gap="medium")
grid_cols = [row1_col1, row1_col2, row2_col1, row2_col2]

for idx, (abbr, gradient, title, desc, page_file, enabled) in enumerate(MENU_ITEMS):
    with grid_cols[idx]:
        disabled_cls = "" if enabled else " disabled"
        st.markdown(f"""
        <div class="menu-card{disabled_cls}">
            <div class="card-icon" style="background: {gradient};">{abbr}</div>
            <p class="card-title">{title}</p>
            <p class="card-desc">{desc}</p>
        </div>
        """, unsafe_allow_html=True)
        if enabled:
            st.page_link(page_file, label=f"{title} 바로가기 →")


# ── 푸터 ───────────────────────────────────────────────────
st.markdown("""
<div class="dashboard-footer">
    (주)지산손해사정 v1.0 &nbsp;|&nbsp; Insurance Claim Automation Platform
</div>
""", unsafe_allow_html=True)
