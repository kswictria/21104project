from google import genai
from google.genai import types

from pydantic import BaseModel
from typing import Literal

import streamlit as st


# =========================================================
# Gemini가 반환해야 하는 데이터 구조
# =========================================================

class RoverDecision(BaseModel):

    action: Literal[
        "FORWARD",
        "LEFT",
        "RIGHT",
        "STOP"
    ]

    speed: int

    risk: Literal[
        "LOW",
        "MEDIUM",
        "HIGH"
    ]

    reason: str


# =========================================================
# Gemini AI 호출
# =========================================================

def ask_gemini(environment):

    api_key = st.secrets["GEMINI_API_KEY"]

    model_name = st.secrets.get(
        "GEMINI_MODEL",
        "gemini-2.5-flash"
    )

    client = genai.Client(
        api_key=api_key
    )


    terrain = environment["terrain"]
    slope = environment["slope"]
    battery = environment["battery"]
    obstacle = environment["obstacle"]


    prompt = f"""
당신은 화성 탐사 로버의 자율주행 의사결정 AI입니다.

다음 환경을 분석하여 로버의 주행 행동을 결정하세요.

[화성 환경]

지형:
{terrain}

경사도:
{slope}도

배터리:
{battery}%

장애물:
{obstacle}


[가능한 행동]

FORWARD
= 전진

LEFT
= 왼쪽 회전

RIGHT
= 오른쪽 회전

STOP
= 정지


[판단 규칙]

1. 정면에 장애물이 있으면 STOP을 선택하세요.

2. 배터리가 10% 이하라면 STOP을 선택하세요.

3. 경사도가 25도 이상이면 STOP을 선택하세요.

4. 경사도가 15도 이상이면 속도를 낮추세요.

5. 위험한 지형에서는 낮은 속도를 사용하세요.

6. speed는 0~100 사이의 정수여야 합니다.

7. 안전한 탐사를 우선하세요.

8. reason에는 판단 근거를 한국어로 작성하세요.

반드시 지정된 JSON 구조에 맞게 답변하세요.
"""


    response = client.models.generate_content(

        model=model_name,

        contents=prompt,

        config=types.GenerateContentConfig(

            response_mime_type="application/json",

            response_schema=RoverDecision
        )
    )


    result = RoverDecision.model_validate_json(
        response.text
    )


    return result.model_dump()
