import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D

LW = 1.4
FS_PIN = 11
FS_LABEL = 14
FS_TITLE = 22
FS_SUB = 12.5
FS_SMALL = 10.5
FS_NOTES = 12.5


def line(ax, x1, y1, x2, y2, lw=LW):
    ax.add_line(Line2D([x1, x2], [y1, y2], color='black', lw=lw, solid_capstyle='round'))


def dot(ax, x, y, r=0.06):
    ax.add_patch(patches.Circle((x, y), r, color='black', zorder=5))


def box(ax, x, y, w, h, label, sublabel=None):
    ax.add_patch(patches.Rectangle((x, y), w, h, fill=False, lw=1.6, edgecolor='black'))
    ax.text(x + w / 2, y + h + 0.3, label, ha='center', va='bottom', fontsize=FS_LABEL, fontweight='bold')
    if sublabel:
        ax.text(x + w / 2, y + h + 0.65, sublabel, ha='center', va='bottom', fontsize=FS_SMALL)


def pin_left(ax, box_x, y, stub_len, name):
    x1 = box_x - stub_len
    line(ax, x1, y, box_x, y)
    ax.text((x1 + box_x) / 2, y + 0.18, name, ha='center', va='bottom', fontsize=FS_PIN)
    return (x1, y)


def pin_right(ax, box_x, y, stub_len, name):
    x2 = box_x + stub_len
    line(ax, box_x, y, x2, y)
    ax.text((box_x + x2) / 2, y + 0.18, name, ha='center', va='bottom', fontsize=FS_PIN)
    return (x2, y)


def resistor_h(ax, x1, y, length, label):
    zz_len = length * 0.55
    lead = (length - zz_len) / 2
    x_start_zz = x1 + lead
    n = 6
    xs = [x_start_zz + i * (zz_len / n) for i in range(n + 1)]
    amp = 0.26
    ys = [y + (amp if i % 2 == 1 else -amp) for i in range(n + 1)]
    ys[0] = y
    ys[-1] = y
    line(ax, x1, y, x_start_zz, y)
    for i in range(n):
        line(ax, xs[i], ys[i], xs[i + 1], ys[i + 1])
    line(ax, x_start_zz + zz_len, y, x1 + length, y)
    ax.text(x1 + length / 2, y + 0.55, label, ha='center', va='bottom', fontsize=FS_PIN)
    return (x1 + length, y)


def ground_symbol(ax, x, y):
    line(ax, x, y, x, y - 0.35)
    widths = [0.5, 0.32, 0.14]
    for i, w in enumerate(widths):
        yy = y - 0.35 - i * 0.16
        line(ax, x - w / 2, yy, x + w / 2, yy)


def resistor_v(ax, x, y1, length, label, label_side='right'):
    zz_len = length * 0.55
    lead = (length - zz_len) / 2
    y_start_zz = y1 + lead
    n = 6
    ys = [y_start_zz + i * (zz_len / n) for i in range(n + 1)]
    amp = 0.26
    xs = [x + (amp if i % 2 == 1 else -amp) for i in range(n + 1)]
    xs[0] = x
    xs[-1] = x
    line(ax, x, y1, x, y_start_zz)
    for i in range(n):
        line(ax, xs[i], ys[i], xs[i + 1], ys[i + 1])
    line(ax, x, y_start_zz + zz_len, x, y1 + length)
    if label_side == 'right':
        ax.text(x + 0.45, y1 + length / 2, label, ha='left', va='center', fontsize=FS_PIN)
    else:
        ax.text(x - 0.45, y1 + length / 2, label, ha='right', va='center', fontsize=FS_PIN)
    return (x, y1 + length)


def capacitor_h(ax, x1, y, length, label):
    mid = x1 + length / 2
    gap = 0.18
    plate_h = 0.5
    line(ax, x1, y, mid - gap, y)
    line(ax, mid - gap, y - plate_h / 2, mid - gap, y + plate_h / 2)
    line(ax, mid + gap, y - plate_h / 2, mid + gap, y + plate_h / 2)
    line(ax, mid + gap, y, x1 + length, y)
    ax.text(mid, y + 0.32, label, ha='center', va='bottom', fontsize=FS_PIN)
    return (x1 + length, y)


