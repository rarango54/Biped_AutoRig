import maya.cmds as cmds
import maya.api.OpenMaya as om2

def ikspline(module, 
             start, mid, end, 
             twist_jnt,
             forwardaxis, upaxis,
             base_ctrl, mid_ctrl, end_ctrl,
             twistInvDriver = None):
    """with advanced twist controls, twist targets need to exist already
    forward axis points towards tip of chain
    => { x:0, -x:1, y:2, -y:3, z:4, -z:5 }
    up axis points towards twist locator targets
    => { y:0, -y:1, close y:2, z:3, -z:4, close z:5, x:6, -x:7, close x:8 }
    
    creates 3 driver joints for 5 curve CVs
    """
    # components outside joint or ctrl hierarchy
    grp = cmds.group(n = f"{module}_ikSpline_GRP", em = True)
    cmds.parent(grp, "misc_GRP")
    # dictionary to convert str input to int for forw & up axis
    forwx_dict = {"x" : 0, "-x" : 1, "y" : 2, "-y" : 3, "z" : 4, "-z" : 5}
    upx_dict = {
        "y" : 0, "-y" : 1, "close y" : 2, 
        "z" : 3, "-z" : 4, "close z" : 5, 
        "x" : 6, "-x" : 7, "close x" : 8}
    forwx = forwx_dict[forwardaxis]
    upx = upx_dict[upaxis]
    # twist locators
    twistloc1 = cmds.spaceLocator(n = f"{module}_baseTwist_LOC")[0]
    twistloc2 = cmds.spaceLocator(n = f"{module}_endTwist_LOC")[0]
    cmds.parent([twistloc1, twistloc2], start, r = True)
    cmds.matchTransform(twistloc2, end, position = True)
    loc_offset = {"x" : "15,0,0", "-x" : "-15,0,0", 
               "y" : "0,15,0", "-y" : "0,-15,0", 
               "z" : "0,0,15", "-z" : "0,0,-15"}
    eval(f"cmds.move({loc_offset[upaxis]}, \
        (twistloc1, twistloc2), relative = True, localSpace = True)")
    # replace with constraints later and add to grp instead (scl constraint necessary?)
    if twistInvDriver:
        cmds.parent(twistloc1, twist_jnt)
        cmds.parent(twistloc2, end_ctrl)
    else:
        cmds.parent(twistloc1, base_ctrl)
        cmds.parent(twistloc2, twist_jnt)
    # ikSpline setup
    ikSet = cmds.ikHandle(
            solver = "ikSplineSolver", 
            n = f"{module}_IKS",
            simplifyCurve = True,
            numSpans = 2, 
            startJoint = start, 
            endEffector = end)
    # ikSet = [ikHandle1, effector1, curve1]
    ikh = ikSet[0]
    curve = cmds.rename(ikSet[2], f"{module}_ikSpline_CRV")
    effector = cmds.rename(ikSet[1], f"{module}_ikSpline_EFF")
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
        "curveInfo", asUtility = True, n = f"{module}_ikSplineLength_CI")
    norm = cmds.shadingNode(
        "multiplyDivide", asUtility = True, n = f"{module}_ikSplineNormalise_MD")
    cmds.setAttr(f"{norm}.operation", 2) # divide
    cmds.connectAttr(f"{curve}Shape.worldSpace[0]", f"{length}.inputCurve")
    cmds.connectAttr(f"{length}.arcLength", f"{norm}.input1X")
    orig_length = cmds.getAttr(f"{length}.arcLength")
    cmds.setAttr(f"{norm}.input2X", orig_length)
    # determine scale connection based on forw axis
    scale_connect = {0 : "X", 1 : "X", 2 : "Y", 3 : "Y", 4 : "Z", 5 : "Z"}
    axis = "XYZ"
    forwx_scale = scale_connect[forwx]
    sidex_scale = axis.split(forwx_scale)
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
    # then connect ctrls in there
    
    
    # curve driver joints
    joint_list = []
    cmds.select(clear = True)
    for n, obj in enumerate([start, mid, end]):
        driverj = cmds.joint(n = f"{module}_bendy_{n+1}_JNT", radius = 6)
        cmds.matchTransform(driverj, obj, position = True)
        # always take orientation from first target_obj
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
            name = f"{module}_ikSpline_SKIN",
            toSelectedBones = True,
            bindMethod = 0,
            skinMethod = 0,
            normalizeWeights = 1,
            maximumInfluences = 1)[0]
    # middle needs to drive 3 center curve cvs
    cmds.skinPercent(skin, f"{curve}.cv[1]", transformValue = (joint_list[1], 1))
    cmds.skinPercent(skin, f"{curve}.cv[3]", transformValue = (joint_list[1], 1))
    # constrain driver joints to resp. ctrl
    for n, ctrl in enumerate([base_ctrl, mid_ctrl, end_ctrl]):
        cmds.parentConstraint(ctrl, joint_list[n], mo = True, weight = 1)
        cmds.scaleConstraint(ctrl, joint_list[n], mo = True, weight = 1)


# might be redundant, maybe keep in util?
# def globalscale(module):
#     """return MD node with global scale on input 2"""
#     global_scale = cmds.shadingNode(
#         "multiplyDivide", asUtility = True, n = f"{module}_globalScale_MD")
#     cmds.connectAttr(f"{'global_CTRL'}.scaleY", f"{global_scale}.input2X")
#     cmds.connectAttr(f"{'global_CTRL'}.scaleY", f"{global_scale}.input2Y")
#     cmds.connectAttr(f"{'global_CTRL'}.scaleY", f"{global_scale}.input2Z")
#     return global_scale

if __name__ == "__main__":
    
    sel = cmds.ls(sl = True)
    
    jnts = ikspline(
        module = "neck", 
        start = "neck_1_JNT", 
        mid = "neckmid_CTRL", 
        end = "head_JNT", 
        twist_jnt = "neck_twist_JNT",
        forwardaxis = "y", 
        upaxis = "-z",
        base_ctrl = "neck_sub_CTRL", 
        mid_ctrl = "neckmid_CTRL", 
        end_ctrl = "head_sub_CTRL")
    pass