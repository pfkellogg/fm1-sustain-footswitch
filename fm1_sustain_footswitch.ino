// Reads a 1/8" (3.5mm) TRS sustain pedal jack (or a built-in panel button,
// wired in parallel) and sends MIDI CC64 (sustain) out the Arduino's
// hardware Serial MIDI circuit, straight to a second 3.5mm TRS jack wired
// Type A, into the FM-1's MIDI IN. Also drives a linear softpot pitch strip
// (see below), closer to how the Arturia MiniLab 3's own pitch strip works.
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
//   Linear softpot pitch strip (SpectraSymbol SoftPot, 100mm, or similar):
//     End 1  -> 5V
//     End 2  -> GND
//     Wiper  -> A1, with a 10kohm pull-down resistor (A1 -> GND) so the
//       reading is a stable near-0 "no bend" baseline when not touched,
//       rather than floating/noisy (softpots have no contact when idle,
//       unlike a knob-style pot)
//   The base note sounds continuously from power-on (no button needed).
//   Touching the strip and sliding bends pitch; releasing lets it settle
//   back to center (no bend). Confirmed 2026-08-06 that the FM-1's physical
//   MIDI IN (unlike its USB MIDI) applies pitch bend continuously to an
//   already-sounding note, same as a real MIDI controller's wheel/strip.
//
// NOTE: pins 0/1 are shared with USB serial. Unplug the TRS output jack's
// TX line while uploading, or the upload will fail.
//
// The OLED display, mode switch, and audio-input pitch detector that used
// to live on this board have been removed. The OLED moved permanently to a
// separate project, fm1-midi-voice-tuner -- see git history on this repo
// if the mode switch or pitch detector need to be resurrected.

constexpr uint8_t kPedalPin = 2;
constexpr uint8_t kChannel  = 0;      // 0 = MIDI channel 1; match FM-1's Note Channel
constexpr uint8_t kCC       = 0x40;   // CC64, sustain
constexpr uint16_t kDebounceMs = 15;

// Flip this if the pedal (or its polarity switch) turns out normally-closed,
// i.e. sustain reads as "on" at rest and "off" when pressed.
constexpr bool kInvert = false;

// ---- Softpot pitch strip control (MIDI OUT) ----
constexpr uint8_t  kStripPin            = A1;
constexpr uint8_t  kBaseNote            = 60;   // middle C, sounds continuously
constexpr int16_t  kBendFullScale       = 8191; // matches FM-1's Pitch Bend Range, set to +/-12
constexpr uint16_t kStripTouchThreshold = 20;   // raw reading below this = not touched
constexpr uint8_t  kStripStepMs         = 15;   // pitch bend update interval

bool lastReading = HIGH;
bool pedalDown = false;
unsigned long lastChangeMs = 0;

unsigned long stripLastStepMs = 0;

void sendCC(uint8_t cc, uint8_t value) {
  uint8_t msg[] = {(uint8_t)(0xB0 | kChannel), cc, value};
  Serial.write(msg, 3);
}

void sendNoteOn(uint8_t note, uint8_t velocity) {
  uint8_t msg[] = {(uint8_t)(0x90 | kChannel), note, velocity};
  Serial.write(msg, 3);
}

void sendNoteOff(uint8_t note) {
  uint8_t msg[] = {(uint8_t)(0x80 | kChannel), note, 0};
  Serial.write(msg, 3);
}

void sendPitchBend(int16_t bend) {
  uint16_t raw = (uint16_t)(bend + 8192);  // 0..16383, center 8192
  uint8_t msg[] = {(uint8_t)(0xE0 | kChannel), (uint8_t)(raw & 0x7F), (uint8_t)((raw >> 7) & 0x7F)};
  Serial.write(msg, 3);
}

void setup() {
  pinMode(kPedalPin, INPUT_PULLUP);
  Serial.begin(31250);
  sendNoteOn(kBaseNote, 100);
}

void loop() {
  // Pedal/sustain handling.
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

  // Pitch strip control -- always active, no button needed. The base note
  // sounds continuously; sliding the strip bends it, releasing centers it.
  if (millis() - stripLastStepMs >= kStripStepMs) {
    stripLastStepMs = millis();

    int raw = analogRead(kStripPin);
    int16_t bend;
    if (raw < kStripTouchThreshold) {
      // Not touched -- the pull-down resistor holds this near 0 with no
      // finger contact, which we treat as "centered, no bend" rather than
      // as a touch at the strip's bottom-most position.
      bend = 0;
    } else {
      long span = 1023 - kStripTouchThreshold;
      long pos = raw - kStripTouchThreshold;
      bend = (int16_t)(pos * (long)(kBendFullScale + 8192) / span - 8192);
    }
    bend = constrain(bend, -8192, kBendFullScale);

    sendPitchBend(bend);
  }
}