def power_flag(ax, x, y, label, up=True):
    # Short labeled stub representing a rail tap, not routed all the way
    # back to its source pin -- keeps long power-rail wires off the diagram.
    y2 = y + 0.5 if up else y - 0.5
    line(ax, x, y, x, y2)
    ax.text(x, y2 + (0.12 if up else -0.12), label, ha='center',
            va='bottom' if up else 'top', fontsize=FS_PIN, fontweight='bold')
    return (x, y2)


# ===========================================================================
# FIGURE 1 — Schematic
# ===========================================================================
fig1, ax1 = plt.subplots(figsize=(24, 10.2))
ax1.set_xlim(-1, 39)
ax1.set_ylim(-3.5, 13.5)
ax1.set_aspect('equal')
ax1.axis('off')

ax1.text(0, 13.15, 'FM-1 Sustain Footswitch — Schematic', fontsize=FS_TITLE, fontweight='bold', va='top')
ax1.text(0, 12.45, 'Arduino Uno R3  +  TRS Pedal In  +  Built-in Button  +  TRS MIDI Out (Type A)  +  OLED Mode Switch  +  Pitch-Detect Audio In', fontsize=FS_SUB, va='top', style='italic')

GND_Y = 1.0
line(ax1, 0.5, GND_Y, 38.0, GND_Y, lw=1.8)
ground_symbol(ax1, 0.9, GND_Y)

# --- Pedal input jack (TRS) ---
PJ_X, PJ_Y, PJ_W, PJ_H = 1.0, 6.5, 2.8, 4.0
box(ax1, PJ_X, PJ_Y, PJ_W, PJ_H, 'Pedal IN', '3.5mm TRS jack')
pj_t = pin_right(ax1, PJ_X + PJ_W, 9.7, 0.9, 'Tip')
pj_r = pin_right(ax1, PJ_X + PJ_W, 8.4, 0.9, 'Ring')
pj_s = pin_right(ax1, PJ_X + PJ_W, 7.1, 0.9, 'Sleeve')

# Ring + Sleeve tied together, dropped to GND bus
line(ax1, pj_r[0], pj_r[1], pj_r[0], pj_s[1])
dot(ax1, pj_r[0], pj_r[1])
dot(ax1, pj_r[0], pj_s[1])
line(ax1, pj_r[0], pj_s[1], pj_r[0], GND_Y)

# --- Arduino Uno R3 ---
AU_X, AU_Y, AU_W, AU_H = 6.5, 2.3, 4.5, 8.7
box(ax1, AU_X, AU_Y, AU_W, AU_H, 'Arduino Uno R3')
au_d2 = pin_left(ax1, AU_X, 9.7, 1.1, 'D2')
au_gnd_l = pin_left(ax1, AU_X, 5.5, 1.1, 'GND')
au_tx = pin_right(ax1, AU_X + AU_W, 9.7, 1.1, 'TX (D1)')
au_5v = pin_right(ax1, AU_X + AU_W, 8.0, 1.1, '5V')
au_gnd_r = pin_right(ax1, AU_X + AU_W, 6.3, 1.1, 'GND')
au_a0 = pin_right(ax1, AU_X + AU_W, 5.0, 1.1, 'A0')
au_sda = pin_right(ax1, AU_X + AU_W, 4.3, 1.1, 'SDA (A4)')
au_scl = pin_right(ax1, AU_X + AU_W, 3.6, 1.1, 'SCL (A5)')
au_d3 = pin_right(ax1, AU_X + AU_W, 2.9, 1.1, 'D3')
ax1.text(AU_X + AU_W / 2, AU_Y - 0.35, 'INPUT_PULLUP on D2 and D3', ha='center', fontsize=FS_SMALL, style='italic', color='dimgray')

# Pedal Tip -> Arduino D2 (straight wire, same y)
line(ax1, pj_t[0], pj_t[1], au_d2[0], au_d2[1])
dot(ax1, au_d2[0], au_d2[1])

# Arduino left GND -> GND bus
line(ax1, au_gnd_l[0], au_gnd_l[1], au_gnd_l[0], GND_Y)
dot(ax1, au_gnd_l[0], GND_Y)

