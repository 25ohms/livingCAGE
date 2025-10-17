# slider_functionality
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

def onValueChange(channel, sampleIndex, val, prev):
    # Step 1: Isolate functionality so that it only uses sliders
    name = channel.name
    #print(f"Name: {name}, Val: {val}")
    if name == 'ch1n50':
        raw = 1 if val > 0.5 else 0
        #print(raw)
        Sset('pb_trigger', raw)
        if raw == 0:
            #print("released")
            Sset('pb_value', 0)
        return
    
    if name == 'ch1pitch':
        trigger = Sget('pb_trigger')
        if not trigger:
            Sset('pb_value', 0)
            return
        #print(f"trigger called, current value: {val}")
        #curr = Sget('pb_value')
        Sset('pb_value', (val * 100) + 100)
#        print(f"pb_value: {Sget('pb_value')}")
        return


