import streamlit as st
import time
from datetime import datetime

# ★ modules 폴더의 동의서 생성 엔진 연결
try:
    from modules.consent_generator import create_consent_pdf
except ImportError:
    # 테스트용 가짜 함수
    def create_consent_pdf(*args):
        return b"Dummy Consent PDF Data"

st.set_page_config(page_title="의무기록 동의서/위임장", page_icon="✅", layout="wide")

st.title("✅ 의무기록 열람 동의서 & 위임장")
st.markdown("---")

# ---------------------------------------------------------
# 1. 수임인 (서류 발급 대행인) 정보
# ---------------------------------------------------------
st.subheader("1. 수임인 (방문자) 정보")
st.caption("병원에 직접 방문하여 서류를 발급받을 사람의 정보입니다.")

# ★ 프리셋 기능: 체크하면 최효승 사정사님 정보 자동 입력
use_default = st.checkbox("✅ 기본 수임인(최효승) 정보 적용", value=True)

if use_default:
    # 기본값 설정
    def_name = "최효승"
    def_birth = "881114"
    def_phone = "010-4107-2831"
    def_addr = "부산광역시 ..."  # (필요시 상세주소로 수정하세요)
    def_rel = "본인의 위임을 받은 손해사정사"
else:
    # 직접 입력 모드일 땐 빈칸
    def_name = ""
    def_birth = ""
    def_phone = ""
    def_addr = ""
    def_rel = ""

col1, col2 = st.columns(2)
with col1:
    assignee_name = st.text_input("수임인 성명", value=def_name)
    assignee_birth = st.text_input("수임인 생년월일", value=def_birth, placeholder="예: 850101")
    assignee_phone = st.text_input("수임인 연락처", value=def_phone)
with col2:
    assignee_rel = st.text_input("환자와의 관계", value=def_rel, placeholder="예: 대리인, 직원")
    assignee_addr = st.text_input("수임인 주소/소속", value=def_addr)

# ---------------------------------------------------------
# 2. 위임인 (환자) 정보
# ---------------------------------------------------------
st.markdown("---")
st.subheader("2. 위임인 (환자) 정보")
st.caption("계약서 페이지에서 입력한 정보가 있다면 자동으로 채워집니다.")

# ★ 세션 스테이트에서 데이터 가져오기 (마법의 구간!)
saved_name = st.session_state.get('patient_name', '')
saved_birth = st.session_state.get('patient_birth', '')
saved_addr = st.session_state.get('patient_address', '')
saved_phone = st.session_state.get('patient_phone', '')

c1, c2 = st.columns(2)
with c1:
    p_name = st.text_input("환자 성명", value=saved_name)
    p_birth = st.text_input("생년월일/주민번호", value=saved_birth, placeholder="800101-1******")
with c2:
    p_addr = st.text_input("환자 주소", value=saved_addr)
    p_phone = st.text_input("환자 연락처", value=saved_phone)

# ---------------------------------------------------------
# 3. PDF 생성 버튼
# ---------------------------------------------------------
st.markdown("---")

if st.button("🚀 위임장/동의서 PDF 생성", type="primary"):
    if not p_name or not assignee_name:
        st.error("환자 이름과 수임인 이름은 필수입니다!")
    else:
        with st.spinner('서류를 생성 중입니다...'):
            time.sleep(1)
            
            # 엔진 가동!
            try:
                pdf_bytes = create_consent_pdf(
                    p_name, p_birth, p_addr, p_phone,                          # 환자 정보
                    assignee_name, assignee_phone, assignee_rel, assignee_addr, # 수임인 정보
                    applicant_birth=assignee_birth,                             # 수임인 생년월일
                )
                
                st.success("문서 생성이 완료되었습니다!")
                
                # 파일명 생성 (예: 홍길동_동의서위임장_20260215.pdf)
                today_str = datetime.now().strftime("%Y%m%d")
                file_name = f"{p_name}_동의서위임장_{today_str}.pdf"
                
                st.download_button(
                    label="📥 PDF 다운로드",
                    data=pdf_bytes,
                    file_name=file_name,
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"오류 발생: {e}")
                st.info("modules/consent_generator.py 파일이 잘 생성되었는지 확인해주세요.")