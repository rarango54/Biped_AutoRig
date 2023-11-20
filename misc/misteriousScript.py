def matrix_connect(driver, target):
    """connect driver to target"s offsetParentMatrix with offset!
    target transforms are left at 0
    exception for joints due to joint orient
    don't use on main skeleton!! cannot be baked!!
    """
    # setup
    tparent = cmds.listRelatives(target, parent = True)[0]
    suffix = str(driver).split("_")[-1]
    newname = str(driver).replace(suffix, "driverMatrix_MM")
    multmtx = cmds.shadingNode("multMatrix", n = newname, asUtility = True)
    driver_wInv_rot = None
    # offset = target(world) x driver(worldInv)
    targ_w = om2.MMatrix(cmds.getAttr(f"{target}.worldMatrix[0]"))
    driv_wInv = om2.MMatrix(cmds.getAttr(f"{driver}.worldInverseMatrix[0]"))
    offset = targ_w * driv_wInv
    if cmds.nodeType(target) == "joint":
        # joint orient takes care of rotation
        # -> set rotation in offset mtx to 0 (identity)
        side = str(driver).split("_")[0] # prefix (L_ or R_)
        # setElement(row, column, value)
        if side == "R":
            # scaleX -1 space
            offset.setElement(0, 0, -1)
        else:
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
        driver_wInv = om2.MMatrix(cmds.getAttr(f"{driver}.worldInverseMatrix[0]"))
        # zero translation
        driver_wInv.setElement(3, 0, 0)
        driver_wInv.setElement(3, 1, 0)
        driver_wInv.setElement(3, 2, 0)
        if side == "R":
            mirror = om2.MMatrix(((-1, 0, 0, 0), 
                                  (0, 1, 0, 0), 
                                  (0, 0, 1, 0), 
                                  (0, 0, 0, 1)))
            driver_wInv_rot = driver_wInv * mirror
            pass
        else:
            driver_wInv_rot = driver_wInv
    # add driver's invRotation matrix to the mix
    # OPM = driver(wInv:rot only) * offset(no rot:jointOri) * driver(w) * tparent(wInv)
    # both offset and d_wInv_rot need to be mirrored into scaleX -1 space
    if driver_wInv_rot:
        cmds.setAttr(f"{multmtx}.matrixIn[0]", driver_wInv_rot, type = "matrix")
    
    # rest for non-joint object connections:
    # OPM = offset * driver(world) * tparent(worldInv)
    cmds.setAttr(f"{multmtx}.matrixIn[1]", offset, type = "matrix") # offset
    cmds.connectAttr(f"{driver}.worldMatrix[0]", f"{multmtx}.matrixIn[2]")
    cmds.connectAttr(f"{tparent}.worldInverseMatrix[0]", f"{multmtx}.matrixIn[3]")
    cmds.connectAttr(f"{multmtx}.matrixSum", f"{target}.offsetParentMatrix")
    cmds.xform(target, 
               translation = (0, 0, 0), 
               rotation = (0, 0, 0), 
               scale = (1, 1, 1))