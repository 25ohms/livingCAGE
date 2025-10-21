import numpy as np

def onCook(scriptOp):
    parentComp = scriptOp.parent()
    strips = sorted(parentComp.ops('*_null'), key=lambda o: int(o.digits))

    if not strips:
        return

    height = strips[0].height

    # get pixel lag
    lag_chop = parentComp.op('pixel_lag')
    lag_val = int(lag_chop[0]) if lag_chop and lag_chop.numSamples > 0 else 0

    # compute total width: strips + gaps
    total_width = sum([s.width for s in strips]) + lag_val * (len(strips) - 1)

    img = np.zeros((height, total_width, 4), dtype=np.float32)

    offset = 0
    for i, s in enumerate(strips):
        arr = s.numpyArray()  # (height, width, 4)
        w = s.width
        img[:, offset:offset+w, :] = arr
        offset += w

        # add black gap after each strip except the last
        if i < len(strips) - 1 and lag_val > 0:
            offset += lag_val

    scriptOp.copyNumpyArray(img)
    #print("Script TOP output:", total_width, "x", height)
    return
