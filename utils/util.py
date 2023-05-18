import maya.cmds as cmds



def matrix_connect(driver, target):
    """ connects driver to target's offsetParentMatrix with offset! """
    # offset
    cmds.shadingNode('multMatrix', n='tempMM', au=True)
    cmds.connectAttr(f'{target}.worldMatrix[0]', 'tempMM.matrixIn[0]')
    cmds.connectAttr(f'{driver}.worldInverseMatrix[0]', 'tempMM.matrixIn[1]')
    offset = cmds.getAttr('tempMM.matrixSum')
    cmds.delete('tempMM')
    # parent
    parent = cmds.listRelatives(target, p=True)[0]
    ending = str(driver).split("_")[-1]
    # connect
    name = str(driver).replace(ending, 'driverMatrix_MM')
    dm = cmds.shadingNode('multMatrix', n=name, au=True)
    
    cmds.setAttr(f'{dm}.matrixIn[0]', offset, type='matrix') # offset
    cmds.connectAttr(f'{driver}.worldMatrix[0]', f'{dm}.matrixIn[1]')
    cmds.connectAttr(f'{parent}.worldInverseMatrix[0]', f'{dm}.matrixIn[2]')
    cmds.connectAttr(f'{dm}.matrixSum', f'{target}.offsetParentMatrix')
    cmds.xform(target, translation=[0, 0, 0], rotation=[0, 0, 0], scale=[1, 1, 1])

def zero_transforms(objects, t=True, r=True, s=True):
    """ transfers matrix to offset parent matrix -> objects end up with zeroed channels
    for joints it keeps jointOrients intact"""
    if type(objects) is str: # in case only one object is selected to make the loop work with a list
        targets = [objects]
    else:
        targets = objects
        
    for i in targets:
        if cmds.nodeType(i) == 'joint':
            # get .matrix from a temp object without rot, all JNTs have 0 rot after orientation
            parent = cmds.listRelatives(i, p=True)[0]
            cmds.group(n='temp_GRP', p=parent, em=True) # matching parent's orientation
            cmds.matchTransform('temp_GRP', i, pos=True)
            offset = cmds.getAttr('temp_GRP.matrix')
            cmds.setAttr(i+'.offsetParentMatrix', offset, typ='matrix')
            cmds.xform(i, t=[0,0,0])
            cmds.delete('temp_GRP')
        else:
            # temp multMatrix to recalculate matrix
            tempMM = cmds.shadingNode('multMatrix', n='temp_MM', au=True)
            parent = cmds.listRelatives(i, p=True)[0]
            cmds.connectAttr(i+'.worldMatrix[0]', tempMM+'.matrixIn[0]')
            cmds.connectAttr(parent+'.worldInverseMatrix[0]', tempMM+'.matrixIn[1]')
            # temp pickMatrix with options based on keyword flags
            tempPM = cmds.createNode('pickMatrix', n='temp_PM')
            cmds.connectAttr(tempMM+'.matrixSum', tempPM+'.inputMatrix')
            cmds.setAttr(tempPM+'.useTranslate', t)
            cmds.setAttr(tempPM+'.useRotate', r)
            cmds.setAttr(tempPM+'.useScale', s)
            # get offsetParent Matrix
            trans = cmds.getAttr(tempPM+'.outputMatrix')
            # delete temp nodes
            cmds.delete(tempMM, tempPM)
            # Set the offset parent matrix to the transform attributes
            cmds.setAttr(f"{i}.offsetParentMatrix", trans, type="matrix")
            # Zero out the transform attributes
            if t == True:
                cmds.xform(i, translation = [0, 0, 0])
            if r == True:
                cmds.xform(i, rotation = [0, 0, 0])
            if s == True:
                cmds.xform(i, scale = [1, 1, 1])

def get_distance(object1, object2):
    cmds.shadingNode('distanceBetween', au=True, n='tempDist')
    
    cmds.connectAttr(f'{object1}.worldMatrix[0]', 'tempDist.inMatrix1')
    cmds.connectAttr(f'{object2}.worldMatrix[0]', 'tempDist.inMatrix2')
    
    distance = cmds.getAttr('tempDist.distance')
    cmds.delete('tempDist')
    
    return distance
    
def attr_separator(target):
    cmds.addAttr(target,ln='separator',nn='____________',at='enum',en='____:')
    cmds.setAttr(f'{target}.separator',e=True,cb=True,k=False,l=True)
    

def insert_scaleInvJoint(controls):
    """ inserts invisible jnt to invert scale into a ctrl chain hierarchy """
    if type(controls) is str: # in case only one object is selected to make the loop work with a list
        targets = [controls]
    else:
        targets = controls
    for target in targets:
        if target[-4:] != 'CTRL':
            raise RuntimeError(f'{target} is not a ctrl - scale inverse joints can only be added to ctrl chains ')
        
        childCtrl = cmds.listRelatives(target, c=True, typ='transform')[0]
        name = target.replace('_CTRL', '_sclInv_JNT')
        rotateOrder = cmds.getAttr(f'{target}.ro')
        
        cmds.select(cl=True)
        sclJoint = cmds.joint(n=name)
        cmds.setAttr(f'{sclJoint}.ro', rotateOrder)
        
        cmds.matchTransform(sclJoint, childCtrl, pos=True)
        cmds.matchTransform(sclJoint, target, rot=True)
        cmds.parent(sclJoint, target)
        cmds.parent(childCtrl, sclJoint)
        cmds.connectAttr(f'{target}.scale', f'{sclJoint}.inverseScale')
        cmds.setAttr(f'{sclJoint}.drawStyle', 2) # 2 = None
    
def buffer_grp(target, prefix='buffer_GRP'):
    """ creates a buffer group on top of all the target transforms """
    suffix = target.split('_')[-1]
    name = target.replace(f'{suffix}', prefix)
    parent = cmds.listRelatives(target, p=True)
    
    buff_grp = cmds.group(n=name, p=target, em=True, r=True)
    cmds.parent(buff_grp, parent)
    cmds.parent(target, buff_grp)
    return buff_grp



if __name__ == "__main__":
    
    loc = cmds.spaceLocator(n='test', r=True)[0]
    cmds.xform(loc, t=[0,1,0])

    pass