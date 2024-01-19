import maya.cmds as cmds
import maya.api.OpenMaya as om2

from body_modules.base import Base

from utils.ctrl_library import Nurbs
from utils import util

    
def make_proxies(proxy_dict, parent_grp, module_name):
    """dict setup = {"name" : 
            [pos], "shape", size, "color", [lock axes] )}
    """
    module_grp = cmds.group(n = f"{module_name}_proxy_GRP", empty = True)
    cmds.parent(module_grp, parent_grp)
    for proxy in list(proxy_dict):
            shape = proxy_dict[proxy][1]
            size = proxy_dict[proxy][2]
            color = proxy_dict[proxy][3]
            loc = cmds.spaceLocator(n = proxy, absolute = True)[0]
            temp_obj = eval(f'Nurbs.{shape}("temp", {size}, "{color}")')
            temp_shape = cmds.listRelatives(temp_obj, shapes = True)
            for s in temp_shape:
                # make visible through geo like xRay
                cmds.setAttr(f"{s}.alwaysDrawOnTop", 1)
            cmds.parent(temp_shape, loc, relative = True, shape = True)
            new_shapes = cmds.listRelatives(loc, shapes = True)
            for s in new_shapes:
                cmds.rename(s, f"{loc}Shape")
            cmds.delete(temp_obj)
            cmds.xform(loc, t=proxy_dict[proxy][0])
            cmds.parent(loc, module_grp)
            previous = proxy
    return list(proxy_dict)

def proxy_lock(proxy_dict):
    for proxy in list(proxy_dict):
        lock_axes = proxy_dict[proxy][4]
        for axis in lock_axes:
            cmds.setAttr(f"{proxy}.{axis}", lock = True, keyable = False)
            cmds.setAttr(f"{proxy}.{axis}", channelBox = False)

def make_joints(proxies_list, rot_order, radius, prxorient = False, set = "joints"):
    cmds.select(clear = True)
    joints_list = []
    for proxy in proxies_list:    # skip proxies that don't need joints!
        fitted_pos = cmds.xform(
                proxy, q = True, rotatePivot = True, worldSpace = True)
        new_joint = cmds.joint(
                n = proxy.replace("PRX", "JNT"), position = fitted_pos, 
                rotationOrder = rot_order, radius = radius)
        if prxorient == True:
            cmds.matchTransform(new_joint, proxy, rot = True)
            cmds.makeIdentity(new_joint, apply = True, rotate = True)
        cmds.sets(new_joint, add =set)
        joints_list.append(new_joint)
    return joints_list

def mirror_ctrls(upChain_ctrls, ctrl_parent):
    """upChain_ctrl = list of first-of-chain or world space ctrls.
    Mirror IK and FK separately since they have different parents
    e.g. only shoulderFK, without elbowFK or handFK
    """
    objects = [upChain_ctrls] if isinstance(upChain_ctrls, str) else upChain_ctrls
    for l_ctrl in objects:
        new_ctrls = cmds.duplicate(l_ctrl, renameChildren = True)
        for new in new_ctrls:
            new1 = new.replace("L_", "R_")
            suffix = new.split("_")[-1]
            new2 = new1.replace(suffix, suffix[:-1]) # remove '1' suffix from duplication
            cmds.rename(new, new2)
            shapes = cmds.listRelatives(new2, children = True, shapes = True)
            if not shapes:
                # skip objects that have no shapes
                continue
            for s in shapes:
                if cmds.getAttr(f"{s}.overrideColor") == 6:
                    cmds.setAttr(f"{s}.overrideColor", 13)
                elif cmds.getAttr(f"{s}.overrideColor") == 18:
                    cmds.setAttr(f"{s}.overrideColor", 20)
    r_upChain_ctrls = [x.replace("L_", "R_") for x in objects]
    mirror_grp = cmds.group(n = "mirror_GRP", empty = True)
    # mirror_grp = cmds.group(n = "mirror_GRP", empty = True, parent = ctrl_parent)
    cmds.parent(r_upChain_ctrls, mirror_grp)
    cmds.setAttr(f"{mirror_grp}.sx", -1)
    cmds.parent(r_upChain_ctrls, ctrl_parent)
    cmds.delete(mirror_grp)
    return mirror_grp
            
