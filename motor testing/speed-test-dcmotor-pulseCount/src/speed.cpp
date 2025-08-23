#include <config.h>
#include <Arduino.h>
#include <speed.h>
#include <stdint.h>

volatile int pulseCount = 0;
volatile uint32_t lastPulseTime = 0;
uint32_t lastMeasurementTime = 0;
float currentSpeed = 0.0;

float speedHistory[MOVING_AVG_SIZE] = {0};
int historyIndex = 0;
bool historyFilled = false;

void IRAM_ATTR encoderISR()
{
    uint32_t now = micros();
    if (now - lastPulseTime > DEBOUNCE_US)
    {
        pulseCount++;
        lastPulseTime = now;
    }
}

void encoderSetup()
{
    pinMode(ENCODER, INPUT);
    attachInterrupt(digitalPinToInterrupt(ENCODER), encoderISR, FALLING);
    lastMeasurementTime = millis();
}

float encoderLoop()
{
    uint32_t now = millis();
    if (now - lastMeasurementTime >= 100)
    {

        noInterrupts();
        int pulses = pulseCount;
        pulseCount = 0;
        interrupts();

        lastMeasurementTime = now;

        if (pulses > 0)
        {
            float rotationsPerInterval = (float)pulses / ENCODER_PPR;
            float intervalInMinutes = 100.0 / 60000.0;
            currentSpeed = rotationsPerInterval / intervalInMinutes;
        }
        else
        {
            currentSpeed = 0.0;
        }

        updateAvg(currentSpeed);
    }
    return getAvg();
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

void resetAvg()
{
    for (int i = 0; i < MOVING_AVG_SIZE; i++)
    {
        speedHistory[i] = 0.0;
    }
    historyIndex = 0;
    historyFilled = false;
}