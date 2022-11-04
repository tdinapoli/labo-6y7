

#include <Arduino.h>
#include <AccelStepper.h>

#include <math.h>

class StepMotor {

  AccelStepper stepper;
  float currentAngle;
  float stepsPerDegree;


  public:


    StepMotor();
    
    StepMotor(int, int, int, float);

    void initialize();
    void finalize();

    void moveTo(float);

    void moveUntilDone(int);

    void moveRelative(float);

    float getAngle();

};
