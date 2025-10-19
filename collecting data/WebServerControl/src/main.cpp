#include <Arduino.h>
#include <config.h>

int pwm = 0;

void motor(int vel)
{
  ledcWrite(PWM_CHANNEL_LEFT, abs(vel)) - 10;
  ledcWrite(PWM_CHANNEL_RIGHT, abs(vel));
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
  digitalWrite(IN1_RIGHT, LOW);
  digitalWrite(IN2_RIGHT, HIGH);

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
}