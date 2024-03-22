import maya.cmds as cmds

from face_proxies.proxybrows import ProxyBrows

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig

JNT_RAD = 0.5
LOC_S = 0.2

class Brows(object):
    
    def __init__(self, joint_socket, ctrl_socket):
        self.module_name = "brows"
        
        self.center_jnt = "brows_center_JNT"
        
        self.bin = "L_brow_in_CTRL"
        self.bcurr = "L_brow_curr_CTRL"
        self.bmid = "L_brow_mid_CTRL"
        self.bout = "L_brow_out_CTRL"
        self.bend = "L_brow_end_CTRL"
        self.banchor = "L_brow_anchor_CTRL"
        self.bmain = "L_brow_main_CTRL"
        
        self.brow_ctrls = [self.bin, self.bcurr, self.bmid, self.bout, self.bend,
                          self.banchor, self.bmain]
        
        self.brow_crv_jnts = []
        
        self.build_rig(joint_socket, ctrl_socket)
    
    def skeleton(self, joint_socket):
        pbrows = ProxyBrows()
        brow_vtx = cmds.listRelatives(pbrows.vtx_grp, c = True, typ = "transform")
    ### joints
        joints = []
        for nr, v in enumerate(brow_vtx):
            cmds.select(clear = True)
            pos = cmds.xform(v, q = True, t = True, ws = True)
            jnt = cmds.joint(n = f"L_brow_{nr+1}_JNT", p = pos, rad = JNT_RAD)
            self.brow_crv_jnts.append(jnt)
            joints.append(jnt)
            # cmds.joint(jnt, e = True, orientJoint = "zyx", 
            #            secondaryAxisOrient = "yup")
        # mirror
            cmds.parent(jnt, joint_socket, noInvScale = True) # head_JNT
            mirr_jnt = cmds.mirrorJoint(
                jnt, 
                mirrorYZ = True, 
                mirrorBehavior = True, 
                searchReplace = ["L_", "R_"])[0]
            joints.append(mirr_jnt)
        
        cmds.select(clear = True)
        mid = cmds.joint(n = self.center_jnt, rad = JNT_RAD*1.5)
        cmds.parent(mid, joint_socket, noInvScale = True)
        cmds.matchTransform(mid, self.brow_crv_jnts[0], py = True, pz = True)

        cmds.sets(joints, add = "fbind_joints")
        cmds.sets(joints, add = "fjoints")
    
##### CONTROLS #####################################################################
    def controls(self, ctrl_socket):
        # Setup
        pbrows = ProxyBrows()
        ctrl_grp = cmds.group(
                n = "L_brows_ctrls_GRP", empty = True, parent = ctrl_socket)
        ro = "yxz"
        dist = util.distance(pbrows.bin, pbrows.bout)
        size = dist / 10
      
    ### CTRL SHAPES
        b_in = Nurbs.sphere(self.bin, size*0.8, "green", ro)
        b_out = Nurbs.sphere(self.bout, size*0.8, "green", ro)
        b_curr = Nurbs.sphere(self.bcurr, size/3, "grass", ro)
        b_mid = Nurbs.sphere(self.bmid, size/2, "grass", ro)
        b_end = Nurbs.sphere(self.bend, size/2, "grass", ro)
        b_anchor = Nurbs.sphere(self.banchor, size/3, "purple", ro)
        b_main = Nurbs.octahedron(self.bmain, size, "purple", ro)
        # offset shapes a bit forward
        for c in self.brow_ctrls[:-1]: # without main ctrl
            cmds.move(0, 0, size/2, c+".cv[0:7]", r = True, localSpace = True)
        
    # position & parent
### better to remap connect main to in & out?
        relations = {
            b_main :   (pbrows.bmain,   ctrl_grp),
            b_in :     (pbrows.bin,     b_main),
            b_out :    (pbrows.bout,    b_main),
            b_curr :   (pbrows.bcurr,   ctrl_grp),
            b_mid :    (pbrows.bmid,    ctrl_grp),
            b_end :    (pbrows.bend,    ctrl_grp),
            b_anchor : (pbrows.banchor, ctrl_grp),
            }
        for ctrl in list(relations):
            cmds.matchTransform(ctrl, relations[ctrl][0], pos = True, rot = True)
            cmds.parent(ctrl, relations[ctrl][1])
    # buffer grps for 2ndary ctrls
        buffers = []
        for sec in [b_curr, b_mid, b_end]:
            buff = util.buffer(sec)
            buffers.append(buff)
        
