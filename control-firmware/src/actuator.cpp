#include <Arduino.h>
#include <stdint.h>
#include <config.h>
#include <actuator.h>

void spinCW()
{
    digitalWrite(IN1_LEFT, HIGH);
    digitalWrite(IN2_LEFT, LOW);
    digitalWrite(IN1_RIGHT, LOW);
    digitalWrite(IN2_RIGHT, HIGH);
    ledcWrite(PWM_CHANNEL_LEFT, 200);
    ledcWrite(PWM_CHANNEL_RIGHT, 200);
}

void spinCCW()
{
    digitalWrite(IN1_LEFT, LOW);
    digitalWrite(IN2_LEFT, HIGH);
    digitalWrite(IN1_RIGHT, LOW);
    digitalWrite(IN2_RIGHT, HIGH);
    ledcWrite(PWM_CHANNEL_LEFT, 200);
    ledcWrite(PWM_CHANNEL_RIGHT, 200);
}

void stop()
{
    digitalWrite(IN1_LEFT, LOW);
    digitalWrite(IN2_LEFT, LOW);
    digitalWrite(IN1_RIGHT, LOW);
    digitalWrite(IN2_RIGHT, LOW);
    ledcWrite(PWM_CHANNEL_LEFT, 0);
    ledcWrite(PWM_CHANNEL_RIGHT, 0);
}

void forward(u_int8_t vel)
{
    digitalWrite(IN1_LEFT, HIGH);
    digitalWrite(IN2_LEFT, LOW);
    digitalWrite(IN1_RIGHT, HIGH);
    digitalWrite(IN2_RIGHT, LOW);
    ledcWrite(PWM_CHANNEL_LEFT, vel);
    ledcWrite(PWM_CHANNEL_RIGHT, vel);
}

void backwards(u_int8_t vel)
{
    digitalWrite(IN1_LEFT, LOW);
    digitalWrite(IN2_LEFT, HIGH);
    digitalWrite(IN1_RIGHT, LOW);
    digitalWrite(IN2_RIGHT, HIGH);
    ledcWrite(PWM_CHANNEL_LEFT, vel);
    ledcWrite(PWM_CHANNEL_RIGHT, vel);
}