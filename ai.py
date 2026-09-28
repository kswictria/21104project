import json
import requests
import streamlit as st


OPENAI_URL = "https://api.openai.com/v1/responses"


def analyze_mission(
    terrain,
    slope,
    battery,
    obstacle
):

    # --------------------------------------------------
    # API 키 확인
    # --------------------------------------------------

    try:
        api_key = st.secrets["OPENAI_API_KEY"]

    except Exception:

        return {
            "success": False,
            "message": "OPENAI_API_KEY가 설정되지 않았습니다."
        }


    # --------------------------------------------------
    # 사용할 모델
    # --------------------------------------------------

    model = st.secrets.get(
        "OPENAI_MODEL",
        "gpt-5.6-luna"
    )


    # --------------------------------------------------
    # AI에게 전달할 정보
    # --------------------------------------------------

    mission_data = {
        "terrain": terrain,
        "slope_degree": slope,
        "battery_percent": battery,
        "obstacle": obstacle
    }


    # --------------------------------------------------
    # AI 지시문
    # --------------------------------------------------

    instructions = """
너는 화성 탐사 로버의 주행 판단을 보조하는 AI이다.

주어진 환경에서 가장 안전한 주행 행동을 선택한다.

사용 가능한 행동은 반드시 다음 중 하나이다.

FORWARD
LEFT
RIGHT
STOP

속도는 0부터 100 사이의 정수로 표현한다.

다음 안전 규칙을 반드시 지킨다.

1. 전방 장애물이 있으면 STOP
2. 배터리가 10% 이하이면 STOP
3. 경사가 20도 이상이면 속도는 최대 30
4. 모래나 자갈에서는 지나치게 높은 속도를 피한다
5. 위험한 상황에서는 STOP을 우선한다

반드시 아래 JSON 형식만 반환한다.

{
    "action": "FORWARD",
    "speed": 40,
    "risk": "낮음",
    "reason": "간단한 한국어 설명"
}

JSON 외의 설명은 작성하지 않는다.
"""


    # --------------------------------------------------
    # API 요청
    # --------------------------------------------------

    payload = {
        "model": model,
        "instructions": instructions,
        "input": json.dumps(
            mission_data,
            ensure_ascii=False
        ),
        "max_output_tokens": 200
    }


    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


    try:

        response = requests.post(
            OPENAI_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()


    except Exception as e:

        return {
            "success": False,
            "message": f"AI API 연결 오류: {e}"
        }


    # --------------------------------------------------
    # AI 결과 가져오기
    # --------------------------------------------------

    try:

        output_text = data["output"][0]["content"][0]["text"]

        result = json.loads(output_text)

    except Exception:

        return {
            "success": False,
            "message": "AI 결과를 JSON으로 해석하지 못했습니다."
        }


    # --------------------------------------------------
    # 결과 검증
    # --------------------------------------------------

    allowed_actions = [
        "FORWARD",
        "LEFT",
        "RIGHT",
        "STOP"
    ]

    action = str(
        result.get("action", "STOP")
    ).upper()


    if action not in allowed_actions:

        action = "STOP"


    try:

        speed = int(
            result.get("speed", 0)
        )

    except Exception:

        speed = 0


    speed = max(
        0,
        min(100, speed)
    )


    risk = str(
        result.get("risk", "알 수 없음")
    )

    reason = str(
        result.get("reason", "AI 판단 이유가 없습니다.")
    )


    # --------------------------------------------------
    # 프로그램 자체의 안전장치
    # --------------------------------------------------

    if obstacle == "있음":

        action = "STOP"
        speed = 0

        reason = "전방에 장애물이 있어 안전을 위해 정지합니다."


    if battery <= 10:

        action = "STOP"
        speed = 0

        reason = "배터리가 10% 이하이므로 정지합니다."


    if slope >= 20:

        speed = min(
            speed,
            30
        )


    return {
        "success": True,
        "action": action,
        "speed": speed,
        "risk": risk,
        "reason": reason
    }
