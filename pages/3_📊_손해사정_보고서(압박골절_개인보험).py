# -*- coding: utf-8 -*-
"""
페이지: 손해사정 보고서 — AI 자동 생성 (Gemini API)
5단계 위저드: 자료입력 → 검증 → 초안작성 → 검수 → 완료
"""
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="손해사정 보고서(압박골절_개인보험)", page_icon="📊", layout="wide")

# ── 모듈 임포트 ─────────────────────────────────────────────
try:
    from modules.report_prompt_builder import load_prompt_files, build_user_message
    from modules.report_ai_client import (
        get_api_key,
        send_message,
        extract_text_from_pdf,
    )
except ImportError as e:
    st.error(f"모듈 로드 실패: {e}")
    st.stop()

# ── 상수 ─────────────────────────────────────────────────────
PHASES = ["input", "verifying", "drafting", "reviewing", "complete"]
PHASE_LABELS = {
    "input": "자료입력",
    "verifying": "검증",
    "drafting": "초안작성",
    "reviewing": "검수",
    "complete": "완료",
}

# ── Session State 초기화 ──────────────────────────────────────
defaults = {
    "report_phase": "input",
    "report_messages": [],
    "report_data": {},
    "report_draft": "",
    "report_review": "",
    "report_uploaded_texts": [],
    "report_uploaded_names": [],
    "report_contracts": [{}],
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ── API 키 확인 ───────────────────────────────────────────────
api_key = get_api_key()
if not api_key:
    st.title("📊 손해사정 보고서")
    st.warning("Gemini API 키가 설정되지 않았습니다.")
    st.markdown(
        """
        ### API 키 설정 방법
        1. [Google AI Studio](https://aistudio.google.com/apikey) 접속
        2. **Get API key** → 키 생성
        3. `.streamlit/secrets.toml` 파일에 아래와 같이 입력:
        ```toml
        GEMINI_API_KEY = "발급받은_API_키"
        ```
        4. 앱 재시작
        """
    )
    st.stop()


# ── 헬퍼 함수 ────────────────────────────────────────────────
def set_phase(phase: str):
    st.session_state["report_phase"] = phase


def reset_all():
    for key in defaults:
        st.session_state[key] = type(defaults[key])()
    st.session_state["report_phase"] = "input"
    st.session_state["report_contracts"] = [{}]


@st.cache_data(show_spinner="참고자료 및 프롬프트 로딩 중...")
def get_system_prompt() -> str:
    """시스템 프롬프트를 로드하고 오늘 날짜를 추가합니다. 캐싱됩니다."""
    base = load_prompt_files()
    today = datetime.now().strftime("%Y년 %m월 %d일")
    return f"{base}\n\n---\n\n# 현재 날짜\n오늘 날짜: {today}\n손해사정서의 작성 날짜로 위 날짜를 사용하세요."


# ── 진행 표시바 ───────────────────────────────────────────────
st.title("📊 손해사정 보고서")

current = st.session_state["report_phase"]
cols = st.columns(len(PHASES))
for i, (phase, label) in enumerate(PHASE_LABELS.items()):
    idx_current = PHASES.index(current)
    idx_phase = PHASES.index(phase)
    if idx_phase < idx_current:
        cols[i].markdown(f"~~:green[**{label}**]~~")
    elif idx_phase == idx_current:
        cols[i].markdown(f":blue[**{label}**]")
    else:
        cols[i].markdown(f":gray[{label}]")

st.markdown("---")

# ── 사이드바: 초기화 버튼 ─────────────────────────────────────
with st.sidebar:
    st.markdown("### 보고서 도구")
    if st.button("새 보고서 시작", use_container_width=True):
        reset_all()
        st.rerun()
    if current != "input":
        st.markdown(f"**현재 단계**: {PHASE_LABELS[current]}")


# ══════════════════════════════════════════════════════════════
# Phase 1: 자료입력
# ══════════════════════════════════════════════════════════════
if current == "input":
    st.subheader("1단계: 자료입력")
    st.caption("손해사정서 작성에 필요한 기본 정보를 입력하세요.")

    # ── 피보험자 정보 (계약서 페이지에서 자동채움) ──
    st.markdown("#### 피보험자 인적사항")
    c1, c2 = st.columns(2)
    with c1:
        insured_name = st.text_input(
            "성명",
            value=st.session_state.get("patient_name", ""),
            key="inp_name",
        )
        insured_birth = st.text_input(
            "생년월일",
            value=st.session_state.get("patient_birth", ""),
            key="inp_birth",
        )
    with c2:
        insured_address = st.text_input(
            "주소",
            value=st.session_state.get("patient_address", ""),
            key="inp_address",
        )
        insured_phone = st.text_input(
            "연락처",
            value=st.session_state.get("patient_phone", ""),
            key="inp_phone",
        )

    # ── 보험계약사항 (동적 행 추가) ──
    st.markdown("#### 보험계약사항")
    contracts = st.session_state["report_contracts"]

    for i, contract in enumerate(contracts):
        with st.expander(f"보험계약 {i + 1}", expanded=(i == len(contracts) - 1)):
            cc1, cc2 = st.columns(2)
            with cc1:
                contract["company"] = st.text_input(
                    "보험회사", value=contract.get("company", ""), key=f"co_{i}"
                )
                contract["product"] = st.text_input(
                    "보험종목(상품명)", value=contract.get("product", ""), key=f"prod_{i}"
                )
                contract["policy_no"] = st.text_input(
                    "증권번호", value=contract.get("policy_no", ""), key=f"pno_{i}"
                )
            with cc2:
                contract["period"] = st.text_input(
                    "보험기간", value=contract.get("period", ""), key=f"per_{i}"
                )
                contract["coverage"] = st.text_area(
                    "담보내역",
                    value=contract.get("coverage", ""),
                    key=f"cov_{i}",
                    height=100,
                )

    bcol1, bcol2 = st.columns([1, 5])
    with bcol1:
        if st.button("+ 계약 추가"):
            st.session_state["report_contracts"].append({})
            st.rerun()
    with bcol2:
        if len(contracts) > 1 and st.button("- 마지막 삭제"):
            st.session_state["report_contracts"].pop()
            st.rerun()

    # ── 사고정보 ──
    st.markdown("#### 사고정보")
    ac1, ac2 = st.columns(2)
    with ac1:
        accident_date = st.text_input("사고일시", key="inp_acc_date")
        accident_place = st.text_input("사고장소", key="inp_acc_place")
    with ac2:
        accident_desc = st.text_area("사고경위", key="inp_acc_desc", height=100)

    # ── 추가정보 ──
    additional_info = st.text_area(
        "추가 정보 (선택사항)",
        placeholder="진단명, 치료내용, 특이사항 등 AI에게 전달할 추가 정보를 자유롭게 입력하세요.",
        key="inp_additional",
        height=120,
    )

    # ── 자료 업로드 ──
    st.markdown("#### 자료 업로드")
    st.caption("의무기록, 보험증권/약관, 장해진단서, 기타 자료를 업로드하세요. (PDF, 이미지)")
    uploaded_files = st.file_uploader(
        "파일 업로드",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="inp_uploads",
    )

    # ── 제출 버튼 ──
    st.markdown("---")
    submit = st.button("보고서 생성 시작", type="primary", use_container_width=True)

    if submit:
        if not insured_name and not uploaded_files:
            st.error("피보험자 성명을 입력하거나, 진단서/보험증권 등 자료를 업로드해주세요.")
            st.stop()

        # 데이터 수집
        data = {
            "insured_name": insured_name,
            "insured_birth": insured_birth,
            "insured_address": insured_address,
            "insured_phone": insured_phone,
            "contracts": [c for c in contracts if c.get("company")],
            "accident_date": accident_date,
            "accident_place": accident_place,
            "accident_desc": accident_desc,
            "additional_info": additional_info,
        }
        st.session_state["report_data"] = data

        # 업로드 파일 처리
        uploaded_texts = []
        uploaded_names = []
        if uploaded_files:
            progress = st.progress(0, text="업로드 자료 처리 중...")
            for idx, f in enumerate(uploaded_files):
                progress.progress(
                    (idx + 1) / len(uploaded_files),
                    text=f"자료 처리 중: {f.name}",
                )
                fbytes = f.read()
                uploaded_names.append(f.name)
                if f.type == "application/pdf":
                    try:
                        text = extract_text_from_pdf(fbytes)
                        uploaded_texts.append(f"[파일: {f.name}]\n{text}")
                    except Exception as ex:
                        uploaded_texts.append(
                            f"[파일: {f.name}] - PDF 텍스트 추출 실패: {ex}"
                        )
                else:
                    uploaded_texts.append(
                        f"[이미지 파일: {f.name}] - 이미지가 업로드되었습니다."
                    )
            progress.empty()

        st.session_state["report_uploaded_texts"] = uploaded_texts
        st.session_state["report_uploaded_names"] = uploaded_names

        # 사용자 메시지 구성
        user_msg = build_user_message(data, uploaded_texts)
        st.session_state["report_messages"] = [
            {"role": "user", "content": user_msg}
        ]

        set_phase("verifying")
        st.rerun()


# ══════════════════════════════════════════════════════════════
# Phase 2: 검증
# ══════════════════════════════════════════════════════════════
elif current == "verifying":
    st.subheader("2단계: 자료 검증")
    st.caption("AI가 제공된 자료를 검토하고 누락/모호/상충 사항을 확인합니다.")

    messages = st.session_state["report_messages"]
    system_prompt = get_system_prompt()

    # 아직 AI 검증 응답이 없으면 생성
    if len(messages) == 1 or messages[-1]["role"] == "user":
        verify_instruction = (
            "위 자료를 검토하여 손해사정서 작성에 필요한 필수 정보가 모두 제공되었는지 확인하세요.\n"
            "02_PROCESS.md의 Phase 1에 따라 필수정보(피보험자 인적사항, 보험계약사항, 사고정보, "
            "의료정보, 약관, 장해평가)를 점검하세요.\n\n"
            "누락·모호·상충이 있으면 05_DATA_PROTOCOL.md의 질의 프로토콜 형식으로 질문하세요.\n"
            "모든 정보가 충분하면 '자료 검증이 완료되었습니다. 초안 작성을 시작하겠습니다.'라고 답하세요."
        )

        if len(messages) == 1:
            # 처음 검증 요청 — 기존 user 메시지에 검증 지시 추가
            messages[0]["content"] += f"\n\n---\n\n{verify_instruction}"
        # else: 사용자가 추가 응답을 했으므로 그대로 진행

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            try:
                stream = send_message(system_prompt, messages, stream=True)
                for chunk in stream:
                    full_response += chunk
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
            except Exception as ex:
                st.error(f"AI 응답 생성 중 오류: {ex}")
                st.stop()

        messages.append({"role": "model", "content": full_response})
        st.session_state["report_messages"] = messages

    # 대화 히스토리 표시
    for msg in messages:
        role = msg["role"]
        if role == "user":
            with st.chat_message("user"):
                # 첫 메시지는 길 수 있으므로 요약 표시
                if msg == messages[0]:
                    st.markdown("**[입력 자료 전달됨]**")
                    with st.expander("전체 내용 보기"):
                        st.markdown(msg["content"])
                else:
                    st.markdown(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])

    # 자료 검증 완료 판단 + 다음 단계 전환
    last_ai = messages[-1]["content"] if messages[-1]["role"] == "model" else ""
    verification_done = any(
        kw in last_ai
        for kw in ["검증이 완료", "초안 작성을 시작", "충분합니다", "진행하겠습니다"]
    )

    st.markdown("---")
    col_a, col_b = st.columns([3, 1])

    with col_a:
        user_reply = st.chat_input("AI 질문에 답변하거나 추가 자료를 설명하세요...")
        if user_reply:
            messages.append({"role": "user", "content": user_reply})
            st.session_state["report_messages"] = messages
            st.rerun()

    with col_b:
        if verification_done:
            if st.button("초안 작성 진행", type="primary", use_container_width=True):
                set_phase("drafting")
                st.rerun()
        else:
            if st.button(
                "검증 생략 → 초안 작성",
                use_container_width=True,
                help="필수 정보가 부족할 수 있습니다",
            ):
                set_phase("drafting")
                st.rerun()


