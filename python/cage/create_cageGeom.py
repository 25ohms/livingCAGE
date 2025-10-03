import math


def cook(scriptOP):
    scriptOP.clear()

    # parameters
    num_sides = int(op("numSides")["chan1"].eval())
    total_points = int(op('resample_val')[0].eval())  # per side

    # DAT to CHOP source
    coords = op("datto1")  # must have 'x' and 'z' channels
    x_vals = coords['x'].vals
    z_vals = coords['z'].vals

    for i in range(num_sides):
        x = float(x_vals[i])
        z = float(z_vals[i])

        # create total_points points from y=0 → y=1
        pts = []
        for j in range(total_points):
            t = j / (total_points - 1) if total_points > 1 else 0
            p = scriptOP.appendPoint()
            p.P = [x, t, z]
            pts.append(p)

        # connect all total_points into a vertical line
        line = scriptOP.appendPoly(len(pts), closed=False, addPoints=False)
        for j, p in enumerate(pts):
            line[j].point = p

    return
