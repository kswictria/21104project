/*
 * =========================================================
 * MARS-AI Rover
 * ESP32 + L298N + 2 DC Motors
 *
 * Serial command
 *
 * FORWARD,50
 * LEFT,40
 * RIGHT,40
 * STOP,0
 * =========================================================
 */


// =========================================================
// L298N 핀
// =========================================================

// 왼쪽 모터
const int LEFT_IN1 = 26;
const int LEFT_IN2 = 27;
const int LEFT_EN  = 25;

// 오른쪽 모터
const int RIGHT_IN1 = 14;
const int RIGHT_IN2 = 12;
const int RIGHT_EN  = 13;


// =========================================================
// PWM
// =========================================================

const int PWM_FREQUENCY = 1000;
const int PWM_RESOLUTION = 8;


// =========================================================
// 안전 설정
// =========================================================

const unsigned long COMMAND_DURATION = 1500;

unsigned long commandStartTime = 0;

bool motorRunning = false;


// =========================================================
// 모터 정지
// =========================================================

void stopMotors() {

    digitalWrite(
        LEFT_IN1,
        LOW
    );

    digitalWrite(
        LEFT_IN2,
        LOW
    );

    digitalWrite(
        RIGHT_IN1,
        LOW
    );

    digitalWrite(
        RIGHT_IN2,
        LOW
    );


    ledcWrite(
        LEFT_EN,
        0
    );

    ledcWrite(
        RIGHT_EN,
        0
    );


    motorRunning = false;
}


// =========================================================
// 전진
// =========================================================

void moveForward(
    int speedValue
) {

    digitalWrite(
        LEFT_IN1,
        HIGH
    );

    digitalWrite(
        LEFT_IN2,
        LOW
    );


    digitalWrite(
        RIGHT_IN1,
        HIGH
    );

    digitalWrite(
        RIGHT_IN2,
        LOW
    );


    int pwm = map(
        speedValue,
        0,
        100,
        0,
        255
    );


    ledcWrite(
        LEFT_EN,
        pwm
    );

    ledcWrite(
        RIGHT_EN,
        pwm
    );


    motorRunning = true;

    commandStartTime = millis();
}


// =========================================================
// 왼쪽 회전
// =========================================================

void turnLeft(
    int speedValue
) {

    digitalWrite(
        LEFT_IN1,
        LOW
    );

    digitalWrite(
        LEFT_IN2,
        HIGH
    );


    digitalWrite(
        RIGHT_IN1,
        HIGH
    );

    digitalWrite(
        RIGHT_IN2,
        LOW
    );


    int pwm = map(
        speedValue,
        0,
        100,
        0,
        255
    );


    ledcWrite(
        LEFT_EN,
        pwm
    );

    ledcWrite(
        RIGHT_EN,
        pwm
    );


    motorRunning = true;

    commandStartTime = millis();
}


// =========================================================
// 오른쪽 회전
// =========================================================

void turnRight(
    int speedValue
) {

    digitalWrite(
        LEFT_IN1,
        HIGH
    );

    digitalWrite(
        LEFT_IN2,
        LOW
    );


    digitalWrite(
        RIGHT_IN1,
        LOW
    );

    digitalWrite(
        RIGHT_IN2,
        HIGH
    );


    int pwm = map(
        speedValue,
        0,
        100,
        0,
        255
    );


    ledcWrite(
        LEFT_EN,
        pwm
    );

    ledcWrite(
        RIGHT_EN,
        pwm
    );


    motorRunning = true;

    commandStartTime = millis();
}


// =========================================================
// Serial 명령
// =========================================================

void processCommand(
    String command
) {

    command.trim();


    int commaIndex =
        command.indexOf(',');


    if (commaIndex == -1) {

        stopMotors();

        return;
    }


    String action =
        command.substring(
            0,
            commaIndex
        );


    String speedText =
        command.substring(
            commaIndex + 1
        );


    int speedValue =
        speedText.toInt();


    speedValue =
        constrain(
            speedValue,
            0,
            100
        );


    if (action == "FORWARD") {

        moveForward(
            speedValue
        );

    }

    else if (action == "LEFT") {

        turnLeft(
            speedValue
        );

    }

    else if (action == "RIGHT") {

        turnRight(
            speedValue
        );

    }

    else if (action == "STOP") {

        stopMotors();

    }

    else {

        stopMotors();
    }
}


// =========================================================
// Setup
// =========================================================

void setup() {

    Serial.begin(
        115200
    );


    pinMode(
        LEFT_IN1,
        OUTPUT
    );

    pinMode(
        LEFT_IN2,
        OUTPUT
    );

    pinMode(
        RIGHT_IN1,
        OUTPUT
    );

    pinMode(
        RIGHT_IN2,
        OUTPUT
    );


    ledcAttach(
        LEFT_EN,
        PWM_FREQUENCY,
        PWM_RESOLUTION
    );


    ledcAttach(
        RIGHT_EN,
        PWM_FREQUENCY,
        PWM_RESOLUTION
    );


    stopMotors();


    Serial.println(
        "MARS-AI Rover Ready"
    );
}


// =========================================================
// Loop
// =========================================================

void loop() {

    if (Serial.available()) {

        String command =
            Serial.readStringUntil(
                '\n'
            );


        processCommand(
            command
        );


        Serial.print(
            "Received: "
        );

        Serial.println(
            command
        );
    }


    // =====================================================
    // 자동 정지
    // =====================================================

    if (
        motorRunning &&
        millis() - commandStartTime
        >= COMMAND_DURATION
    ) {

        stopMotors();

        Serial.println(
            "AUTO STOP"
        );
    }
}
