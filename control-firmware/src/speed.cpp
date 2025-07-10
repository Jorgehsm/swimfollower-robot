#include <config.h>
#include <Arduino.h>
#include <speed.h>
#include <stdint.h>

volatile uint32_t lastPulseTime = 0;
volatile bool newPulse = false;

volatile float w = 0.0;
float speed = 0;
float wheelRadius = WHEEL_RADIUS / 1000;

uint32_t delta = 0;

float speedHistory[MOVING_AVG_SIZE] = {0};
int historyIndex = 0;
bool historyFilled = false;

void IRAM_ATTR encoderISR()
{
    uint32_t now = micros();
    delta = now - lastPulseTime;
    lastPulseTime = now;
    newPulse = true;
}

void calcSpeed()
{
    float seconds = delta / 1e6;
    w = (2.0 * PI) / (ENCODER_PPR * seconds);
    speed = w * wheelRadius;
}

void updateAvg(float newSpeed)
{
    speedHistory[historyIndex] = newSpeed;
    historyIndex = (historyIndex + 1) % MOVING_AVG_SIZE;
    if (historyIndex == 0)
    {
        historyFilled = true;
    }
}

float getAvg()
{
    int count = historyFilled ? MOVING_AVG_SIZE : historyIndex;
    float sum = 0.0;
    for (int i = 0; i < count; i++)
    {
        sum += speedHistory[i];
    }
    return (count > 0) ? sum / count : 0.0;
}