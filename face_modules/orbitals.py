import maya.cmds as cmds

from face_proxies.proxyorbitals import ProxyOrbitals

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig

class Orbitals(object):
    
    # difference betw. lids & orbitals
        # center joint & aimConstraint
        # ctrl shape & color
        # different locked axes on ctrls
        # orbital no corner ctrls (moved by lid corners)
    
    def __init__(self, joint_socket, ctrl_socket, lidcorner_ctrls):

        self.module_name = "orbitals"
        
        
        self.corner_in = "L_orbcorner_in_CTRL" # no ctrl shape needed
        self.corner_out = "L_orbcorner_out_CTRL" # no ctrl shape needed
        self.uporb_in = "L_uporb_in_CTRL"
        self.uporb_main = "L_uporb_main_CTRL"
        self.uporb_out = "L_uporb_out_CTRL"
        self.loworb_in = "L_loworb_in_CTRL"
        self.loworb_main = "L_loworb_main_CTRL"
        self.loworb_out = "L_loworb_out_CTRL"
        
        
        self.orb_ctrls = [self.corner_in, self.corner_out, self.uporb_in, 
                          self.uporb_main, self.uporb_out, self.loworb_in,
                          self.loworb_main, self.loworb_out]
        
        self.build_rig(joint_socket, ctrl_socket, lidcorner_ctrls)
        
    def skeleton(self, joint_socket):
        porbs = ProxyOrbitals()
        all_vtx = cmds.listRelatives(porbs.vtx_grp, children = True, typ = "transform")
        # first/last are orb corners
        incorner = all_vtx[0]
        nr = int(len(all_vtx)/2)
        outcorner = all_vtx[nr]
        up_vtx = all_vtx[1:nr]
        low_vtx = all_vtx[nr+1:]
        low_vtx.reverse()
        # setup
        rad = cmds.getAttr(joint_socket+".radius")/5
        orb_jnts = []
        for part, vtx in enumerate([up_vtx, low_vtx, [incorner, outcorner]]):
            # part 0 = uporb, 1 = loworb, 2 = inoutcorners
            if part == 0:
                name = "L_uporb"
            elif part == 1:
                name = "L_loworb"
            elif part == 2:
                name = "L_orbcorner"
        ### joints
            for nr, v in enumerate(vtx):
                cmds.select(clear = True)
                vpos = cmds.xform(v, q = True, t = True, ws = True)
                vjnt = cmds.joint(n = f"{name}_{nr+1}_JNT", p = vpos, rad = rad)
                orb_jnts.append(vjnt)
            # mirror
                cmds.parent(vjnt, "head_JNT")
                mirr_jnt = cmds.mirrorJoint(
                    vjnt, 
                    mirrorYZ = True, 
                    mirrorBehavior = True, 
                    searchReplace = ["L_", "R_"])[0]
                orb_jnts.append(mirr_jnt)

                cmds.parent(vjnt, joint_socket, noInvScale = True)
                cmds.parent(mirr_jnt, joint_socket.replace("L_", "R_"), noInvScale = True)
        
        cmds.sets(orb_jnts, add = "fbind_joints")
        cmds.sets(orb_jnts, add = "fjoints")
    
##### CONTROLS #####################################################################
    def controls(self, ctrl_socket):
        # Setup
        porbs = ProxyOrbitals()
        ctrl_grp = cmds.group(
                n = "L_orbs_ctrls_GRP", empty = True, parent = ctrl_socket)
        ro = "yzx"
        dist = util.distance(porbs.corner_in, porbs.corner_out)
      
    ### CTRL SHAPES
        for name in self.orb_ctrls:
            if "orb_in" in name:
                color = "sky"
                size = dist/25
            elif "orb_out" in name:
                color = "sky"
                size = dist/25
            elif "tear" in name:
                color = "sky"
                size = dist/30
            else:
                color = "blue"
                size = dist/18
            if "corner" in name:
                ctrl = cmds.group(n = name, em = True)
            else:
                ctrl = Nurbs.sphere(name, size, color, ro)
            prx = name.replace("_CTRL", "_PRX")
            cmds.matchTransform(ctrl, prx, pos = True, rot = True)
            cmds.parent(ctrl, ctrl_grp)
        
        # buffer grps for 2ndary ctrls
        buffers = []
        for sec in [self.uporb_in, self.uporb_out, self.loworb_in, self.loworb_out]:
            buff = util.buffer(sec)
            buffers.append(buff)
        
