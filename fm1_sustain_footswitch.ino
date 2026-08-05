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
//
//   Mode switch (SPDT, ON-ON): common -> GND, one throw -> D3, other throw
//   unconnected. D3 uses INPUT_PULLUP: grounded = Pitch mode, floating
//   (default) = Sustain mode. Only changes what the OLED shows -- the
//   pedal/button still sends CC64 sustain in both modes.
//
//   Pitch mode audio input (from FM-1 headphone out, needs a small bias
//   circuit since the Arduino's ADC only reads 0-5V, but headphone output
//   swings positive and negative around 0V):
//     FM-1 headphone out (tip, one channel) -> 100kohm resistor -> node X
//     node X -> 1uF cap -> Arduino A0
//     5V  -> 10kohm resistor -> node Y
//     GND -> 10kohm resistor -> node Y
//     node Y -> Arduino A0  (same node the cap feeds -- this is the DC
//       bias point, ~2.5V, that the AC audio signal rides on top of)
//     FM-1 headphone out sleeve (ground) -> Arduino GND
//   This board has no incoming MIDI, so pitch mode reads the note directly
//   from the FM-1's audio output rather than from MIDI note messages.
//
// NOTE: pins 0/1 are shared with USB serial. Unplug the TRS output jack's
// TX line while uploading, or the upload will fail.

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <math.h>

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

constexpr uint8_t kModeSwitchPin = 3;  // LOW = Pitch mode, HIGH (pulled up) = Sustain mode

// ---- Pitch mode (autocorrelation pitch detection on the audio input) ----
constexpr uint8_t  kAudioPin         = A0;
constexpr uint16_t kSampleRateHz     = 6000;
constexpr uint16_t kSampleIntervalUs = 1000000UL / kSampleRateHz;
constexpr uint8_t  kBufferSize       = 240;  // 240 bytes RAM; ~40ms capture window
constexpr uint8_t  kMinLag           = 6;    // ~1000 Hz ceiling
constexpr uint8_t  kMaxLag           = 120;  // ~50 Hz floor
constexpr uint8_t  kMinAmplitude     = 8;    // peak-to-peak noise floor, out of 0-255
constexpr float    kMinConfidence    = 0.4f; // bestCorr/zeroLagCorr, rejects noisy/unclear pitch

const char* const kNoteNames[12] = {
  "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"
};

Adafruit_SSD1306 g_display(kScreenWidth, kScreenHeight, &Wire, kOledReset);

bool lastReading = HIGH;
bool pedalDown = false;
unsigned long lastChangeMs = 0;

uint8_t audioBuf[kBufferSize];

struct PitchResult {
  bool  valid;
  float freqHz;
};

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

void captureAudio() {
  unsigned long nextSampleUs = micros();
  for (uint16_t i = 0; i < kBufferSize; i++) {
    while ((long)(micros() - nextSampleUs) < 0) {}
    audioBuf[i] = analogRead(kAudioPin) >> 2;  // 10-bit -> 8-bit
    nextSampleUs += kSampleIntervalUs;
  }
}

// Autocorrelation at a given lag, samples centered on `mean` first.
long autocorrAtLag(uint8_t lag, int16_t mean) {
  long sum = 0;
  for (uint8_t i = 0; i + lag < kBufferSize; i++) {
    int16_t a = (int16_t)audioBuf[i]       - mean;
    int16_t b = (int16_t)audioBuf[i + lag] - mean;
    sum += (long)a * b;
  }
  return sum;
}

PitchResult detectPitch() {
  uint16_t sum = 0;
  uint8_t  minV = 255, maxV = 0;
  for (uint8_t i = 0; i < kBufferSize; i++) {
    uint8_t v = audioBuf[i];
    sum += v;
    if (v < minV) minV = v;
    if (v > maxV) maxV = v;
  }

  if ((uint8_t)(maxV - minV) < kMinAmplitude) {
    return {false, 0};  // near-silence, nothing playing
  }

  int16_t mean = sum / kBufferSize;
  long zeroLag = autocorrAtLag(0, mean);
  if (zeroLag <= 0) return {false, 0};

  uint8_t bestLag  = kMinLag;
  long    bestCorr = autocorrAtLag(kMinLag, mean);
  for (uint8_t lag = kMinLag + 1; lag <= kMaxLag; lag++) {
    long c = autocorrAtLag(lag, mean);
    if (c > bestCorr) {
      bestCorr = c;
      bestLag  = lag;
    }
  }

  float confidence = (float)bestCorr / (float)zeroLag;
  if (confidence < kMinConfidence) {
    return {false, 0};  // no clear periodicity -- noise or unclear signal
  }

  // Parabolic interpolation across the neighboring lags for sub-sample
  // precision -- integer-lag resolution alone gives coarse, jumpy Hz steps.
  float refinedLag = bestLag;
  if (bestLag > kMinLag && bestLag < kMaxLag) {
    long cPrev  = autocorrAtLag(bestLag - 1, mean);
    long cNext  = autocorrAtLag(bestLag + 1, mean);
    float denom = (float)(cPrev - 2 * bestCorr + cNext);
    if (denom != 0) {
      refinedLag += 0.5f * (float)(cPrev - cNext) / denom;
    }
  }

  return {true, (float)kSampleRateHz / refinedLag};
}

void showPitch(const PitchResult& r) {
  g_display.clearDisplay();

  if (!r.valid) {
    g_display.setTextSize(2);
    g_display.setCursor(0, 24);
    g_display.print(F("NO SIGNAL"));
    g_display.display();
    return;
  }

  float noteNumF = 69.0f + 12.0f * log(r.freqHz / 440.0f) / log(2.0f);
  int   noteNum  = (int)round(noteNumF);
  float cents    = (noteNumF - noteNum) * 100.0f;
  int8_t octave  = noteNum / 12 - 1;
  const char* name = kNoteNames[((noteNum % 12) + 12) % 12];

  g_display.setTextSize(3);
  g_display.setCursor(0, 0);
  g_display.print(name);
  g_display.print(octave);

  g_display.setTextSize(2);
  g_display.setCursor(0, 30);
  g_display.print(r.freqHz, 1);
  g_display.print(F(" Hz"));

  g_display.setTextSize(1);
  g_display.setCursor(0, 52);
  if (cents >= 0) g_display.print('+');
  g_display.print(cents, 0);
  g_display.print(F(" cents"));

  g_display.display();
}

void setup() {
  pinMode(kPedalPin, INPUT_PULLUP);
  pinMode(kModeSwitchPin, INPUT_PULLUP);
  Serial.begin(31250);

  Wire.begin();
  Wire.setClock(400000);  // Fast Mode I2C -- cuts full-frame OLED refresh time ~4x
  g_display.begin(SSD1306_SWITCHCAPVCC, kOledAddress);
  g_display.setTextColor(SSD1306_WHITE);
  showSustainState(pedalDown);
}

void loop() {
  bool pitchMode = digitalRead(kModeSwitchPin) == LOW;

  static bool lastPitchMode = false;
  if (pitchMode != lastPitchMode) {
    lastPitchMode = pitchMode;
    if (!pitchMode) showSustainState(pedalDown);  // redraw immediately on switching back
  }

  // Pedal/sustain handling always runs, regardless of which mode is displayed.
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
      if (!pitchMode) showSustainState(pedalDown);
    }
  }

  // Capturing+analyzing audio blocks for ~80-100ms, so sustain response can
  // lag by that much while in Pitch mode. Switch back to Sustain mode for
  // the tightest pedal response.
  if (pitchMode) {
    captureAudio();
    PitchResult r = detectPitch();
    showPitch(r);
  }
}
