#include <Arduino.h>
#include <config.h>
#include <speed.h>

float motorSpeed = 0.0;
uint32_t t = millis();

void motor(int vel);

void setup()
{
  Serial.begin(115200);

  // Configura o PWM
  ledcSetup(PWM_CHANNEL, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(PWM_LEFT, PWM_CHANNEL);

  pinMode(IN1_LEFT, OUTPUT);
  pinMode(IN2_LEFT, OUTPUT);
  digitalWrite(IN1_LEFT, LOW);
  digitalWrite(IN2_LEFT, HIGH);
  encoderSetup();
  t = millis();

  delay(5000); // Wait for 1 second before starting the motor
  for (int i = 165; i <= 255; i += 15)
  {
    motor(i);

    delay(3000); // tempo para estabilizar

    resetAvg(); // limpa a média
    t = millis();

    while (millis() - t < 10000)
    {
      encoderLoop();
    }

    motorSpeed = getAvg();
    Serial.print(i);
    Serial.print(", ");
    Serial.println(motorSpeed);
  }
  for (int i = 255; i >= 0; i--)
  {
    motor(i);
    delay(10);
  }

}

void loop()
{
}

void motor(int vel)
{
  ledcWrite(PWM_CHANNEL, vel);
}