####### Attributes
### not RUMBA friendly :'(
        # for c in self.brow_ctrls:
        #     cmds.addAttr(c, longName = "Z", attributeType = "double", 
        #                  defaultValue = 0)
        #     cmds.setAttr(c+".Z", e = True, keyable = True)
        
    ### R_ctrls & Mirroring
        mirr_grp = cmds.group(
                n = "R_brows_ctrls_mirror_GRP", empty = True, 
                parent = ctrl_socket)
        cmds.setAttr(mirr_grp+".sx", -1)
        rig.mirror_ctrls(ctrl_grp, mirr_grp)
    
    # selection sets
        set_grp = self.brow_ctrls.copy()
        for ctrl in set_grp:
            if ctrl.startswith("L_"):
                set_grp.append(ctrl.replace("L_", "R_"))
        cmds.sets(set_grp, add = "brows")
        
    # cleanup
        util.mtx_zero(self.brow_ctrls, rsidetoo = True)
        util.mtx_zero(buffers, rsidetoo = True)
        
###### RIGGING ####################################################################
    def build_rig(self, joint_socket, ctrl_socket):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket)
### crv & loc grps into "misc_GRP"

    ### locators to drive joints
        locs = []
        loc_grps = []
        for s in ["L_", "R_"]:
            loc_grp = cmds.group(n = s+"brows_loc_GRP", em = True)
            loc_grps.append(loc_grp)
            joints = cmds.ls(s+"brow_*_JNT")
            for j in joints:
                loc = cmds.spaceLocator(n = j.replace("_JNT", "_LOC"))[0]
                locs.append(loc)
                cmds.setAttr(loc+".localScale", LOC_S, LOC_S, LOC_S)
                cmds.matchTransform(loc, j, pos = True)
                cmds.parent(loc, loc_grp)
        # point constraints
            for loc in locs:
                jnt = loc.replace("_LOC", "_JNT")
                cmds.pointConstraint(
                    loc, jnt, n = loc.replace("_LOC", "_POINT"), 
                    offset = (0,0,0), weight = 1)
    ### curves
        crv_grp = cmds.group(n = "brows_curves_GRP", em = True)
        ## highrez curve
        for s in ["L_", "R_"]:
            brow_locs = cmds.ls(s+"brow*_LOC")
            hr_crv = util.pointcurve(s+"brow_highrez_CRV", brow_locs, 1)
            # attach locs to curve
            for loc in brow_locs:
                # u position on curve from number in name of loc
                nr = eval(loc.split("_")[2])-1
                pci = cmds.createNode(
                        "pointOnCurveInfo", n = loc.replace("_LOC", "_PCI"))
                cmds.connectAttr(hr_crv+"Shape.worldSpace", pci+".inputCurve")
                cmds.setAttr(pci+".parameter", nr)
                cmds.connectAttr(pci+".position", loc+".translate")
            cmds.parent(hr_crv, crv_grp)
            
        ## lowrez curve - recreated PRX curve (degree = 2)
        # 2 points for curr and out
### make __init__ argument for "sharp" which determines 2 points or 1 for curr & out
        for s in ["L_", "R_"]:
            ctrls = ["brow_in", f"brow_curr", f"brow_curr", f"brow_mid", 
                        f"brow_out", f"brow_out", "brow_end", "brow_anchor"]
            ctrls = [s+x+"_CTRL" for x in ctrls] # pre & suffix
            lr_crv = util.pointcurve(s+"brow_lowrez_CRV", ctrls, 2)
            cmds.parent(lr_crv, crv_grp)
        # ctrls drive cv on lowrez crv through decomposeMtx
            for n, ctrl in enumerate(ctrls):
                dmtx = cmds.createNode(
                        "decomposeMatrix", n = f"{s}brow_lowrez_crv_cv{n}_DM")
                cmds.connectAttr(f"{ctrl}.worldMatrix[0]", f"{dmtx}.inputMatrix")
                cmds.connectAttr(f"{dmtx}.outputTranslateX", 
                                 f"{lr_crv}Shape.controlPoints[{n}].xValue")
                cmds.connectAttr(f"{dmtx}.outputTranslateY", 
                                 f"{lr_crv}Shape.controlPoints[{n}].yValue")
                cmds.connectAttr(f"{dmtx}.outputTranslateZ", 
                                 f"{lr_crv}Shape.controlPoints[{n}].zValue")
        # wire deformer
            wire = cmds.wire(
                    lr_crv.replace("lowrez", "highrez"),
                    n = f"{s}brow_WIRE", groupWithBase = False, envelope = 1,
                    crossingEffect = 0, localInfluence = 0, 
                    wire = lr_crv)[0]
