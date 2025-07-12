#include <Arduino.h>
#include <config.h>
#include <speed.h>
#include <control.h>

void setup()
{
  controlSetup();
  encoderSetup();
}

void loop()
{
  checkSerialInput();
  encoderLoop();
}
