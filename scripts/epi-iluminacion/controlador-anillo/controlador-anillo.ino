#include "FastLED.h"
#include "pixeltypes.h"

#define NUM_LEDS 16
#define DATA_PIN 3

CRGB leds[NUM_LEDS];



//Turns off every led
void disable_output(){
    for (int i; i < NUM_LEDS; i++){
        leds[i] = CRGB::Black;
        FastLED.show();
        }
    }

void set_led(int led_number, CRGB color){
        disable_output();
        leds[led_number] = color;
        FastLED.show();
    }

void setup(){
    Serial.begin(115200);
    Serial.println("Chanoscopio v0.2");
    FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);
    disable_output();
    }

void serialEvent() {
    static int serial_calls = 0;
    Serial.println("hola");
    if (Serial.available() == 2){
        Serial.println("available");
        if (serial_calls % 2 == 0){
            set_led(0, CRGB::Red);
            }
        else {
            set_led(0, CRGB::Blue);
            }
         Serial.flush();
        delay(1000);
        serial_calls = serial_calls + 1;
        }
}

void loop(){
    }
