#include <SoftwareSerial.h>
#include <ArduinoJson.h>
#include <Servo.h>
Servo Servo1;
SoftwareSerial ESPserial(3, 1);

bool LegoGubbar;
int ClosestObject[1];
int RoadType[3];
int BothV;
int BothX;
int arraySize;

String readString;

void setup() {
  Serial.begin(115200);
  Servo1.attach(13);
}

void loop() {
  while (Serial.available()) {
    delay(1);
    char c = Serial.read();
    readString += c; 
  }
  
  if (readString.length()) {
    StaticJsonBuffer<256> jsonBuffer;
    JsonArray& obj = jsonBuffer.parseArray(readString);
    
    bool LegoGubbar = obj[0];
    Serial.print("LegoGubbar: "+String(LegoGubbar));

    Serial.print(" | ClosestObject: ");
    arraySize = obj[1].size();
    for (int i = 0; i < arraySize; i++){
      ClosestObject[i] = obj[1][i];
      Serial.print(String(ClosestObject[i])+", ");
    }
    
    Serial.print(" | RoadType: ");
    arraySize = obj[2].size();
    for (int i = 0; i < arraySize; i++){
      RoadType[i] = obj[2][i];
      Serial.print(String(RoadType[i])+", ");

    }
    
    int BothV = obj[3];
    int BothX = obj[4];
    
    Serial.println(" | BothV: "+String(1023/180*BothV)+" | BothX: "+String(BothX));
    
    readString="";
    Servo1.write(int(1023/180*BothV));
  }
}

