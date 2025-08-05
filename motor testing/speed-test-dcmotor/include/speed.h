#ifndef SPEED_H
#define SPEED_H

#include <Arduino.h>
#include <config.h>

//extern volatile uint32_t lastPulseTime;
//extern volatile bool newPulse;
extern volatile uint32_t delta;

void encoderISR();
float calcSpeed();
void updateAvg(float newSpeed);
float getAvg();
void encoderSetup();
float encoderLoop();
void resetAvg();

#endif
