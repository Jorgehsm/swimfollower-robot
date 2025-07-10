#ifndef SPEED_H
#define SPEED_H

#include <Arduino.h>

extern volatile unsigned long lastPulseTime;
extern volatile bool newPulse;

void encoderISR();
void updateAvg(float speed);
float getAvg();
void calcSpeed()

#endif
