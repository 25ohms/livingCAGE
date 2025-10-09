# logic_events CHOP Execute
# Purpose: listen to MIDI inputs and update state_storage

STATE = '/project1/state_storage'

# ------------------- utils -------------------


def _ensure_state():
    t = op(STATE)
    if not t:
        t = op('/project1').create(tableDAT, 'state_storage')
    if t.numRows == 0 or t.numCols < 2 or t[0, 0].val != 'key' or t[0, 1].val != 'val':
        t.clear()
        t.appendRow(['key', 'val'])
    return t


def Sget(k, cast=int):
    t = _ensure_state()
    r = t.row(k)
    if not r:
        t.appendRow([k, '0'])
        return cast(0)
    v = t[k, 'val']
    return cast(v) if v not in (None, '') else cast(0)


def Sset(k, v):
    t = _ensure_state()
    if not t.row(k):
        t.appendRow([k, str(int(v))])
    else:
        t[k, 'val'] = str(int(v))


# --- color helpers ---
COLORS = ('white', 'black', 'uv')
NAME_BY_CH = {
    'ch1n46': 'white',
    'ch1n47': 'black',
    'ch1n48': 'uv',
}


def _clear_all_colors():
    for c in COLORS:
        Sset(c, 0)
        Sset(c + '_hold', 0)


def _select_color(key, raw, shift_on):
    """
    Enforce exclusivity:
    - On press (raw==1): zero ALL colors (raw + hold), then:
        * shift==1  -> set key_hold=1 and key=1 (latched + immediate light)
        * shift==0  -> set key=1 (momentary)
    - On release (raw==0): set key=0 (hold persists only if shift latched earlier)
    """
    if raw == 1:
        _clear_all_colors()
        if shift_on:
            Sset(key + '_hold', 1)
        Sset(key, 1)
    else:
        # release: raw off; holds persist only if previously set
        Sset(key, 0)

# ------------------- main -------------------


def onValueChange(channel, sampleIndex, val, prev):
    #print(f'Channel: {channel.name}, Sample Index: {sampleIndex}, Val: {val}, Prev: {prev}')
    name = channel.name
    raw = 1 if val > 0.5 else 0

    # Play/Pause toggle (rising edge)
    if name == 'ch1n52':
        if prev <= 0.5 and val > 0.5:
            cur = Sget('play_pause')
            Sset('play_pause', 0 if cur == 1 else 1)
        return

    # Autoloop Override (Audio-reactivity) toggle
    if name == 'ch1n56':
        if prev <= 0.5 and val > 0.5:  # rising edge
            cur = Sget('autoloop_override')
            if cur == 0:  # currently OFF -> turn ON
                # store original state
                if Sget('_prev_strobe_idx') == 0:
                    Sset('_prev_strobe_idx', Sget('strobe_idx'))
                Sset('autoloop_override', 1)
                Sset('autoloop', 1)
                Sset('strobe_idx', 10)  # special audio-reactive index
            else:  # currently ON -> turn OFF
                prev_idx = Sget('_prev_strobe_idx')
                if prev_idx != 0:
                    Sset('strobe_idx', prev_idx)
                Sset('_prev_strobe_idx', 0)  # clear only after restoring
                Sset('autoloop_override', 0)
                Sset('autoloop', 0)
        return

    # Autoloop Momentary (Audio-reactivity) button
    if name == 'ch1n61':  # autoloop momentary
        if val > 0.5:  # pressed
            # save previous strobe_idx (only once)
            if Sget('_prev_strobe_idx') == 0:  # unused slot to store
                Sset('_prev_strobe_idx', Sget('strobe_idx'))
            Sset('autoloop', 1)
            Sset('strobe_idx', 10)
        else:  # released
            Sset('autoloop', 0)
            prev_idx = Sget('_prev_strobe_idx')
            if prev_idx != 0:
                Sset('strobe_idx', prev_idx)
            Sset('_prev_strobe_idx', 0)  # clear
        return

    # Shift (momentary)
    if name == 'ch1n53':
        Sset('shift', raw)
        return

    # BPM Tap (momentary)
    if name == 'ch1n55':
        Sset('bpm_tap', raw)
        return

    # White / Black / UV (exclusive; most recent wins)
    if name in NAME_BY_CH:
        key = NAME_BY_CH[name]
        _select_color(key, raw, Sget('shift') == 1)
        return

    # Movement / Strobe / Hue (mutually exclusive on press)
    # Let's make it so that Smoke is a "test" state that visualizes different colour mappings
    if name in ('ch1n57', 'ch1n58', 'ch1n59', 'ch1n60'):
        if prev <= 0.5 and val > 0.5:
            Sset('movement_mode', 1 if name == 'ch1n57' else 0)
            Sset('strobe_mode',   1 if name == 'ch1n58' else 0)
            Sset('hue_mode',      1 if name == 'ch1n59' else 0)
            Sset('smoke_mode',    1 if name == 'ch1n60' else 0)
        return

    # Pads p1..p9 (momentary; also store index for active mode on press)
    if name.startswith('ch1n'):
        n = int(name[4:])
        if 37 <= n <= 45:
            idx = n - 36  # p1..p9
            Sset(f'p{idx}', raw)
            if raw == 1:
                if Sget('movement_mode') == 1:
                    Sset('move_idx', idx)
                if Sget('strobe_mode') == 1:
                    Sset('strobe_idx', idx)
                    Sset('autoloop', 0)
                    Sset('autoloop_override', 0)
                if Sget('hue_mode') == 1:
                    Sset('hue_idx', idx)
            return

        # Scenes b1..b32 (on press)
        if 1 <= n <= 32 and prev <= 0.5 and val > 0.5:
            Sset('scene', n)
            return

    return
