#include <Arduino.h>
#include "BasicStepperDriver.h"

// Motor steps per revolution. Most steppers are 200 steps or 1.8 degrees/step
#define MOTOR_STEPS 200
#define RPM 120

// Since microstepping is set externally, make sure this matches the selected mode
// If it doesn't, the motor will move at a different RPM than chosen
// 1=full step, 2=half step etc.
#define MICROSTEPS 1

// All the wires needed for full functionality
#define DIR 13
#define STEP 12

#define BAUDRATE 115200

BasicStepperDriver stepper(MOTOR_STEPS, DIR, STEP);

void setup() {
  Serial.begin(BAUDRATE);
  Serial.println("Chanoscopio v0.2");
  stepper.begin(RPM, MICROSTEPS);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
}

void set_rpm(float rpm) {
  stepper.setRPM(rpm);
}

void rotate(float deg) {
  stepper.rotate(deg);
}

void serialFlush(){
  while (Serial.available() > 0){
    char a = Serial.read();
  }
}

long getLong(){
    int byteArray[4];
    for (int i=0; i<4; i++){
        byteArray[i] = Serial.read();
        Serial.write(byteArray[i]);
        }
    for (int i=0; i<4; i++){
      Serial.write(byteArray[i]);
    }
    
    long combined;
    long x1 = (long)byteArray[0] << 0;
    long x2 = (long)byteArray[1] << 8;
    long x3 = (long)byteArray[2] << 16;
    long x4 = (long)byteArray[3] << 24;
    combined = x1 | x2 | x3 | x4;
    return combined;
    }

float getFloat(){
    }

void blinkSignal(){
  digitalWrite(LED_BUILTIN, HIGH);
  delay(200);
  digitalWrite(LED_BUILTIN, LOW);
  delay(200);

  digitalWrite(LED_BUILTIN, HIGH);
  delay(200);
  digitalWrite(LED_BUILTIN, LOW);
  delay(200);

  digitalWrite(LED_BUILTIN, HIGH);
  delay(200);
  digitalWrite(LED_BUILTIN, LOW);
  delay(200);
}

void serialEvent() {
  if (Serial.available() > 1) {
    unsigned char function_byte = (char) Serial.read();
    

    if (function_byte & B000001) {
        int parameter = Serial.read(); 
        if (parameter == 100){
          blinkSignal();
        }
        stepper.setRPM(parameter);
    }
    else if (function_byte & B000010) {
        int parameter = (int) Serial.read();
        //blinkSignal();
        if (parameter == 100){
            blinkSignal();
            }
        stepper.move(parameter);
    }
    else {
        serialFlush();
        }
  }
}

void loop() {
  //stepper.move(360);
  delay(1000);
}
