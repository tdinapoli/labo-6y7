//// ****** THIS FILE IS AUTOGENERATED ******
////
////          >>>> PLEASE ADAPT IT TO YOUR NEEDS <<<<
////
/// 
///  Filename; /Users/grecco/Documents/code/spim/spim/drivers/arduino.py
///  Source class: MultiController
///  Generation timestamp: 2019-05-23T23:42:14.868531
///  Class code hash: d1b05b40a9df1b4a1656d0c3765fd920b632719c
///
/////////////////////////////////////////////////////////////



#include "inodriver_user.h"

#define SHUTTER_ENABLE 10

#define COUNT_WHEELS 1
#define COUNT_SHUTTERS 3

#define LASER_PIN 11

StepMotor angular_controller;


void user_setup() {

  angular_controller = StepMotor(1, 12, 13, 1/360);

}

void user_loop() {
}

int call_INITIALIZE() {
  angular_controller.initialize();
  return 0;
};

int call_FINALIZE() {
  return 0;
};


// COMMAND: THETA, FEAT: theta
float get_THETA() {
  return angular_controller.getAngle();
};

int set_THETA(float value) {
  angular_controller.moveTo(value);
  return 0;
};