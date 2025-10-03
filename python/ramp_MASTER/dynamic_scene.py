# dynamic scene for the scene pads
def onCook(dat):
    src = op('pad_state')
    dat.clear()

    for c in range(src.numCols):
        for r in range(src.numRows):
            dat.appendRow([src[r, c]. val])
    return
