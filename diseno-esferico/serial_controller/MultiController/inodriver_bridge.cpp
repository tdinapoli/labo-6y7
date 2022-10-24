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


  // initialize

  // Call:
  //   INITIALIZE
  // Returns: OK or ERROR  
  sCmd.addCommand("INITIALIZE", wrapperCall_INITIALIZE); 

  // finalize

  // Call:
  //   FINALIZE
  // Returns: OK or ERROR  
  sCmd.addCommand("FINALIZE", wrapperCall_FINALIZE); 

  // theta
  // <F> float as string 

  // Getter:
  //   THETA? 
  // Returns: <F> 
  sCmd.addCommand("THETA?", wrapperGet_THETA); 

  // Setter:
  //   THETA <F> 
  // Returns: OK or ERROR    
  sCmd.addCommand("THETA", wrapperSet_THETA); 

  // Setter:
  //   STEP <F> 
  // Returns: OK or ERROR    
  sCmd.addCommand("STEP", wrapperSet_STEP); 
}

//// Code 

void getInfo() {
  Serial.print("MultiController,");
  Serial.println(COMPILE_DATE_TIME);
}

void unrecognized(const char *command) {
  error("Unknown command");
}
//// Auto generated Feat and DictFeat Code
// COMMAND: INITIALIZE, Action: initialize

void wrapperCall_INITIALIZE() {
  int err = call_INITIALIZE();
  if (err == 0) {
    ok();
  } else {
    error_i(err);
  }
};

// COMMAND: FINALIZE, Action: finalize

void wrapperCall_FINALIZE() {
  int err = call_FINALIZE();
  if (err == 0) {
    ok();
  } else {
    error_i(err);
  }
};


// COMMAND: THETA, FEAT: theta

void wrapperGet_THETA() { 
  Serial.println(get_THETA()); 
}; 


void wrapperSet_THETA() {
  char *arg;
  
  arg = sCmd.next();
  if (arg == NULL) {
    error("No value stated");
    return;
  }
  float value = atof(arg);

  int err = set_THETA(value);
  if (err == 0) {
    ok();
  } else {
    error_i(err);
  }
};

void wrapperSet_STEP() {
  char *arg;
  
  arg = sCmd.next();
  if (arg == NULL) {
    error("No value stated");
    return;
  }
  int value = atoi(arg);

  int err = set_STEP(value);
  if (err == 0) {
    ok();
  } else {
    error_i(err);
  }
};