### could be connected to global scale
            cmds.setAttr(wire+".dropoffDistance[0]", 100)
            
    ### ctrl constraints
        for s in ["L_", "R_"]:
            # in & out -> curr & mid
            # out & anchor -> end
            target = f"{s}brow__buffer_GRP"
            curr_p = cmds.parentConstraint(
                [f"{s}brow_in_CTRL", f"{s}brow_mid_CTRL"],
                f"{s}brow_curr_buffer_GRP", mo = True, 
                n = f"{s}brow_curr_PC", weight = 1)[0]
            mid_p = cmds.parentConstraint(
                [f"{s}brow_in_CTRL", f"{s}brow_out_CTRL"],
                f"{s}brow_mid_buffer_GRP", mo = True, 
                n = f"{s}brow_mid_PC", weight = 1)[0]
            end_p = cmds.parentConstraint(
                [f"{s}brow_out_CTRL", f"{s}brow_anchor_CTRL"],
                f"{s}brow_end_buffer_GRP", mo = True, 
                n = f"{s}brow_end_PC", weight = 1)[0]
        # make & connect attr to drive constraint weight
            buffs = {"curr" : 0.4, "mid" : 0.5, "end" : 0.4}
            for buff in list(buffs):
                target = f"{s}brow_{buff}_buffer_GRP"
                cmds.addAttr(target, longName = "follow",
                             attributeType = "double", defaultValue = buffs[buff],
                             min = 0, max = 1)
                cmds.setAttr(target+".follow", e = True, keyable = True)
                rev = cmds.shadingNode("reverse", n = f"{s}brow_{buff}_REV",
                                       au = True)
                con = f"{s}brow_{buff}_PC"
                if buff == "curr":
                    cmds.connectAttr(target+".follow", rev+".inputX")
                    cmds.connectAttr(target+".follow", con+f".{s}brow_in_CTRLW0")
                    cmds.connectAttr(rev+".outputX", con+f".{s}brow_mid_CTRLW1")
                elif buff == "end":
                    cmds.connectAttr(target+".follow", rev+".inputX")
                    cmds.connectAttr(target+".follow", con+f".{s}brow_out_CTRLW0")
                    cmds.connectAttr(rev+".outputX", con+f".{s}brow_anchor_CTRLW1")
                else:
                    cmds.connectAttr(target+".follow", rev+".inputX")
                    cmds.connectAttr(target+".follow", con+f".{s}brow_in_CTRLW0")
                    cmds.connectAttr(rev+".outputX", con+f".{s}brow_out_CTRLW1")
            
    # center jnt parent constraint
        cmds.parentConstraint(
                [self.bin, self.bin.replace("L_", "R_")], self.center_jnt,
                mo = True, weight = 1, n = "brows_centerjnt_PC")
        
    ### clean up
        sort = [crv_grp]
        sort.extend(loc_grps)
        brows_grp = cmds.group(n = "brows_GRP", em = True, p = "fmisc_GRP")
        cmds.parent(sort, brows_grp)
### not RUMBA firendly :'(
        # for ctrl in self.brow_ctrls:
        #     mult = cmds.shadingNode(
        #             "multDoubleLinear", n = ctrl.replace("CTRL", "zattr_MULT"), au = True)
        #     cmds.setAttr(mult+".input2", 0.1)
        #     cmds.connectAttr(ctrl+".Z", mult+".input1")
        #     cmds.connectAttr(mult+".output", ctrl+".tz")
        util.lock(self.brow_ctrls, ["tz","rx","ry", "rz","sx","sy","sz"])
        # util.lock(self.brow_ctrls, ["tz","rx","ry","sx","sy","sz"], rsidetoo = True)

### missing:
    # Face Tuning for in & out ctrls:
        # Z depth for currogator (in_ctrl.tx drives tz)
        # Z depth for overall brow UD (layered from main.ty + ctrl.ty)

if __name__ == "__main__":
    
    cmds.select(cl = True)
    cmds.joint(n = "head_JNT", p = (0,160,0))
    hc = cmds.group(n = "head_CTRL", em = True)
    cmds.move(0, 160, 0, hc, r = True)
    
    test = Brows(joint_socket = "head_JNT", 
                 ctrl_socket = "head_CTRL")
    pass