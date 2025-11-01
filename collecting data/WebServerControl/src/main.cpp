#include <Arduino.h>
#include <config.h>
#include <actuator.h>

int pwm = 0;

bool S1_status = 0, S2_status = 0;

void motor(uint8_t vel)
{
  forward(vel);
}

void setup()
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

  digitalWrite(IN1_LEFT, LOW);
  digitalWrite(IN2_LEFT, HIGH);
  digitalWrite(IN1_RIGHT, HIGH);
  digitalWrite(IN2_RIGHT, LOW);

  pinMode(S1, INPUT);
  pinMode(S2, INPUT);

  Serial.setTimeout(10);
}

void loop()
{
  if (Serial.available() > 0)
  {
    String val = Serial.readStringUntil('\n'); // até newline
    int pwm = val.toInt();
    motor(pwm);
    Serial.println(pwm);
  }

  /*if (digitalRead(S1) != S1_status || digitalRead(S2) != S2_status)
  {
    Serial.print(digitalRead(S1));
    Serial.print(", ");
    Serial.println(digitalRead(S2));
  }

  S1_status = digitalRead(S1);
  S2_status = digitalRead(S2);*/
}