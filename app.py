import streamlit as st

from ai import analyze_mission
from mqtt_control import publish_rover_command


# --------------------------------------------------
# 페이지 설정
# --------------------------------------------------

st.set_page_config(
    page_title="MARS-AI Rover",
    page_icon="🚀",
    layout="wide"
)


# --------------------------------------------------
# 제목
# --------------------------------------------------

st.title("🚀 MARS-AI Rover")
st.subheader("AI 기반 화성 탐사 로버 주행 시스템")

st.markdown(
    """
    화성의 가상 환경을 입력하면 AI가 탐사 로버의
    적절한 주행 방향과 속도를 판단합니다.

    AI의 판단 결과는 MQTT를 통해 실제 ESP32 로버로 전달됩니다.
    """
)


# --------------------------------------------------
# 사이드바 - 환경 설정
# --------------------------------------------------

st.sidebar.header("🪐 화성 환경 설정")

terrain = st.sidebar.selectbox(
    "지형",
    [
        "평지",
        "모래",
        "암석",
        "자갈"
    ]
)

slope = st.sidebar.slider(
    "경사도",
    min_value=0,
    max_value=30,
    value=5,
    step=1
)

battery = st.sidebar.slider(
    "배터리 잔량",
    min_value=0,
    max_value=100,
    value=80,
    step=5
)

obstacle = st.sidebar.selectbox(
    "전방 장애물",
    [
        "없음",
        "있음"
    ]
)


# --------------------------------------------------
# 현재 환경 표시
# --------------------------------------------------

st.header("📡 현재 탐사 환경")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("지형", terrain)

with col2:
    st.metric("경사도", f"{slope}°")

with col3:
    st.metric("배터리", f"{battery}%")

with col4:
    st.metric("장애물", obstacle)


st.divider()


# --------------------------------------------------
# AI 분석 버튼
# --------------------------------------------------

if st.button(
    "🤖 AI 탐사 판단 시작",
    type="primary",
    use_container_width=True
):

    with st.spinner("AI가 화성 환경을 분석하고 있습니다..."):

        result = analyze_mission(
            terrain=terrain,
            slope=slope,
            battery=battery,
            obstacle=obstacle
        )

    if not result["success"]:

        st.error(result["message"])

    else:

        st.session_state["mission_result"] = result


# --------------------------------------------------
# AI 분석 결과
# --------------------------------------------------

if "mission_result" in st.session_state:

    result = st.session_state["mission_result"]

    st.header("🤖 AI 탐사 판단")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "추천 행동",
            result["action"]
        )

    with col2:
        st.metric(
            "추천 속도",
            f'{result["speed"]}%'
        )

    with col3:
        st.metric(
            "위험도",
            result["risk"]
        )

    st.info(result["reason"])

    st.divider()

    st.header("🚀 실제 로버 실행")

    st.warning(
        "실행 버튼을 누르면 AI의 판단이 실제 로버의 모터로 전달됩니다."
    )

    if st.button(
        "🚀 AI 추천 주행 실행",
        type="primary",
        use_container_width=True
    ):

        action = result["action"]
        speed = result["speed"]

        # ------------------------------------------
        # 추가 안전장치
        # ------------------------------------------

        # 경사가 너무 높으면 속도를 강제로 제한
        if slope >= 20:
            speed = min(speed, 30)

        # 장애물이 있으면 무조건 정지
        if obstacle == "있음":
            action = "STOP"
            speed = 0

        # 배터리가 매우 낮으면 정지
        if battery <= 10:
            action = "STOP"
            speed = 0

        command_result = publish_rover_command(
            action=action,
            speed=speed
        )

        if command_result["success"]:

            st.success(
                f"명령 전달 완료: {action} / 속도 {speed}%"
            )

        else:

            st.error(
                command_result["message"]
            )


# --------------------------------------------------
# 시스템 설명
# --------------------------------------------------

st.divider()

st.header("⚙️ 시스템 구조")

st.code(
    """
Streamlit
    ↓
AI 환경 분석
    ↓
안전 규칙 검사
    ↓
MQTT Cloud
    ↓
ESP32
    ↓
L298N 모터 드라이버
    ↓
DC 모터 × 2
    ↓
Mars Rover
""",
    language="text"
)

st.caption(
    "※ 본 프로젝트는 실제 화성 환경이 아닌 교육용 시뮬레이션입니다."
)
