# fm1-sustain-footswitch

A small Arduino-based board that converts a 1/8" (3.5mm) sustain pedal into MIDI CC64 (sustain) for the [M-VAVE FM-1](https://www.m-vave.com/products), via its 3.5mm TRS MIDI IN. Includes a built-in panel pushbutton wired in parallel with the pedal jack, so sustain still works with no external pedal plugged in. Also drives a linear softpot pitch strip for continuous pitch-bend control — **ON HOLD as of 2026-08-09, pending sourcing the strip itself** (see Parts below).

Confirmed working end-to-end: physical pedal → Arduino → TRS MIDI (Type A) → FM-1 sustain. The pitch-strip code is written and compiles clean, but is untested on real hardware since the part hasn't been bought yet.

## Schematic and layout

| Schematic | Physical layout |
|---|---|
| [![schematic](schematics/fm1_footswitch_schematic.png)](schematics/fm1_footswitch_schematic.pdf) | [![layout](schematics/fm1_footswitch_layout.png)](schematics/fm1_footswitch_layout.pdf) |

PDFs (linked above) are the high-res versions. `schematics/generate_fm1_footswitch_schematic.py` regenerates both from source (matplotlib; `pip install matplotlib` first).

## Why a board at all

MIDI is a serial protocol, so a plain switch-to-jack cable can't talk to the FM-1 directly — something has to turn "switch closed" into a `CC64` message. This uses the spare Arduino Uno R3 as that translator.

## Parts

- Arduino Uno R3
- 1/8" (3.5mm) TRS panel-mount jack, wired to the sustain pedal
- 1/8" (3.5mm) TRS panel-mount jack, for MIDI out
- Momentary panel pushbutton (normally-open SPST), for sustain with no pedal plugged in
- 2x 220ohm resistors (MIDI out circuit)
- 3.5mm TRS-to-TRS cable, to reach the FM-1's MIDI IN
- **Linear softpot pitch strip, 100mm — NOT YET SOURCED.** The originally-planned SparkFun SKU (SEN-08607) is discontinued. Buy the same physical part from [Adafruit #178](https://www.adafruit.com/product/178) instead (also available via Mouser, Newark, Jameco). It was never available on Amazon, despite some listings suggesting otherwise.
- 10kohm resistor, for the pitch strip's pull-down

## Wiring

**Pedal input (TRS jack):**
```
pedal jack tip           -> Arduino D2
pedal jack ring + sleeve -> Arduino GND (tied together)
```
D2 is `INPUT_PULLUP`, so the pedal just needs to short tip to ring/sleeve when pressed. Ring and sleeve are tied together so a plain mono (TS) pedal plug still grounds correctly when inserted into the TRS jack. This covers the vast majority of 1/8" sustain pedals (simple momentary SPST, normally open).

**Built-in button (optional, for no pedal):**
```
button leg 1 -> Arduino D2   (same node as pedal jack tip)
button leg 2 -> Arduino GND  (same node as pedal jack ring/sleeve)
```
Wired straight in parallel with the pedal jack — no separate pin, no code changes. Either the button or the pedal alone can pull D2 low, so pressing the button works whether or not a pedal is plugged in. If a pedal *is* plugged in and its footswitch is a normally-closed momentary (rare), it'll hold D2 low all the time, which would also hold the panel button's effect at "always on" — not an issue for the standard normally-open pedals this is designed for.

**MIDI output (direct to TRS, Type A):**
```
Arduino TX (pin 1) -> 220ohm resistor -> TRS jack tip
Arduino 5V         -> 220ohm resistor -> TRS jack ring
Arduino GND        -> TRS jack sleeve
```
Then a plain 3.5mm TRS-to-TRS cable into the FM-1's MIDI IN.

**Pitch strip (linear softpot, 100mm — ON HOLD, part not yet sourced):**
```
Strip End 1 -> Arduino 5V
Strip End 2 -> Arduino GND
Strip Wiper -> Arduino A1, with a 10kohm pull-down resistor (A1 -> GND)
```
The pull-down keeps A1 at a stable near-0 reading when the strip isn't touched (softpots float with no finger contact, unlike a knob-style pot), which the sketch reads as "centered, no bend." A base note (middle C) sounds continuously from power-on — no button needed. Sliding the strip bends pitch; releasing lets it settle back to center. Confirmed 2026-08-06 that the FM-1's physical MIDI IN (unlike its USB MIDI) applies continuous pitch bend to an already-sounding note, same as a real controller's wheel/strip — so this should work once the part is in hand, but hasn't been bench-tested yet.

## Flashing

Upload `fm1_sustain_footswitch.ino` as usual. **Disconnect the TRS output jack (or at least the TX line) from the Arduino before uploading** — pins 0/1 are shared with the USB serial the IDE uses to program the board, and the resistor circuit sitting on TX can interfere with the upload.

## If it comes up backwards

Two independent polarity unknowns here, each with a one-line fix — don't chase the other one first:

- **Pedal polarity** (sustain reads "on" at idle, "off" when pressed): flip `kInvert` to `true` in the sketch and re-upload.
- **TRS MIDI type** (FM-1 doesn't respond at all): this board is wired Type A (tip = signal, ring = +5V, sleeve = GND). If the FM-1 turns out to expect Type B, swap tip and ring at the jack (or re-wire): tip = GND, ring = signal, sleeve = GND.

## History

An OLED display, a mode switch (to flip the OLED between sustain status and a live pitch readout), and an audio-input pitch detector (reading the FM-1's own headphone output) all previously lived on this board. All three were removed 2026-08-09 — the OLED moved permanently to a separate project, [fm1-midi-voice-tuner](https://github.com/pfkellogg/fm1-midi-voice-tuner), which reads the FM-1's MIDI output instead of its audio output. See git history on this repo if the mode switch or audio pitch detector are ever needed again.
