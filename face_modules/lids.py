import maya.cmds as cmds

from face_proxies.proxylids import ProxyLids

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig

class Lids(object):
    
    # difference betw. lids & orbitals
        # center joint & aimConstraint
        # ctrl shape & color
        # different locked axes on ctrls
        # orbital no corner ctrls (moved by lid corners)
    
    def __init__(self, tearduct = None):

        self.module_name = "lid"
        
        
        self.corner_in = "L_lidcorner_in_CTRL"
        self.corner_out = "L_lidcorner_out_CTRL"
        self.uplid_in = "L_uplid_in_CTRL"
        self.uplid_main = "L_uplid_main_CTRL"
        self.uplid_out = "L_uplid_out_CTRL"
        self.lowlid_in = "L_lowlid_in_CTRL"
        self.lowlid_main = "L_lowlid_main_CTRL"
        self.lowlid_out = "L_lowlid_out_CTRL"
        
        
        self.lid_ctrls = [self.corner_in, self.corner_out, self.uplid_in, 
                          self.uplid_main, self.uplid_out, self.lowlid_in,
                          self.lowlid_main, self.lowlid_out]
        if tearduct:
            self.tearduct = True
            self.uplid_tear = "L_uplid_tear_CTRL"
            self.lowlid_tear = "L_lowlid_tear_CTRL"
            self.lid_ctrls.extend([self.uplid_tear, self.lowlid_tear])
    
    def skeleton(self, joint_socket):
        plids = ProxyLids()
        all_vtx = cmds.listRelatives(plids.vtx_grp, children = True, typ = "transform")
        # first/last are lid corners
        incorner = all_vtx[0]
        nr = int(len(all_vtx)/2)
        outcorner = all_vtx[nr]
        up_vtx = all_vtx[1:nr]
        low_vtx = all_vtx[nr+1:]
        low_vtx.reverse()
        # setup
        rad = cmds.getAttr(joint_socket+".radius")/5
        center_jnts = []
        tip_jnts = []
        for part, vtx in enumerate([up_vtx, low_vtx, [incorner, outcorner]]):
            # part 0 = uplid, 1 = lowlid, 2 = inoutcorners
            if part == 0:
                name = "L_uplid"
            elif part == 1:
                name = "L_lowlid"
            elif part == 2:
                name = "L_lidcorner"
        ### joints
            for nr, v in enumerate(vtx):
                cmds.select(clear = True)
                cpos = cmds.xform(joint_socket, q = True, t = True, ws = True)
                vpos = cmds.xform(v, q = True, t = True, ws = True)
                cjnt = cmds.joint(n = f"{name}_{nr+1}_center_JNT", p = cpos, rad = rad)
                vjnt = cmds.joint(n = f"{name}_{nr+1}_tip_JNT", p = vpos, rad = rad)
                center_jnts.append(cjnt)
                tip_jnts.append(vjnt)
                # cmds.joint(cjnt, e = True, orientJoint = "zyx", 
                #            secondaryAxisOrient = "yup")
                # cmds.joint(vjnt, e = True, orientJoint = "none")
            # mirror
                cmds.parent(cjnt, "head_JNT")
                mirr_jnt = cmds.mirrorJoint(
                    cjnt, 
                    mirrorYZ = True, 
                    mirrorBehavior = True, 
                    searchReplace = ["L_", "R_"])[0]
                center_jnts.append(mirr_jnt)
                r_tip = cmds.listRelatives(mirr_jnt, children = True)[0]
                tip_jnts.append(r_tip)
### noInvScale = True ???
                cmds.parent(cjnt, joint_socket, noInvScale = True)
                cmds.parent(mirr_jnt, joint_socket.replace("L_", "R_"), 
                            noInvScale = True)
        cmds.sets(center_jnts, add = "fbind_joints")
        cmds.sets(center_jnts, add = "fjoints")
        cmds.sets(tip_jnts, add = "fjoints")
        
##### CONTROLS #####################################################################
    def controls(self, ctrl_socket):
        # Setup
        plids = ProxyLids()
        ctrl_grp = cmds.group(
                n = "L_lids_ctrls_GRP", empty = True, parent = ctrl_socket)
        ro = "yzx"
        dist = util.distance(plids.corner_in, plids.corner_out)
      
    ### CTRL SHAPES
        for name in self.lid_ctrls:
            if "lid_in" in name:
                color = "sky"
                size = dist/25
            elif "lid_out" in name:
                color = "sky"
                size = dist/25
            elif "tear" in name:
                color = "sky"
                size = dist/30
            else:
                color = "blue"
                size = dist/18
            ctrl = Nurbs.sphere(name, size, color, ro)
            prx = name.replace("_CTRL", "_PRX")
            cmds.matchTransform(ctrl, prx, pos = True, rot = True)
            cmds.parent(ctrl, ctrl_grp)
        
        # buffer grps for 2ndary ctrls
        buffers = []
        for sec in [self.uplid_in, self.uplid_out, self.lowlid_in, self.lowlid_out]:
            buff = util.buffer(sec)
            buffers.append(buff)
        if self.tearduct:
            for sec in [self.uplid_tear, self.lowlid_tear]:
                buff = util.buffer(sec)
                buffers.append(buff)
        
