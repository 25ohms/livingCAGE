# color_out_callbacks — Script CHOP
# Maps controlone_logic + mapping_csv -> exact MIDI LED channels (ch1nXX)
# Idle: pads/scenes show their base color; Selected: they blink using a clock.

import math
from enum import Enum

STATE_CHOP = 'controlone_logic'    # <-- your logic CHOP
MAP_DAT = 'mapping_csv'         # <-- CSV: param, channel, color, active
# <-- optional: a CHOP that outputs 0/1; else we use internal clock
BLINK_CHOP = 'blink_clock'
BLINK_HZ = 2.0                   # internal blink rate (if no blink CHOP)
COLOR_TEST = op('lfo3')[0]

MOVEMENT_COLORS = [40]*9              # all pads = 40
# all pads = 70 (replace with COLOR_TEST when testing)
STROBE_COLORS = [70]*9
HUE_COLORS = [10, 60, 50, 112, 3, 34, 117, 123, 126]  # stepped hue
TEMPO_CLOCK = op('tempo')[0]
SMOKE_COLORS = [COLOR_TEST]*9
S_PAD_STATE = op('/project1/ramp_MASTER/pad_flat')

colors = {
    'white': 127,
    'black': 0,
    'uv': 59
}


# 59: UV color
# 0 : Black color
# 127: White color


# ---------- helpers ----------


def _logic():
    return op(STATE_CHOP)


def L(name, cast=int, default=0):
    c = _logic().chan(name) if _logic() else None
    if not c:
        return cast(default)
    try:
        return cast(c.eval())
    except:
        return cast(default)


def load_mapping():
    """param -> {channel(str), color(int), active(bool)}"""
    d = op(MAP_DAT)
    cols = {d[0, c].val: c for c in range(d.numCols)}
    items = {}
    for r in range(1, d.numRows):
        param = d[r, cols['param']].val.strip()
        channel = d[r, cols['channel']].val.strip()
        color = int(float(d[r, cols['color']].val or 0))
        active = d[r, cols['active']].val.strip(
        ).lower() in ('1', 'true', 'yes', '1.0')
        # Guard: channel must look like ch1nNN
        if not channel.startswith('ch'):
            continue
        items[param] = {'channel': channel, 'color': color, 'active': active}
    return items


def put(scriptOp, chan_name, val):
    ch = scriptOp.appendChan(chan_name)
    ch[0] = val

# ---------- main ----------


def onCook(scriptOp):
    scriptOp.clear()
    m = load_mapping()
    logic = _logic()
    if not logic or not m:
        return

    # 0) Safety: detect duplicate channel assignments in CSV (can cause cross-talk)
    #    We'll warn once per cook if duplicates found.
    chan_to_params = {}
    for p, row in m.items():
        chan_to_params.setdefault(row['channel'], []).append(p)
    dupes = [c for c, ps in chan_to_params.items() if len(ps) > 1]
    if dupes:
        debug("[color_out] WARNING: duplicate channel(s) in CSV: " + ", ".join(dupes))
        # We do not early-return; we still output, but you should fix the CSV.

    # 1) Read logic
    movemode = int(L('movement'))
    strobemode = int(L('strobe'))
    huemode = int(L('hue'))
    smokemode = int(L('smoke'))
    move_idx = int(L('move_idx'))
    strobe_idx = int(L('strobe_idx'))
    hue_idx = int(L('hue_idx'))
    scene_idx = int(L('scene'))

    # Decide which (if any) pad is selected for blinking
    active_mode = None
    sel_idx = 0
    if movemode:
        active_mode, sel_idx = 'movement', move_idx
    elif strobemode:
        active_mode, sel_idx = 'strobe', strobe_idx
    elif huemode:
        active_mode, sel_idx = 'hue', hue_idx
    # elif smokemode:
    #     active_mode = 'smoke'

    clock_val = TEMPO_CLOCK
    # print(clock_val)

    # PADS p1..p9
    for i in range(1, 10):
        key = f'p{i}'
        row = m.get(key)
        if not row:
            continue
        chan = row['channel']
        base_col = row['color']

        if movemode:
            col = MOVEMENT_COLORS[i-1]
        elif strobemode:
            col = STROBE_COLORS[i-1]
            # print(f"Colour Test: {COLOR_TEST}")
        elif huemode:
            col = HUE_COLORS[i-1]
        elif smokemode:
            col = SMOKE_COLORS[i-1]
        else:
            col = base_col

        # col  = row['color']
        is_selected = (active_mode is not None and sel_idx == i)
        val = col if not is_selected else int(col * clock_val)
        put(scriptOp, chan, val)

    # SCENES b1..b32
    scene_states = []
    if S_PAD_STATE is not None:
        scene_states = [int(cell.val) for cell in S_PAD_STATE.col(0)]
    # print(len(scene_states))

    # 4) White / Black / UV — on/off (exclusive already handled in logic_events)
    # Let's also make it so that when any of these states are toggled, the scene display is also set to the respective colours.
    override_color = None
    for name in ('white', 'black', 'uv'):
        row = m.get(name)
        if not row:
            continue
        active = int(L(name)) == 1
        put(scriptOp, row['channel'], 127 if int(L(name)) == 1 else 0)
        if active:
            override_color = colors[name]

    for i in range(1, 33):
        key = f'b{i}'
        row = m.get(key)
        if not row:
            continue
        chan = row['channel']
        col = row['color'] * HUE_COLORS[hue_idx - 1]
        is_active = (scene_idx == i)
        val = col * scene_states[i -
                                 1] if not is_active else 127
        if override_color is not None:
            val = override_color
        put(scriptOp, chan, val)

    # 4) Mode buttons — light when active (their CSV color), else off
    for name, state in (('movement', movemode),
                        ('strobe',   strobemode),
                        ('hue',      huemode),
                        ('smoke',    smokemode)):
        row = m.get(name)
        if not row:
            continue
        put(scriptOp, row['channel'], row['color'] if state else 0)
        # TEST: Colour
        # if name == 'smoke':
        #     print(f"Current Color: {SMOKE_COLORS[0]}")

    # # 6) BPM Flashing for BPM_TAP
    # bpm_chan = m.get('bpm_tap')
    # put(scriptOp, bpm_chan['channel'], 127 * clock_val)

    # --- Autoloop (momentary) ---
    if 'autoloop' in m:
        val = int(L('autoloop'))
        put(scriptOp, m['autoloop']['channel'], 127 if val == 1 else 0)

    # --- Autoloop Override (toggle) ---
    if 'autoloop_override' in m:
        val = int(L('autoloop_override'))
        put(scriptOp, m['autoloop_override']
            ['channel'], 127 if val == 1 else 0)

        # If override is ON, force autoloop channel to white as well
        if val == 1 and 'autoloop' in m:
            put(scriptOp, m['autoloop']['channel'], 127)

    # 6) Play/Pause and BPM Tap — on/off
    if 'play_pause' in m:
        put(scriptOp, m['play_pause']['channel'], 127 *
            clock_val if int(L('play_pause')) == 1 else 0)
    if 'shift' in m:
        put(scriptOp, m['shift']['channel'],
            127 if int(L('shift')) == 1 else 0)
    if 'bpm_tap' in m:
        is_pressed = int(L('bpm_tap')) == 1
        put(scriptOp, m['bpm_tap']['channel'],
            int(127 * clock_val) if is_pressed else 0)

    return
