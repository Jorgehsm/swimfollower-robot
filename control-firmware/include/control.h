#ifndef CONTROL_H
#define CONTROL_H

#include <Arduino.h>

void checkSerialInput();
void control(float error);
void controlSetup();
void motor();

#endif
