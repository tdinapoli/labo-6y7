//// ****** THIS FILE IS AUTOGENERATED ******
////
////          >>>> DO NOT CHANGE <<<<
////
/// 
///  Filename; /Users/grecco/Documents/code/spim/spim/drivers/arduino.py
///  Source class: MultiController
///  Generation timestamp: 2019-05-23T23:42:14.867609
///  Class code hash: d1b05b40a9df1b4a1656d0c3765fd920b632719c
///
/////////////////////////////////////////////////////////////


#include "inodriver_bridge.h"

SerialCommand sCmd;

void ok() {
  Serial.println("OK");
}

void error(const char* msg) {
  Serial.print("ERROR: ");
  Serial.println(msg);
}

void error_i(int errno) {
  Serial.print("ERROR: ");
  Serial.println(errno);
}

void bridge_loop() {
  while (Serial.available() > 0) {
    sCmd.readSerial();
  }
}

void bridge_setup() {
  //// Setup callbacks for SerialCommand commands

  // All commands might return
  //    ERROR: <error message>

  // All set commands return 
  //    OK 
  // if the operation is successfull

  // All parameters are ascii encoded strings
  sCmd.addCommand("INFO?", getInfo); 

  sCmd.setDefaultHandler(unrecognized); 

  sCmd.addCommand("LED ON", wrapperSet_LED);

  sCmd.addCommand("LEDS OFF", wrapperTurn_Off_LEDS)

}

//// Code 

void getInfo() {
  Serial.print("MultiController,");
  Serial.println(COMPILE_DATE_TIME);
}

void unrecognized(const char *command) {
  error("Unknown command");
}

void wrapperSet_LED() {
  char *arg;
  
  arg = sCmd.next();
  if (arg == NULL) {
    error("No value stated");
    return;
  }
  int value = atoi(arg);

  int err = set_LED(value);
  if (err == 0) {
    ok();
  } else {
    error_i(err);
  }
};

void wrapperTurn_Off_LEDS() {

  int err = turn_off_LEDS();
  if (err == 0) {
    ok();
  } else {
    error_i(err);
  }
};
