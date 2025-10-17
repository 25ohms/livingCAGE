# logic_out_callbacks Script CHOP
# Purpose: read state_storage and output clean channels

STATE = '/project1/state_storage'


def _t():
    return op(STATE)


def Sget(k, cast=int):
    t = _t()
    if not t:
        return cast(0)
    r = t.row(k)
    if not r:
        return cast(0)
    v = t[k, 'val']
    return cast(v) if v not in (None, '') else cast(0)


def onCook(scriptOp):
    scriptOp.clear()

    # Core controls
    scriptOp.appendChan('play_pause')[0] = Sget('play_pause')
    scriptOp.appendChan('shift')[0] = Sget('shift')
    scriptOp.appendChan('bpm_tap')[0] = Sget('bpm_tap')
    scriptOp.appendChan('ft_value')[0] = Sget('ft_value')
    scriptOp.appendChan('pb_value')[0] = Sget('pb_value')
    scriptOp.appendChan('pb_trigger')[0] = Sget('pb_trigger')
    scriptOp.appendChan('autoloop')[0] = Sget('autoloop')
    scriptOp.appendChan('autoloop_override')[0] = Sget('autoloop_override')

    # Exclusive color outputs: hold overrides raw; only one should be active
    white = 1 if Sget('white_hold') == 1 else Sget('white')
    black = 1 if Sget('black_hold') == 1 else Sget('black')
    uv = 1 if Sget('uv_hold') == 1 else Sget('uv')

    # (Safety) If multiple are 1 (shouldn't happen), keep the last pressed by priority order white<-black<-uv
    if white + black + uv > 1:
        # simple deterministic tie-breaker (you can change policy)
        uv = 0 if Sget('uv_hold') == 0 else uv
        black = 0 if Sget('black_hold') == 0 else black
        # if still multiple, drop to just the first non-zero
        if white and black and uv:
            black = 0
            uv = 0
        elif white and black:
            black = 0
        elif white and uv:
            uv = 0
        elif black and uv:
            uv = 0

    scriptOp.appendChan('white')[0] = white
    scriptOp.appendChan('black')[0] = black
    scriptOp.appendChan('uv')[0] = uv

    # Modes + indices
    scriptOp.appendChan('movement')[0] = Sget('movement_mode')
    scriptOp.appendChan('strobe')[0] = Sget('strobe_mode')
    scriptOp.appendChan('hue')[0] = Sget('hue_mode')
    scriptOp.appendChan('smoke')[0] = Sget('smoke_mode')  # FOR TESTING
    scriptOp.appendChan('move_idx')[0] = Sget('move_idx')
    scriptOp.appendChan('strobe_idx')[0] = Sget('strobe_idx')
    scriptOp.appendChan('hue_idx')[0] = Sget('hue_idx')

    # Pads p1..p9 (momentary)
    for i in range(1, 10):
        scriptOp.appendChan(f'p{i}')[0] = Sget(f'p{i}')

    # Scene
    scriptOp.appendChan('scene')[0] = Sget('scene')

    return
