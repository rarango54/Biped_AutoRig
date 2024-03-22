import maya.cmds as cmds
import maya.api.OpenMaya as om2

from utils import util
from utils.ctrl_library import Nurbs

def setup(mod_name, 
          base_driver, head_driver,
          forwardaxis, upaxis,
          mid_ctrl,
          twistInvDriver = None,
          elbow_bendy_ctrl = None,
          offset_driver = None):
    """
    creates 5 jnt bendy chain betw. base & head drivers
        forward axis => tip of chain
        up axis => twist locators
        twistInvDriver only for uparm & thigh -> clavicle & hip ctrls
    - twist joint & ikh
    - 2 twist locator targets
    - 3 driver joints for 5 curve CVs
    - stretchy setup
    - ikspline with advanced twist controls
    
    main jnts under base_driver (make sure it's part of the main skeleton)
    rest of components hidden -> grouped in misc, outside jnt or ctrl hierarchy
    """
    # jointchain
    if cmds.objectType(base_driver, isType = "joint"):
        orig = base_driver
    else:
        orig = head_driver
    radius = cmds.joint(orig, q = True, radius = True)[0] * 1.5
    rotord = cmds.joint(orig, q = True, roo = True)
    ### probs a better way to determine orientation...
    oridict = {"x" : "horizontal", "-x" : "horizontal",
               "y" : "vertical", "-y" : "vertical",
               "z" : "horizontal", "-z" : "horizontal"}
    bendy_joints = jointchain(
            mod_name = mod_name,
            number = 5,
            start_obj = base_driver,
            end_obj = head_driver,
            radius = radius,
            rotord = rotord,
            orient = oridict[forwardaxis])
    cmds.sets(bendy_joints[:-1], add = "bind_joints")
    cmds.sets(bendy_joints, add = "joints")
    cmds.parent(bendy_joints[0], base_driver)
    
    curve = crv(mod_name+"_ikSpline_CRV", bendy_joints, 3)
    
    ikspline(
            mod_name = mod_name, 
            start_jnt = bendy_joints[0],  
            end_jnt = bendy_joints[-1], 
            forwardaxis = forwardaxis, 
            upaxis = upaxis,
            base_driver = base_driver, 
            head_driver = head_driver,
            mid_ctrl = mid_ctrl,
            curve = curve, 
            twistInvDriver = twistInvDriver,
            elbow_bendy_ctrl = elbow_bendy_ctrl,
            offset_driver = offset_driver)
    # middle needs to drive 3 center curve cvs
    skin = f"{mod_name}_ikSpline_SKIN"
    cmds.skinPercent(skin, f"{curve}.cv[1]", 
                     transformValue = (f"{mod_name}_bendy_2_JNT", 1))
    cmds.skinPercent(skin, f"{curve}.cv[2]", 
                     transformValue = (f"{mod_name}_bendy_2_JNT", 1))
    cmds.skinPercent(skin, f"{curve}.cv[3]", 
                     transformValue = (f"{mod_name}_bendy_2_JNT", 1))
    return bendy_joints

def jointchain(mod_name, number, start_obj, end_obj, radius, rotord, orient):
    """return -> joint_list    # parent to child"""
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
    jcstart = cmds.xform(start_obj, q = True, translation = True, worldSpace = True)
    jcend = cmds.xform(end_obj, q = True, translation = True, worldSpace = True)
    # define vector xyz = (end - start) / (jnt_nr - 1)
    vx = (jcend[0] - jcstart[0]) / (number - 1)
    vy = (jcend[1] - jcstart[1]) / (number - 1)
    vz = (jcend[2] - jcstart[2]) / (number - 1)
    joint_list = []
    # generate joints
    cmds.select(clear = True)
    for i in range(1, number + 1):
        if i == 1:
            pos = jcstart
        else:
            pos = (jcstart[0] + vx,
                   jcstart[1] + vy,
                   jcstart[2] + vz)
        j = cmds.joint(
            n = f"{mod_name}_{i}_JNT", position = pos, 
            radius = radius, rotationOrder = rotord)
        joint_list.append(j)
        jcstart = pos
    # orient joints
    cmds.joint(joint_list[0], e = True, orientJoint = oj, 
            secondaryAxisOrient = sao, children = True, zeroScaleOrient = True)
    # orient last joint to "world"
    cmds.joint(joint_list[-1], e = True, orientJoint = "none", 
            children = False, zeroScaleOrient = False)
    return joint_list