# --- Built-in panel pushbutton (wired in parallel with the pedal jack) ---
BTN_X, BTN_Y, BTN_R = 3.6, 3.2, 0.32
ax1.add_patch(patches.Circle((BTN_X, BTN_Y), BTN_R, fill=False, lw=1.6))
ax1.text(BTN_X - BTN_R - 0.25, BTN_Y + 0.15, 'Built-in Button', ha='right', va='bottom', fontsize=FS_LABEL, fontweight='bold')
ax1.text(BTN_X - BTN_R - 0.25, BTN_Y - 0.05, '(panel momentary, normally-open)', ha='right', va='top', fontsize=FS_SMALL, style='italic', color='dimgray')

# One button leg up to the D2 line, the other down to GND bus -- same
# nodes the pedal jack lands on, so button and pedal are electrically
# in parallel (either one alone can pull D2 low).
line(ax1, BTN_X, BTN_Y + 0.32, BTN_X, au_d2[1])
line(ax1, BTN_X, au_d2[1], au_d2[0], au_d2[1])
dot(ax1, BTN_X, au_d2[1])
line(ax1, BTN_X, BTN_Y - 0.32, BTN_X, GND_Y)
dot(ax1, BTN_X, GND_Y)

# --- MIDI OUT jack (TRS, Type A) ---
MJ_X, MJ_Y, MJ_W, MJ_H = 17.0, 5.5, 2.8, 5.0
box(ax1, MJ_X, MJ_Y, MJ_W, MJ_H, 'MIDI OUT', '3.5mm TRS jack (Type A)')
mj_t = pin_left(ax1, MJ_X, 9.7, 0.9, 'Tip')
mj_r = pin_left(ax1, MJ_X, 8.0, 0.9, 'Ring')
mj_s = pin_left(ax1, MJ_X, 6.3, 0.9, 'Sleeve')

# Arduino TX -> R1 (220ohm) -> MIDI jack Tip (signal)
r1_end = resistor_h(ax1, au_tx[0], au_tx[1], mj_t[0] - au_tx[0], 'R1\n220Ω')
line(ax1, r1_end[0], r1_end[1], mj_t[0], mj_t[1])

# Arduino 5V -> R2 (220ohm) -> MIDI jack Ring (current source)
r2_end = resistor_h(ax1, au_5v[0], au_5v[1], mj_r[0] - au_5v[0], 'R2\n220Ω')
line(ax1, r2_end[0], r2_end[1], mj_r[0], mj_r[1])

# Arduino GND -> MIDI jack Sleeve (direct wire, no resistor)
line(ax1, au_gnd_r[0], au_gnd_r[1], mj_s[0], mj_s[1])
dot(ax1, au_gnd_r[0], au_gnd_r[1])
line(ax1, au_gnd_r[0], au_gnd_r[1], au_gnd_r[0], GND_Y)

# Extend the four new pins (A0, SDA, SCL, D3) rightward, passing clear
# beneath the MIDI OUT jack (which starts at y=5.5), out to where the new
# mode-switch/OLED/pitch-audio components sit.
EXT_X = 21.0
line(ax1, au_a0[0], au_a0[1], EXT_X, au_a0[1])
line(ax1, au_sda[0], au_sda[1], EXT_X, au_sda[1])
line(ax1, au_scl[0], au_scl[1], EXT_X, au_scl[1])
line(ax1, au_d3[0], au_d3[1], EXT_X, au_d3[1])

# --- Mode switch (selects OLED content: Sustain status or Pitch reading) ---
SW_X, SW_Y, SW_R = 21.0, 2.9, 0.32
line(ax1, EXT_X, au_d3[1], SW_X - SW_R, SW_Y)
ax1.add_patch(patches.Circle((SW_X, SW_Y), SW_R, fill=False, lw=1.6))
ax1.text(SW_X, SW_Y + SW_R + 0.25, 'Mode Switch', ha='center', va='bottom', fontsize=FS_LABEL, fontweight='bold')
ax1.text(SW_X, SW_Y - SW_R - 0.3, '(SPDT ON-ON,\nthrow 2 = NC)', ha='center', va='top', fontsize=FS_SMALL, style='italic', color='dimgray')
line(ax1, SW_X, SW_Y - SW_R, SW_X, GND_Y)
dot(ax1, SW_X, GND_Y)

