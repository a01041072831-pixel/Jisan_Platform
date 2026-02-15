import streamlit as st
import time
from datetime import datetime

# ★ 중요: modules 폴더의 PDF 생성 엔진을 가져옵니다.
# (아직 modules/pdf_generator.py를 안 만들었다면 에러가 날 수 있으니, 
#  우선은 아래 줄을 주석(#) 처리하고 테스트하세요.)
try:
    from modules.pdf_generator import create_contract_pdf
except ImportError:
    # 테스트용 가짜 함수 (모듈이 없을 때 에러 방지)
    def create_contract_pdf(*args):
        return b"Dummy PDF Data"

# ---------------------------------------------------------
# 1. 페이지 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="지산법인 계약서 작성",
    page_icon="📝",
    layout="wide"
)

st.title("📝 지산손해사정법인 계약서 작성")
st.markdown("---")

# ---------------------------------------------------------
# 2. 계약자 (보호자) 정보 입력
# ---------------------------------------------------------
st.subheader("1. 계약자 (보호자) 정보")
st.caption("계약서에 실제로 서명하고 계약을 체결하는 사람의 정보입니다.")

col1, col2 = st.columns(2)

with col1:
    client_name = st.text_input("계약자 성명", placeholder="예: 홍길동 (보호자)")
    client_phone = st.text_input("계약자 연락처", placeholder="예: 010-1234-5678")

with col2:
    client_relation = st.text_input("사고당사자와의 관계", placeholder="예: 본인, 부, 모, 배우자")
    client_birth = st.text_input("계약자 생년월일/주민번호", placeholder="예: 800101-1******")

# ---------------------------------------------------------
# 3. 사고당사자 (환자) 정보 입력
# ---------------------------------------------------------
st.markdown("---")
st.subheader("2. 사고당사자 (환자) 정보")
st.caption("실제 진료를 받고 의무기록을 떼야 하는 환자의 정보입니다.")

# ★ 편의 기능: 체크하면 위의 정보를 그대로 복사합니다.
is_same_person = st.checkbox("✅ 계약자와 사고당사자가 동일인입니다.")

if is_same_person:
    # 위에서 입력한 정보를 변수에 담습니다.
    patient_name = client_name
    patient_phone = client_phone
    patient_birth = client_birth
    
    # 화면에는 읽기 전용으로 보여줍니다 (수정 불가)
    st.success(f"환자 정보가 계약자({client_name}) 정보로 자동 설정되었습니다.")
else:
    # 다르면 직접 입력받습니다.
    c1, c2 = st.columns(2)
    with c1:
        patient_name = st.text_input("환자 성명", placeholder="진료기록 열람 대상자")
        patient_phone = st.text_input("환자 연락처", placeholder="없으면 보호자 번호")
    with c2:
        patient_birth = st.text_input("환자 생년월일/주민번호", placeholder="예: 900505-1******")

# 주소와 사고 내용은 공통 입력
patient_address = st.text_input("주소 (등본상 주소)", placeholder="부산광역시 ...")
accident_details = st.text_area("사고 내용 (간략)", placeholder="교통사고, 배상책임 등 사고 경위", height=80)

# ---------------------------------------------------------
# 4. 수임 조건 설정
# ---------------------------------------------------------
st.markdown("---")
st.subheader("3. 수임 조건")

fee_col1, fee_col2 = st.columns(2)
with fee_col1:
    fee_rate = st.number_input("수임료율 (%)", min_value=0.0, max_value=30.0, value=10.0, step=0.1, format="%.1f")
with fee_col2:
    contract_date = st.date_input("계약일자", datetime.today())

# ---------------------------------------------------------
# 5. 데이터 저장 및 PDF 생성
# ---------------------------------------------------------
st.markdown("---")

# ★★★ 핵심: 다음 페이지(동의서/위임장)를 위해 데이터 세션에 저장 ★★★
# 입력할 때마다 실시간으로 저장됩니다.
if patient_name:
    st.session_state['patient_name'] = patient_name
    st.session_state['patient_birth'] = patient_birth
    st.session_state['patient_address'] = patient_address
    st.session_state['patient_phone'] = patient_phone

# 버튼 클릭
if st.button("🚀 계약서 PDF 생성하기", type="primary"):
    if not client_name or not patient_name:
        st.error("계약자와 환자 성명은 필수 입력입니다!")
    else:
        with st.spinner('계약서를 작성 중입니다...'):
            time.sleep(1) # 처리하는 척 (UX)
            
            try:
                pdf_bytes = create_contract_pdf(
                    사고당사자=patient_name,
                    위임인=client_name,
                    주민번호=client_birth,
                    연락처=client_phone,
                    주소=patient_address,
                    관계=client_relation,
                    보수율=str(int(fee_rate)),
                    보수율한글="",
                    작성날짜=contract_date.strftime("%m월 %d일"),
                )
                
                # 성공 메시지
                st.success(f"📄 {client_name}님의 계약서 생성이 완료되었습니다!")
                st.balloons()
                
                # 다운로드 버튼 표시
                st.download_button(
                    label="📥 PDF 다운로드",
                    data=pdf_bytes,
                    file_name=f"계약서_{client_name}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"PDF 생성 중 오류가 발생했습니다: {e}")
                st.info("💡 modules/pdf_generator.py 파일이 올바르게 설정되었는지 확인해주세요.")