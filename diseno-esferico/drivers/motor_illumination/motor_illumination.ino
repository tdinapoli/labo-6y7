// comentario
#define MIN_PIN 9
#define MAX_PIN 13
#define BAUD_RATE 115200

void turn_off_leds(){
  for (int i=MIN_PIN; i < MAX_PIN + 1; i++){
    digitalWrite(i, LOW);
  }
}

void set_led(int led_number){
  turn_off_leds();
  digitalWrite(led_number, HIGH);
}

void setup(){
  Serial.begin(BAUD_RATE);
  pinMode(13, OUTPUT);
  pinMode(12, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(9, OUTPUT);

  
  Serial.println("Chanoscopio v0.1");
  
}

void loop() {
  Serial.println("hola");
  delay(1000);
  set_led(12);
  delay(1000);
  set_led(11);
  delay(1000);
  set_led(10);
  delay(1000);
  set_led(9);
  delay(1000);
}
