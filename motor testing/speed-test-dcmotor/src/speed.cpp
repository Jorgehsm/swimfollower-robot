#include <config.h>
#include <Arduino.h>
#include <speed.h>
#include <stdint.h>

volatile uint32_t lastPulseTime = 0, delta = 0;
volatile bool newPulse = false;

uint32_t lastSend = 0;

float w = 0.0;
float speed = 0;

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

float calcSpeed()
{
    float seconds = delta / 1e6;
    w = (2.0 * PI) / (ENCODER_PPR * seconds);
    float rpm = w;
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
    lastPulseTime = millis();
    lastSend = millis();
    pinMode(ENCODER, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(ENCODER), encoderISR, RISING);
}

float encoderLoop()
{
    if (newPulse)
    {
        if (delta > 0)
        {
            speed = calcSpeed();
        }
        updateAvg(speed);
    }

    float avgSpeed = getAvg();
    return avgSpeed;
}