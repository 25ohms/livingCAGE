def onFrameStart(frame):
    """
    Called once per frame. Executes the send_ddp() function inside ddp_sender.
    Logs number of bytes sent each frame.
    """
    try:
        sender = op('ddp_sender').module  # safer than mod.ddp_sender
        sent_bytes = sender.send_ddp() or 0
        debug("DDP bytes sent:", sent_bytes)
    except Exception as e:
        debug("DDP send error:", e)
    return
