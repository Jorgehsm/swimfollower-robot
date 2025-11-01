#ifndef ACTUATOR_H
#define ACTUATOR_H

#include <Arduino.h>

void spinCW();
void spinCCW();
void stop();
void forward(u_int8_t vel);
void backwards(u_int8_t vel);

#endif
