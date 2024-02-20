import maya.cmds as cmds

from face_proxies.proxycheeks import ProxyCheeks

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig

class Cheeks(object):
    
    def __init__(self):

        self.module_name = "cheeks"
        
        self.inner_jnt = "L_cheek_inner_JNT"
        self.main_jnt = "L_cheek_main_JNT"
        self.bone_jnt = "L_cheek_bone_JNT"
        
        self.inner = "L_cheek_inner_CTRL"
        self.main = "L_cheek_main_CTRL"
        self.bone = "L_cheek_bone_CTRL"
        
        self.inner_buff = "L_cheek_inner_buffer_GRP"
        self.main_buff = "L_cheek_main_buffer_GRP"
        self.bone_buff = "L_cheek_bone_buffer_GRP"
        
        self.cheek_ctrls = [self.inner, self.main, self.bone]
    
    def skeleton(self, joint_socket):
        pcheeks = ProxyCheeks()
        rad = cmds.getAttr(joint_socket+".radius")
        cheek_jnts = rig.make_joints(
                proxies_list = pcheeks.proxies,
                rot_order = "xzy", 
                radius = rad/2,
                set = "fjoints")
        cmds.parent(cheek_jnts[0], joint_socket, noInvScale = True)
        mirr_jnts = cmds.mirrorJoint(
            cheek_jnts[0], mirrorYZ = True, 
            mirrorBehavior = True, 
            searchReplace = ["L_", "R_"])
        cheek_jnts.extend(mirr_jnts)
        cmds.parent(cheek_jnts, world = True)
        for j in cheek_jnts:
            cmds.parent(j, joint_socket, noInvScale = True)
        cmds.sets(cheek_jnts, add = "fbind_joints")
        cmds.sets(cheek_jnts, add = "fjoints")
    
##### CONTROLS #####################################################################
    def controls(self, ctrl_socket):
        # Setup
        pcheeks = ProxyCheeks()
        # ctrl_grp = cmds.group(
        #         n = "L_orbs_ctrls_GRP", empty = True, parent = ctrl_socket)
        ro = "xzy"
        dist = util.distance(pcheeks.inner, pcheeks.bone)
      
    ### CTRL SHAPES
        inner = Nurbs.sphere(self.inner, dist/10, "sky")
        main = Nurbs.sphere(self.main, dist/6, "blue")
        bone = Nurbs.sphere(self.bone, dist/10, "blue")
        
    # position & parent
        relations = {
            inner :     (pcheeks.inner,    ctrl_socket),
            main :      (pcheeks.main,     ctrl_socket),
            bone :      (pcheeks.bone,     ctrl_socket),}
        
        for ctrl in list(relations):
            cmds.matchTransform(ctrl, relations[ctrl][0], pos = True, rot = True)
            cmds.parent(ctrl, relations[ctrl][1])
    
    # buffers
        buffers = []
        for ctrl in self.cheek_ctrls:
            buff = util.buffer(ctrl)
            buffers.append(buff)

####### Attributes
        # util.attr_separator([base, nostril])
        # attr_dict = {
        #     base : ["skew"],
        #     nostril : ["flare"],}
        # for ctrl in attr_dict.keys():
        #     for attr in attr_dict[ctrl]:
        #         cmds.addAttr(ctrl, longName = attr, attributeType = "double")
        #         cmds.setAttr(f"{ctrl}.{attr}", e = True, keyable = True)
        # FACE TUNING
        # attrs to control macro connection to lipcorners
        util.attr_separator("FACE_TUNING", name = "cheeks")
        for faceattr in ["main_macrotz", "main_macroty", "bone_macrotz", "bone_macroty"]:
            cmds.addAttr(
                "FACE_TUNING", longName = faceattr, attributeType = "double")
            cmds.setAttr(f"FACE_TUNING.{faceattr}", e = True, keyable = True)
        
    ### R_ctrls & Mirroring
        mirr_grp = cmds.group(
                n = "R_cheek_ctrls_mirror_GRP", empty = True, 
                parent = ctrl_socket)
        cmds.setAttr(mirr_grp+".sx", -1)
        rig.mirror_ctrls(buffers, mirr_grp)
    
    # selection sets
        set_grp = self.cheek_ctrls.copy()
        for ctrl in set_grp:
            if ctrl.startswith("L_"):
                set_grp.append(ctrl.replace("L_", "R_"))
        cmds.sets(set_grp, add = "cheeks")
        
    # cleanup
        util.mtx_zero(self.cheek_ctrls, rsidetoo = True)
        util.mtx_zero(buffers, rsidetoo = True)
        
###### RIGGING ####################################################################
    def build_rig(self, joint_socket, ctrl_socket, lipcorners = None):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket)
    # connect joint to ctrls
        for s in ["L_", "R_"]:
            for ctrl in [f"{s}cheek_inner_CTRL", 
                         f"{s}cheek_main_CTRL", 
                         f"{s}cheek_bone_CTRL"]:
                jnt = ctrl.replace("CTRL", "JNT")
                name = jnt[:-3]
                cmds.parentConstraint(ctrl, jnt, mo = True, w = 1, n = name+"PC")
                cmds.scaleConstraint(ctrl, jnt, offset = (1,1,1), w = 1, n = name+"PC")
### MACRO uplip follow with tuner
    # MACRO lipcorner follow
        if not lipcorners:
            lipcorners = ["L_lipcorner_CTRL", "R_lipcorner_CTRL"]
        cmds.setAttr("FACE_TUNING.main_macroty", 0.2) # default
        cmds.setAttr("FACE_TUNING.main_macrotz", 0.2) # default
        cmds.setAttr("FACE_TUNING.bone_macroty", 0.1) # default
        cmds.setAttr("FACE_TUNING.bone_macrotz", 0.1) # default
        for lipc in lipcorners:
            side = lipc.split("_")[0]
            for part in ["main", "bone"]:
                cheek_buff = f"{side}_cheek_{part}_buffer_GRP"
                mult = cmds.shadingNode(
                    "multiplyDivide", n = f"{side}_cheek_{part}_macro_MULT", au = True)
                cmds.connectAttr(lipc+".tx", mult+".input1X")
                cmds.connectAttr(lipc+".ty", mult+".input1Y")
                cmds.connectAttr(lipc+".ty", mult+".input1Z")
                cmds.connectAttr("FACE_TUNING.main_macroty", mult+".input2Y")
                cmds.connectAttr("FACE_TUNING.main_macrotz", mult+".input2Z")
                cmds.setAttr(mult+".input2X", 0.025)
                cmds.connectAttr(mult+".outputX", cheek_buff+".tx")
                cmds.connectAttr(mult+".outputY", cheek_buff+".ty")
                cmds.connectAttr(mult+".outputZ", cheek_buff+".tz")
    ### clean up attributes - lock & hide
        util.lock([self.inner, self.main, self.bone], 
                  ["sx","sy","sz"], rsidetoo = True)

### missing:

if __name__ == "__main__":
    
    test = Cheeks()
    test.build_rig(
        joint_socket = "head_JNT", 
        ctrl_socket = "head_CTRL",
        lipcorners = ["L_lipcorner_macroOut_GRP", 
                      "R_lipcorner_macroOut_GRP"])
    cmds.hide("proxy_test_GRP")
    pass