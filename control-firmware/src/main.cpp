#include <Arduino.h>
#include <config.h>
#include <speed.h>
#include <control.h>

unsigned long int lastSend = millis();

void setup()
{
  Serial.begin(115200);
  t = millis();
  pinMode(ENCODER, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER), encoderISR, RISING);
}

void loop()
{
  checkSerialInput();

  if (newPulse)
  {
    if (delta > 0)
    speed = calcSpeed();
    updateAvg(speed);

  }

  if (millis() - lastSend >= 200)
  {
    lastSend = millis();
    float avg = getAvg();
    Serial.println(avg);
    ;
  }
}
