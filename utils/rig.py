import maya.cmds as cmds

from utils.ctrl_library import Nurbs
from body_modules.base import Base

    
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
            cmds.setAttr(f"{proxy}.{axis}", lock = True)

def make_joints(proxies_list, rot_order, radius):
    cmds.select(clear = True)
    joints_list = []
    for proxy in proxies_list:    # skip proxies that don't need joints!
        fitted_pos = cmds.xform(
                proxy, q = True, rotatePivot = True, worldSpace = True)
        new_joint = cmds.joint(
                n = proxy.replace("PRX", "JNT"), position = fitted_pos, 
                rotationOrder = rot_order, radius = radius)
        cmds.sets(new_joint, add = "joints")
        joints_list.append(new_joint)
    return joints_list

def mirror_ctrls(upChain_ctrls, ctrl_parent):
    """upChain_ctrl = list of first-of-chain or world space ctrls.
    Mirror IK and FK separately since they have different parents
    e.g. only shoulderFK, without elbowFK or handFK
    """    
    for l_ctrl in upChain_ctrls:
        new_ctrls = cmds.duplicate(l_ctrl, renameChildren = True)
        for new in new_ctrls:
            new1 = new.replace("L_", "R_")
            new2 = new1.replace(new1[-1], "") # remove '1' suffix from duplication
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
    r_upChain_ctrls = [x.replace("L_", "R_") for x in upChain_ctrls]
    mirror_grp = cmds.group(n = "mirror_GRP", empty = True, parent = ctrl_parent)
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

def ikfk_chains(joint_list, switcher_ctrl):
    """ joint_list must be in order of parent to child hierarchy, top to bottom
    new chains are siblings of original chain
    rotateOrder connected from FK -> main -> IK 
    (rO will be driven by FK ctrls, doesn't matter on IK, but needs to match)
    """
    cmds.addAttr(
        switcher_ctrl, longName = "ikfk", 
        attributeType = "double", defaultValue = 0, 
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
    
    

if __name__ == "__main__":
    
    
        
    
    pass