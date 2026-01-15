#ifndef CONFIG_H
#define CONFIG_H

#define ENCODER 4 
#define PWM_LEFT 14
#define IN1_LEFT 27
#define IN2_LEFT 26

#define PWM_RIGHT 32
#define IN1_RIGHT 25
#define IN2_RIGHT 33

// LOW = N detecta / HIGH = Detecta
#define S1 35 //Laranja
#define S2 34 //Amarelo

#define ENCODER_PPR 10

#define MOVING_AVG_SIZE 10

#define STOP_TIMEOUT 200000  //200 ms em microssegundos
#define DEBOUNCE_US 17000 //17 ms

#define PWM_CHANNEL_LEFT 0
#define PWM_CHANNEL_RIGHT 1
#define PWM_FREQ 15000      // 5 kHz
#define PWM_RESOLUTION 8    // 8 bits -> duty 0-255

#define WHEEL_DIAMETER 305 //wheel radius in mm

#define DEADZONE 15.0f

#endif // CONFIG_H