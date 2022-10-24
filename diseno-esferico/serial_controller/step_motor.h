

#include <Arduino.h>
#include <AccelStepper.h>

#include <math.h>

class StepMotor {

  AccelStepper stepper;
  float currentAngle;
  float stepsPerDegree;

  void moveUntilDone(int);

  public:

    StepMotor();
    
    StepMotor(int, int, int, int);

    void initialize();
    void finalize();

    void moveTo(float);

    void moveRelative(float);

    float getAngle();

};

