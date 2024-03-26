#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"

Adafruit_MotorShield AFMS = Adafruit_MotorShield();
Adafruit_StepperMotor *stepperLinear = AFMS.getStepper(200, 2);
Adafruit_StepperMotor *stepperRotary = AFMS.getStepper(200, 1);
int STEPTYPE = DOUBLE;
float SPEED = 10;
#define LIMIT_SWITCH 7

String currentState = "idle";

void setup() {
  Serial.begin(9600);
  AFMS.begin();
  pinMode(LIMIT_SWITCH, INPUT_PULLUP);
  stepperLinear->setSpeed(SPEED);
  stepperRotary->setSpeed(SPEED);
  Serial.println("Ready");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }
}

void calibrateMachine() {
  currentState = "calibrating";
  Serial.println("calibrating");
  while (digitalRead(LIMIT_SWITCH) == HIGH) {
    stepperLinear->step(1, BACKWARD, STEPTYPE);
  }
  Serial.println("Calibration complete");
  currentState = "idle";
}


void processCommand(String command) {
  if (command == "calibrate") {
    calibrateMachine();
  } else if (command == "getState") {
    Serial.println(currentState);
  } else if (command.startsWith("moveLinear")) {
    int steps = command.substring(command.indexOf(" ") + 1).toInt();
    moveLinear(steps, steps > 0);
  } else if (command.startsWith("rotateEgg")) {
    int steps = command.substring(command.indexOf(" ") + 1).toInt();
    rotateEgg(steps, steps > 0);
  } else if (command.startsWith("wait")) {
    String key = command.substring(command.indexOf(" ") + 1);
    wait(key);
  } else if (command.startsWith("config")) {
    String commandCopy = command;
    commandCopy.trim(); // Remove leading and trailing whitespace

    // Find the position of the first space
    int spaceIndex = commandCopy.indexOf(' ');

    // Extract the key
    String key = commandCopy.substring(7, spaceIndex); // Assuming "config " is 7 characters long

    // Extract the value
    String value = commandCopy.substring(spaceIndex + 1);

    set(key, value);
}

  // Add more commands as needed
}

void set(String key, String value)  {
  if(key == "steptype") {
    STEPTYPE = value.toInt();
    Serial.println("Steptype is now " +String(STEPTYPE));
  } else if(key == "speed") {
    SPEED = value.toInt();
    Serial.println("Speed is now " +String(SPEED));
  }
  
}

void wait(String unlock) {
  Serial.println("waiting");
  currentState = "waiting"; 
  while (true) {
    if (Serial.available() > 0) {
      String command = Serial.readStringUntil('\n');
      if (command.startsWith("breakwait: ")) {
        String key = command.substring(11); // Assuming "breakwait: " is 11 characters
        if (key == unlock) {
          Serial.println("breakwait successful");
          currentState = "idle";
          return;
        } else {
          Serial.println("incorrect breakwait key");
        }
      } else if (command == "BREAKWAIT") {
        Serial.println("emergency breakwait successful");
        currentState = "idle";
        return;
      } else if (command == "getState") {
        Serial.println(currentState);
      } else {
        Serial.println("In BRAKESTATE, command ignored");
      }
    }
  }
}

void moveLinear(int steps, bool direction) {
  stepperLinear->step(abs(steps), direction ? FORWARD : BACKWARD, STEPTYPE);
  Serial.println("Linear move complete.");
}

void rotateEgg(int steps, bool direction) {
  stepperRotary->step(abs(steps), direction ? FORWARD : BACKWARD, STEPTYPE);
  Serial.println("Rotation complete.");
}
