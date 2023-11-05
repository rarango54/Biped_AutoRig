import maya.cmds as cmds

from utils import util

def bendysetup(mod_name, 
               start_jnt, end_jnt,
               forwardaxis, upaxis,
               base_ctrl, mid_ctrl, end_ctrl,
               twistInvDriver = None):
    """creates bendy rig A to Z
    1) straight joint chain from start to end
        parented under start (make sure it's part of the main skeleton)
    2) twist-joint in the middle with single chain IK pointing to either start or end
    3) twist-locators based on upaxis, parenting dependent on reversal
    4) ikspline and 3 driver joints connected to ctrls
    """
    # bendy ctrl in the middle can be generated, radius based on distance
    # base_ctrl, mid_ctrl etc are misleading args because there are no ctrls when 
    # generating a bendy chain for e.g. an arm...
    
    # jointchain
    # radius? rotord? orient? can those be logically derived from bendy(args)?
    bendy_joints = jointchain(
            mod_name = mod_name,
            number = 5,
            start_obj = start_jnt,
            end_obj = end_jnt,
            radius = 3,
            rotord = "zxy",
            orient = "horizontal")
    cmds.parent(bendy_joints[0], start_jnt)
    # ikspline
    ikspline(
            mod_name = mod_name, 
            start = bendy_joints[0], 
            mid = mid_ctrl, 
            end = bendy_joints[-1], 
            forwardaxis = forwardaxis, 
            upaxis = upaxis,
            base_ctrl = base_ctrl, 
            mid_ctrl = mid_ctrl, 
            end_ctrl = end_ctrl,
            twistInvDriver = twistInvDriver)
    return

def jointchain(mod_name, number, start_obj, end_obj, radius, rotord, orient):
    # oj = orientJoint; sao = secondaryAxisOrient
    if orient == "vertical":
        oj = "yxz"
        sao = "xup"
    elif orient == "horizontal":
        oj = "zxy"
        sao = "zup"
    elif orient == "forward":
        oj = "zyx"
        sao = "yup"
    # define start & end transforms in world space
    start = cmds.xform(start_obj, q = True, translation = True, worldSpace = True)
    end = cmds.xform(end_obj, q = True, translation = True, worldSpace = True)
    # define vector xyz = (end-start) / (joint_nr-1)
    vx = (end[0]-start[0]) / (number-1)
    vy = (end[1]-start[1]) / (number-1)
    vz = (end[2]-start[2]) / (number-1)
    joint_list = []
    # generate joints
    cmds.select(clear = True)
    for i in range(1, number + 1):
        if i == 1:
            pos = start
        else:
            pos = (start[0] + vx,
                   start[1] + vy,
                   start[2] + vz)
        j = cmds.joint(
            n = f"{mod_name}_{i}_JNT", position = pos, 
            radius = radius, rotationOrder = rotord)
        joint_list.append(j)
        start = pos
    # orient joints
    cmds.joint(joint_list[0], e=True, orientJoint = oj, 
            secondaryAxisOrient = sao, children = True, zeroScaleOrient = True)
    # last joint to "world"
    cmds.joint(joint_list[-1], e=True, orientJoint = "none", 
            children = False, zeroScaleOrient = False)
    return joint_list

def twist_setup(mod_name, start, end, driver, twistInvDriver = None):
    """creates 2 joints with single chain IK solver
    return -> group with [twist_jnt, ikh]
    """
    rot_order = cmds.joint(start, q = True, roo = True)
    radius = cmds.joint(start, q = True, radius = True)[0] * 1.25
    start_pos = cmds.xform(start, q = True, rotatePivot = True, worldSpace = True)
    end_pos = cmds.xform(end, q = True, rotatePivot = True, worldSpace = True)
    # make joints
    cmds.select(clear = True)
    twist_joint = cmds.joint(
            n = f"{mod_name}_twist_JNT", position = start_pos, 
            rotationOrder = rot_order, radius = radius)
    # snap to middle
    mid_pc = cmds.pointConstraint(
            (start, end), twist_joint, offset = (0,0,0), weight = 1)
    cmds.delete(mid_pc)
    # twist reversal
    if twistInvDriver:
        twist_tip = start_pos
        driver = twistInvDriver
    else:
        twist_tip = end_pos
    end_joint = cmds.joint(
            n = f"{mod_name}_twist_end_JNT", position = twist_tip, 
            rotationOrder = rot_order, radius = radius)
    # orient joints
    cmds.joint(twist_joint, e = True, orientJoint = "xyz", secondaryAxisOrient = "yup")
    cmds.joint(end_joint, e = True, orientJoint = "none")
    # single chain ik handle
    twist_ikh = cmds.ikHandle(
            twist_joint,
            solver = "ikSCsolver",
            startJoint = twist_joint,
            endEffector = end_joint,
            n = f"{mod_name}_twist_IKH")
    cmds.rename(twist_ikh[1], f"{mod_name}_twist_EFF")
    necktwist_grp = cmds.group(n = f"{mod_name}_twist_GRP", em = True)
    cmds.parent((twist_ikh[0], twist_joint), necktwist_grp)
    util.matrix_connect(driver, twist_ikh[0])
    # cmds.parentConstraint(driver, twist_ikh[0])
    # what do I connect twist_jnt to?? snap in the middle?
    
    return necktwist_grp