####### Attributes
        # util.attr_separator([self.uporb_main, self.loworb_main])
        # cmds.addAttr(self.uporb_main, longName = "curl_lashes", attributeType = "double", 
        #              defaultValue = 0)
        # cmds.setAttr(self.uporb_main+".curl_lashes", e = True, keyable = True)
        
    ### R_ctrls & Mirroring
        mirr_grp = cmds.group(
                n = "R_orbs_ctrls_mirror_GRP", empty = True, 
                parent = ctrl_socket.replace("L_", "R_"))
        cmds.setAttr(mirr_grp+".sx", -1)
        rig.mirror_ctrls(ctrl_grp, mirr_grp)
    
    # selection sets
        set_grp = self.orb_ctrls.copy()
        for ctrl in set_grp:
            if ctrl.startswith("L_"):
                set_grp.append(ctrl.replace("L_", "R_"))
        cmds.sets(set_grp, add = "lids")
        
    # cleanup
        util.mtx_zero(self.orb_ctrls, rsidetoo = True)
        util.mtx_zero(buffers, rsidetoo = True)
        
###### RIGGING ####################################################################
    def build_rig(self, joint_socket, ctrl_socket, lidcorner_ctrls):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket)
    # setup
### crv_grp into "misc_GRP"
        crv_grp = cmds.group(n = "orbs_curves_GRP", em = True)

    ### point locators
        rad = cmds.getAttr(joint_socket+".radius")/5
        loc_grps = []
        for s in ["L_", "R_"]:
### loc groups under "misc_GRP"
            loc_grp = cmds.group(n = s+"orbs_loc_GRP", em = True)
            loc_grps.append(loc_grp)
            locs = []
            joints = cmds.ls(s+"*orb*_JNT")
            for j in joints:
                loc = cmds.spaceLocator(n = j.replace("_JNT", "_LOC"))[0]
                locs.append(loc)
                cmds.setAttr(loc+".localScale", rad, rad, rad)
                cmds.matchTransform(loc, j, pos = True)
                cmds.parent(loc, loc_grp)
        # point constraints
            for loc in locs:
                jnt = loc.replace("_LOC", "_JNT")
                cmds.pointConstraint(
                    loc, jnt, n = loc.replace("_LOC", "_POINT"), 
                    offset = (0,0,0), weight = 1)
        
    ### ctrl parent constraints
        for s in ["L_", "R_"]:
            for a in ["up", "low"]:
                for k in ["in", "out"]:
                    target = f"{s}{a}orb_{k}_buffer_GRP"
                    pc = cmds.parentConstraint(
                        [f"{s}{a}orb_main_CTRL", f"{s}orbcorner_{k}_CTRL"],
                        target, mo = True, 
                        n = f"{s}{a}orb_{k}_PC",weight = 0.5)[0]
                    cmds.addAttr(target, longName = "mid_follow",
                                 attributeType = "double", defaultValue = 0.8,
                                 min = 0, max = 1)
                    cmds.setAttr(target+".mid_follow", e = True, keyable = True)
                    rev = cmds.shadingNode("reverse", n = f"{s}{a}orb_{k}_REV",
                                           au = True)
                    cmds.connectAttr(target+".mid_follow", rev+".inputX")
                    cmds.connectAttr(target+".mid_follow", pc+f".{s}{a}orb_main_CTRLW0")
                    cmds.connectAttr(rev+".outputX", pc+f".{s}orbcorner_{k}_CTRLW1")
    ### curves
        for s in ["L_", "R_"]:
        ## up highrez curve
            uporb_locs = cmds.ls(s+"uporb*_LOC")
            uporb_locs.insert(0, s+"orbcorner_1_LOC") # at start
            uporb_locs.append(s+"orbcorner_2_LOC") # at end
            upcrv = util.pointcurve(s+"uporb_highrez_CRV", uporb_locs, 1)
            # attach locs to curve
            for loc in uporb_locs:
                if loc == uporb_locs[0]:
                    nr = 0
                elif loc == uporb_locs[-1]:
                    nr = len(uporb_locs)-1
                else:
                    nr = eval(loc.split("_")[2])
                pci = cmds.createNode(
                        "pointOnCurveInfo", n = loc.replace("_LOC", "_PCI"))
                cmds.connectAttr(upcrv+"Shape.worldSpace", pci+".inputCurve")
                cmds.setAttr(pci+".parameter", nr)
                cmds.connectAttr(pci+".position", loc+".translate")
        ## low highrez curve
            loworb_locs = cmds.ls(s+"loworb*_LOC")
            loworb_locs.insert(0, s+"orbcorner_1_LOC") # at start
            loworb_locs.append(s+"orbcorner_2_LOC") # at end
            lowcrv = util.pointcurve(s+"loworb_highrez_CRV", loworb_locs, 1)
            # loworb don't attach corner LOCs
            for loc in loworb_locs[1:-1]:
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
                ctrls = ["orbcorner_in", f"{a}orb_in", f"{a}orb_main", 
                            f"{a}orb_out", "orbcorner_out"]
                ctrls = [s+x+"_CTRL" for x in ctrls] # pre & suffix
                ctrlcrv = util.pointcurve(s+a+"orb_lowrez_CRV", ctrls, 2)
                cmds.parent(ctrlcrv, crv_grp)
            # ctrls drive cv on lowrez crv through decomposeMtx
                for n, ctrl in enumerate(ctrls):
                    dmtx = cmds.createNode(
                            "decomposeMatrix", n = f"{s}{a}orb_lowrez_crv_cv{n}_DM")
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
                        n = f"{s}{a}orb_WIRE", groupWithBase = False, envelope = 1,
                        crossingEffect = 0, localInfluence = 0, 
                        wire = ctrlcrv)[0]