def twist_setup(mod_name, 
                start_jnt, end_jnt, 
                base_driver, head_driver, 
                twistInvDriver = None):
    """creates 2 joints with single chain IK solver
    twistInvDriver replaces head_driver
    return -> group with [twist_jnt, ikh] in misc, outside jnt or ctrl hierarchy
    """
    rotord = cmds.joint(start_jnt, q = True, roo = True)
    radius = cmds.joint(start_jnt, q = True, radius = True)[0] * 3
    start_pos = cmds.xform(start_jnt, q = True, rotatePivot = True, worldSpace = True)
    end_pos = cmds.xform(end_jnt, q = True, rotatePivot = True, worldSpace = True)
    # make main twist joint
    cmds.select(clear = True)
    twist_joint = cmds.joint(
            n = f"{mod_name}_twist_JNT", position = start_pos, 
            rotationOrder = rotord, radius = radius)
    # snap to middle
    mid_pointc = cmds.pointConstraint(
            (start_jnt, end_jnt), twist_joint, offset = (0,0,0), weight = 0.5)
    cmds.delete(mid_pointc)
    # match orientation to first joint in chain
    cmds.matchTransform(twist_joint, start_jnt, rotation = True)
    cmds.makeIdentity(twist_joint, apply = True, rotate = True)
    # pointConstraint drivers:
    pcdrivers = [head_driver, base_driver]
    # twist reversal condition
    if twistInvDriver:
        twist_tip = start_pos
        head_driver = twistInvDriver
    else:
        twist_tip = end_pos
    # end joint
    twist_end_jnt = cmds.joint(
            n = f"{mod_name}_twist_end_JNT", position = twist_tip, 
            rotationOrder = rotord, radius = radius/6)
    cmds.setAttr(f"{twist_end_jnt}.r", 0,0,0)
    # single chain ik handle
    twist_ikh = cmds.ikHandle(
            twist_joint,
            solver = "ikSCsolver",
            startJoint = twist_joint,
            endEffector = twist_end_jnt,
            n = f"{mod_name}_twist_IKH")
    cmds.rename(twist_ikh[1], f"{mod_name}_twist_EFF")
    twist_grp = cmds.group(n = f"{mod_name}_twist_GRP", em = True)
    cmds.parent((twist_ikh[0], twist_joint), twist_grp)
    # connect to rig
    util.mtx_hook(head_driver, twist_ikh[0])
    # twist_jnt orient driven by IKH, scaleConstr causes double transform
    # mtx_hook not compatible with Rumba
    cmds.pointConstraint(pcdrivers, twist_joint, offset = (0,0,0), weight = 1)
    cmds.connectAttr(base_driver+".s", twist_joint+".s")
    return twist_grp