def sub_ctrl_vis(sub_ctrl):
    parent_ctrl = cmds.listRelatives(sub_ctrl, parent = True)[0]
    sub_shapes = cmds.listRelatives(sub_ctrl, children = True, shapes = True)
    cmds.addAttr(
        parent_ctrl, longName = "sub_ctrl_vis", 
        attributeType = "double", defaultValue = 0, 
        min = 0, max = 1, keyable = True)
    cmds.setAttr(
        f"{parent_ctrl}.sub_ctrl_vis", e = True, 
        keyable = True, lock = False)
    for s in sub_shapes:
        cmds.connectAttr(f"{parent_ctrl}.sub_ctrl_vis", f"{s}.visibility")

def ikfk_chains(joint_list, switcher_ctrl, default = 0):
    """ joint_list must be in order of parent to child hierarchy, top to bottom
    new chains are siblings of original chain
    rotateOrder connected from FK -> main -> IK 
    (rO will be driven by FK ctrls, doesn't matter on IK, but needs to match)
    """
    cmds.addAttr(
        switcher_ctrl, longName = "ikfk", niceName = "IKFK",
        attributeType = "double", defaultValue = default, 
        min = 0, max = 1, keyable = True)
    cmds.setAttr(
        f"{switcher_ctrl}.ikfk", e = True, keyable = True, lock = False)
    # duplicate joints
    for chain in ["IK", "FK"]:
        firstj = None
        for orig_jnt in joint_list:
            secondj = cmds.duplicate(orig_jnt, 
                           n = orig_jnt.replace("JNT", f"{chain}_JNT"), 
                           parentOnly = True)
            cmds.sets(secondj, remove = "bind_joints")
            if firstj != None:
                cmds.parent(secondj, firstj)
            firstj = secondj
    # ik fk blending
    for orig_jnt in joint_list:
        ik_jnt = orig_jnt.replace("JNT", "IK_JNT")
        fk_jnt = orig_jnt.replace("JNT", "FK_JNT")
        t_blend = cmds.shadingNode(
            "blendColors", n = orig_jnt.replace("JNT", "t_BLEND"), asUtility = True)
        r_blend = cmds.shadingNode(
            "blendColors", n = orig_jnt.replace("JNT", "r_BLEND"), asUtility = True)
        s_blend = cmds.shadingNode(
            "blendColors", n = orig_jnt.replace("JNT", "s_BLEND"), asUtility = True)
        # connect ik first to make sense with Attribute name
        # ikfk i.e. ik = 0, fk = 1
        # translates
        cmds.connectAttr(f"{ik_jnt}.translate", f"{t_blend}.color1")
        cmds.connectAttr(f"{fk_jnt}.translate", f"{t_blend}.color2")
        cmds.connectAttr(f"{switcher_ctrl}.ikfk", f"{t_blend}.blender")
        cmds.connectAttr(f"{t_blend}.output", f"{orig_jnt}.translate")
        # rotates
        cmds.connectAttr(f"{ik_jnt}.rotate", f"{r_blend}.color1")
        cmds.connectAttr(f"{fk_jnt}.rotate", f"{r_blend}.color2")
        cmds.connectAttr(f"{switcher_ctrl}.ikfk", f"{r_blend}.blender")
        cmds.connectAttr(f"{r_blend}.output", f"{orig_jnt}.rotate")
        # scales
        cmds.connectAttr(f"{ik_jnt}.scale", f"{s_blend}.color1")
        cmds.connectAttr(f"{fk_jnt}.scale", f"{s_blend}.color2")
        cmds.connectAttr(f"{switcher_ctrl}.ikfk", f"{s_blend}.blender")
        cmds.connectAttr(f"{s_blend}.output", f"{orig_jnt}.scale")
        # rotateOrders
        cmds.connectAttr(f"{fk_jnt}.rotateOrder", f"{orig_jnt}.rotateOrder")
        cmds.connectAttr(f"{orig_jnt}.rotateOrder", f"{ik_jnt}.rotateOrder")