### could be connected to global scale or head scale
                cmds.setAttr(wire+".dropoffDistance[0]", 100)
        
    ### upOrbital MACRO
        for s in ["L_", "R_"]:
            uplid = s+"uplid_main_CTRL"
            uporb = s+"uporb_main_CTRL"
            # as uplid goes up, uporb follows at 0.6
            dist = util.distance(uplid, uporb)
            mbuff = util.buffer(uporb, "macro1_uplid_up_GRP")
            util.mtx_zero([uporb, mbuff])
            mult = cmds.shadingNode(
                "multiplyDivide", n = s+"uporb_main_macro1_uplid_up_MULT", au = True)
            con = cmds.shadingNode(
                "condition", n = s+"uporb_main_macro1_uplid_up_CON", au = True)
            cmds.setAttr(con+".operation", 2) # greater than
            cmds.connectAttr(uplid+".ty", con+".firstTerm")
            cmds.setAttr(con+".colorIfTrue", 0, 0.6, -0.2)
            cmds.setAttr(con+".colorIfFalse", 0, 0, 0)
            cmds.connectAttr(con+".outColor", mult+".input2")
            cmds.connectAttr(uplid+".ty", mult+".input1Y")
            cmds.connectAttr(uplid+".ty", mult+".input1Z") # macro1 output = mult
            # follow uplid 0.05
            mult2 = cmds.shadingNode(
                "multiplyDivide", n = s+"uporb_main_macro2_uplid_MULT", au = True)
            cmds.connectAttr(uplid+".t", mult2+".input1")
            cmds.setAttr(mult2+".input2", 0.05, 0.05, 0.05) # macro2 output = mult2
            # follow brow avg ty 0.05
            browin = s+"brow_in_CTRL"
            browout = s+"brow_out_CTRL"
            browmain = s+"brow_main_CTRL"
            browmid = s+"brow_mid_CTRL"
            bpma = cmds.shadingNode(
                "plusMinusAverage", n = s+"uporb_main_macro_brow_AVG", au = True)
            cmds.setAttr(bpma+".operation", 3) # average
            for n, b in enumerate([browin, browmid, browout, browmain]):
                cmds.connectAttr(b+".ty", f"{bpma}.input1D[{n}]")
            mult3 = cmds.shadingNode(
                "multDoubleLinear", n = s+"uporb_main_macro3_brow_MULT", au = True)
            cmds.connectAttr(bpma+".output1D", mult3+".input1")
            cmds.setAttr(mult3+".input2", 0.3) # macro2 output = mult3
        # ADD macro1 + macro 2 + macro3
            macro_add = cmds.shadingNode(
                "plusMinusAverage", n = s+"uporb_main_macro_ADD", au = True)
            cmds.connectAttr(mult+".output", macro_add+".input3D[0]")
            cmds.connectAttr(mult2+".output", macro_add+".input3D[1]")
            cmds.connectAttr(mult3+".output", macro_add+".input3D[2].input3Dy")
            cmds.connectAttr(macro_add+".output3D", mbuff+".t")
                
    ### connect corners to lidcorner_ctrls
        for lc in lidcorner_ctrls:
            lidc = lc[2:]
            for s in ["L_", "R_"]:
                orbc = lidc.replace("lid", "orb")
                cmds.pointConstraint(s+lidc, s+orbc, mo = True, weight = 1,
                                     n = s+orbc.replace("_CTRL", "lidcorner_POINT"))
        
    ### clean up
        sort = [crv_grp]
        sort.extend(loc_grps)
        orbs_grp = cmds.group(n = "orbitals_GRP", em = True, p = "fmisc_GRP")
        cmds.parent(sort, orbs_grp)
        util.lock(self.orb_ctrls, ["rx","ry","sx","sy","sz"], rsidetoo = True)

### missing:
    # loworb macro
    # Face Tuning for:
        # uporb_uplid_follow
        # uporb_brow_follow
        # loworb_lowlid_follow
        # cheek_push_UD - add ty attrs from lipcorners, & cheeks and plug into this

if __name__ == "__main__":
    
    test = Orbitals()
    test.build_rig(
        joint_socket = "L_eye_socket_JNT", 
        ctrl_socket = "L_eye_socket_CTRL")
    pass