

#include "step_motor.h"

const float VOLTAGE_THRESHOLD = 4.0;

StepMotor::StepMotor() {
  
}

StepMotor::StepMotor(int interface, int pin1, int pin2, int stepsPerDeg) {
  stepper = AccelStepper(interface, pin1, pin2);
  stepsPerDegree = stepsPerDeg;

  stepper.setMaxSpeed(100000);
  stepper.setAcceleration(3700);
}

void StepMotor::initialize() {
  currentAngle = 0;
}

void StepMotor::finalize() {

}

void StepMotor::moveUntilDone(int steps) {
  stepper.move(steps);
  // Doesn´t return control of Arduino until every step has been made
  while (stepper.distanceToGo() != 0) { 
    stepper.run();
  }
}

void StepMotor::moveTo(float angle) {
  float delta = angle - currentAngle;

  if (delta >= 180) {
    moveRelative(delta - currentAngle); 
  } else if (delta <= -180) {
    moveRelative(currentAngle + delta);
  } else {
    moveRelative(delta); // Caller for move executer function
  }

}

// Private function that actually executes the steps
void StepMotor::moveRelative(float degrees) {
  int steps = stepsPerDegree * degrees; // Calculates how many steps
  moveUntilDone(steps);

  currentAngle += degrees;
  currentAngle = fmod(currentAngle, 360.0);
}

float StepMotor::getAngle() {
  return currentAngle;
}
