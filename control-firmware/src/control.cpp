#include <Arduino.h>
#include <stdint.h>
#include <config.h>
#include <control.h>
#include <actuator.h>

float kp = 0, ki = 0, kd = 0, last_error = 0, error_deriv = 0, error_int = 0;

bool S1_status = 0, S2_status = 0;

uint32_t t = 0;

void checkSensor()
{
    S1_status = digitalRead(S1);
    S2_status = digitalRead(S2);
}

void checkSerialInput()
{
    if (Serial.available() > 0)
    {
        String input_string = Serial.readStringUntil('\n');
        input_string.trim();

        if (input_string.indexOf(',') != -1)
        {
            // Parsing
            int first_comma = input_string.indexOf(',');
            int second_comma = input_string.indexOf(',', first_comma + 1);

            if (second_comma == -1)
            {
                Serial.println("ERRO: Comando de ganho incompleto. Use Kp,Ki,Kd");
                return;
            }

            // Converts to float
            float new_kp = input_string.substring(0, first_comma).toFloat();
            float new_ki = input_string.substring(first_comma + 1, second_comma).toFloat();
            float new_kd = input_string.substring(second_comma + 1).toFloat();

            if (new_kp >= 0.0f && new_ki >= 0.0f && new_kd >= 0.0f)
            {
                kp = new_kp;
                ki = new_ki;
                kd = new_kd;

                // Feedback
                Serial.print("GANHOS ATUALIZADOS: Kp=");
                Serial.print(kp);
                Serial.print(", Ki=");
                Serial.print(ki);
                Serial.print(", Kd=");
                Serial.println(kd);
            }
            else
            {
                Serial.println("ERRO: Valores de ganho invalidos.");
            }
        }

        else
        {
            float error = input_string.toFloat();

            // Verifica se a conversao para float foi bem-sucedida
            if (input_string.length() > 0 && error != 0.0f)
            {
                if (error == 999.0f)
                {
                    control(0.0f);
                    stop();
                }
                else
                {
                    checkSensor();
                    control(error);
                }
            }
            // Trata o caso de erro ser 0.0 (pode ser intencional ou falha na conversao)
            else if (input_string.equals("0") || input_string.equals("0.0"))
            {
                checkSensor();
                control(0.0f);
            }

            // Unknown command
            else if (input_string.length() > 0)
            {
                Serial.println("Comando/Erro desconhecido: ");
            }
        }
    }
}

void motor(int16_t vel)
{
    if (S1_status == LOW && S2_status == LOW)
    {
        if (vel <= 0)
        {
            forward(abs(vel));
        }

        else if (vel > 0)
        {
            backwards(abs(vel));
        }
    }
    else if (S1_status == HIGH && S2_status == LOW)
    {
        spinCCW();
    }
    else if (S1_status == LOW && S2_status == HIGH)
    {
        //spinCW();
    }
    else
    {
        stop();
    }
}

void control(float error)
{

        if (fabs(error) < DEADZONE)
    {
        error = 0.0f;
    }

    uint32_t now = millis();
    uint32_t dt = (now - t);
    if (dt == 0) dt = 1;
    t = now;
    float dt_s = dt * 0.001f;

    error_deriv = (error - last_error) / (dt_s);

    float u = kp * error + ki * error_int + kd * error_deriv;

    if (u < 255 && u > -255)
    {
        error_int += 0.5f * (last_error + error) * dt_s;
    }

    u = constrain(u, -255, 255);
    last_error = error;

    float pwm = u;
    motor(int(pwm));
}

void controlSetup()
{
    Serial.begin(115200);

    ledcSetup(PWM_CHANNEL_LEFT, PWM_FREQ, PWM_RESOLUTION);
    ledcSetup(PWM_CHANNEL_RIGHT, PWM_FREQ, PWM_RESOLUTION);
    ledcAttachPin(PWM_LEFT, PWM_CHANNEL_LEFT);
    ledcAttachPin(PWM_RIGHT, PWM_CHANNEL_RIGHT);

    pinMode(IN1_LEFT, OUTPUT);
    pinMode(IN2_LEFT, OUTPUT);
    pinMode(IN1_RIGHT, OUTPUT);
    pinMode(IN2_RIGHT, OUTPUT);

    stop();

    pinMode(S1, INPUT);
    pinMode(S2, INPUT);

    t = millis();
}