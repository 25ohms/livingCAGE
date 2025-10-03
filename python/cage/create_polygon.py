import math


def onCook(dat):
    dat.clear()
    dat.appendRow(["x", "z"])  # column headers

    numSides = int(op("numSides")['chan1'].eval())
    side_len = 1.0

    # circumradius formula for regular n-gon
    R = side_len / (2 * math.sin(math.pi / numSides))

    # angle step
    step = 2 * math.pi / numSides

    for k in range(numSides):
        # starting at angle = pi/numSides to make polygon "flat" at bottom
        theta = math.pi / numSides + k * step
        x = R * math.cos(theta)
        z = R * math.sin(theta)
        dat.appendRow([x, z])

    return