# ══════════════════════════════════════════════════════════════
# Phase 3: 초안작성 (스트리밍)
# ══════════════════════════════════════════════════════════════
elif current == "drafting":
    st.subheader("3단계: 초안 작성")

    if not st.session_state["report_draft"]:
        st.caption("AI가 손해사정서 초안을 작성하고 있습니다...")

        messages = st.session_state["report_messages"]
        system_prompt = get_system_prompt()

        # 초안 작성 지시 (할루시네이션 방지 강화)
        draft_instruction = (
            "이제 손해사정서 초안을 작성하세요.\n\n"
            "## 절대 준수 사항\n"
            "- **제공된 자료에 명시된 수치·금액·날짜만 사용하세요.** 자료에 없는 금액이나 정보를 절대 추측하지 마세요.\n"
            "- 보험가입금액, 증권번호, 보험기간 등은 제공된 자료의 원본 수치를 그대로 사용하세요.\n"
            "- 제공되지 않은 정보는 반드시 '정보 미제공'으로 표시하세요. 임의로 채우지 마세요.\n"
            "- 담보내역, 보험금액은 첨부자료(보험증권)에 기재된 그대로만 기재하세요.\n\n"
            "## 작성 형식\n"
            "- 03_DOCUMENT_STRUCTURE.md의 구조(첫 페이지 공문 → Ⅰ~Ⅵ 섹션)를 정확히 따르세요.\n"
            "- 04_TONE_AND_STYLE.md의 문체·서식 규칙을 준수하세요.\n"
            "- 마크다운 형식으로 작성하되, Typora에서 PDF 변환이 가능하도록 구성하세요.\n"
            "- 각 주요 섹션 앞에 <div style=\"page-break-before: always;\"></div>를 삽입하세요."
        )
        messages.append({"role": "user", "content": draft_instruction})

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_draft = ""
            try:
                stream = send_message(system_prompt, messages, stream=True)
                for chunk in stream:
                    full_draft += chunk
                    placeholder.markdown(full_draft + "▌")
                placeholder.markdown(full_draft)
            except Exception as ex:
                st.error(f"초안 생성 중 오류: {ex}")
                st.stop()

        messages.append({"role": "model", "content": full_draft})
        st.session_state["report_messages"] = messages
        st.session_state["report_draft"] = full_draft

    else:
        st.markdown(st.session_state["report_draft"])

    st.markdown("---")
    if st.button("검수 진행", type="primary", use_container_width=True):
        set_phase("reviewing")
        st.rerun()