def ikfk_ctrlvis(ik_ctrls, fk_ctrls, bendies, switch):
    """0 = fk, 1 = ik
    plug ikfk into all ik ctrl shapes
    plug reverse into all fk ctrl shapes"""
    cmds.addAttr(
        switch, longName = "bendies",
        attributeType = "double", defaultValue = 0, 
        min = 0, max = 1, keyable = False)
    cmds.setAttr(
        f"{switch}.bendies", e = True, channelBox = True, lock = False)
    name = switch.replace("_CTRL", "_ikfk_REV")
    rev = cmds.shadingNode("reverse", n = name, asUtility = True)
    cmds.connectAttr(f"{switch}.ikfk", f"{rev}.inputX")
    for grp in [ik_ctrls, fk_ctrls, bendies]:
        for ctrl in grp:
            shapes = cmds.listRelatives(ctrl, children = True, shapes = True)
            for s in shapes:
                if grp == ik_ctrls:
                    cmds.connectAttr(f"{switch}.ikfk", f"{s}.v")
                if grp == fk_ctrls:
                    cmds.connectAttr(f"{rev}.outputX", f"{s}.v")
                if grp == bendies:
                    cmds.connectAttr(f"{switch}.bendies", f"{s}.v")

def fk_sclinvert(ctrls, rsidetoo = False):
    """for fk ctrl chain
    inverts scale from ctrl's parent to itself
    identical to joints' natural behaviour when parented in a chain
    leaving child with zeroed channels
    """
    objects = [ctrls] if isinstance(ctrls, str) else ctrls
    if rsidetoo == True:
        r_objects = [x.replace("L_", "R_") for x in objects]
        objects.extend(r_objects)
    for child in objects:
        parent = cmds.listRelatives(child, parent = True)[0]
        suffix = parent.split("_")[-1]
        child_w = om2.MMatrix(cmds.getAttr(f"{child}.worldMatrix[0]"))
        parent_wInv = om2.MMatrix(cmds.getAttr(f"{parent}.worldInverseMatrix[0]"))
    # rotation and translation into 2 separate matrixes
        offset_rot = child_w * parent_wInv
        offset_t = child_w * parent_wInv
    # setElement(row, column, value)
        # set translation to 0:
        offset_rot.setElement(3, 0, 0)
        offset_rot.setElement(3, 1, 0)
        offset_rot.setElement(3, 2, 0)
        # set rotation to 0:
        offset_t.setElement(0, 0, 1)
        offset_t.setElement(0, 1, 0)
        offset_t.setElement(0, 2, 0)
        offset_t.setElement(1, 0, 0)
        offset_t.setElement(1, 1, 1)
        offset_t.setElement(1, 2, 0)
        offset_t.setElement(2, 0, 0)
        offset_t.setElement(2, 1, 0)
        offset_t.setElement(2, 2, 1)
    # compose mtx from parent scale & invert it
        comp = cmds.createNode("composeMatrix", n = parent.replace(suffix, "scl_COMP"))
        inv = cmds.shadingNode(
                "inverseMatrix", n = parent.replace(suffix, "sclInv_MTX"), au = True)
        cmds.connectAttr(f"{parent}.s", f"{comp}.inputScale")
        cmds.connectAttr(f"{comp}.outputMatrix", f"{inv}.inputMatrix")
    # OPM = offset_rot * scaleInverse * offset_t
        opm = cmds.shadingNode(
                "multMatrix", n = parent.replace(suffix, "sclInv_MM"), au = True)
        cmds.setAttr(f"{opm}.matrixIn[0]", offset_rot, type = "matrix")
        cmds.connectAttr(f"{inv}.outputMatrix", f"{opm}.matrixIn[1]")
        cmds.setAttr(f"{opm}.matrixIn[2]", offset_t, type = "matrix")
        cmds.connectAttr(f"{opm}.matrixSum", f"{child}.offsetParentMatrix")
        cmds.xform(child, 
           translation = (0, 0, 0), 
           rotation = (0, 0, 0), 
           scale = (1, 1, 1))
    return comp
        
