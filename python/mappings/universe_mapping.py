def onCook(dat):
    dat.clear()
    dat.appendRow(['channel', 'net', 'subnet', 'universe'])

    pix_chop = op('null2')
    if not pix_chop:
        debug('DMX routing: null2 not found')
        return

    # Get all channel names (e.g., ['r0', 'r1', 'r2', ...])
    chan_names = [c.name for c in pix_chop.chans()]
    num_channels = len(chan_names)
    if num_channels == 0:
        return

    for i, chan_name in enumerate(chan_names):
        # Extract the numeric suffix (if any)
        suffix = ''.join(ch for ch in chan_name if ch.isdigit())
        idx = int(suffix) if suffix else i
        universe = idx + 1  # Universe number starts at 1

        # Add R, G, and B rows for this channel index
        dat.appendRow([f'r{idx}', 0, 0, universe])
        dat.appendRow([f'g{idx}', 0, 0, universe])
        dat.appendRow([f'b{idx}', 0, 0, universe])

    return