# ══════════════════════════════════════════════════════════════
# Phase 4: 검수 (자동)
# ══════════════════════════════════════════════════════════════
elif current == "reviewing":
    st.subheader("4단계: 품질 검수")

    if not st.session_state["report_review"]:
        st.caption("AI가 06_CHECKLIST.md 기준으로 자기 검수를 수행합니다...")

        messages = st.session_state["report_messages"]
        system_prompt = get_system_prompt()

        review_instruction = (
            "방금 작성한 손해사정서 초안에 대해 06_CHECKLIST.md의 모든 항목을 점검하세요.\n\n"
            "아래 6개 영역을 각각 검증하고 결과를 보고하세요:\n"
            "1. 사실관계 정확성\n"
            "2. 논리적 일관성\n"
            "3. 계산 정확성\n"
            "4. 법적 적합성\n"
            "5. 형식적 완결성\n"
            "6. 할루시네이션 검증\n\n"
            "각 항목에 대해 통과/미통과를 표시하고, 미통과 시 수정 사항을 제시하세요.\n"
            "수정이 필요한 경우 수정된 최종 보고서를 다시 제출하세요."
        )
        messages.append({"role": "user", "content": review_instruction})

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_review = ""
            try:
                stream = send_message(system_prompt, messages, stream=True)
                for chunk in stream:
                    full_review += chunk
                    placeholder.markdown(full_review + "▌")
                placeholder.markdown(full_review)
            except Exception as ex:
                st.error(f"검수 중 오류: {ex}")
                st.stop()

        messages.append({"role": "model", "content": full_review})
        st.session_state["report_messages"] = messages
        st.session_state["report_review"] = full_review

    else:
        st.markdown(st.session_state["report_review"])

    st.markdown("---")
    if st.button("완료 및 다운로드", type="primary", use_container_width=True):
        set_phase("complete")
        st.rerun()


