#include <config.h>
#include <Arduino.h>
#include <speed.h>
#include <stdint.h>

volatile uint32_t lastPulseTime = 0, delta = 0;
volatile bool newPulse = false;

uint32_t lastSend = 0;

float speed = 0;

float speedHistory[MOVING_AVG_SIZE] = {0};
int historyIndex = 0;
bool historyFilled = false;

void IRAM_ATTR encoderISR()
{
    uint32_t now = micros();
    if (now - lastPulseTime > DEBOUNCE_US)
    {
        delta = now - lastPulseTime;
        lastPulseTime = now;
        newPulse = true;
    }
}

float calcSpeed()
{
    float f = 1e6 / (ENCODER_PPR * delta); // rad/s
    float rpm = f * 60;
    return rpm;
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

void encoderSetup()
{
    lastPulseTime = micros();
    lastSend = micros();
    pinMode(ENCODER, INPUT);
    attachInterrupt(digitalPinToInterrupt(ENCODER), encoderISR, FALLING);
}

float encoderLoop()
{
    uint32_t now = micros();
    if (newPulse)
    {
        newPulse = false;
        if (delta > 0)
        {
            speed = calcSpeed();
        }
        updateAvg(speed);
    }

    else if ((now - lastPulseTime) > STOP_TIMEOUT)
    {
        speed = 0;
        updateAvg(speed);
    }

    return getAvg();
}

void resetAvg()
{
    for (int i = 0; i < MOVING_AVG_SIZE; i++)
    {
        speedHistory[i] = 0.0;
    }
    historyIndex = 0;
    historyFilled = false;
}