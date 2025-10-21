import math

def cook(scriptOP):
    scriptOP.clear()

    # parameters
    num_sides = int(op("numSides")["chan1"].eval())
    total_points = int(op("resample_val")[0].eval())  # vertical resolution per bar

    # DAT to CHOP source
    coords = op("datto1")  # must have 'x' and 'z' channels
    # if coords is None or 'x' not in coords.channels or 'z' not in coords.channels:
    #     debug = "create_cageGeom: missing 'datto1' or missing x/z channels"
    #     print(debug)
    #     return

    x_vals = coords['x'].vals
    z_vals = coords['z'].vals
    n = min(len(x_vals), len(z_vals))

    # --- Special case: single panel (2 bars) ---
    if num_sides == 2:
        n = min(n, 2)

    # --- Build bars ---
    for i in range(n):
        x = float(x_vals[i])
        z = float(z_vals[i])

        # create vertical points (Y = 0 → 1)
        pts = []
        for j in range(total_points):
            t = j / (total_points - 1) if total_points > 1 else 0
            p = scriptOP.appendPoint()
            p.P = [x, t, z]
            pts.append(p)

        # connect all points into a vertical line
        line = scriptOP.appendPoly(len(pts), closed=False, addPoints=False)
        for j, p in enumerate(pts):
            line[j].point = p

    return