# --- OLED display (I2C SSD1306 128x64) -- sits directly above where the
# pitch-mode bias circuit lands below, but on a separate y-band so the two
# never actually cross paths.
OL_X, OL_Y, OL_W, OL_H = 23.5, 6.8, 4.2, 3.6
box(ax1, OL_X, OL_Y, OL_W, OL_H, 'OLED Display', 'SSD1306 128x64, I2C')
ol_vcc = pin_left(ax1, OL_X, 10.1, 0.9, 'VCC')
ol_gnd = pin_left(ax1, OL_X, 9.2, 1.6, 'GND')
ol_scl = pin_left(ax1, OL_X, 8.3, 0.9, 'SCL')
ol_sda = pin_left(ax1, OL_X, 7.4, 0.9, 'SDA')

# SDA/SCL up from the Arduino extension wires (unmarked crossings below are
# fine -- standard schematic convention, no dot means no connection)
line(ax1, EXT_X, au_sda[1], 22.0, au_sda[1])
line(ax1, 22.0, au_sda[1], 22.0, ol_sda[1])
line(ax1, 22.0, ol_sda[1], ol_sda[0], ol_sda[1])

line(ax1, EXT_X, au_scl[1], 22.4, au_scl[1])
line(ax1, 22.4, au_scl[1], 22.4, ol_scl[1])
line(ax1, 22.4, ol_scl[1], ol_scl[0], ol_scl[1])

# GND down to the shared ground bus
line(ax1, ol_gnd[0], ol_gnd[1], ol_gnd[0], GND_Y)
dot(ax1, ol_gnd[0], GND_Y)

# VCC as a local "5V" rail flag (points up, clear above the box) rather than
# a long wire back to the Arduino's one 5V pin (already used for R2).
power_flag(ax1, ol_vcc[0], ol_vcc[1], '5V', up=True)

# --- Pitch-mode audio input: bias/coupling circuit + Audio IN jack ---
# Placed well clear of the OLED's x-range so R4's rise to its own 5V flag
# never runs into the OLED box above it.
NODE_X, NODE_Y = 30.0, 5.0
line(ax1, EXT_X, au_a0[1], NODE_X, NODE_Y)
dot(ax1, NODE_X, NODE_Y)

# R5 (10k, node -> GND) and R4 (10k, node -> 5V flag) bias the node to ~2.5V
r5_top = resistor_v(ax1, NODE_X, GND_Y, NODE_Y - GND_Y, 'R5\n10kΩ')
dot(ax1, NODE_X, GND_Y)
r4_top = resistor_v(ax1, NODE_X, NODE_Y, 1.6, 'R4\n10kΩ', label_side='left')
power_flag(ax1, r4_top[0], r4_top[1], '5V', up=True)

# C1 (DC block) + R3 (current limit / attenuation) out to the jack
c1_end = capacitor_h(ax1, NODE_X, NODE_Y, 1.8, 'C1\n1µF')
r3_end = resistor_h(ax1, c1_end[0], c1_end[1], 2.2, 'R3\n100kΩ')

AJ_X, AJ_Y, AJ_W, AJ_H = 35.0, 3.5, 2.8, 3.0
box(ax1, AJ_X, AJ_Y, AJ_W, AJ_H, 'Audio IN', "FM-1 headphone out, tip only")
aj_t = pin_left(ax1, AJ_X, 5.0, 0.9, 'Tip')
aj_s = pin_left(ax1, AJ_X, 3.9, 0.9, 'Sleeve')
line(ax1, r3_end[0], r3_end[1], aj_t[0], aj_t[1])
line(ax1, aj_s[0], aj_s[1], aj_s[0], GND_Y)
dot(ax1, aj_s[0], GND_Y)

