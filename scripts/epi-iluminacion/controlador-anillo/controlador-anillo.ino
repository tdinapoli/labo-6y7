#include "FastLED.h"
#include "pixeltypes.h"

#define NUM_LEDS 16
#define DATA_PIN 3

CRGB leds[NUM_LEDS];
CRGB colors[5] = {CRGB::Red, CRGB::Green, CRGB::Blue, CRGB::White, CRGB::Yellow};


//Turns off every led
void disable_output(){
    for (int i; i < NUM_LEDS; i++){
        leds[i] = CRGB::Black;
        FastLED.show();
        }
    }

void set_led(int led_number, int color_index){
        disable_output();
        leds[led_number] = colors[color_index];
        FastLED.show();
    }

void setup(){
    Serial.begin(115200);
    Serial.println("Chanoscopio v0.2");
    FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);
    disable_output();
    }

void serialEvent() {
  //set_led(0, 1);

//  while (Serial.available()){
//    unsigned char number = (char) Serial.read();
//    set_led(0, number);
//  }
  if (Serial.available() >= 3){
    unsigned char led_number = (char) Serial.read();
    unsigned char exp_time = (char) Serial.read();
    unsigned char rgb = (char) Serial.read();
    set_led(led_number, rgb);
    delay(exp_time*100);
    disable_output();
//    if (0 == rgb){
//      set_led(0, 0);
//    }
//    else if(1 == rgb){
//      set_led(0, 1);
//    }
//    else if(2 == rgb){
//      set_led(0, 2);
//    }
//    else if(3 == rgb){
//      set_led(0, 3);
//    }
  }
}

void loop(){
//  set_led(0, 0);
//  delay(1000);
//  disable_output();
//  delay(1000);
    }
