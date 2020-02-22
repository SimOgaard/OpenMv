#include <SoftwareSerial.h>
SoftwareSerial ESPserial(3, 1);

String readString;

void setup() {
  Serial.begin(9600);
}

void loop() {
  while (Serial.available()) {
    delay(3);
    char c = Serial.read();
    readString += c; 
  }
  
  if (readString.length()) {
    Serial.println("I added this so it must work now right?: "+readString);
    readString="";
  } 
}