def spaces(spacedrivers, target, r_only = False, t_only = False, rside = False,
           split = False):
    """use in controls function before cleanup & mtx_zero()
    return [buffer_grp, space_constraint]"""
    drivers = [spacedrivers] if isinstance(spacedrivers, str) else spacedrivers
    suffix = target.split("_")[-1]
    if split == True:
        buff = target.replace(suffix, "spaces_GRP")
    else:
        buff = util.buffer(target, "spaces_GRP")
    if rside == True:
        drivers = [x.replace("L_", "R_") for x in drivers]
    # extract enum names from spacedrivers
    spacenames = ""
    for i, sp in enumerate(drivers):
        if "L_" in sp[0:2] or "R_" in sp[0:2]:
            spn = sp.split("_")[1]
        else:
            spn = sp.split("_")[0]
        if i == 0:
            spacenames = spacenames + spn
        else:
            spacenames = spacenames + ":" + spn
    # constraints
    if r_only == True:
        attr = "r_space"
        sconstr = cmds.orientConstraint(
                drivers, buff, mo = True, n = target.replace(suffix, "r_space_ORI"))[0]
    elif t_only == True:
        attr = "t_space"
        sconstr = cmds.parentConstraint(
                drivers, buff, mo = True, n = target.replace(suffix, "t_space_PAR"),
                skipRotate = ["x","y","z"])[0]
    else:
        attr = "space"
        sconstr = cmds.parentConstraint(
                drivers, buff, mo = True, n = target.replace(suffix, "space_PAR"))[0]
    cmds.addAttr(
            target, longName = attr, attributeType = "enum",
            enumName = spacenames, )
    cmds.setAttr(f"{target}.{attr}", e = True, keyable = True)
    # 1 condition node per space
    for nr, space in enumerate(drivers):
        suffix = space.split("_")[-1]
        con = cmds.shadingNode(
                "condition", n = space.replace(suffix, "space_CON"), au = True)
        # attr -> first term
        cmds.connectAttr(f"{target}.{attr}", f"{con}.firstTerm")
        # 2nd term = nr
        cmds.setAttr(f"{con}.secondTerm", nr)
        # True = 1, False = 0
        cmds.setAttr(f"{con}.colorIfTrueR", 1)
        cmds.setAttr(f"{con}.colorIfFalseR", 0)
        # connect con.outColorR to {sconstr}.{drivers[nr]}{nr} attr
        cmds.connectAttr(f"{con}.outColorR", f"{sconstr}.{drivers[nr]}W{nr}")
    return [buff, sconstr]

def spaceblend(space1, space2, target, attr_obj, attr_name,
               r_only = False, t_only = False, rside = False):
    """for wrist/ankle align & pin elbow/knee
    defaults to space1"""
    suffix = target.split("_")[-1]
    cmds.addAttr(
            attr_obj, longName = attr_name, attributeType = "double",
            dv = 0, min = 0, max = 1)
    cmds.setAttr(f"{attr_obj}.{attr_name}", e = True, keyable = True)
    # constraints
    if r_only == True:
        # offset = (0,0,0)
        sconstr = cmds.orientConstraint(
                [space1, space2], target, mo = True, weight = 0,
                n = target.replace(suffix, "r_space_ORI"))[0]
    elif t_only == True:
        sconstr = cmds.pointConstraint(
                [space1, space2], target, mo = False, 
                n = target.replace(suffix, "t_space_PAR"))[0]
    else:
        sconstr = cmds.parentConstraint(
                [space1, space2], target, mo = True, 
                n = target.replace(suffix, "space_PAR"))[0]
    # connect attr to constraint
    rev = cmds.shadingNode(
            "reverse", n = target.replace(suffix, "spaceblend_REV"), au = True)
    cmds.connectAttr(f"{attr_obj}.{attr_name}", f"{rev}.inputX")
    cmds.connectAttr(f"{rev}.outputX", f"{sconstr}.{space1}W0")
    cmds.connectAttr(f"{attr_obj}.{attr_name}", f"{sconstr}.{space2}W1")
    return

if __name__ == "__main__":
    
    
        
    
    pass