def ikspline(mod_name, 
             start_jnt, end_jnt, 
             forwardaxis, upaxis,
             base_driver, head_driver,
             mid_ctrl,
             curve,
             twistInvDriver = None,
             elbow_bendy_ctrl = None,
             offset_driver = None):
    """
    start & end jnts from bendy joint chain
    base & head drivers can be either ctrls or jnts driving the twist
        forward axis => tip of chain
        up axis => twist locators
        twistInvDriver only for uparm & thigh -> clavicle & hip ctrls
    - twist joint & ikh
    - 2 twist locator targets
    - 3 driver joints for 5 curve CVs
    - stretchy setup
    - ikspline with advanced twist controls
    
    components hidden -> grouped in misc, outside jnt or ctrl hierarchy
    """
    # components outside joint or ctrl hierarchy
    grp = cmds.group(n = f"{mod_name}_ikSpline_GRP", em = True)
    if cmds.objExists("misc_GRP"):
        cmds.parent(grp, "misc_GRP")
    else:
        cmds.parent(grp, "fmisc_GRP")
        
    
    # create twist joint + ikh
    twist_grp = twist_setup(
            mod_name = mod_name,
            start_jnt = start_jnt,
            end_jnt = end_jnt,
            base_driver = base_driver,
            head_driver = head_driver,
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
    cmds.parent((twistloc1, twistloc2), start_jnt, r = True)
    cmds.matchTransform(twistloc2, end_jnt, position = True)
    loc_offset = {"x" : "30,0,0", "-x" : "-30,0,0", 
                  "y" : "0,30,0", "-y" : "0,-30,0", 
                  "z" : "0,0,30", "-z" : "0,0,-30"}
    eval(f"cmds.move({loc_offset[upaxis]}, \
        (twistloc1, twistloc2), relative = True, localSpace = True)")
    cmds.parent((twistloc1, twistloc2), twist_grp)
    # A) if reverse twisting (uparm & upleg) -> reverse parenting
    # B) if elbow_bendy -> parent middle twistLocs to it (avoids flipping)
    if twistInvDriver: # A)
        util.mtx_hook(twist_jnt, twistloc1)
        if elbow_bendy_ctrl: # B) end twist
            util.mtx_hook(elbow_bendy_ctrl, twistloc2)
        else:
            util.mtx_hook(base_driver, twistloc2)
    else:
        util.mtx_hook(twist_jnt, twistloc2)
        if offset_driver:
            util.mtx_hook(offset_driver, twistloc1)
        elif elbow_bendy_ctrl: # B) start twist
            util.mtx_hook(elbow_bendy_ctrl, twistloc1)
        else:
            util.mtx_hook(base_driver, twistloc1)
    
    # ikSpline setup
    ikSet = cmds.ikHandle(
            solver = "ikSplineSolver", 
            n = f"{mod_name}_IKS",
            simplifyCurve = False,
            numSpans = 2, 
            startJoint = start_jnt, 
            endEffector = end_jnt,
            createCurve = False,
            curve = curve,
            parentCurve = False)
# ikSet = [ikHandle1, effector1, curve1]
    ikh = ikSet[0]
# curve = cmds.rename(ikSet[2], f"{mod_name}_ikSpline_CRV")
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
        "multiplyDivide", asUtility = True, n = f"{mod_name}_ikSpline_NORM")
    cmds.setAttr(f"{norm}.operation", 2) # divide
    cmds.connectAttr(f"{curve}Shape.worldSpace[0]", f"{length}.inputCurve")
    cmds.connectAttr(f"{length}.arcLength", f"{norm}.input1X")
    orig_length = cmds.getAttr(f"{length}.arcLength")
    cmds.setAttr(f"{norm}.input2X", orig_length)
    # determine scale connection based on forw axis
    scale_connect = {0 : "X", 1 : "X", 2 : "Y", 3 : "Y", 4 : "Z", 5 : "Z"}
    scalex = ["X", "Y", "Z"]
    forwx_scale = scale_connect[forwx]
    scalex.remove(forwx_scale)
    joints = cmds.ikHandle(f"{ikh}", q = True, jointList = True)
    for j in joints:
        # stretch by connecting to joint's scale Z
        # global scale not necessary since curve length scales naturally with rig
        cmds.connectAttr(f"{norm}.outputX", f"{j}.scale{forwx_scale}")
        # global scale only for thickness
        cmds.connectAttr(f"{'global_CTRL'}.scaleY", f"{j}.scale{scalex[0]}")
        cmds.connectAttr(f"{'global_CTRL'}.scaleY", f"{j}.scale{scalex[1]}")
    
    # 3 curve driver joints
    joint_list = []
    cmds.select(clear = True)
    rad = cmds.getAttr(start_jnt+".radius")*1.5
    for n, obj in enumerate([start_jnt, mid_ctrl, end_jnt]):
        driverj = cmds.joint(n = f"{mod_name}_bendy_{n+1}_JNT", radius = rad)
        cmds.matchTransform(driverj, obj, position = True)
        # orientation from first target_obj
        cmds.matchTransform(driverj, base_driver, rotation = True)
        cmds.makeIdentity(driverj, apply = True, rotate = True)
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
    # reassign head/base driver for flipped twisting scenarios
    if elbow_bendy_ctrl and twistInvDriver:
        head_driver = elbow_bendy_ctrl
    if elbow_bendy_ctrl and twistInvDriver == None:
        base_driver = elbow_bendy_ctrl
    if offset_driver and twistInvDriver == None:
        base_driver = offset_driver
    # connect driver joints to resp. ctrl
    for n, ctrl in enumerate([base_driver, mid_ctrl, head_driver]):
        cmds.parentConstraint(ctrl, joint_list[n], mo = True, weight = 1)
        cmds.scaleConstraint(ctrl, joint_list[n], mo = True, weight = 1)
        # cmds.connectAttr(ctrl+".s", joint_list[n]+".s")
    
    ###### missing:
        # base/mid/end-twists ?
    
