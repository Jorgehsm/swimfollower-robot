#include <Arduino.h>
#include <stdint.h>
#include <config.h>
#include <control.h>

float kp = 1, ki = 1, error_int = 0, error_ant = 0, u = 0;
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
    unsigned long int dt = millis() - t;
    error_int += ((error_ant + error) * (dt) / 2000);

    u = kp * error + ki * error_int;

    if (u >= 100)
    {
        u = 100;
        error_int -= ((error_ant + error) * dt / 2000);
    }
    else if (u <= 0)
    {
        u = 0;
    }

    t = millis();
    error_ant = error;

    u = u * 255.0 / 100.0;
    motor(int(u));
}