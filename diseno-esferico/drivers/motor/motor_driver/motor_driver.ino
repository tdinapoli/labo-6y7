#include <Arduino.h>
#include "BasicStepperDriver.h"

// Motor steps per revolution. Most steppers are 200 steps or 1.8 degrees/step
#define MOTOR_STEPS 200
#define RPM 120

// Since microstepping is set externally, make sure this matches the selected mode
// If it doesn't, the motor will move at a different RPM than chosen
// 1=full step, 2=half step etc.
#define MICROSTEPS 2

// All the wires needed for full functionality
#define DIR 13
#define STEP 12

#define BAUDRATE 115200

BasicStepperDriver stepper(MOTOR_STEPS, DIR, STEP);

void setup() {
  Serial.begin(BAUDRATE);
  Serial.println("Chanoscopio v0.2");
  stepper.begin(RPM, MICROSTEPS);
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

void serialEvent() {
  if (Serial.available() > 0) {
    unsigned char function_byte = (char) Serial.read();
    
    int parameter_byte = (int) Serial.read();

    if (function_byte & B000001) {

      stepper.setRPM(parameter_byte);
    }
    else if (function_byte & B000010) {
//      stepper.rotate(90);
//      delay(1000);
      stepper.rotate(parameter_byte);
    }
    serialFlush();
  }
}

void loop() {
//  stepper.move(-MOTOR_STEPS * MICROSTEPSSTEPS);
}