notes1 = (
    "Notes:\n"
    "• Built-in Button is wired in parallel with the pedal jack (same D2/GND nodes) -- either one alone can trigger sustain, so an external pedal is optional\n"
    "• Pedal ring + sleeve are tied together so a plain mono (TS) pedal plug still grounds correctly in the TRS jack\n"
    "• D2 uses INPUT_PULLUP -- the button or pedal only needs to short D2 to GND when pressed (normally-open momentary)\n"
    "• Type A TRS MIDI: tip = signal, ring = +5V current source, sleeve = ground\n"
    "• R1 limits current through the FM-1's opto-isolated MIDI input; R2 sources the +5V loop current -- both 220Ω, matching the standard DIN MIDI-out circuit\n"
    "• TX (D1) is shared with the USB-serial programmer -- disconnect the MIDI OUT jack (or at least the R1 lead) before uploading a new sketch\n"
    "• If the FM-1 doesn't respond, it may expect Type B instead: swap Tip and Ring at the MIDI OUT jack (tip = GND, ring = signal, sleeve = GND)\n"
    "• Mode Switch is optional -- D3 uses INPUT_PULLUP, so leaving it unwired (or on throw 2) defaults to Sustain mode, identical to the switch-less build\n"
    "• Pitch mode reads the FM-1's own headphone output, not MIDI -- this board has no incoming MIDI connection at all\n"
    "• R4/R5 bias A0 to ~2.5V so the AC headphone signal (which swings positive and negative around 0V) stays inside the ADC's 0-5V range\n"
    "• C1 blocks the DC bias from reaching the FM-1; R3 limits current and knocks down the signal as cheap insurance against clipping at high FM-1 volume\n"
    "• Pitch detection (autocorrelation, in-sketch) is tuned for roughly 50Hz-1000Hz (about G1-B5) -- a practical range for one ATmega328p doing this in real time, not the FM-1's full range\n"
    "• Untested against a real FM-1 signal as of this diagram -- the sketch's noise-floor and confidence thresholds are starting points and will likely need tuning"
)
line(ax1, 0.5, GND_Y - 0.8, 38.0, GND_Y - 0.8, lw=0.8)
ax1.lines[-1].set_linestyle('dashed')
ax1.lines[-1].set_color('gray')
ax1.text(0, GND_Y - 1.2, notes1, fontsize=FS_NOTES, va='top', ha='left', family='sans-serif', linespacing=1.6)

plt.tight_layout()

# ===========================================================================
# FIGURE 2 — Physical layout / assembly diagram
# ===========================================================================
fig2, ax2 = plt.subplots(figsize=(19, 13))
ax2.set_xlim(-1, 26)
ax2.set_ylim(-4, 14.2)
ax2.set_aspect('equal')
ax2.axis('off')

ax2.text(0, 13.7, 'FM-1 Sustain Footswitch — Layout / Assembly Diagram', fontsize=FS_TITLE - 3, fontweight='bold', va='top')
ax2.text(0, 13.05, 'Top-down view of enclosure: pedal jack + built-in button + mode switch (left panel), Arduino Uno (center), MIDI out + audio in jacks (right panel), OLED (front panel)', fontsize=FS_SUB - 1, va='top', style='italic')

# Enclosure outline
ENC_X, ENC_Y, ENC_W, ENC_H = 0.5, 1.0, 24.0, 10.9
ax2.add_patch(patches.FancyBboxPatch((ENC_X, ENC_Y), ENC_W, ENC_H,
                                      boxstyle="round,pad=0,rounding_size=0.25",
                                      fill=False, lw=2.0, edgecolor='black'))
ax2.text(ENC_X + ENC_W / 2, ENC_Y + ENC_H + 0.3, 'project box (top cover removed)', ha='center', fontsize=FS_SMALL, style='italic', color='dimgray')

# Arduino Uno footprint (roughly to scale: ~2.7" x 2.1")
UNO_X, UNO_Y, UNO_W, UNO_H = 5.5, 4.0, 5.0, 4.0
ax2.add_patch(patches.Rectangle((UNO_X, UNO_Y), UNO_W, UNO_H, fill=True, facecolor='#eef2ff', edgecolor='black', lw=1.6))
ax2.text(UNO_X + UNO_W / 2, UNO_Y + UNO_H + 0.25, 'Arduino Uno R3', ha='center', fontsize=FS_LABEL, fontweight='bold')
ax2.add_patch(patches.Rectangle((UNO_X + 0.3, UNO_Y + UNO_H - 0.9), 1.6, 0.6, fill=True, facecolor='#c7d2fe', edgecolor='black', lw=1.0))
ax2.text(UNO_X + 0.3 + 0.8, UNO_Y + UNO_H - 0.6, 'USB', ha='center', va='center', fontsize=FS_SMALL)

