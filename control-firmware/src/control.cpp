#include <Arduino.h>
#include <stdint.h>
#include <config.h>
#include <control.h>

float kp = 1, ki = 1, last_error = 0, error_int = 0;

uint32_t t = 0;

void checkSerialInput()
{
    if (Serial.available() > 0)
    {
        float error = Serial.parseFloat();
        control(error);
    }
}

void motor(int vel)
{
    analogWrite(PWM_LEFT, abs(vel));
    analogWrite(PWM_RIGHT, abs(vel) + 10);
}

void control(float error)
{
    uint32_t now = millis();
    uint32_t dt = (now - t);
    t = now;

    error_int += (0.0005f * (last_error + error) * (dt));

    float u = kp * error + ki * error_int;

    if (u >= 100)
    {
        u = 100;
        error_int -= (0.0005f * (last_error + error) * (dt));
    }
    else if (u <= 0)
    {
        u = 0;
        error_int -= (0.0005f * (last_error + error) * (dt));
    }

    last_error = error;

    float pwm = u * 255.0 / 100.0;
    motor(int(pwm));
}

void controlSetup()
{
    Serial.begin(115200);

    ledcSetup(PWM_CHANNEL_LEFT, PWM_FREQ, PWM_RESOLUTION);
    ledcSetup(PWM_CHANNEL_RIGHT, PWM_FREQ, PWM_RESOLUTION);
    ledcAttachPin(PWM_LEFT, PWM_CHANNEL);
    ledcAttachPin(PWM_LEFT, PWM_CHANNEL);

    pinMode(IN1_LEFT, OUTPUT);
    pinMode(IN2_LEFT, OUTPUT);
    digitalWrite(IN1_LEFT, LOW);
    digitalWrite(IN2_LEFT, HIGH);

    t = millis();
}