####### Attributes
        util.attr_separator([self.uplid_main, self.lowlid_main])
        cmds.addAttr(self.uplid_main, longName = "curl_lashes", attributeType = "double", 
                     defaultValue = 0)
        cmds.setAttr(self.uplid_main+".curl_lashes", e = True, keyable = True)
        cmds.addAttr(self.lowlid_main, longName = "curl_lashes", attributeType = "double", 
                     defaultValue = 0)
        cmds.setAttr(self.lowlid_main+".curl_lashes", e = True, keyable = True)
        
    ### R_ctrls & Mirroring
        mirr_grp = cmds.group(
                n = "R_lids_ctrls_mirror_GRP", empty = True, 
                parent = ctrl_socket.replace("L_", "R_"))
        cmds.setAttr(mirr_grp+".sx", -1)
        rig.mirror_ctrls(ctrl_grp, mirr_grp)
        
    
    # selection sets
        set_grp = self.lid_ctrls.copy()
        for ctrl in set_grp:
            if ctrl.startswith("L_"):
                set_grp.append(ctrl.replace("L_", "R_"))
        cmds.sets(set_grp, add = "lids")
        
    # cleanup
        util.mtx_zero(self.lid_ctrls, rsidetoo = True)
        util.mtx_zero(buffers, rsidetoo = True)
        
###### RIGGING ####################################################################
    def build_rig(self, joint_socket, ctrl_socket):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket)
    # setup
### crv_grp into "misc_GRP"
        crv_grp = cmds.group(n = "lids_curves_GRP", em = True)

    # aim locators
        rad = cmds.getAttr(joint_socket+".radius")/5
        loc_grps = []
        for s in ["L_", "R_"]:
### loc groups under "misc_GRP"
            loc_grp = cmds.group(n = s+"lids_aimloc_GRP", em = True)
            loc_grps.append(loc_grp)
            locs = []
            joints = cmds.ls(s+"*lid*_tip_JNT")
            for j in joints:
                loc = cmds.spaceLocator(n = j.replace("_tip_JNT", "_aim_LOC"))[0]
                locs.append(loc)
                cmds.setAttr(loc+".localScale", rad, rad, rad)
                cmds.matchTransform(loc, j, pos = True)
                cmds.parent(loc, loc_grp)
        # aim constraints
