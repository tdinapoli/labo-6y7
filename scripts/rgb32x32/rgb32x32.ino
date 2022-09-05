#define LAT B00000100
#define OE B00000010
#define CLK B00000001


void set_led_pin(int state){
  PORTD = (PORTD | state);
}

void clear_led_pins(){
  PORTD &= B00000011;
}

void set_target_row(int num){
  PORTC = (PORTC & B11110000) + num;
}

void clock_data(int n){
  for(int i = 0; i<n; i++){
    PORTB |= CLK;
    PORTB &= ~CLK;
  }
}

void latch() {
  PORTB &= ~LAT;
  PORTB |= LAT;
  PORTB &= ~LAT;
}

void enable_output(){
  PORTB &= ~OE;
}

void disable_output(){
  PORTB |= OE;
}


void set_led(int row, int column, int color){
  int state = color << 2;
  if (row >= 16){
    row -= 16;
    state = state << 3;
  }
  disable_output();
  clear_led_pins();
  clock_data(column);
  set_led_pin(state);
  clock_data(1);
  clear_led_pins();
  clock_data(32-column-1);
  set_target_row(row);
  latch();
  enable_output();
}


void setup() {
  Serial.begin(115200);
  Serial.println("Chanoscopio v0.1");
  DDRD = DDRD | B11111100;
  DDRB = DDRB | B00100111;
  DDRC = DDRC | B00001111;

  disable_output();
 // set_led(16,16,7);
}

void serialEvent() {
  if (Serial.available() == 2){
    unsigned char x1 = (char) Serial.read();
    unsigned char x2 = (char) Serial.read();
    unsigned char x = x1 & B00011111;
    unsigned char y = x2 & B00011111;
    unsigned char rgb = x1 >> 5;
    if (rgb > 0) {
      set_led(y, x, rgb);
    } else {
      disable_output();
    }
    
  }
}

void loop() {
  
}
