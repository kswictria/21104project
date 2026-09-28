import streamlit as st
import serial
from serial.tools import list_ports

from ai import ask_gemini
from motor import send_command


# =========================================================
# 페이지 설정
# =========================================================

st.set_page_config(
    page_title="AI 탐사 임무",
    page_icon="🤖",
    layout="wide"
)


# =========================================================
# Session State
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

st.title("🤖 AI 탐사 임무")

st.write(
    "화성 환경을 입력하면 Gemini AI가 탐사 전략을 결정합니다."
)

st.divider()


# =========================================================
# ESP32 연결 설정
# =========================================================

st.header("🔌 1. ESP32 연결")

ports = list_ports.comports()

if ports:

    port_options = [
        f"{port.device} | {port.description}"
        for port in ports
    ]

    selected_index = st.selectbox(
        "ESP32 Serial 포트",
        range(len(port_options)),
        format_func=lambda x: port_options[x]
    )

    selected_port = ports[selected_index].device

else:

    st.warning(
        "현재 ESP32 Serial 포트를 자동으로 찾지 못했습니다."
    )

    selected_port = st.text_input(
        "Serial 포트를 직접 입력하세요.",
        value="COM3"
    )


baudrate = st.selectbox(
    "통신 속도",
    [9600, 19200, 38400, 57600, 115200],
    index=4
)


# =========================================================
# 연결 테스트
# =========================================================

if st.button("🔌 연결 상태 확인"):

    try:

        ser = serial.Serial(
            selected_port,
            baudrate,
            timeout=1
        )

        ser.close()

        st.success(
            f"ESP32 연결 가능: {selected_port}"
        )

    except Exception as e:

        st.error(
            f"ESP32 연결 실패: {e}"
        )


st.divider()


# =========================================================
# 화성 환경
# =========================================================

st.header("🪐 2. 화성 환경 입력")

col1, col2 = st.columns(2)


with col1:

    terrain = st.selectbox(
        "화성 지형",
        [
            "평탄한 암석 지형",
            "모래 지형",
            "자갈 지형",
            "바위가 많은 지형",
            "경사가 있는 암석 지형"
        ]
    )

    slope = st.slider(
        "경사도",
        0,
        40,
        5,
        1
    )


with col2:

    battery = st.slider(
        "배터리 잔량",
        0,
        100,
        80,
        1
    )

    obstacle = st.selectbox(
        "장애물 위치",
        [
            "없음",
            "왼쪽에 있음",
            "오른쪽에 있음",
            "정면에 있음"
        ]
    )


# =========================================================
# 환경 요약
# =========================================================

environment = {
    "terrain": terrain,
    "slope": slope,
    "battery": battery,
    "obstacle": obstacle
}


st.divider()

st.header("🧠 3. Gemini AI 판단")


# =========================================================
# AI 분석
# =========================================================

if st.button(
    "🤖 AI 탐사 판단 시작",
    type="primary",
    use_container_width=True
):

    with st.spinner(
        "Gemini가 화성 환경을 분석하고 있습니다..."
    ):

        try:

            result = ask_gemini(
                environment
            )

            action = result["action"]
            speed = int(result["speed"])
            risk = result["risk"]
            reason = result["reason"]


            # =================================================
            # 안전 규칙
            # =================================================

            if obstacle == "정면에 있음":

                action = "STOP"
                speed = 0
                risk = "HIGH"

                reason = (
                    "정면에 장애물이 있기 때문에 "
                    "충돌 방지를 위해 정지합니다."
                )


            elif battery <= 10:

                action = "STOP"
                speed = 0
                risk = "HIGH"

                reason = (
                    "배터리가 10% 이하이므로 "
                    "탐사 로버를 정지합니다."
                )


            elif slope >= 25:

                action = "STOP"
                speed = 0
                risk = "HIGH"

                reason = (
                    "경사도가 25도 이상이므로 "
                    "전복 위험을 고려하여 정지합니다."
                )


            elif slope >= 15:

                speed = min(
                    speed,
                    30
                )

                reason += (
                    " 경사도가 높기 때문에 "
                    "안전을 위해 속도를 30% 이하로 제한했습니다."
                )


            # 속도 범위
            speed = max(
                0,
                min(100, speed)
            )


            result = {
                "action": action,
                "speed": speed,
                "risk": risk,
                "reason": reason
            }


            # 결과 저장
            st.session_state.ai_result = result

            st.session_state.last_environment = environment


            # 기록
            history_item = {
                "time": datetime.now().strftime(
                    "%H:%M:%S"
                ),
                "terrain": terrain,
                "slope": slope,
                "battery": battery,
                "obstacle": obstacle,
                "action": action,
                "speed": speed,
                "risk": risk,
                "reason": reason,
                "executed": False
            }

            st.session_state.mission_history.append(
                history_item
            )


            st.success(
                "Gemini AI 탐사 판단 완료"
            )


        except Exception as e:

            st.error(
                f"AI 분석 오류: {e}"
            )


# =========================================================
# AI 결과
# =========================================================

if st.session_state.ai_result:

    result = st.session_state.ai_result

    st.subheader("📡 AI 판단 결과")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "주행 명령",
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
        f"🧠 판단 근거\n\n"
        f"{result['reason']}"
    )


    st.divider()


    # =====================================================
    # 실제 로버 실행
    # =====================================================

    st.header("🚀 4. AI 추천 주행 실행")

    st.warning(
        "이 버튼은 수동 조종 버튼이 아닙니다. "
        "Gemini AI가 앞에서 결정한 명령만 ESP32로 전달합니다."
    )


    if st.button(
        "🚀 AI 판단대로 로버 실행",
        type="primary",
        use_container_width=True
    ):

        try:

            send_command(
                port=selected_port,
                baudrate=baudrate,
                action=result["action"],
                speed=result["speed"]
            )


            # 가장 최근 기록을 실행 완료로 변경
            if st.session_state.mission_history:

                st.session_state.mission_history[-1][
                    "executed"
                ] = True


            st.success(
                f"ESP32에 전달 완료\n\n"
                f"{result['action']} / "
                f"{result['speed']}%"
            )


        except Exception as e:

            st.error(
                f"로버 실행 실패: {e}"
            )


# =========================================================
# 실행 원리
# =========================================================

st.divider()

st.header("⚙️ AI 주행 처리 과정")

st.markdown(
    """
    **① 화성 환경 입력**

    ↓

    **② Gemini AI가 환경 분석**

    ↓

    **③ 주행 방향과 속도 결정**

    ↓

    **④ 프로그램 안전 규칙 검증**

    ↓

    **⑤ USB Serial로 ESP32 전송**

    ↓

    **⑥ L298N이 모터 구동**

    ↓

    **⑦ 약 1.5초 후 자동 정지**
    """
)
