import ssl
import uuid
import paho.mqtt.client as mqtt
import streamlit as st


def publish_rover_command(
    action,
    speed
):

    # --------------------------------------------------
    # Secrets 읽기
    # --------------------------------------------------

    try:

        host = st.secrets["MQTT_HOST"]
        port = int(st.secrets.get("MQTT_PORT", 8884))
        username = st.secrets["MQTT_USERNAME"]
        password = st.secrets["MQTT_PASSWORD"]

    except Exception:

        return {
            "success": False,
            "message": "MQTT 설정이 없습니다."
        }


    topic = st.secrets.get(
        "MQTT_TOPIC",
        "mars-rover/command"
    )


    # --------------------------------------------------
    # 명령 데이터
    # --------------------------------------------------

    message = f"{action},{speed}"


    # --------------------------------------------------
    # MQTT 클라이언트
    # --------------------------------------------------

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"streamlit-{uuid.uuid4().hex[:8]}",
        transport="websockets"
    )


    # HiveMQ Cloud WebSocket 경로
    client.ws_set_options(
        path="/mqtt"
    )


    # TLS
    client.tls_set(
        cert_reqs=ssl.CERT_REQUIRED
    )


    try:

        client.connect(
            host,
            port,
            keepalive=30
        )

        client.loop_start()

        result = client.publish(
            topic,
            message,
            qos=1
        )

        result.wait_for_publish()

        client.loop_stop()

        client.disconnect()


        if result.rc == mqtt.MQTT_ERR_SUCCESS:

            return {
                "success": True,
                "message": "MQTT 명령 전달 성공"
            }

        else:

            return {
                "success": False,
                "message": f"MQTT 전송 실패: {result.rc}"
            }


    except Exception as e:

        try:
            client.loop_stop()
            client.disconnect()
        except:
            pass

        return {
            "success": False,
            "message": f"MQTT 연결 오류: {e}"
        }
