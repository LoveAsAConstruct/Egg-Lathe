#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"
#include "LedControl.h"
#include "CommandMapping.h"
Adafruit_MotorShield AFMS = Adafruit_MotorShield();
Adafruit_StepperMotor *stepperLinear = AFMS.getStepper(200, 2);
Adafruit_StepperMotor *stepperRotary = AFMS.getStepper(200, 1);
LedControl lc=LedControl(12,11,10,1);
unsigned long delaytime=250;
bool manualControl = true;
int STEPTYPE = DOUBLE;
float SPEED = 10;
#define LIMIT_SWITCH 7
int xHome = 0;
int yHome = 0;
int xPos = 0;
int yPos = 0;
String currentState = "idle";
String displayText = "HELLO EGG";
void setup() {
  Serial.begin(9600);
  AFMS.begin();
  pinMode(LIMIT_SWITCH, INPUT_PULLUP);
  stepperLinear->setSpeed(SPEED);
  stepperRotary->setSpeed(SPEED/2);
  xHome = analogRead(A0);
  yHome = analogRead(A1);
  Serial.println("Ready");
  /*
   The MAX72XX is in power-saving mode on startup,
   we have to do a wakeup call
   */
  lc.shutdown(0,false);
  /* Set the brightness to a medium values */
  lc.setIntensity(0,8);
  /* and clear the display */
  lc.clearDisplay(0);
  displayString("CAL");
  calibrateMachine();
}

void loop() {
  int xValue = analogRead(A0)-xHome;
  int yValue = analogRead(A1)-yHome;
  if (xPos == 0 && yPos == 0) {
    displayText = "HELLO EGG";
  }
  else {
    int newY = yPos % 200;
    if (newY < 0){
      newY = 200-newY;
    }
    displayText = formatIntegers(xPos,yPos);
  }
  displayString(displayText);
  if(manualControl){
    processMovement(xValue, yValue);
  }
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }
}

void processMovement(int xValue, int yValue){
  int limit = 100;
  if (abs(xValue) >= limit){
    int distance = 1;
    if (xValue >= limit){
      if(xPos - distance > 0){
        moveLinear(distance,false);
      }
    }
    else{
      if(xPos + distance < 200){
        moveLinear(distance,true);
      }
    }
  }
  if (abs(yValue) >= limit){
    if (yValue <= -limit){
      rotateEgg(1,false);
    }
    else if (yValue >= limit){
      rotateEgg(1,true );
    }
  }
}

void calibrateMachine() {
  currentState = "calibrating";
  Serial.println("calibrating");
  while (digitalRead(LIMIT_SWITCH) == HIGH) {
    stepperLinear->step(1, BACKWARD, STEPTYPE);
  }
  xPos = 0;
  Serial.println("Calibration complete");
  currentState = "idle";
}


void processCommand(String command) {
  if (command.startsWith(CommandPrefix)){
    if (command.startsWith(CommandPrefix + CalibratePrefix)) {
      calibrateMachine();
    } else if (command == "getState") {
      Serial.println(currentState);
    } else if (command.startsWith(CommandPrefix+MovementPrefix+XString)) {
      int steps = command.substring(command.indexOf(" ") + 1).toInt();
      moveLinear(steps, steps > 0);
    } else if (command.startsWith(CommandPrefix+MovementPrefix+YString)) {
      int steps = command.substring(command.indexOf(" ") + 1).toInt();
      rotateEgg(steps, steps > 0);
    } else if (command.startsWith(CommandPrefix+WaitPrefix)) {
      String key = command.substring(command.indexOf(" ") + 1);
      wait(key);
    } else if (command.startsWith(CommandPrefix+ConfigPrefix+SetPrefix)) {
      String key = command.substring(command.indexOf(":") + 1);
      String value = command.substring(command.indexOf(" ") + 1);
      set(key, value);
    }
    Serial.println(CommandComplete);
  }

  // Add more commands as needed
}

void set(String key, String value)  {
  Serial.println(StatusPrefix + " Setting key " +key +" to " +value);
  if(key.startsWith(SteptypePrefix)) {
    if (value == "micro"){
      STEPTYPE = MICROSTEP;
    } else if (value == "double"){
      STEPTYPE = DOUBLE;
    } else if (value == "inter"){
      STEPTYPE = INTERLEAVE;
    } else if (value == "single"){
      STEPTYPE = SINGLE;
    }
    Serial.println(ResponsePrefix+ "Steptype is now " +String(STEPTYPE));
  } else if(key.startsWith(SpeedPrefix)) {
    SPEED = value.toInt();
    Serial.println(ResponsePrefix+ "Speed is now " +String(SPEED));
    stepperLinear->setSpeed(SPEED);
    stepperRotary->setSpeed(SPEED/2);
  } else if(key.startsWith(InputPrefix)) {
    if (value == "enabled" or value == "true" or value == "T"){
      manualControl = true; 
    }
    else{
      manualControl = false; 
    }
    Serial.println(ResponsePrefix+ "Manual input is now " +String(manualControl));
  }
  
}