def aim(bendy, aimtarget, uptarget, root, vaim, vup, scldriver = None):
    """scldriver only for reverse aiming (lowarm & lowleg)
    makes a buffer group and stretchy behaviour between 2 targets"""
    suffix = bendy.split("_")[-1]
    name = bendy.replace("_"+suffix, "")
    bendy_buff = util.buffer(bendy)
    util.mtx_zero([bendy_buff, bendy])
    cmds.pointConstraint(
            [root, aimtarget], bendy_buff,
            n = f"{name}_POINT", offset = (0,0,0), weight = 0.5)
    cmds.aimConstraint(
            aimtarget, bendy_buff, 
            n = f"{name}_AIM", aimVector = vaim, upVector = vup,
            worldUpObject = uptarget, worldUpType = 1)
    # stretching setup
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
    # scale axes based on vaim
    # last element in axis list is for the stretch axis, others for thickness
    if vaim in ((0,0,1), (0,0,-1)):
        axis = ["sx","sy", "input1X","input1Y", "input1Z"]
    elif vaim in ((0,1,0), (0,-1,0)):
        axis = ["sx","sz", "input1X","input1Z", "input1Y"]
    elif vaim in ((1,0,0), (-1,0,0)):
        axis = ["sy","sz", "input1Y","input1Z", "input1X"]
    # hook it up
    cmds.connectAttr(f"{norm}.outputX", f"{glob}.{axis[-1]}")
    if scldriver:
        cmds.connectAttr(f"{scldriver}.{axis[0]}", f"{glob}.{axis[2]}")
        cmds.connectAttr(f"{scldriver}.{axis[1]}", f"{glob}.{axis[3]}")
    else:
        cmds.connectAttr(f"{root}.{axis[0]}", f"{glob}.{axis[2]}")
        cmds.connectAttr(f"{root}.{axis[1]}", f"{glob}.{axis[3]}")
    cmds.connectAttr("global_CTRL.scale", f"{glob}.input2")
    cmds.connectAttr(f"{glob}.output", f"{bendy_buff}.scale")

def crv(name, points, degree):
    coords = []
    for p in points:
        pos = cmds.xform(p, q = True, translation = True, worldSpace = True)
        coords.append(pos)
    curve = cmds.curve(n = name, d = degree, point = coords)
    shape = cmds.listRelatives(curve, children = True, shapes = True)[0]
    cmds.rename(shape, name + "Shape")
    return curve
                  
def weightedscl(weight, input_attr, target):
    """weighted = (scale - 1) * weight (+ 1)
    creates 2 nodes for formula - add & mult
    the (+ 1) comes after all the weighted scales have been chained up
    target just for naming
    return: addDoubleLinear.output attr"""
    inname = input_attr.replace(".", "_") # e.g. mid_sx
    targsuff = target.split("-")[-1]
    targname = target.replace("_"+targsuff, "") # e.g. L_uparm_2
    name = inname + "_" + targname # e.g. mid_sx_L_uparm_2
    # nodes
    minus = cmds.shadingNode("addDoubleLinear", n = name+"_MINUS", au = True)
    cmds.setAttr(minus+".input2", -1)
    mult = cmds.shadingNode("multDoubleLinear", n = name+"_MULT", au = True)
    cmds.setAttr(mult+".input2", weight)
    # connections
    cmds.connectAttr(input_attr, minus+".input1")
    cmds.connectAttr(minus+".output", mult+".input1")
    return mult+".output"

