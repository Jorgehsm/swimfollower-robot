#include <Arduino.h>
#include <config.h>
#include <speed.h>

float motorSpeed = 0.0;
uint32_t t = millis();

void motor(int vel);

void setup()
{
  Serial.begin(9600);
  pinMode(PWM_LEFT, OUTPUT);
  pinMode(IN1_LEFT, OUTPUT);
  pinMode(IN2_LEFT, OUTPUT);
  digitalWrite(IN1_LEFT, HIGH);
  digitalWrite(IN2_LEFT, LOW);
  encoderSetup();

  delay(1000); // Wait for 1 second before starting the motor
  for (int i = 0; i <= 255; i += 15)
  {
    motor(i);

    delay(1000); // tempo para estabilizar

    resetAvg(); // limpa a média
    t = millis();

    while (millis() - t < 3000)
    {
      motorSpeed = calcSpeed();
    }

    Serial.print(i);
    Serial.print(", ");
    Serial.println(motorSpeed);
  }
  for (int i = 255; i >= 0; i--)
  {
    motor(i);
    delay(1);
  }
}

void loop()
{
}

void motor(int vel)
{
  analogWrite(PWM_LEFT, vel);
}