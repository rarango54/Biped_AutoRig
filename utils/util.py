import maya.cmds as cmds
import maya.api.OpenMaya as om2


def matrix_connect(driver, target):
    """connects driver to target"s offsetParentMatrix with offset! """
    # offset could be directly calculated with matrix math 
    # without using a temp node
    cmds.shadingNode("multMatrix", n = "tempMM", asUtility = True)
    cmds.connectAttr(f"{target}.worldMatrix[0]", "tempMM.matrixIn[0]")
    cmds.connectAttr(f"{driver}.worldInverseMatrix[0]", "tempMM.matrixIn[1]")
    offset = cmds.getAttr("tempMM.matrixSum")
    cmds.delete("tempMM")
    # parent
    parent = cmds.listRelatives(target, p=True)[0]
    ending = str(driver).split("_")[-1]
    # connect
    name = str(driver).replace(ending, "driverMatrix_MM")
    dm = cmds.shadingNode("multMatrix", n=name, au=True)
    
    cmds.setAttr(f"{dm}.matrixIn[0]", offset, type="matrix") # offset
    cmds.connectAttr(f"{driver}.worldMatrix[0]", f"{dm}.matrixIn[1]")
    cmds.connectAttr(f"{parent}.worldInverseMatrix[0]", f"{dm}.matrixIn[2]")
    cmds.connectAttr(f"{dm}.matrixSum", f"{target}.offsetParentMatrix")
    cmds.xform(
        target, translation=[0, 0, 0], rotation=[0, 0, 0], scale=[1, 1, 1])

def zero_transforms(nodes):
    """ 
    transfers local matrix to offset parent matrix 
    leaving nodes with zeroed channels
    (maintains jointOrients for joints)
    """
    objects = [nodes] if isinstance(nodes, str) else nodes
    for obj in objects:
        if cmds.nodeType(obj) == "joint":
            # get .matrix from a temp node without rotation
            # since JNTs have 0 rot after orientation
            parent = cmds.listRelatives(obj, parent=True)[0]
            temp_grp = cmds.group(n="temp_GRP", p=parent, em=True)
            cmds.matchTransform(temp_grp, obj, position=True)
            offset = cmds.getAttr(f"{temp_grp}.matrix")
            cmds.setAttr(f"{obj}.offsetParentMatrix", offset, typ="matrix")
            cmds.setAttr(f"{obj}.translate", 0,0,0)
            cmds.delete(temp_grp)
        else:
            # direct matrix muliplication with OpenMaya
            parent = cmds.listRelatives(obj, parent=True)[0]
            invparent_mtx = om2.MMatrix(
                cmds.getAttr(f"{parent}.worldInverseMatrix[0]"))
            objworld_mtx = om2.MMatrix(
                cmds.getAttr(f"{obj}.worldMatrix[0]"))
            offsetparent_mtx = objworld_mtx * invparent_mtx
            cmds.setAttr(
                f"{obj}.offsetParentMatrix", offsetparent_mtx, type="matrix")
            cmds.setAttr(f"{obj}.translate", 0,0,0)
            cmds.setAttr(f"{obj}.rotate", 0,0,0)

def get_distance(obj1, obj2):
    temp = cmds.shadingNode("distanceBetween", asUtility=True, n="tempDist")
    cmds.connectAttr(f"{obj1}.worldMatrix[0]", "tempDist.inMatrix1")
    cmds.connectAttr(f"{obj2}.worldMatrix[0]", "tempDist.inMatrix2")
    distance = cmds.getAttr("tempDist.distance")
    cmds.delete(temp)
    return distance
    
def attr_separator(targets):
    objects = [targets] if isinstance(targets, str) else targets
    for obj in objects:
        cmds.addAttr(
            obj,
            longName = "separator",
            niceName = "____________",
            attributeType = "enum",
            enumName = "____:")
        cmds.setAttr(
            f"{obj}.separator",
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
        name = obj.replace("_CTRL", "_sclInv_JNT")
        rotateOrder = cmds.getAttr(f"{obj}.ro")
        cmds.select(cl=True)
        sclJoint = cmds.joint(n=name)
        cmds.setAttr(f"{sclJoint}.ro", rotateOrder)
        cmds.matchTransform(sclJoint, childCtrl, position = True)
        cmds.matchTransform(sclJoint, obj, rotation = True)
        cmds.parent(sclJoint, obj)
        cmds.parent(childCtrl, sclJoint)
        cmds.connectAttr(f"{obj}.scale", f"{sclJoint}.inverseScale")
        cmds.setAttr(f"{sclJoint}.drawStyle", 2) # 2 = None / Invisible
    
def buffer_grp(target, new_suffix="buffer_GRP"):
    """ creates a buffer group as a parent"""
    suffix = target.split("_")[-1]
    name = target.replace(f"{suffix}", new_suffix)
    parent = cmds.listRelatives(target, parent = True)
    buff_grp = cmds.group(
        n = name, parent = target, empty =True, relative = True)
    cmds.parent(buff_grp, parent)
    cmds.parent(target, buff_grp)
    return buff_grp
    
def connect_transforms(driver, driven, t=True, r=True, s=True):
    if t == True:
        cmds.connectAttr(f"{driver}.translate", f"{driven}.translate")
    if r == True:
        cmds.connectAttr(f"{driver}.rotate", f"{driven}.rotate")
    if s == True:
        cmds.connectAttr(f"{driver}.scale", f"{driven}.scale")




if __name__ == "__main__":
    
    loc = cmds.spaceLocator(n="test_LOC", r=True)[0]
    buffer_grp(loc)

    pass