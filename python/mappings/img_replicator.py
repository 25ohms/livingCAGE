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
	for i, c in enumerate(newOps):
		# manually wire input1 of replicant to the same source as master
		if master.inputs:
			c.inputConnectors[0].connect(master.inputs[0])
	
	return
