#include <Arduino.h>
#include <stdint.h>
#include <config.h>
#include <control.h>
#include <actuator.h>

float kp = 1, ki = 1, kd = 1, last_error = 0, error_deriv = 0, error_int = 0;

bool S1_status = 0, S2_status = 0;

uint32_t t = 0;

void checkSensor()
{
    S1_status = digitalRead(S1);
    S2_status = digitalRead(S2);
}

void checkSerialInput()
{
    if (Serial.available() > 0)
    {
        float error = Serial.parseFloat();
        if (error == 999) // valor sentinela recebido por serial
        {
            control(0);
        }
        else
        {
            control(error);
        }
    }
}

void motor(int16_t vel)
{
    if (S1_status == LOW && S2_status == LOW)
    {
        if (vel >= 0)
        {
            forward(abs(vel));
        }

        else if (vel < 0)
        {
            backwards(abs(vel));
        }
    }
    else if (S1_status == HIGH && S2_status == LOW)
    {
        spinCW();
    }
    else if (S1_status == LOW && S2_status == HIGH)
    {
        spinCCW();
    }
    else
    {
        stop();
    }
}

void control(float error)
{
    uint32_t now = millis();
    uint32_t dt = (now - t);
    t = now;

    error_int += (0.0005f * (last_error + error) * (dt));

    error_deriv = (error - last_error) / 0.001 * dt;

    float u = kp * error + ki * error_int + kd * error_deriv;

    if (u >= 100)
    {
        u = 100;
        error_int -= (0.0005f * (last_error + error) * (dt));
    }
    else if (u <= -100)
    {
        u = -100;
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
    ledcAttachPin(PWM_LEFT, PWM_CHANNEL_LEFT);
    ledcAttachPin(PWM_RIGHT, PWM_CHANNEL_RIGHT);

    pinMode(IN1_LEFT, OUTPUT);
    pinMode(IN2_LEFT, OUTPUT);
    pinMode(IN1_RIGHT, OUTPUT);
    pinMode(IN2_RIGHT, OUTPUT);

    stop();

    pinMode(S1, INPUT);
    pinMode(S2, INPUT);

    t = millis();
}