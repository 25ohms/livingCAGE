# /project1/execute1  — Execute DAT
# Sends DDP every frame, with detailed logging

import socket, struct, numpy as np

# ---- USER CONFIG ----
WLED_IP   = "4.3.2.1"     # WLED-AP default
WLED_PORT = 4048          # DDP port
CHOP_PATH = "topto3"      # TOP to CHOP with r,g,b channels
LOG_BYTES = True          # print packet size per frame
LOG_META  = True          # print CHOP meta (shape, chans, samples) once
# ---------------------

_sock = None
_logged_meta = False

def onStart():
    """Called once when the DAT activates / project starts."""
    global _sock, _logged_meta
    try:
        _sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _sock.setblocking(False)
        _logged_meta = False
        debug("DDP: socket ready → {}:{}".format(WLED_IP, WLED_PORT))
    except Exception as e:
        debug("DDP socket init error:", e)
        _sock = None
    return


def onExit():
    """Close socket on shutdown."""
    global _sock
    if _sock is not None:
        try:
            _sock.close()
            debug("DDP: socket closed.")
        except Exception as e:
            debug("DDP: socket close error:", e)
        finally:
            _sock = None
    return


def onFrameStart(frame):
    """Called once per frame — pack and send one DDP packet."""
    global _sock, _logged_meta

    # --- safety check ---
    if _sock is None:
        debug("DDP: socket not initialized — skipping frame")
        return

    try:
        c = op(CHOP_PATH)
        if not c or c.numSamples < 1 or c.numChans < 3:
            if LOG_META and not _logged_meta:
                debug("DDP: source CHOP invalid or not ready ({} chans, {} samples)".format(
                    c.numChans if c else -1, c.numSamples if c else -1))
            return

        # --- CHOP → NumPy (shape = (numChans, numSamples)) ---
        arr = c.numpyArray()  # (3, N)
        if LOG_META and not _logged_meta:
            debug("DDP: CHOP '{}': shape={} (chans={}, samples={})".format(
                c.path, arr.shape, c.numChans, c.numSamples))
            _logged_meta = True

        # RGB conversion
        rgb_f32 = arr[0:3, :].T
        rgb_u8 = (np.clip(rgb_f32, 0.0, 1.0) * 255.0).astype('uint8')
        data = rgb_u8.tobytes()

        # --- DDP header ---
        # hdr = bytearray(b"DDP\x01")
        # hdr += bytes([0b11000000, 1])        # flags + data type
        # hdr += struct.pack(">H", 0)          # offset = 0
        # hdr += struct.pack(">H", len(data))  # length = bytes

        packet = data # used to be hdr + data

        _sock.sendto(packet, (WLED_IP, WLED_PORT))

        if LOG_BYTES and frame % 30 == 0:
            print(f"[Frame {frame}] Sent {len(packet)} bytes to {WLED_IP}:{WLED_PORT}")
    except Exception as e:
        debug("DDP send error:", e)
    return
