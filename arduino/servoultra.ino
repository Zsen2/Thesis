#include <Servo.h>
#define Servo_PWM 9 // A descriptive name for D6 pin of Arduino to provide PWM signal
Servo MG995_Servo; 


void setup() {
  Serial.begin(2000000);

  MG995_Servo.attach(Servo_PWM);
  MG995_Servo.write(0);
}

void loop() {
  
  if (Serial.available() >= 2) {
    int received_value;
    Serial.readBytes((char *)&received_value, sizeof(received_value));
    if(received_value == 1){
      delay(1700);
     MG995_Servo.write(90);
    delay(350);
    MG995_Servo.write(0);
    delay(350);
    }
  }
  
}
