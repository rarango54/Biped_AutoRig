import maya.cmds as cmds

from utils.ctrl_library import Control

    
def make_proxies(proxy_dict, parent_grp, module_name):
    """dict setup = {"name" : 
        ( [pos], "shape", size, "color", [lock axes] )}
    """
    module_grp = cmds.group(n=f"{module_name}_proxy_GRP", em=True)
    cmds.parent(module_grp, parent_grp)
    for proxy in list(proxy_dict):
            shape = proxy_dict[proxy][1]
            size = proxy_dict[proxy][2]
            color = proxy_dict[proxy][3]
            
            loc = cmds.spaceLocator(n=proxy, a=True)[0]
            
            temp_obj = eval(
                f'Control.{shape}("temp", {size}, "{color}")'
                )
            temp_shape = cmds.listRelatives(temp_obj, s=True)
            for s in temp_shape:
                cmds.setAttr(f"{s}.alwaysDrawOnTop", 1)
            cmds.parent(temp_shape, loc, r=True, s=True)
            new_shapes = cmds.listRelatives(loc, s=True)
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
            cmds.setAttr(f"{proxy}.{axis}", l=True)

def make_joints(proxies_list, rot_order, radius):
    cmds.select(cl=True)
    joints_list = []
    for proxy in proxies_list:    # skip proxies that don't need joints
        fitted_pos = cmds.xform(proxy, q=True, rp=True, ws=True)
        j = cmds.joint(
            n=proxy.replace("PRX", "JNT"), p=fitted_pos, 
            roo=rot_order, rad=radius
            )
        cmds.sets(j, add="joints")
        joints_list.append(j)
    return joints_list

def mirror_ctrls(upChain_ctrls, module, ctrl_parent):
    """upChain_ctrl = list of first-of-chain or world space ctrls
    IK and FK separately since they have different parents
    e.g. only shoulderFK, without elbowFK or handFK
    """    
    for l_ctrl in upChain_ctrls:
        new_ctrls = cmds.duplicate(l_ctrl, rc=True)
        for new in new_ctrls:
            new1 = new.replace("L_", "R_")
            new2 = new1.replace(new1[-1], "") # remove '1' suffix from duplication
            cmds.rename(new, new2)
            shapes = cmds.listRelatives(new2, c=True, s=True)
            if not shapes:
                # skip objects that have no shapes
                continue
            for s in shapes:
                if cmds.getAttr(f"{s}.overrideColor") == 6:
                    cmds.setAttr(f"{s}.overrideColor", 13)
                elif cmds.getAttr(f"{s}.overrideColor") == 18:
                    cmds.setAttr(f"{s}.overrideColor", 20)
    r_ctrls = [x.replace("L_", "R_") for x in upChain_ctrls]
    mirror_grp = cmds.group(n=f"{module}_mirror_GRP", em=True)
    cmds.parent(r_ctrls, mirror_grp)
    cmds.setAttr(f"{mirror_grp}.sx", -1)
    cmds.parent(mirror_grp, ctrl_parent)
    return mirror_grp
            
def sub_ctrl_vis(sub_ctrl):
    parent_ctrl = cmds.listRelatives(sub_ctrl, p=True)[0]
    sub_shapes = cmds.listRelatives(sub_ctrl, c=True, s=True)
    
    cmds.addAttr(
        parent_ctrl, ln='sub_ctrl_vis', 
        at="double", dv=0 ,min=0 ,max=1 ,k=True)
    cmds.setAttr(
        f'{parent_ctrl}.sub_ctrl_vis', e=True, k=True, l=False)
        
    for s in sub_shapes:
        cmds.connectAttr(f"{parent_ctrl}.sub_ctrl_vis", f"{s}.visibility")

def ikfk(start_jnt, mid_jnt, end_jnt, tip_jnt, switcher_ctrl):
    cmds.addAttr(
        switcher_ctrl, ln='ikfk', 
        at="double", dv=0 ,min=0 ,max=1 ,k=True)
    cmds.setAttr(
        f'{switcher_ctrl}.ikfk', e=True, k=True, l=False)
    # duplicate joints
    for chain in ["IK", "FK"]:
        start = cmds.duplicate(
            start_jnt, n=start_jnt.replace("JNT", f"{chain}_JNT"), po=True)
        mid = cmds.duplicate(
            mid_jnt, n=mid_jnt.replace("JNT", f"{chain}_JNT"), po=True)
        end = cmds.duplicate(
            end_jnt, n=end_jnt.replace("JNT", f"{chain}_JNT"), po=True)
        tip = cmds.duplicate(
            tip_jnt, n=tip_jnt.replace("JNT", f"{chain}_JNT"), po=True)
        cmds.parent(tip, end)
        cmds.parent(end, mid)
        cmds.parent(mid, start)
    # ik fk blending
    for jnt in [start_jnt, mid_jnt, end_jnt]:
        ik_jnt = jnt.replace("JNT", "IK_JNT")
        fk_jnt = jnt.replace("JNT", "FK_JNT")
        
        t_blend = cmds.shadingNode(
            "blendColors", n=jnt.replace("JNT", "t_blend"), au=True)
        r_blend = cmds.shadingNode(
            "blendColors", n=jnt.replace("JNT", "r_blend"), au=True)
        s_blend = cmds.shadingNode(
            "blendColors", n=jnt.replace("JNT", "s_BLEND"), au=True)
        
        # connect ik first to make sense with Attribute name
        # ikfk i.e. ik = 0, fk = 1
        # translates
        cmds.connectAttr(f"{ik_jnt}.translate", f"{t_blend}.color1")
        cmds.connectAttr(f"{fk_jnt}.translate", f"{t_blend}.color2")
        cmds.connectAttr(f"{switcher_ctrl}.ikfk", f"{t_blend}.blender")
        cmds.connectAttr(f"{t_blend}.output", f"{jnt}.translate")
        # rotates
        cmds.connectAttr(f"{ik_jnt}.rotate", f"{r_blend}.color1")
        cmds.connectAttr(f"{fk_jnt}.rotate", f"{r_blend}.color2")
        cmds.connectAttr(f"{switcher_ctrl}.ikfk", f"{r_blend}.blender")
        cmds.connectAttr(f"{r_blend}.output", f"{jnt}.rotate")
        # scales
        cmds.connectAttr(f"{ik_jnt}.scale", f"{s_blend}.color1")
        cmds.connectAttr(f"{fk_jnt}.scale", f"{s_blend}.color2")
        cmds.connectAttr(f"{switcher_ctrl}.ikfk", f"{s_blend}.blender")
        cmds.connectAttr(f"{s_blend}.output", f"{jnt}.scale")

    

if __name__ == "__main__":
    
    ikfk("L_upArm_JNT",
         "L_foreArm_JNT",
         "L_hand_JNT",
         "L_handEnd_JNT",
         "nurbsCircle1")
    # cmds.duplicate("L_upArm_JNT")
    
    pass