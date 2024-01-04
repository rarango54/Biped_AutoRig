import maya.cmds as cmds
import maya.api.OpenMaya as om2

from body_modules.base import Base

from utils.ctrl_library import Nurbs
from utils import util

def stretchylocs(loc_start, loc_end):
    """cube ctrl between locators
    aim to end, point to middle (with attr to slide),
    scale (with attr to control voume preserv)"""
    dist = util.distance(loc_start, loc_end)
    suffix = loc_start.split("_")[-1]
    name = loc_start.replace(suffix, "")
### rot order? aim axis?
    ctrl = Nurbs.cube(name+"CTRL", dist/3, "brown")
    # buffer
    cmds.group(ctrl, n = name+"buffer_GRP")
    # point constraint with attr slider
    # aim constraint with which axis? does it matter?
    # scale based on distance / global scale
    # leave attr to connect global scale later manually?
    return ctrl

def partial(joints, rsidetoo = False):
    """ duplicate / rename joint, mult 0.5 of rotations"""
    jnts = [joints] if isinstance(joints, str) else joints
    if rsidetoo == True:
        r_jnts = [x.replace("L_", "R_") for x in jnts]
        jnts.extend(r_jnts)
    partials = []
    for j in jnts:
        name = j.replace("_JNT", "_partial_JNT")
        rad = cmds.getAttr(j+".radius")
        partial = cmds.duplicate(j, n = name, parentOnly = True)[0]
        cmds.setAttr(partial+".radius", rad * 1.5)
        mult = cmds.shadingNode(
                "multiplyDivide", n = j.replace("_JNT", "_partial_MULT"), au = True)
        cmds.connectAttr(j+".r", mult+".input1")
        cmds.setAttr(mult+".input2", 0.5, 0.5, 0.5)
        cmds.connectAttr(mult+".output", partial+".r")
        partials.append(partial)
    return partials

def anglelocs(target, measure, fwd = (0,0,1), bend = (0,1,0), tilt = (-1,0,0)):
    """measures angle change of target to measure object
    relative to parent on 2 axes in 90 degree range
    returns locator with .bend and .tilt attributes"""
    parent = cmds.listRelatives(target, parent = True)[0]
    d = util.distance(parent, target)
    suffix = target.split("_")[-1]
    name = target.replace(suffix, "corrDriver")
    # create locators
    main_loc = cmds.spaceLocator(n = name+"_main_LOC", p = (0,0,0))[0]
    fwd_loc = cmds.spaceLocator(n = name+"_follow_LOC", p = (0,0,0))[0]
    bend_loc = cmds.spaceLocator(n = name+"_bend_LOC", p = (0,0,0))[0]
    tilt_loc = cmds.spaceLocator(n = name+"_tilt_LOC", p = (0,0,0))[0]
    # position 3 locs based on input and distance betw parent & child
    fwd = [x*d for x in fwd]
    bend = [x*d for x in bend]
    tilt = [x*d for x in tilt]
    cmds.xform(fwd_loc, t = fwd)
    cmds.xform(bend_loc, t = bend)
    cmds.xform(tilt_loc, t = tilt)
    cmds.parent([fwd_loc, bend_loc, tilt_loc], main_loc)
    cmds.parent(main_loc, "correctiveDrivers_GRP")
    # hook it up
    cmds.pointConstraint(target, main_loc, offset = (0,0,0), weight = 1)
    cmds.matchTransform(main_loc, target, rot = True)
    cmds.orientConstraint(parent, main_loc, mo = True, weight = 1)
    cmds.parentConstraint(measure, fwd_loc, weight = 1)
    util.lock(main_loc, ["tx","ty","tz","rx","ry","rz","sx","sy","sz","v"])
    # 2 angleBetween nodes
    bend_angle = cmds.shadingNode("angleBetween", n = name+"_bend_ANG", au = True)
    tilt_angle = cmds.shadingNode("angleBetween", n = name+"_tilt_ANG", au = True)
    # add attrs bend, tilt/swing, twist
    cmds.addAttr(main_loc, longName = "bend", attributeType = "double")
    cmds.setAttr(main_loc+".bend", e = True, keyable = True)
    cmds.addAttr(main_loc, longName = "tilt", attributeType = "double")
    cmds.setAttr(main_loc+".tilt", e = True, keyable = True)
    # connect it all into the attrs on the main locator
    cmds.connectAttr(fwd_loc+".t", bend_angle+".vector1")
    cmds.connectAttr(fwd_loc+".t", tilt_angle+".vector1")
    cmds.connectAttr(bend_loc+".t", bend_angle+".vector2")
    cmds.connectAttr(tilt_loc+".t", tilt_angle+".vector2")
    cmds.connectAttr(bend_angle+".angle", main_loc+".bend")
    cmds.connectAttr(tilt_angle+".angle", main_loc+".tilt")
    return main_loc
    
def calibrate(angleloc, target, bendattrs = None, tiltattrs = None):
    """based on angle change calibrate range for driving target with attributes on it"""
    bend = angleloc + ".bend"
    tilt = angleloc + ".tilt"
    tsuffix = target.split("_")[-1]
    for nr, attrs in enumerate([bendattrs, tiltattrs]):
        if nr == 0:
            axis = bend
        else:
            axis = tilt
        for a in attrs:
            att = "help_" + a
            if "s" in a:
            # scale range => 1 + attr  <->  1 - attr
                cmds.addAttr(target, longName = att, at = "double", 
                             dv = 0, min = 0, max = 1)
                cmds.setAttr(f"{target}.{att}", e = True, channelBox = True)
                rmv = util.remap(target.replace(tsuffix, a+"_RMV"), axis, 180, 0)
                pos = cmds.shadingNode(
                        "plusMinusAverage", n = target.replace(tsuffix, a+"_ADD"),
                        au = True)
                cmds.setAttr(pos+".input1D[0]", 1)
                cmds.connectAttr(f"{target}.{att}", pos+".input1D[1]")
                neg = cmds.shadingNode(
                        "plusMinusAverage", n = target.replace(tsuffix, a+"_SUB"),
                        au = True)
                cmds.setAttr(neg+".input1D[0]", 1)
                cmds.setAttr(neg+".operation", 2) # subtract
                cmds.connectAttr(f"{target}.{att}", neg+".input1D[1]")
                # cmds.connectAttr(f"{target}.{att}", rmv+".outputMax")
                cmds.connectAttr(pos+".output1D", rmv+".outputMax")
                cmds.connectAttr(neg+".output1D", rmv+".outputMin")
                # connect into target
                cmds.connectAttr(rmv+".outValue", f"{target}.{a}")
            else:
            # t & r range => attr  <->  attr * -1
                cmds.addAttr(target, longName = att, at = "double")
                cmds.setAttr(f"{target}.{att}", e = True, channelBox = True)
                rmv = util.remap(target.replace(tsuffix, a+"_RMV"), axis, 180, 0)
                neg = cmds.shadingNode(
                        "multDoubleLinear", n = target.replace(tsuffix, a+"_NEG"),
                        au = True)
                cmds.connectAttr(f"{target}.{att}", neg+".input1")
                cmds.setAttr(neg+".input2", -1)
                cmds.connectAttr(f"{target}.{att}", rmv+".outputMax")
                cmds.connectAttr(neg+".output", rmv+".outputMin")
                # connect into target
                cmds.connectAttr(rmv+".outValue", f"{target}.{a}")
    return


if __name__ == "__main__":
    
    
    
    pass