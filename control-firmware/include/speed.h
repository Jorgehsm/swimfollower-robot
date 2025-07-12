#ifndef SPEED_H
#define SPEED_H

#include <Arduino.h>

extern volatile uint32_t lastPulseTime;
extern volatile bool newPulse;

void encoderISR();
float calcSpeed();
void updateAvg(float newSpeed);
float getAvg();
void encoderSetup();
void encoderLoop();

#endif
