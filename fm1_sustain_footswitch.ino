// Reads a 1/8" (3.5mm) TRS sustain pedal jack (or a built-in panel button,
// wired in parallel) and sends MIDI CC64 (sustain) out the Arduino's
// hardware Serial MIDI circuit, straight to a second 3.5mm TRS jack wired
// Type A, into the FM-1's MIDI IN.
//
// Wiring:
//   Pedal jack tip           -> D2
//   Pedal jack ring + sleeve -> GND (tied together)
//   (D2 uses INPUT_PULLUP, so the pedal just needs to short tip to
//    ring/sleeve when pressed -- true for the vast majority of momentary
//    sustain pedals, even when plugged into a TRS jack via a mono TS plug)
//
//   Built-in button leg 1 -> D2  (same node as pedal jack tip)
//   Built-in button leg 2 -> GND (same node as pedal jack ring/sleeve)
//   (in parallel with the pedal jack, so the button works with no pedal
//    plugged in -- no separate pin or code path needed)
//
//   TX (pin 1) -> 220ohm resistor -> MIDI-out TRS jack tip
//   5V         -> 220ohm resistor -> MIDI-out TRS jack ring
//   GND        -> MIDI-out TRS jack sleeve
//   MIDI-out TRS jack (Type A) -> cable -> FM-1 MIDI IN
//
//   OLED (I2C SSD1306 128x64): GND->GND, VCC->5V, SCL->A5, SDA->A4
//   (shows SUSTAIN ON / SUSTAIN OFF, matching this board's own state --
//    it has no incoming MIDI to show note data, only the pedal/button)
//
// NOTE: pins 0/1 are shared with USB serial. Unplug the TRS output jack's
// TX line while uploading, or the upload will fail.

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

constexpr uint8_t kPedalPin = 2;
constexpr uint8_t kChannel  = 0;      // 0 = MIDI channel 1; match FM-1's Note Channel
constexpr uint8_t kCC       = 0x40;   // CC64, sustain
constexpr uint16_t kDebounceMs = 15;

// Flip this if the pedal (or its polarity switch) turns out normally-closed,
// i.e. sustain reads as "on" at rest and "off" when pressed.
constexpr bool kInvert = false;

constexpr uint8_t kScreenWidth  = 128;
constexpr uint8_t kScreenHeight = 64;
constexpr int8_t  kOledReset    = -1;
constexpr uint8_t kOledAddress  = 0x3C;

Adafruit_SSD1306 g_display(kScreenWidth, kScreenHeight, &Wire, kOledReset);

bool lastReading = HIGH;
bool pedalDown = false;
unsigned long lastChangeMs = 0;

void sendCC(uint8_t cc, uint8_t value) {
  uint8_t msg[] = {(uint8_t)(0xB0 | kChannel), cc, value};
  Serial.write(msg, 3);
}

void showSustainState(bool down) {
  g_display.clearDisplay();
  g_display.setTextSize(2);
  g_display.setCursor(0, 24);
  g_display.print(F("SUSTAIN"));
  g_display.setCursor(0, 44);
  g_display.print(down ? F("ON") : F("OFF"));
  g_display.display();
}

void setup() {
  pinMode(kPedalPin, INPUT_PULLUP);
  Serial.begin(31250);

  Wire.begin();
  g_display.begin(SSD1306_SWITCHCAPVCC, kOledAddress);
  g_display.setTextColor(SSD1306_WHITE);
  showSustainState(pedalDown);
}

void loop() {
  bool reading = digitalRead(kPedalPin);

  if (reading != lastReading) {
    lastChangeMs = millis();
    lastReading = reading;
  }

  if (millis() - lastChangeMs > kDebounceMs) {
    bool down = kInvert ? reading : !reading;
    if (down != pedalDown) {
      pedalDown = down;
      sendCC(kCC, pedalDown ? 127 : 0);
      showSustainState(pedalDown);
    }
  }
}