def ikspline(mod_name, 
             start, mid, end, 
             forwardaxis, upaxis,
             base_ctrl, mid_ctrl, end_ctrl,
             twistInvDriver = None):
    """
    twistInvDriver only for uparm & thigh -> clavicle & hip
    
    - twist joint & ikh
    - 2 twist locator targets
    - 3 driver joints for 5 curve CVs
    - stretchy setup
    - ikspline with advanced twist controls
    forward axis => tip of chain
    up axis => twist locators
    
    grouped in misc, outside jnt or ctrl hierarchy
    """
    # components outside joint or ctrl hierarchy
    grp = cmds.group(n = f"{mod_name}_ikSpline_GRP", em = True)
    cmds.parent(grp, "misc_GRP")
    
    # create twist joint + ikh and twist locators
    twist_grp = twist_setup(
            mod_name = mod_name,
            start = start,
            end = end,
            driver = end_ctrl,
            twistInvDriver = twistInvDriver)
    cmds.parent(twist_grp, grp)
    twist_jnt = cmds.listRelatives(twist_grp, children = True)[1]
    
    # dictionary to convert str input to int for forw & up axis
    forwx_dict = {"x" : 0, "-x" : 1, "y" : 2, "-y" : 3, "z" : 4, "-z" : 5}
    upx_dict = {
        "y" : 0, "-y" : 1, "close y" : 2, 
        "z" : 3, "-z" : 4, "close z" : 5, 
        "x" : 6, "-x" : 7, "close x" : 8}
    forwx = forwx_dict[forwardaxis]
    upx = upx_dict[upaxis]
    
    # twist locators
    twistloc1 = cmds.spaceLocator(n = f"{mod_name}_baseTwist_LOC")[0]
    twistloc2 = cmds.spaceLocator(n = f"{mod_name}_endTwist_LOC")[0]
    cmds.parent((twistloc1, twistloc2), start, r = True)
    cmds.matchTransform(twistloc2, end, position = True)
    loc_offset = {"x" : "15,0,0", "-x" : "-15,0,0", 
                  "y" : "0,15,0", "-y" : "0,-15,0", 
                  "z" : "0,0,15", "-z" : "0,0,-15"}
    eval(f"cmds.move({loc_offset[upaxis]}, \
        (twistloc1, twistloc2), relative = True, localSpace = True)")
    cmds.parent((twistloc1, twistloc2), twist_grp)
    if twistInvDriver:
        util.matrix_connect(twist_jnt, twistloc1)
        util.matrix_connect(end_ctrl, twistloc2)
    else:
        util.matrix_connect(base_ctrl, twistloc1)
        util.matrix_connect(twist_jnt, twistloc2)
    
    # ikSpline setup
    ikSet = cmds.ikHandle(
            solver = "ikSplineSolver", 
            n = f"{mod_name}_IKS",
            simplifyCurve = True,
            numSpans = 2, 
            startJoint = start, 
            endEffector = end)
    # ikSet = [ikHandle1, effector1, curve1]
    ikh = ikSet[0]
    curve = cmds.rename(ikSet[2], f"{mod_name}_ikSpline_CRV")
    effector = cmds.rename(ikSet[1], f"{mod_name}_ikSpline_EFF")
    cmds.parent((ikh, curve), grp)
    # advanced twist controls
    cmds.setAttr(f"{ikh}.dTwistControlEnable", 1)
    cmds.setAttr(f"{ikh}.dWorldUpType", 2) # object up (start/end)
    cmds.setAttr(f"{ikh}.dForwardAxis", forwx)
    cmds.setAttr(f"{ikh}.dWorldUpAxis", upx)
    cmds.connectAttr(f"{twistloc1}.worldMatrix[0]", f"{ikh}.dWorldUpMatrix")
    cmds.connectAttr(f"{twistloc2}.worldMatrix[0]", f"{ikh}.dWorldUpMatrixEnd")
    # make it stretchy!!
    # normalized = current length / original length
    length = cmds.shadingNode(
        "curveInfo", asUtility = True, n = f"{mod_name}_ikSplineLength_CI")
    norm = cmds.shadingNode(
        "multiplyDivide", asUtility = True, n = f"{mod_name}_ikSplineNormalise_MD")
    cmds.setAttr(f"{norm}.operation", 2) # divide
    cmds.connectAttr(f"{curve}Shape.worldSpace[0]", f"{length}.inputCurve")
    cmds.connectAttr(f"{length}.arcLength", f"{norm}.input1X")
    orig_length = cmds.getAttr(f"{length}.arcLength")
    cmds.setAttr(f"{norm}.input2X", orig_length)
    # determine scale connection based on forw axis
    scale_connect = {0 : "X", 1 : "X", 2 : "Y", 3 : "Y", 4 : "Z", 5 : "Z"}
    axis = "XYZ"
    forwx_scale = scale_connect[forwx]
    sidex_scale = axis.split(forwx_scale)[0]
    joints = cmds.ikHandle(f"{ikh}", q = True, jointList = True)
    for j in joints:
        # stretch by connecting to joint's scale Z
        # global scale not necessary since curve length scales naturally with rig
        cmds.connectAttr(f"{norm}.outputX", f"{j}.scale{forwx_scale}")
        # global scale only for thickness
        cmds.connectAttr(f"{'global_CTRL'}.scaleY", f"{j}.scale{sidex_scale[0]}")
        cmds.connectAttr(f"{'global_CTRL'}.scaleY", f"{j}.scale{sidex_scale[1]}")
    
    
    # blend volume preservation with attr
    # create curve at exact joint locations instead of letting maya auto create it
    # create curve as part of the joint chain script?
    # return empty group node with attributes (thickness, auto-volume, base/mid/end-twists?)
    # then connect ctrl attrs to that
    
    
    # curve driver joints
    joint_list = []
    cmds.select(clear = True)
    for n, obj in enumerate([start, mid, end]):
        driverj = cmds.joint(n = f"{mod_name}_bendy_{n+1}_JNT", radius = 4)
        cmds.matchTransform(driverj, obj, position = True)
        # orientation from first target_obj
        cmds.matchTransform(driverj, start, rotation = True)
        cmds.makeIdentity(driverj, apply = True, t = True, r = True, s = True)
        joint_list.append(driverj)
        cmds.select(clear = True)
    # package joints in grp
    cmds.parent(joint_list, grp)
    influences = joint_list
    influences.append(curve)
    skin = cmds.skinCluster(
            influences, 
            name = f"{mod_name}_ikSpline_SKIN",
            toSelectedBones = True,
            bindMethod = 0,
            skinMethod = 0,
            normalizeWeights = 1,
            maximumInfluences = 1)[0]
    # middle needs to drive 3 center curve cvs
    cmds.skinPercent(skin, f"{curve}.cv[1]", transformValue = (joint_list[1], 1))
    cmds.skinPercent(skin, f"{curve}.cv[2]", transformValue = (joint_list[1], 1))
    cmds.skinPercent(skin, f"{curve}.cv[3]", transformValue = (joint_list[1], 1))
    # constrain driver joints to resp. ctrl
    for n, ctrl in enumerate([base_ctrl, mid_ctrl, end_ctrl]):
        cmds.parentConstraint(ctrl, joint_list[n], mo = True, weight = 1)
        cmds.scaleConstraint(ctrl, joint_list[n], mo = True, weight = 1)

if __name__ == "__main__":
    
    bendysetup(
            mod_name = "testbendy", 
            start_jnt = "L_uparm_JNT", 
            end_jnt = "L_elbow_JNT",
            forwardaxis = "z", 
            upaxis = "-x",
            base_ctrl = "L_uparm_JNT", 
            mid_ctrl = "L_uparm_FK_CTRL", 
            end_ctrl = "L_elbow_JNT",
            twistInvDriver = "L_clavicle_CTRL")
                
    pass