# Named pin points on the Uno footprint edge
uno_d2 = (UNO_X, UNO_Y + 3.1)
uno_gnd_l = (UNO_X, UNO_Y + 2.3)
uno_d3 = (UNO_X, UNO_Y + 1.5)
uno_tx = (UNO_X + UNO_W, UNO_Y + 3.1)
uno_5v = (UNO_X + UNO_W, UNO_Y + 2.3)
uno_gnd_r = (UNO_X + UNO_W, UNO_Y + 1.5)
uno_a0 = (UNO_X + UNO_W, UNO_Y + 0.7)
uno_i2c = (UNO_X + UNO_W / 2, UNO_Y + UNO_H)  # SDA/SCL leave from the top edge, toward the OLED
for (px, py), name, ha, dx in [
    (uno_d2, 'D2', 'right', -0.15),
    (uno_gnd_l, 'GND', 'right', -0.15),
    (uno_d3, 'D3', 'right', -0.15),
    (uno_tx, 'TX', 'left', 0.15),
    (uno_5v, '5V', 'left', 0.15),
    (uno_gnd_r, 'GND', 'left', 0.15),
    (uno_a0, 'A0', 'left', 0.15),
]:
    dot(ax2, px, py, r=0.07)
    ax2.text(px + dx, py, name, ha=ha, va='center', fontsize=FS_PIN)
dot(ax2, uno_i2c[0], uno_i2c[1], r=0.07)

# Pedal jack on left panel
PJACK = (ENC_X + 1.3, UNO_Y + 3.1)
ax2.add_patch(patches.Circle(PJACK, 0.35, fill=True, facecolor='#fef3c7', edgecolor='black', lw=1.6))
ax2.text(PJACK[0], PJACK[1] + 0.65, 'Pedal IN', ha='center', fontsize=FS_LABEL, fontweight='bold')
ax2.text(PJACK[0], PJACK[1] + 0.30, '3.5mm TRS', ha='center', fontsize=FS_SMALL)
ax2.text(PJACK[0], ENC_Y + 0.25, '(mounted on left panel,\nto external pedal)', ha='center', fontsize=FS_SMALL, style='italic', color='dimgray')

# Built-in panel pushbutton, also on the left panel, wired in parallel
# with the pedal jack (same D2/GND nodes -- either one triggers sustain)
BTN_R = 0.35
BUTTON = (ENC_X + 1.3, UNO_Y + 0.9)
ax2.add_patch(patches.Circle(BUTTON, BTN_R, fill=True, facecolor='#d1fae5', edgecolor='black', lw=1.6))
ax2.text(BUTTON[0], BUTTON[1] + BTN_R + 0.25, 'Button', ha='center', va='bottom', fontsize=FS_LABEL, fontweight='bold')
ax2.text(BUTTON[0], BUTTON[1] - BTN_R - 0.25, '(parallel with Pedal IN)', ha='center', va='top', fontsize=FS_SMALL, style='italic', color='dimgray')

# MIDI out jack on right panel
MJACK = (ENC_X + 18.0, UNO_Y + 2.7)
ax2.add_patch(patches.Circle(MJACK, 0.35, fill=True, facecolor='#fecaca', edgecolor='black', lw=1.6))
ax2.text(MJACK[0], MJACK[1] + 0.75, 'MIDI OUT', ha='center', fontsize=FS_LABEL, fontweight='bold')
ax2.text(MJACK[0], MJACK[1] + 0.55, '3.5mm TRS (Type A)', ha='center', fontsize=FS_SMALL)
ax2.text(MJACK[0], ENC_Y + 0.25, '(mounted on right panel,\ncable to FM-1 MIDI IN)', ha='center', fontsize=FS_SMALL, style='italic', color='dimgray')

# Small perfboard patch for the two resistors, sitting between Uno and MIDI jack
PERF_X, PERF_Y, PERF_W, PERF_H = MJACK[0] - 2.1, UNO_Y + 1.1, 1.5, 1.4
ax2.add_patch(patches.Rectangle((PERF_X, PERF_Y), PERF_W, PERF_H, fill=True, facecolor='#f3f4f6', edgecolor='black', lw=1.2, linestyle='dashed'))
ax2.text(PERF_X + PERF_W / 2, PERF_Y + PERF_H / 2, 'R1, R2\n(220Ω)', ha='center', va='center', fontsize=FS_SMALL)

