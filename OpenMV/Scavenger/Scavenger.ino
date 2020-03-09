// Biblotek //
#include "EspMQTTClient.h"  //Hantering av hämtning/skickning av data (Mqtt)
#include <ArduinoJson.h>    //Hantering av strängar i json format
#include <SoftwareSerial.h> //Hantering av UART
#include <Servo.h>          //Hantering av Servo

// Pins //
SoftwareSerial ESPserial(3, 1); // Rx, Tx pin
Servo Servo1;                   // Definerar servot
#define D1 0                    // Motor Dir pin
#define Pw 5                    // Motor pin
#define He 4                    // Hallelement input pin

// Variabler //
String OWNER="A";                                                         // (Sträng) Ändra beroende på vems bil
unsigned long previousMillis, currentMillis = 0;                          // (Unsigned long) för användningen av millis (pga datatypens storlek)
const int RoadDist = 500;                                                 //      -||-      Längden på en väg
String payload, readString;                                               // (Sträng) Strängar som vi kan Jsonifiera
int LedState = LOW;                                                       // (Int) Lampans status

// Mqtt //
void onConnectionEstablished();                 // Krävs för att bibloteket ska fungera när denna har körts klart är du säker på att du är ansluten

EspMQTTClient client(                           // Alla parametrar för att anslutningen ska funka, ip, namn, lösen osv
  "ABB_Indgym_Guest",                           // SSD
  "Welcome2abb",                                // SSD lösen
  "maqiatto.com",                               // Mqtt ip
  1883,                                         // Mqtt port
  "simon.ogaardjozic@abbindustrigymnasium.se",  // Namn
  "scavenger",                                  // Lösen
  "scavengerA",                                 // Client Namn
  onConnectionEstablished,
  true,
  true
);

void onConnectionEstablished() {
  client.publish("simon.ogaardjozic@abbindustrigymnasium.se/Scavenger", OWNER + " ready");              // Vid lyckad anslutning skicka medelandet till representerande adress
  client.subscribe("simon.ogaardjozic@abbindustrigymnasium.se/Scavenger", [] (const String & payload) { // Prenumererar till "simon.og..." tillåter motagning av data
    StaticJsonBuffer<500> JsonBuffer;                                                                   // Skapar en buffer, hur mycket minne som vårt blivand jsonobject får använda
    JsonArray& root = JsonBuffer.parseArray(payload);                                                   // Skapar ett jsonobject av datan payload som vi kallar root
    if(root.success() && root[0] == OWNER || root.success() && root[0] == "A" ) {                       // Om ovan lyckas och Jsonobjekten är pointerat till "A" eller "B" (representativ till variabeln "OWNER")
      if (root[1] == 0){                                                                                // root[1] konstanterar uppgiften värdena ör 0 = follow, 1 = left, 2 = right, 3 = drop
        State = FollowLine;                                                                                
      } else if (root[1] == 1) {                                                                                
        State = Turn;                                                                                
      } else if (root[1] == 2) {                                                                                
        State = Turn;                                                                                
      } else if (root[1] == 3) {
        State = Dispose;
      }

      // itterera igenom en lista med uppgifter [0,1,2,1,0,0,1] gå igenom en för en.
      
      // Change State!!!
    
    }
  });
}

// States //
typedef enum State {                  // Skapar enumeration kallad State
  Stopped, FollowLine, Claw, Dispose  // Alla cases
};

// Setup //
void setup() {
  Serial.begin(115200);                                                   // Sätter datarate i bits per sekund för serial data överförning (9600 bits per sekund)
  attachInterrupt(digitalPinToInterrupt(He), HtoL, FALLING);              // Digitala pin med interuppt till pin "He" funktionen "HtoL" ska köras vid "Falling" högt värde till lågt 
  pinMode(Pw, OUTPUT), pinMode(D1, OUTPUT), pinMode(LED_BUILTIN, OUTPUT); // Konfigurerar pins att bete sig som outputs
  digitalWrite(D1, HIGH);                                                 // Skriver till pin "D1" hög volt (3.3v) 
  Servo1.attach(13);                                                      // Sätter servo pin
  State = Stopped;                                                        // Går till casen Stopped
}

