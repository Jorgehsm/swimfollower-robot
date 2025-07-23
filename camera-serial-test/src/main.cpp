#include <Arduino.h>

void setup()
{
  Serial.begin(115200);
}

void loop()
{
   if (Serial.available() > 0)
    {
        float error = Serial.parseFloat();
        Serial.println(error);
    }
}