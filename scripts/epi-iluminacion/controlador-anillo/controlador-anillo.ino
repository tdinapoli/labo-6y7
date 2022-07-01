#include "FastLED.h"
#include "pixeltypes.h"

#define NUM_LEDS 16
#define DATA_PIN 3
#define BRIGHTNESS 255


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
        //disable_output();
        FastLED.setBrightness(BRIGHTNESS);
        leds[led_number] = colors[color_index];
        FastLED.show();
    }

void setup(){
    Serial.begin(115200);
    Serial.println("Chanoscopio v0.2");
    FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);
    disable_output();
    set_led(8, 3);
    }

void serialEvent() {
  if (Serial.available() >= 3){
    unsigned char led_number = (char) Serial.read();
    unsigned char exp_time = (char) Serial.read();
    unsigned char rgb = (char) Serial.read();
    set_led(led_number, rgb);
    delay(exp_time*100);
    disable_output();
  }
  set_led(0, 3);


}

void loop(){
    }