# Wires: pedal jack -> Uno D2 / GND
line(ax2, PJACK[0] + 0.35, PJACK[1] + 0.15, uno_d2[0], uno_d2[1])
line(ax2, PJACK[0] + 0.35, PJACK[1] - 0.15, uno_gnd_l[0], uno_gnd_l[1])
ax2.text((PJACK[0] + uno_d2[0]) / 2, (PJACK[1] + 0.15 + uno_d2[1]) / 2 + 0.15, 'tip', ha='center', fontsize=FS_SMALL, color='dimgray')
ax2.text((PJACK[0] + uno_gnd_l[0]) / 2, (PJACK[1] - 0.15 + uno_gnd_l[1]) / 2 - 0.25, 'ring+sleeve', ha='center', fontsize=FS_SMALL, color='dimgray')

# Wires: built-in button -> same Uno D2 / GND nodes (parallel with pedal jack)
line(ax2, BUTTON[0] + 0.35, BUTTON[1] + 0.15, uno_d2[0], uno_d2[1])
line(ax2, BUTTON[0] + 0.35, BUTTON[1] - 0.15, uno_gnd_l[0], uno_gnd_l[1])
dot(ax2, uno_d2[0], uno_d2[1], r=0.06)
dot(ax2, uno_gnd_l[0], uno_gnd_l[1], r=0.06)

# Wires: Uno -> perfboard -> MIDI jack
line(ax2, uno_tx[0], uno_tx[1], PERF_X, PERF_Y + PERF_H - 0.3)
line(ax2, uno_5v[0], uno_5v[1], PERF_X, PERF_Y + PERF_H - 0.9)
line(ax2, uno_gnd_r[0], uno_gnd_r[1], MJACK[0] - 0.35, MJACK[1] - 0.15)
line(ax2, PERF_X + PERF_W, PERF_Y + PERF_H - 0.3, MJACK[0] - 0.35, MJACK[1] + 0.15)
line(ax2, PERF_X + PERF_W, PERF_Y + PERF_H - 0.9, MJACK[0] - 0.35, MJACK[1])

# Mode switch, left panel, below the Button (same style/parallel logic to D2 above)
SWITCH = (ENC_X + 1.3, UNO_Y - 1.3)
ax2.add_patch(patches.Circle(SWITCH, 0.32, fill=True, facecolor='#e0e7ff', edgecolor='black', lw=1.6))
ax2.text(SWITCH[0], SWITCH[1] + 0.32 + 0.25, 'Mode Switch', ha='center', va='bottom', fontsize=FS_LABEL, fontweight='bold')
ax2.text(SWITCH[0], SWITCH[1] - 0.32 - 0.25, '(panel toggle, D3)', ha='center', va='top', fontsize=FS_SMALL, style='italic', color='dimgray')
line(ax2, SWITCH[0] + 0.32, SWITCH[1] + 0.1, uno_d3[0], uno_d3[1])
dot(ax2, uno_d3[0], uno_d3[1], r=0.06)

# OLED, front panel -- drawn well above the Uno since this is a top-down
# view and the OLED itself mounts facing outward on the front panel, not
# flat inside. Its description sits to the right, not below, so it never
# competes with the "Arduino Uno R3" label for vertical space.
OLED_W, OLED_H = 3.4, 1.6
OLED_XY = (UNO_X + UNO_W / 2 - OLED_W / 2, UNO_Y + UNO_H + 1.3)
ax2.add_patch(patches.Rectangle(OLED_XY, OLED_W, OLED_H, fill=True, facecolor='#1f2937', edgecolor='black', lw=1.6))
ax2.text(OLED_XY[0] + OLED_W / 2, OLED_XY[1] + OLED_H + 0.25, 'OLED Display', ha='center', va='bottom', fontsize=FS_LABEL, fontweight='bold')
ax2.text(OLED_XY[0] + OLED_W / 2, OLED_XY[1] + OLED_H / 2, 'SSD1306\n128x64', ha='center', va='center', fontsize=FS_SMALL, color='white')
ax2.text(OLED_XY[0] + OLED_W + 0.3, OLED_XY[1] + OLED_H / 2, '(front panel, facing out;\nwires drop to Uno GND/5V/SDA/SCL)', ha='left', va='center', fontsize=FS_SMALL, style='italic', color='dimgray')
line(ax2, uno_i2c[0], uno_i2c[1], OLED_XY[0] + OLED_W / 2, OLED_XY[1])

