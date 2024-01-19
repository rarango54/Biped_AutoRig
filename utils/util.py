import maya.cmds as cmds
import maya.api.OpenMaya as om2


def mtx_hook(driver, target, force = False):
    """connect driver to target"s offsetParentMatrix (OPM) with offset!
    target transforms are left at 0
    exception for joints due to joint orient
    don't use on main skeleton!! cannot be baked!!
    """
    # setup
    tparent = cmds.listRelatives(target, parent = True)[0]
    suffix = str(driver).split("_")[-1]
    newname = str(driver).replace(suffix, "driverMtx_MM")
    multmtx = cmds.shadingNode("multMatrix", n = newname, asUtility = True)
    driver_rotInv = None
    # offset = target(world) x driver(worldInv)
    targ_w = om2.MMatrix(cmds.getAttr(f"{target}.worldMatrix[0]"))
    driv_wInv = om2.MMatrix(cmds.getAttr(f"{driver}.worldInverseMatrix[0]"))
    offset = targ_w * driv_wInv
    if cmds.nodeType(target) == "joint":
        # joint orient takes care of rotation
        # -> set rotation in offset matrix to 0 (identity)
        # setElement(row, column, value)
        offset.setElement(0, 0, 1)
        offset.setElement(0, 1, 0)
        offset.setElement(0, 2, 0)
        offset.setElement(1, 0, 0)
        offset.setElement(1, 1, 1)
        offset.setElement(1, 2, 0)
        offset.setElement(2, 0, 0)
        offset.setElement(2, 1, 0)
        offset.setElement(2, 2, 1)
        # driver worldInv
        driver_rotInv = om2.MMatrix(cmds.getAttr(f"{driver}.worldInverseMatrix[0]"))
        # zero translation in matrix
        driver_rotInv.setElement(3, 0, 0)
        driver_rotInv.setElement(3, 1, 0)
        driver_rotInv.setElement(3, 2, 0)
        # OPM = 
        # driver(wInv:rot only) * offset(no rot:jointOri) * driver(w) * tparent(wInv)
        # both offset and d_wInv_rot need to be mirrored into scaleX -1 space
    if driver_rotInv:
        cmds.setAttr(f"{multmtx}.matrixIn[0]", driver_rotInv, type = "matrix")
    
    # connections unrelated to joints:
    # OPM = offset * driver(world) * tparent(worldInv)
    cmds.setAttr(f"{multmtx}.matrixIn[1]", offset, type = "matrix") # offset
    cmds.connectAttr(f"{driver}.worldMatrix[0]", f"{multmtx}.matrixIn[2]")
    cmds.connectAttr(f"{tparent}.worldInverseMatrix[0]", f"{multmtx}.matrixIn[3]")
    cmds.connectAttr(f"{multmtx}.matrixSum", f"{target}.offsetParentMatrix", f = force)
    cmds.xform(target, 
               translation = (0, 0, 0), 
               rotation = (0, 0, 0), 
               scale = (1, 1, 1))

def mtx_zero(nodes, rsidetoo = False):
    """ 
    target needs to be parented somewhere!
    transfers local matrix to offset parent matrix 
    leaving nodes with zeroed channels
    (maintains jointOrients for joints)
    """
    objects = [nodes] if isinstance(nodes, str) else nodes
    if rsidetoo == True:
        r_objects = [x.replace("L_", "R_") for x in objects]
        objects.extend(r_objects)
    for obj in objects:
        if cmds.nodeType(obj) == "joint":
            # get .matrix from a temp node without rotation
            # since JNTs have 0 rot after orientation
            parent = cmds.listRelatives(obj, parent = True)[0]
            temp_grp = cmds.group(n="temp_GRP", parent = parent, empty = True)
            cmds.matchTransform(temp_grp, obj, position = True)
            offset = cmds.getAttr(f"{temp_grp}.matrix")
            cmds.setAttr(f"{obj}.offsetParentMatrix", offset, typ = "matrix")
            cmds.setAttr(f"{obj}.translate", 0,0,0)
            cmds.delete(temp_grp)
        else:
            parent = cmds.listRelatives(obj, parent = True)[0]
            par_wInv = om2.MMatrix(cmds.getAttr(f"{parent}.worldInverseMatrix[0]"))
            obj_w = om2.MMatrix(cmds.getAttr(f"{obj}.worldMatrix[0]"))
            # OPM = object(world) * objparent(worldInv)
            offsetparent_mtx = obj_w * par_wInv
            cmds.setAttr(
                f"{obj}.offsetParentMatrix", offsetparent_mtx, type = "matrix")
            cmds.xform(obj, 
               translation = (0, 0, 0), 
               rotation = (0, 0, 0), 
               scale = (1, 1, 1))

def get_distance(obj1, obj2):
    temp = cmds.shadingNode("distanceBetween", asUtility=True, n="tempDist")
    cmds.connectAttr(f"{obj1}.worldMatrix[0]", "tempDist.inMatrix1")
    cmds.connectAttr(f"{obj2}.worldMatrix[0]", "tempDist.inMatrix2")
    distance = cmds.getAttr("tempDist.distance")
    cmds.delete(temp)
    return distance
    
def distance(obj1, obj2):
    vec1 = om2.MVector(cmds.xform(obj1, q = True, t = True, ws = True))
    vec2 = om2.MVector(cmds.xform(obj2, q = True, t = True, ws = True))
    vec = vec2 - vec1
    dist = om2.MVector.length(vec)
    return abs(dist)
    
