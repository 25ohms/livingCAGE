import math

def onCook(dat):
    dat.clear()
    dat.appendRow(["panel_idx", "bar_idx", "x", "z"])

    # --- parameters (standard TD CHOP sources) ---
    num_sides = int(op("numSides")["chan1"].eval())
    _ = int(op("resample_val")[0].eval())  # kept for parity / vertical res

    # --- constants controlling spacing (same as polygon version) ---
    radius     = 1.0      # used only for polygon case
    cornerfrac = 0.07
    barinset   = 0.06

    # --- special case: single panel (numSides == 2) ---
    if num_sides == 2:
        # panel is 1 m wide → bars at ±0.5 m
        dat.appendRow([0, 0, -0.5, 0.0])   # left bar
        dat.appendRow([0, 1,  0.5, 0.0])   # right bar
        return

    # --- regular polygon case (two bars per corner) ---
    verts = []
    for i in range(num_sides):
        theta = 2.0 * math.pi * i / num_sides
        x = radius * math.cos(theta)
        z = radius * math.sin(theta)
        verts.append((x, z))

    # helpers
    def v_add(a, b): return (a[0] + b[0], a[1] + b[1])
    def v_sub(a, b): return (a[0] - b[0], a[1] - b[1])
    def v_mul(a, s): return (a[0] * s, a[1] * s)
    def v_len(a): return math.hypot(a[0], a[1])
    def v_norm(a):
        L = v_len(a)
        return (a[0] / L, a[1] / L) if L > 1e-9 else (0.0, 0.0)

    # generate two bars per corner
    for i in range(num_sides):
        vtx      = verts[i]
        prev_vtx = verts[(i - 1) % num_sides]
        next_vtx = verts[(i + 1) % num_sides]

        dir_prev = v_norm(v_sub(prev_vtx, vtx))
        dir_next = v_norm(v_sub(next_vtx, vtx))

        bisector = v_norm(v_add(dir_prev, dir_next))
        inward   = (-bisector[0], -bisector[1])

        pos0_edge = v_add(vtx, v_mul(dir_prev, cornerfrac * v_len(v_sub(prev_vtx, vtx))))
        pos0      = v_add(pos0_edge, v_mul(inward, barinset))

        pos1_edge = v_add(vtx, v_mul(dir_next, cornerfrac * v_len(v_sub(next_vtx, vtx))))
        pos1      = v_add(pos1_edge, v_mul(inward, barinset))

        dat.appendRow([i, 0, pos0[0], pos0[1]])
        dat.appendRow([i, 1, pos1[0], pos1[1]])

    return
