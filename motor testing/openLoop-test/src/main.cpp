#include <Arduino.h>
#include <config.h>

int pwm = 0;

void motor(int vel, int channel)
{
  ledcWrite(channel, abs(vel));
}

void setup()
{
  Serial.begin(115200);

  ledcSetup(PWM_CHANNEL_LEFT, PWM_FREQ, PWM_RESOLUTION);
  ledcSetup(PWM_CHANNEL_RIGHT, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(PWM_LEFT, PWM_CHANNEL_LEFT);
  ledcAttachPin(PWM_RIGHT, PWM_CHANNEL_RIGHT);

  pinMode(IN1_LEFT, OUTPUT); // talves seja melhor inverter o robo e essa vira roda direita
  pinMode(IN2_LEFT, OUTPUT);
  pinMode(IN1_RIGHT, OUTPUT);
  pinMode(IN2_RIGHT, OUTPUT);

  digitalWrite(IN1_LEFT, LOW); // girando horário
  digitalWrite(IN2_LEFT, HIGH);
  digitalWrite(IN1_RIGHT, HIGH); // girando horário
  digitalWrite(IN2_RIGHT, LOW);

  pwm = 255;
  motor(pwm, PWM_CHANNEL_LEFT);
  delay(15000);
  pwm = 0;
  motor(pwm, PWM_CHANNEL_LEFT);
}

void loop()
{
}