// Loop //
void loop() {
  client.loop();              // När den kallas tillåter du klienten att processera inkommande medelanden, skicka data och bibehålla anslutningen:

  switch (State) {
    case Stopped:
      analogWrite(Pw, 0);                             // Skriver till pin "Pw" värdet 0 (0 representerar lågt)
      currentMillis = millis();                       // Sätter variabeln currentMillis till millis();
      if (currentMillis > previousMillis + BlinkTime){// Om currentMillis är större än förra + parametern BlinkTime:
        previousMillis = currentMillis;               //    Sätter variabeln previousMillis till currentMillis
        LedState = !LedState;                         //    "Nottar Ledstate", sätter LedState till motsatta värdet det var innan
        digitalWrite(LED_BUILTIN, LedState);          //    Skriver till inbyggda led lampan LedState (3.3v eller 0v) 
      }
      continue;

    case FollowLine:
      if (SerialData(false)) {
        Servo1.write(int(obj[3]));
        analogWrite(Pw, obj[4]);
      }
      if (DistanceDriven >= RoadDist){
        DistanceDriven = 0;
        State = Stopped;
      }
      continue;

  }

  while (Serial.available()) {
    delay(1);
    char c = Serial.read();
    readString += c; 
  }

  if (readString.length()) {
    StaticJsonBuffer<256> jsonBuffer;
    JsonArray& obj = jsonBuffer.parseArray(readString);
    Serial.println(readString);
    readString="";
  }

  Servo1.write(1023/180*int(obj[3]));

  if (obj[0]) {
    stopped(500);
  }
  
/*  
  client.loop();              // När den kallas tillåter du klienten att processera inkommande medelanden, skicka data och bibehålla anslutningen:
  if(!client.isConnected()){  // Om funtkionen "client.isConnected()" get False, då har klienten tappat anslutningen
    stopped(500);             //    Anropa funktionen stopped() med parametern Blinktime sätt till 500 ms för att kunna förtydliga felet utan serialmonitor medelande
  } else if (Task == 0) {     // Om vi vill följa en linje:
    FollowLine();             //    Anropa funktionen FollowLine()
  } else {                    // Annars:
    stopped(2500);            //    Anropa funktionen stopped() med parametern Blinktime sätt till 500 ms för att kunna förtydliga felet utan serialmonitor medelande
  }
*/
}

/*
// Funktioner "Använd data" //
void calculateTerms(){
  Pwm = 0;                    // Resetar Pwm så den framtida additionen av värdet proportionellTerm() blir som =, och inte +=
  Pwm += proportionellTerm(); // Anropa funktionen addPayload() med parameterna "strTerm" Kp, "intTerm" funktionen "proportionellTerm()" returnerande värde 
  Pwm += integrationTerm();   // Anropa funktionen addPayload() med parameterna "strTerm" Ki, "intTerm" funktionen "integrationTerm()" returnerande värde 
  Pwm += deriveringTerm();    // Anropa funktionen addPayload() med parameterna "strTerm" Kd, "intTerm" funktionen "deriveringTerm()" returnerande värde 
}

void proportionellTerm(){
  return (float) Kp * e;      // Returnerar flytvärdet av konstanten "Kp" multiplicerat med "e" differansen av Rpm
}

float integrationTerm(){
  return (float) Ki * KiArea; // Returnerar flytvärdet av konstanten "Ki" multiplicerat med "KiArea" grafens "volym"
}

float deriveringTerm() {
  return 0;                   // Returnerar 0, hann inte med deriverandeTermen
}
*/

// Funktion "Kontrolera hastighet" //
float speedControll(){
  if (Pwm > maxPwm){        // Om Pwm är större än största tilllåta värdet:
    return maxPwm;          //    Returnerar största tilllåta värdet
  } else if (Pwm < minPwm) {// Om Pwm är mindre än minsta tillåtna värdet:
    return minPwm;          //    Returnerar minsta tillåtna värdet
  } else {                  // Annars:
    return int(Pwm+0.5);    //    Returnerar avrundande värdet av flyttalet Pwm (användningen av +0.5 motverkar kodens bristfälliga "avrundning" från flyttal till int)
  }
}

/*
// Funktion "Skicka data" //
void sendJSON(){
  payload += (",\"DistanceDriven\":\"" + String(DistanceDriven) + "\",\"Pw\":\"" + String(Pwm) + "\",\"CalculationTime\":\"" + String(millis()-previousMillis) + "}}"); // Lägger till Strängen till payload i jsonformat
  payloadArray += ("\""+String(millis())+"\"]}"); // Lägger till millis() till payloadArray i jsonformat (för mindre data)
  Serial.println(payload);                        // Skriver till serialmonitor vårat fina mer informationrika data
  client.publish("oliver.witzelhelmin@abbindustrigymnasium.se/broom_broom"+OWNER, payloadArray);  // Skickar våran konsentrerade data
}
*/

boolean SerialData(boolean NewData){
  while (Serial.available()) {
    NewData = true;
    delay(1);
    char c = Serial.read();
    readString += c; 
  }
  return NewData;
}

// Funktion "Stannad" //
void Blink(int BlinkTime){
  analogWrite(Pw, 0);                             // Skriver till pin "Pw" värdet 0 (0 representerar lågt)
  currentMillis = millis();                       // Sätter variabeln currentMillis till millis();
  if (currentMillis > previousMillis + BlinkTime){// Om currentMillis är större än förra + parametern BlinkTime:
    previousMillis = currentMillis;               //    Sätter variabeln previousMillis till currentMillis
    LedState = !LedState;                         //    "Nottar Ledstate", sätter LedState till motsatta värdet det var innan
    digitalWrite(LED_BUILTIN, LedState);          //    Skriver till inbyggda led lampan LedState (3.3v eller 0v) 
  }
}

// Funktion "Interupt" //
ICACHE_RAM_ATTR void HtoL(){
  Rev++;                  // Lägger på 1 på variabeln Rev
  DistanceDriven += 1.23; // Lägger på 1.23 på variabeln DistanceDriven (1.23 pga hjulets diameter, motorns växellåda och magneternas ("+" -> "-" -> "+" -> "-") poler)
}
