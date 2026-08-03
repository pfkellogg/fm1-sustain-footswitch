// Reads a 1/8" (3.5mm) TRS sustain pedal jack and sends MIDI CC64 (sustain)
// out the Arduino's hardware Serial MIDI circuit, straight to a second
// 3.5mm TRS jack wired Type A, into the FM-1's MIDI IN.
//
// Wiring:
//   Pedal jack tip           -> D2
//   Pedal jack ring + sleeve -> GND (tied together)
//   (D2 uses INPUT_PULLUP, so the pedal just needs to short tip to
//    ring/sleeve when pressed -- true for the vast majority of momentary
//    sustain pedals, even when plugged into a TRS jack via a mono TS plug)
//
//   TX (pin 1) -> 220ohm resistor -> MIDI-out TRS jack tip
//   5V         -> 220ohm resistor -> MIDI-out TRS jack ring
//   GND        -> MIDI-out TRS jack sleeve
//   MIDI-out TRS jack (Type A) -> cable -> FM-1 MIDI IN
//
// NOTE: pins 0/1 are shared with USB serial. Unplug the TRS output jack's
// TX line while uploading, or the upload will fail.

constexpr uint8_t kPedalPin = 2;
constexpr uint8_t kChannel  = 0;      // 0 = MIDI channel 1; match FM-1's Note Channel
constexpr uint8_t kCC       = 0x40;   // CC64, sustain
constexpr uint16_t kDebounceMs = 15;

// Flip this if the pedal (or its polarity switch) turns out normally-closed,
// i.e. sustain reads as "on" at rest and "off" when pressed.
constexpr bool kInvert = false;

bool lastReading = HIGH;
bool pedalDown = false;
unsigned long lastChangeMs = 0;

void sendCC(uint8_t cc, uint8_t value) {
  uint8_t msg[] = {(uint8_t)(0xB0 | kChannel), cc, value};
  Serial.write(msg, 3);
}

void setup() {
  pinMode(kPedalPin, INPUT_PULLUP);
  Serial.begin(31250);
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
    }
  }
}