def thickness(target_joint, attr_node, ctrl_weight_dict, channels):
    """attr_node is a transform with 1 attr per influence range
    attributes need to match dict and channels
    e.g. ctrl_weight dict = {
        "start" : 0.75,
        "mid" : 0.6,
        "end" : 0.25,
        "elbow" : 0.1}
    """
    for scl in channels: # e.g. [sx, sy]
        ctrls = list(ctrl_weight_dict)
        multchain = len(ctrls)
        for nr, ctrl in enumerate(ctrls):
            side = attr_node.split("_")[0]
            attr = attr_node+"."+ctrl+"_"+scl # e.g. L_uparm_thick_GRP.start_sx
            name = side + attr_node.split("_")[1] + "_thick_" + ctrl +"_"+scl 
                # e.g. L_uparm_thick_start_sx
            weight = ctrl_weight_dict[ctrl]
### a way to ignore channels with weight 0
            sclinfl = weightedscl(weight, attr, target_joint)
            if nr == 0: # skip first one
                previous = sclinfl
            if nr > 0: # chain weighted scales to eachother
                addname = attr.replace(".", "_") + f"_PLUS{nr}"
                add = cmds.shadingNode("addDoubleLinear", n = addname, au = True)
                cmds.connectAttr(previous, add+".input1")
                cmds.connectAttr(sclinfl, add+".input2")
                previous = add+".output"
            if nr == len(ctrls) - 1: # last (+ 1) (* globScl) then plug into joint
                plusname = attr.replace(".", "_") + "_end_PLUS"
                plus = cmds.shadingNode("addDoubleLinear", n = plusname, au = True)
                cmds.setAttr(plus+".input2", 1)
                cmds.connectAttr(previous, plus+".input1")
                # global scale
                globname = name+"_globalScl_MULT"
                glob = cmds.shadingNode("multDoubleLinear", n = globname, au = True)
                cmds.connectAttr(plus+".output", glob+".input1")
                cmds.connectAttr("global_CTRL.sy", glob+".input2")
                cmds.connectAttr(glob+".output", target_joint+"."+scl, force = True)

def chainthick(name, channels, joints):
    """only for bendy chain of 5 joints!!
    create thick_node with 1 attr per range + channel
    then connect the channels into joint scales
    return thick_node to plug in relevant ctrls with ikfk blending, mixing etc
    """
    thick_node = cmds.group(n = name, em = True)
    util.lock(thick_node, vis = True)
    for infl in ["start", "mid", "end"]:
        for scl in channels:
            cmds.addAttr(thick_node, longName = f"{infl}_{scl}", at = "double", dv = 1)
            cmds.setAttr(f"{thick_node}.{infl}_{scl}", e = True, keyable = True)
    # presets for standard bendy chain
    # important!! start and end need to add up to 1 for each (for global scl to work)
    joint1_w = {
        "start" : 1,
        "mid" : 0.1,
        "end" : 0}
    joint2_w = {
        "start" : 0.75,
        "mid" : 0.75,
        "end" : 0.25}
    joint3_w = {
        "start" : 0.5,
        "mid" : 1,
        "end" : 0.5}
    joint4_w = {
        "start" : 0.25,
        "mid" : 0.57,
        "end" : 0.75}
    joint5_w = {
        "start" : 0,
        "mid" : 0.1,
        "end" : 1}
    for nr, joint in enumerate(joints):
        eval(f"thickness(joint, thick_node, joint{nr+1}_w, channels)")
    
    return thick_node

if __name__ == "__main__":
    
    jointchain("test", 5, "L_polevector_PRX", "R_armIK_PV_CTRL", 5, "xyz", "horizontal")
    
    # bendysetup(
    #         mod_name = "R_upArm", 
    #         base_driver = "R_uparm_JNT", 
    #         head_driver = "R_elbow_JNT",
    #         forwardaxis = "z", 
    #         upaxis = "-x",
    #         mid_ctrl = "R_uparm_FK_CTRL", 
    #         twistInvDriver = "R_clavicle_JNT")
    # bendysetup(
    #         mod_name = "L_upArm", 
    #         base_driver = "L_uparm_JNT", 
    #         head_driver = "L_elbow_JNT",
    #         forwardaxis = "z", 
    #         upaxis = "-x",
    #         mid_ctrl = "L_uparm_FK_CTRL", 
    #         twistInvDriver = "L_clavicle_JNT")
                
    pass