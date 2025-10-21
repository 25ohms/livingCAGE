# me - this DAT
# 
# comp - the replicator component which is cooking
# allOps - a list of all replicants, created or existing
# newOps - the subset that were just created
# template - table DAT specifying the replicator attributes
# master - the master operator
#

def onRemoveReplicant(comp, replicant):

	replicant.destroy()
	return


def onReplicate(comp, allOps, newOps, template, master):
    parentComp = comp.parent()

    # Clean up old helper ops
    for o in parentComp.ops('*_flip', '*_padconst', '*_pad', '*_null'):
        o.destroy()

    # Sort replicants by their numeric suffix (digits)
    for r in sorted(allOps, key=lambda o: int(o.digits)):
        idx = int(r.digits)
        src = r

        # horizontal offset for helper nodes
        baseX = r.nodeX + 200
        baseY = r.nodeY

        if idx % 2 == 0:
            # Even → flip horizontally
            t = parentComp.create(transformTOP, f"{r.name}_flip")
            t.inputConnectors[0].connect(src)
            t.par.sx = 1 # previously -1 to account for flip, for now keep it the same
            t.nodeX = baseX
            t.nodeY = baseY
            src = t
        else:
            # Odd → pad with black pixels from pixel_lag
            lag_chop = parentComp.op('pixel_lag')
            lag_val = int(lag_chop[0]) if lag_chop and lag_chop.numSamples > 0 else 0



        # Always end with a Null
        n = parentComp.create(nullTOP, f"{r.name}_null")
        n.inputConnectors[0].connect(src)
        n.nodeX = baseX + 400   # push nulls further right
        n.nodeY = baseY

    print("Replicated ramps:", [o.name for o in allOps])
    return
