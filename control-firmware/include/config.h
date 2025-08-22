#ifndef CONFIG_H
#define CONFIG_H

#define ENCODER 4 
#define PWM_LEFT 14
#define IN1_LEFT 27
#define IN2_LEFT 26

#define PWM_RIGHT 32
#define IN1_RIGHT 25
#define IN2_RIGHT 33

#define S1 35
#define S2 34

#define ENCODER_PPR 10

#define MOVING_AVG_SIZE 10

#define STOP_TIMEOUT 200000  //100 ms em microssegundos
#define DEBOUNCE_US 17000 //17 ms

#define PWM_CHANNEL 0
#define PWM_FREQ 15000      // 5 kHz
#define PWM_RESOLUTION 8    // 8 bits -> duty 0-255

#define WHEEL_DIAMETER 220 //wheel radius in mm

#endif // CONFIG_H