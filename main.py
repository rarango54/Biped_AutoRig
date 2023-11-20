import maya.cmds as cmds
import maya.api.OpenMaya as om2

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig
from utils import bendy

def aim(bendy, aimtarget, uptarget, root, vaim, vup, scldriver = None):
    """scldriver only for reverse aiming (lowarm & lowleg)"""
    suffix = bendy.split("_")[0]
    name = bendy.replace(suffix, "")
    bendy_buff = util.buffer(bendy)
    util.mtx_zero([bendy_buff, bendy])
    cmds.pointConstraint(
            [root, aimtarget], bendy_buff,
            n = f"{name}_POINT", offset = (0,0,0), weight = 0.5)
    cmds.aimConstraint(
            aimtarget, bendy_buff, 
            n = f"{name}_AIM", aimVector = vaim, upVector = vup,
            worldUpObject = uptarget, worldUpType = 1)
    dist = cmds.shadingNode(
            "distanceBetween", n = f"{name}_stretch_DBTW", 
            asUtility = True)
    cmds.connectAttr(f"{root}.worldMatrix[0]", f"{dist}.inMatrix1")
    cmds.connectAttr(f"{aimtarget}.worldMatrix[0]", f"{dist}.inMatrix2")
    orig_dist = cmds.getAttr(f"{dist}.distance")
    norm = cmds.shadingNode(
            "multiplyDivide", n = f"{name}_stretch_NORM", 
            asUtility = True)
    cmds.setAttr(f"{norm}.operation", 2) # divide
    cmds.setAttr(f"{norm}.input2X", orig_dist)
    cmds.connectAttr(f"{dist}.distance", f"{norm}.input1X")
    # need to divide globalScl
    glob = cmds.shadingNode(
            "multiplyDivide", n = f"{name}_globalScl_DIV", 
            asUtility = True)
    cmds.setAttr(f"{glob}.operation", 2) # divide
    cmds.connectAttr(f"{norm}.outputX", f"{glob}.input1Z")
    if scldriver:
        cmds.connectAttr(f"{scldriver}.sx", f"{glob}.input1X")
        cmds.connectAttr(f"{scldriver}.sy", f"{glob}.input1Y")
    else:
        cmds.connectAttr(f"{root}.sx", f"{glob}.input1X")
        cmds.connectAttr(f"{root}.sy", f"{glob}.input1Y")
    cmds.connectAttr("global_CTRL.scale", f"{glob}.input2")
    cmds.connectAttr(f"{glob}.output", f"{bendy_buff}.scale")

    
if __name__ == "__main__":
    
    for s in ["L_", "R_"]:
        aim(bendy = f"{s}uparm_bendy_CTRL",
            aimtarget = f"{s}elbow_bendy_CTRL", 
            uptarget = f"{s}uparm_baseTwist_LOC",
            root = f"{s}uparm_bendy_1_JNT",
            vaim = (0,0,1),
            vup = (1,0,0))
        aim(bendy = f"{s}lowarm_bendy_CTRL",
            aimtarget = f"{s}elbow_bendy_CTRL", 
            uptarget = f"{s}lowarm_endTwist_LOC",
            root = f"{s}lowarm_twist_end_JNT",
            vaim = (0,0,-1),
            vup = (1,0,0),
            scldriver = f"{s}lowarm_JNT")

    pass