# Audio IN jack, right panel, its own column to the right of MIDI OUT (not
# stacked below it) -- feeds the pitch-mode bias circuit, not the Uno directly
AUDJACK = (ENC_X + ENC_W - 1.6, UNO_Y + 0.8)
ax2.add_patch(patches.Circle(AUDJACK, 0.35, fill=True, facecolor='#bfdbfe', edgecolor='black', lw=1.6))
ax2.text(AUDJACK[0], AUDJACK[1] + 0.95, 'Audio IN', ha='center', fontsize=FS_LABEL, fontweight='bold')
ax2.text(AUDJACK[0], AUDJACK[1] + 0.60, '3.5mm TRS,\nFM-1 headphone out', ha='center', va='top', fontsize=FS_SMALL)
ax2.text(AUDJACK[0], ENC_Y + 0.25, '(mounted on right panel,\ncable to FM-1 headphone out)', ha='center', fontsize=FS_SMALL, style='italic', color='dimgray')

# Perfboard patch for the bias/coupling circuit (R3, R4, R5, C1), between
# the Uno's A0 pin and the Audio IN jack
PERF2_X, PERF2_Y, PERF2_W, PERF2_H = AUDJACK[0] - 2.6, UNO_Y - 0.9, 1.8, 1.4
ax2.add_patch(patches.Rectangle((PERF2_X, PERF2_Y), PERF2_W, PERF2_H, fill=True, facecolor='#f3f4f6', edgecolor='black', lw=1.2, linestyle='dashed'))
ax2.text(PERF2_X + PERF2_W / 2, PERF2_Y + PERF2_H / 2, 'R3, R4, R5\n(10k/100k)\n+ C1 (1µF)', ha='center', va='center', fontsize=FS_SMALL - 1)
line(ax2, uno_a0[0], uno_a0[1], PERF2_X, PERF2_Y + PERF2_H - 0.3)
line(ax2, PERF2_X + PERF2_W, PERF2_Y + PERF2_H / 2, AUDJACK[0] - 0.35, AUDJACK[1])
dot(ax2, uno_a0[0], uno_a0[1], r=0.06)

notes2 = (
    "Notes:\n"
    "• Resistors R1/R2 can live on a small offcut of perfboard, or be soldered directly in-line on the wire runs -- exact placement isn't critical\n"
    "• See the schematic for the electrical connections (which wire goes through which resistor) -- this diagram is for physical placement only\n"
    "• Button and Pedal IN jack are wired in parallel to the same D2/GND nodes -- either one alone triggers sustain, so the pedal can be left unplugged\n"
    "• Leave slack on the USB cable path -- the board still needs to be reachable for re-flashing (disconnect MIDI OUT jack's TX lead first)\n"
    "• Mode Switch, OLED, and Audio IN are all optional additions -- the board works exactly as the original sustain-only build without them\n"
    "• OLED needs 4 wires to the Uno (GND, VCC/5V, SDA->A4, SCL->A5) in addition to the single SDA/SCL point shown here for clarity"
)
ax2.text(0, ENC_Y - 0.5, notes2, fontsize=FS_NOTES - 1, va='top', ha='left', family='sans-serif', linespacing=1.6)

plt.tight_layout()

# ===========================================================================
# Save
# ===========================================================================
import os
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
fig1.savefig(os.path.join(OUT_DIR, 'fm1_footswitch_schematic.pdf'))
fig1.savefig(os.path.join(OUT_DIR, 'fm1_footswitch_schematic.png'), dpi=160)
fig1.savefig(os.path.join(OUT_DIR, 'fm1_footswitch_schematic.svg'))
fig2.savefig(os.path.join(OUT_DIR, 'fm1_footswitch_layout.pdf'))
fig2.savefig(os.path.join(OUT_DIR, 'fm1_footswitch_layout.png'), dpi=160)
fig2.savefig(os.path.join(OUT_DIR, 'fm1_footswitch_layout.svg'))
print('saved schematic + layout to', OUT_DIR)