# ══════════════════════════════════════════════════════════════
# Phase 5: 완료
# ══════════════════════════════════════════════════════════════
elif current == "complete":
    st.subheader("5단계: 완료")
    st.success("손해사정서가 완성되었습니다!")

    draft = st.session_state["report_draft"]
    data = st.session_state["report_data"]
    insured = data.get("insured_name", "보고서")

    # 보고서 렌더링
    with st.expander("최종 보고서 보기", expanded=True):
        st.markdown(draft)

    # 다운로드 버튼
    st.markdown("---")
    st.markdown("#### 다운로드")
    dl1, dl2 = st.columns(2)

    with dl1:
        st.download_button(
            label="마크다운(.md) 다운로드",
            data=draft.encode("utf-8"),
            file_name=f"손해사정서_{insured}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with dl2:
        try:
            from modules.report_pdf_exporter import markdown_to_pdf

            pdf_bytes = markdown_to_pdf(draft)
            st.download_button(
                label="PDF 다운로드",
                data=pdf_bytes,
                file_name=f"손해사정서_{insured}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except ImportError:
            st.info("PDF 변환 모듈(report_pdf_exporter)이 없습니다. MD 파일을 Typora에서 PDF로 변환하세요.")
        except Exception as ex:
            st.warning(f"PDF 변환 실패: {ex}")
            st.info("MD 파일을 다운로드하여 Typora에서 PDF로 변환해주세요.")

    # 수정 요청
    st.markdown("---")
    st.markdown("#### 수정 요청")
    revision_request = st.text_area(
        "수정할 내용을 입력하세요",
        placeholder="예: Ⅲ장의 치료내용을 더 상세히 작성해주세요.",
        key="revision_input",
    )
    if st.button("수정 요청 보내기"):
        if revision_request:
            messages = st.session_state["report_messages"]
            messages.append({"role": "user", "content": f"다음 사항을 수정해 주세요:\n\n{revision_request}"})

            system_prompt = get_system_prompt()
            with st.spinner("수정 중..."):
                try:
                    full_revision = ""
                    stream = send_message(system_prompt, messages, stream=True)
                    for chunk in stream:
                        full_revision += chunk

                    messages.append({"role": "model", "content": full_revision})
                    st.session_state["report_messages"] = messages
                    st.session_state["report_draft"] = full_revision
                    st.rerun()
                except Exception as ex:
                    st.error(f"수정 중 오류: {ex}")
        else:
            st.warning("수정 내용을 입력해주세요.")