def attr_separator(targets, nr = 1, name = None):
    objects = [targets] if isinstance(targets, str) else targets
    if name:
        enum = name + ":"
        nr = name
    else: 
        enum = "____:"
    for obj in objects:
        cmds.addAttr(
            obj,
            longName = f"separator{nr}",
            niceName = "_" * 14,
            attributeType = "enum",
            enumName = enum)
        cmds.setAttr(
            f"{obj}.separator{nr}",
            e = True,
            channelBox = True,
            keyable = False,
            lock = True)

def insert_scaleInvJoint(controls):
    """ add invisible jnt to invert scale into a ctrl chain hierarchy """
    objects = [controls] if isinstance(controls, str) else controls
    for obj in objects:
        childCtrl = cmds.listRelatives(
            obj, children = True, type = "transform")[0]
        suffix = obj.split("_")[-1]
        name = obj.replace(suffix, "_sclInv_JNT")
        rotateOrder = cmds.getAttr(f"{obj}.ro")
        cmds.select(cl=True)
        sclJoint = cmds.joint(obj, n = name)
        cmds.setAttr(f"{sclJoint}.ro", rotateOrder)
        cmds.matchTransform(sclJoint, childCtrl, position = True)
        cmds.matchTransform(sclJoint, obj, rotation = True)
        # cmds.parent(sclJoint, obj)
        cmds.parent(childCtrl, sclJoint)
        cmds.connectAttr(f"{obj}.scale", f"{sclJoint}.inverseScale")
        cmds.setAttr(f"{sclJoint}.drawStyle", 2) # 2 = None ~ Invisible
    
def buffer(target, new_suffix = "buffer_GRP", position = None):
    """ creates a buffer group as a parent"""
    suffix = target.split("_")[-1]
    name = target.replace(suffix, new_suffix)
    parent = cmds.listRelatives(target, parent = True)
    buff_grp = cmds.group(
        n = name, parent = target, empty =True, relative = True)
    if not parent:
        cmds.parent(buff_grp, world = True)
    else:
        cmds.parent(buff_grp, parent)
    if position:
        cmds.matchTransform(buff_grp, position, pos = True, rot = True)
    cmds.parent(target, buff_grp)
    return buff_grp
    
def connect_transforms(driver, driven, t = True, r = True, s = True):
    if t == True:
        cmds.connectAttr(f"{driver}.translate", f"{driven}.translate")
    if r == True:
        cmds.connectAttr(f"{driver}.rotate", f"{driven}.rotate")
    if s == True:
        cmds.connectAttr(f"{driver}.scale", f"{driven}.scale")

def lock(transforms, 
         channels = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"], 
         hide = True, rsidetoo = False):
    objects = [transforms] if isinstance(transforms, str) else transforms
    if rsidetoo == True:
        r_objects = [x.replace("L_", "R_") for x in objects]
        objects.extend(r_objects)
    for obj in objects:
        for channel in channels:
            cmds.setAttr(f"{obj}.{channel}", lock = True, keyable = False)
            if hide == True:
                cmds.setAttr(f"{obj}.{channel}", channelBox = False)
    
def remap(name, inputattr, min, max, outmin = 0, outmax = 1, exp = False):
    rmpv = cmds.shadingNode("remapValue", n = name, au = True)
    cmds.connectAttr(inputattr, f"{rmpv}.inputValue")
    cmds.setAttr(rmpv+".inputMin", min)
    cmds.setAttr(rmpv+".inputMax", max)
    cmds.setAttr(rmpv+".outputMin", outmin)
    cmds.setAttr(rmpv+".outputMax", outmax)
    if exp == True:
        cmds.setAttr(rmpv+".value[0].value_Interp", 3)
        cmds.setAttr(rmpv+".value[1].value_Interp", 3)
        cmds.setAttr(rmpv+".value[2].value_FloatValue", 0.075)
        cmds.setAttr(rmpv+".value[2].value_Position", 0.3)
        cmds.setAttr(rmpv+".value[2].value_Interp", 3)
        cmds.setAttr(rmpv+".value[3].value_FloatValue", 0.25)
        cmds.setAttr(rmpv+".value[3].value_Position", 0.6)
        cmds.setAttr(rmpv+".value[3].value_Interp", 3)
        cmds.setAttr(rmpv+".value[4].value_FloatValue", 0.6)
        cmds.setAttr(rmpv+".value[4].value_Position", 0.85)
        cmds.setAttr(rmpv+".value[4].value_Interp", 1)
    return rmpv

def pointcurve(name, nodes, degree = 1):
    objects = [nodes] if isinstance(nodes, str) else nodes
    positions = []
    args = {}
    for n, obj in enumerate(objects):
        pos = cmds.xform(obj, q = True, t = True, worldSpace = True)
        positions.append(pos)
        # args[f"p{n}"] = pos
    curve = eval(
        f"cmds.curve(n = name, degree = degree, p = {positions})")
    shape = cmds.rename(
                cmds.listRelatives(curve, children = True, shapes = True),
                curve+"Shape")
    return curve


if __name__ == "__main__":
    
    loc = cmds.spaceLocator(n="test_LOC", r=True)[0]
    buffer_grp(loc)

    pass