### perhaps use an aim target obj rather than "objectrotation"
            for aim_loc in locs:
                aim_jnt = aim_loc.replace("aim_LOC", "center_JNT")
                if s == "R_":
                    aimv = (0,0,-1)
                else:
                    aimv = (0,0,1)
                cmds.aimConstraint(
                    aim_loc, aim_jnt, n = aim_loc.replace("aim_LOC", "AIM"), 
                    mo = True, 
                    weight = 1, aimVector = aimv, upVector = (0,1,0), 
                    worldUpType = "objectrotation", worldUpVector = (0,1,0), 
                    worldUpObject = joint_socket)
        
    # ctrl parent constraints
        for s in ["L_", "R_"]:
            for a in ["up", "low"]:
                for k in ["in", "out"]:
                    target = f"{s}{a}lid_{k}_buffer_GRP"
                    pc = cmds.parentConstraint(
                        [f"{s}{a}lid_main_CTRL", f"{s}lidcorner_{k}_CTRL"],
                        target, mo = True, 
                        n = f"{s}{a}lid_{k}_PC",weight = 0.5)[0]
                    cmds.addAttr(target, longName = "mid_follow",
                                 attributeType = "double", defaultValue = 0.8,
                                 min = 0, max = 1)
                    cmds.setAttr(target+".mid_follow", e = True, keyable = True)
                    rev = cmds.shadingNode("reverse", n = f"{s}{a}lid_{k}_REV",
                                           au = True)
                    cmds.connectAttr(target+".mid_follow", rev+".inputX")
                    cmds.connectAttr(target+".mid_follow", pc+f".{s}{a}lid_main_CTRLW0")
                    cmds.connectAttr(rev+".outputX", pc+f".{s}lidcorner_{k}_CTRLW1")
    ### curves
        for s in ["L_", "R_"]:
        ## up highrez curve
            uplid_locs = cmds.ls(s+"uplid*aim_LOC")
            uplid_locs.insert(0, s+"lidcorner_1_aim_LOC") # at start
            uplid_locs.append(s+"lidcorner_2_aim_LOC") # at end
            upcrv = util.pointcurve(s+"uplid_highrez_CRV", uplid_locs, 1)
            # attach locs to curve
            for loc in uplid_locs:
                if loc == uplid_locs[0]:
                    nr = 0
                elif loc == uplid_locs[-1]:
                    nr = len(uplid_locs)-1
                else:
                    nr = eval(loc.split("_")[2])
                pci = cmds.createNode(
                        "pointOnCurveInfo", n = loc.replace("_LOC", "_PCI"))
                cmds.connectAttr(upcrv+"Shape.worldSpace", pci+".inputCurve")
                cmds.setAttr(pci+".parameter", nr)
                cmds.connectAttr(pci+".position", loc+".translate")
        ## low highrez curve
            lowlid_locs = cmds.ls(s+"lowlid*aim_LOC")
            lowlid_locs.insert(0, s+"lidcorner_1_aim_LOC") # at start
            lowlid_locs.append(s+"lidcorner_2_aim_LOC") # at end
            lowcrv = util.pointcurve(s+"lowlid_highrez_CRV", lowlid_locs, 1)
            # lowlid don't attach corner LOCs
            for loc in lowlid_locs[1:-1]:
                nr = eval(loc.split("_")[2])
                pci = cmds.createNode(
                        "pointOnCurveInfo", n = loc.replace("_LOC", "_PCI"))
                cmds.connectAttr(lowcrv+"Shape.worldSpace", pci+".inputCurve")
                cmds.setAttr(pci+".parameter", nr)
                cmds.connectAttr(pci+".position", loc+".translate")
            cmds.parent([upcrv, lowcrv], crv_grp)
            
    ## lowrez curves
        for s in ["L_", "R_"]:
            for a in ["up", "low"]:
                ctrls = ["lidcorner_in", f"{a}lid_in", f"{a}lid_main", 
                            f"{a}lid_out", "lidcorner_out"]
                if self.tearduct:
                    ctrls.insert(1, f"{a}lid_tear")
                    ctrls.insert(1, f"{a}lid_tear") # 2nd time to create sharp point
                ctrls = [s+x+"_CTRL" for x in ctrls] # pre & suffix
                ctrlcrv = util.pointcurve(s+a+"lid_lowrez_CRV", ctrls, 2)
                cmds.parent(ctrlcrv, crv_grp)
            # ctrls drive cv on lowrez crv through decomposeMtx
                for n, ctrl in enumerate(ctrls):
                    dmtx = cmds.createNode(
                            "decomposeMatrix", n = f"{s}{a}lid_lowrez_crv_cv{n}_DM")
                    cmds.connectAttr(f"{ctrl}.worldMatrix[0]", f"{dmtx}.inputMatrix")
                    cmds.connectAttr(f"{dmtx}.outputTranslateX", 
                                     f"{ctrlcrv}Shape.controlPoints[{n}].xValue")
                    cmds.connectAttr(f"{dmtx}.outputTranslateY", 
                                     f"{ctrlcrv}Shape.controlPoints[{n}].yValue")
                    cmds.connectAttr(f"{dmtx}.outputTranslateZ", 
                                     f"{ctrlcrv}Shape.controlPoints[{n}].zValue")
            # wire deformer
                wire = cmds.wire(
                        ctrlcrv.replace("lowrez", "highrez"),
                        n = f"{s}{a}lid_WIRE", groupWithBase = False, envelope = 1,
                        crossingEffect = 0, localInfluence = 0, 
                        wire = ctrlcrv)[0]
### could be connected to global scale or head scale
                cmds.setAttr(wire+".dropoffDistance[0]", 100)
            
    # curl lashes attr
        for s in ["L_", "R_"]:
            for a in ["up", "low"]:
                tip_jnts = cmds.ls(f"{s}{a}lid_*_tip_JNT")
                for j in tip_jnts:
                    cmds.connectAttr(f"{s}{a}lid_main_CTRL.curl_lashes", j+".rx")
    # tearduct xtra ctrls MACRO
        if self.tearduct:
            # tear_ctrls follow only 0.1
            for s in ["L_", "R_"]:
                for a in ["up", "low"]:
                    target = f"{s}{a}lid_tear_buffer_GRP"
                    pc = cmds.parentConstraint(
                        [f"{s}{a}lid_in_CTRL", f"{s}lidcorner_in_CTRL"],
                        target, mo = True, 
                        n = f"{s}{a}lid_tear_PC",weight = 0.5)[0]
                    cmds.addAttr(target, longName = "mid_follow",
                                 attributeType = "double", defaultValue = 0.1,
                                 min = 0, max = 1)
                    cmds.setAttr(target+".mid_follow", e = True, keyable = True)
                    rev = cmds.shadingNode("reverse", n = f"{s}{a}lid_tear_REV",
                                           au = True)
                    cmds.connectAttr(target+".mid_follow", rev+".inputX")
                    cmds.connectAttr(target+".mid_follow", pc+f".{s}{a}lid_in_CTRLW0")
                    cmds.connectAttr(rev+".outputX", pc+f".{s}lidcorner_in_CTRLW1")
        
    ### clean up
        sort = [crv_grp]
        sort.extend(loc_grps)
        cmds.hide(sort)
        lids_grp = cmds.group(n = "lids_GRP", em = True, p = "fmisc_GRP")
        cmds.parent(sort, lids_grp)
        util.lock(self.lid_ctrls, ["tz","rx","ry","sx","sy","sz"], rsidetoo = True)

### missing:
    # fleshy lids
    # blink attrs

if __name__ == "__main__":
    
    test = Lids(tearduct = True)
    test.build_rig(
        joint_socket = "L_eye_socket_JNT", 
        ctrl_socket = "L_eye_socket_CTRL")
    # cmds.hide("position_lidsprx_GRP")
    pass