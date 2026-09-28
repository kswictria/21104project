import streamlit as st
from datetime import datetime


# =========================================================
# 페이지 설정
# =========================================================

st.set_page_config(
    page_title="MARS-AI Rover",
    page_icon="🚀",
    layout="wide"
)


# =========================================================
# Session State 초기화
# =========================================================

if "ai_result" not in st.session_state:
    st.session_state.ai_result = None

if "mission_history" not in st.session_state:
    st.session_state.mission_history = []

if "last_environment" not in st.session_state:
    st.session_state.last_environment = None


# =========================================================
# 제목
# =========================================================

st.title("🚀 MARS-AI Rover")

st.subheader(
    "Gemini AI 기반 화성 탐사 로버 자율주행 시스템"
)

st.write(
    "화성의 지형, 경사도, 배터리, 장애물 정보를 분석하여 "
    "Gemini AI가 탐사 로버의 주행 방향과 속도를 결정하고, "
    "USB Serial을 통해 실제 ESP32 로버를 제어하는 프로젝트입니다."
)


st.divider()


# =========================================================
# 시스템 구조
# =========================================================

st.header("🛰️ 시스템 구조")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("### 🪐")
    st.write("화성 환경")

with col2:
    st.markdown("### 🤖")
    st.write("Gemini AI")

with col3:
    st.markdown("### 🛡️")
    st.write("안전 판단")

with col4:
    st.markdown("### 🔌")
    st.write("USB Serial")

with col5:
    st.markdown("### 🚀")
    st.write("실제 Rover")


st.divider()


# =========================================================
# 현재 상태
# =========================================================

st.header("📡 현재 탐사 상태")

if st.session_state.ai_result is None:

    st.info(
        "아직 AI 탐사 판단이 실행되지 않았습니다.\n\n"
        "왼쪽 메뉴에서 **🤖 AI 탐사 임무** 페이지로 이동하세요."
    )

else:

    result = st.session_state.ai_result

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "최근 주행 명령",
            result["action"]
        )

    with col2:
        st.metric(
            "주행 속도",
            f"{result['speed']}%"
        )

    with col3:
        st.metric(
            "위험도",
            result["risk"]
        )

    st.info(
        f"🧠 Gemini 판단: {result['reason']}"
    )


# =========================================================
# 최근 환경
# =========================================================

if st.session_state.last_environment:

    st.divider()

    st.header("🌍 최근 분석 환경")

    env = st.session_state.last_environment

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "지형",
            env["terrain"]
        )

    with col2:
        st.metric(
            "경사도",
            f"{env['slope']}°"
        )

    with col3:
        st.metric(
            "배터리",
            f"{env['battery']}%"
        )

    with col4:
        st.metric(
            "장애물",
            env["obstacle"]
        )


# =========================================================
# 탐사 기록 개수
# =========================================================

st.divider()

st.header("📊 탐사 통계")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "AI 탐사 판단 횟수",
        len(st.session_state.mission_history)
    )

with col2:

    if st.session_state.mission_history:

        executed = sum(
            1
            for item in st.session_state.mission_history
            if item["executed"]
        )

    else:

        executed = 0

    st.metric(
        "실제 로버 실행 횟수",
        executed
    )


# =========================================================
# 프로젝트 목적
# =========================================================

st.divider()

st.header("🎯 프로젝트 목적")

st.write(
    """
    이 프로젝트는 단순한 AI 챗봇이 아니라
    **AI의 판단을 실제 로봇 시스템의 행동으로 연결하는 것**을
    목표로 합니다.

    Gemini AI가 화성 환경을 분석하고 주행 전략을 결정한 뒤,
    프로그램이 안전 조건을 다시 확인하고,
    최종 명령을 ESP32로 전달합니다.

    따라서 인공지능, Python 프로그래밍, 임베디드 시스템,
    모터 제어를 하나의 시스템으로 연결할 수 있습니다.
    """
)


st.caption(
    "MARS-AI Rover | AI Decision → Safety Check → ESP32 → Motor"
)
