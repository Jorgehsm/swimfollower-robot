#include <Arduino.h>
/*#include <config.h>
#include <speed.h>

float motorSpeed = 0.0;

void motor(int vel);

void setup()
{
  encoderSetup();
}

void loop()
{
  for (int i = 0; i <= 255; i++)
  {
    motor(i);
    uint32_t t = millis();
    while (millis() - t < 1000)
    {
      // Wait for 1 second before changing speed
      motorSpeed = encoderLoop();
    }
    Serial.print(i);
    Serial.print(", ");
    Serial.println(motorSpeed);
  }
}

void motor(int vel)
{
  analogWrite(PWM_LEFT, abs(vel));
}*/

void setup() {
  Serial.begin(9600);
  delay(1000); // Wait for Serial to initialize
  for(int i = 0; i <= 255; i++) {
    Serial.print(i);
    Serial.print(", ");
    Serial.println(i*2);
    delay(10);
  }
}

void loop() {
}