void wait(String unlock) {
  Serial.println("waiting");
  currentState = "waiting"; 
  while (true) {
    if (Serial.available() > 0) {
      String command = Serial.readStringUntil('\n');
      if (command.startsWith(CommandPrefix + BreakwaitPrefix)) {
        String key = command.substring(command.indexOf(" ") + 1);
        if (key == unlock) {
          Serial.println(ResponsePrefix+"breakwait successful");
          currentState = "idle";
          return;
        } else {
          Serial.println(ResponsePrefix+"incorrect breakwait key");
        }
      } else if (command == FORCEBREAKWAIT) {
        Serial.println(ResponsePrefix+"emergency breakwait successful");
        currentState = "idle";
        return;
      } else if (command == "getState") {
        Serial.println(currentState);
      } else {
        Serial.println(ResponsePrefix+"In BRAKESTATE, command ignored");
      }
    }
  }
}

void moveLinear(int steps, bool direction) {
  xPos += (abs(steps) * direction ? 1 : -1);
  stepperLinear->step(abs(steps), direction ? FORWARD : BACKWARD, STEPTYPE);
  Serial.println(StatusPrefix + "Linear move complete.");
}

void rotateEgg(int steps, bool direction) {
  yPos += (abs(steps) * direction ? 1 : -1);
  stepperRotary->step(abs(steps), direction ? FORWARD : BACKWARD, STEPTYPE);
  Serial.println(StatusPrefix + "Rotation complete.");
}

// Function to display a string on the LED, corrected for left to right display with original character order.
void displayString(String str) {
  // Ensure the string is not longer than 8 characters.
  if(str.length() > 8) {
    str = str.substring(0, 8);
  }

  // Left-align the text, assuming empty spaces for the unused digits.
  int emptySpaces = 8 - str.length(); // Calculate empty spaces if the string is less than 8 characters.

  for(int i = 0; i < str.length(); i++) {
    // Extract each character from the string from end to start for correct order.
    char c = str.charAt(str.length() - 1 - i);
    // Convert the character to a segment pattern and display it, adjusting for empty spaces.
    byte segmentPattern = charToSegment(c);
    lc.setRow(0, emptySpaces + i, segmentPattern);
  }
}

// Function to map characters to their 7-segment display patterns.
byte charToSegment(char c) {
    switch(c) {
        case '0': return B01111110;
        case '1': return B00110000;
        case '2': return B01101101;
        case '3': return B01111001;
        case '4': return B00110011;
        case '5': return B01011011;
        case '6': return B01011111;
        case '7': return B01110000;
        case '8': return B01111111;
        case '9': return B01111011;
        // Support for uppercase letters that can be represented on a 7-segment display.
        case 'A': case 'a': return B01110111;
        case 'B': case 'b': return B00011111;
        case 'C': return B01001110;
        case 'c': return B00001101;
        case 'D': case 'd': return B00111101;
        case 'E': case 'e': return B01001111;
        case 'F': case 'f': return B01000111;
        case 'G': case 'g': return B01011110;
        case 'H': return B00110111;
        case 'h': return B00010111;
        case 'I': return B00110000;
        case 'i': return B00010000;
        case 'J': case 'j': return B00111100;
        case 'L': case 'l': return B00001110;
        case 'N': case 'n': return B00010101;
        case 'O': case 'o': return B00011101;
        case 'P': case 'p': return B01100111;
        case 'S': case 's': return B01011011;
        case 'U': case 'u': return B00011100;
        case 'Y': case 'y': return B00111011;
        case '-': return B0000001;
        // Note: Some letters like 'K', 'M', 'Q', 'V', 'W', 'X', 'Z' cannot be accurately represented on a 7-segment display.
        default:  return B00000000; // For unsupported characters, no segments are lit.
    }
}
String formatIntegers(int input1, int input2) {
  // Convert both integers to strings.
  String str1 = String(input1);
  String str2 = String(input2);
  
  // Truncate or pad the first string to ensure it is exactly 4 characters.
  if(str1.length() > 4) {
    str1 = str1.substring(str1.length() - 4);
  } else {
    while(str1.length() < 4) {
      str1 = " " + str1; // Left padding with spaces.
    }
  }
  
  // Truncate or pad the second string to ensure it is exactly 4 characters.
  if(str2.length() > 4) {
    str2 = str2.substring(str2.length() - 4);
  } else {
    while(str2.length() < 4) {
      str2 = " " + str2; // Left padding with spaces.
    }
  }
  
  // Concatenate the two strings and return.
  return str1 + str2;
}
