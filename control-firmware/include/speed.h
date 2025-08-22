#ifndef SPEED_H
#define SPEED_H

#include <Arduino.h>
#include <config.h>

void encoderISR();
float calcSpeed();
void updateAvg(float newSpeed);
float getAvg();
void encoderSetup();
float encoderLoop();
void resetAvg();

#endif
