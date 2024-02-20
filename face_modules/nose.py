import maya.cmds as cmds

from face_proxies.proxynose import ProxyNose

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig

class Nose(object):
    
    def __init__(self):

        self.module_name = "orbitals"
        
        self.base_jnt = "nose_base_JNT"
        self.tip_jnt = "nose_tip_JNT"
        self.nostril_jnt = "L_nostril_JNT"
        
        self.base = "nose_base_CTRL"
        self.tip = "nose_tip_CTRL"
        self.nostril = "L_nostril_CTRL"
        self.nostril_buff = "L_nostril_macro_GRP"
        
        self.nose_ctrls = []
    
    def skeleton(self, joint_socket):
        pnose = ProxyNose()
        
        nose_jnts = rig.make_joints(
                proxies_list = pnose.proxies,
                rot_order = "xzy", 
                radius = 0.8,
                set = "fjoints")
        cmds.parent(self.nostril_jnt, self.base_jnt, noInvScale = True)
        cmds.disconnectAttr(self.base_jnt+".s", self.tip_jnt+".inverseScale")
        mirr_jnts = cmds.mirrorJoint(
                self.nostril_jnt, 
                mirrorYZ = True, 
                mirrorBehavior = True, 
                searchReplace = ["L_", "R_"])
        cmds.parent(self.base_jnt, joint_socket)
        set_jnts = nose_jnts.copy()
        set_jnts.extend(mirr_jnts)
        cmds.sets(set_jnts, add = "fbind_joints")
        cmds.sets(set_jnts, add = "fjoints")
    
##### CONTROLS #####################################################################
    def controls(self, ctrl_socket):
        # Setup
        pnose = ProxyNose()
        # ctrl_grp = cmds.group(
        #         n = "L_orbs_ctrls_GRP", empty = True, parent = ctrl_socket)
        ro = "xzy"
        dist = util.distance(pnose.base, pnose.tip)
      
    ### CTRL SHAPES
        base = Nurbs.circle(self.base, dist/3, "brown")
        tip = Nurbs.sphere(self.tip, dist/10, "brown")
        nostril = Nurbs.sphere(self.nostril, dist/6, "blue", "yzx")
        nostril_buff = cmds.group(n = self.nostril.replace("CTRL", "macro_GRP"), em = True)
        
    # see through geo like xRay
        for xray in [base]:
            shapes = cmds.listRelatives(xray, children = True, shapes = True)
            for s in shapes:
                cmds.setAttr(f"{s}.alwaysDrawOnTop", 1)
        
    # position & parent
        relations = {
            base :      (pnose.base,        ctrl_socket),
            tip :       (pnose.tip,         base),
            nostril_buff :   (pnose.nostril,     base),
            nostril :   (pnose.nostril,     nostril_buff),}
        
        for ctrl in list(relations):
            cmds.matchTransform(ctrl, relations[ctrl][0], pos = True, rot = True)
            cmds.parent(ctrl, relations[ctrl][1])

####### Attributes
        util.attr_separator([base, nostril])
        attr_dict = {
            base : ["skew"],
            nostril : ["flare"],}
        for ctrl in attr_dict.keys():
            for attr in attr_dict[ctrl]:
                cmds.addAttr(ctrl, longName = attr, attributeType = "double")
                cmds.setAttr(f"{ctrl}.{attr}", e = True, keyable = True)
        # FACE TUNING
        util.attr_separator("FACE_TUNING", name = "nose")
        for faceattr in ["lipcorner_follow", "uplip_follow"]:
            cmds.addAttr(
                "FACE_TUNING", longName = faceattr, attributeType = "double")
            cmds.setAttr(f"FACE_TUNING.{faceattr}", e = True, keyable = True)
        
    ### R_ctrls & Mirroring
        mirr_grp = cmds.group(
                n = "R_nose_ctrls_mirror_GRP", empty = True, 
                parent = ctrl_socket)
        cmds.setAttr(mirr_grp+".sx", -1)
        rig.mirror_ctrls([nostril_buff], mirr_grp)
    
    # selection sets
        set_grp = [base, tip, nostril, nostril.replace("L_", "R_")]
        cmds.sets(set_grp, add = "nose")
        
    # cleanup
        util.mtx_zero([base, tip, nostril_buff, nostril], rsidetoo = True)
        
###### RIGGING ####################################################################
    def build_rig(self, joint_socket, ctrl_socket, lipcorners = None):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket)
        rig.sub_ctrl_vis(self.tip, self.base)
    # connect joint to ctrls
        for ctrl in [self.base, self.tip, 
            self.nostril, self.nostril.replace("L_", "R_")]:
            
            jnt = ctrl.replace("CTRL", "JNT")
            cmds.parentConstraint(
                    ctrl, jnt, mo = True, w = 1, n = jnt.replace("JNT", "PC"))
            cmds.scaleConstraint(
                    ctrl, jnt, offset = (1,1,1), w = 1, n = jnt.replace("JNT", "SCL"))
### MACRO uplip follow with tuner
    # MACRO lipcorner follow
        if not lipcorners:
            lipcorners = ["L_lipcorner_CTRL", "R_lipcorner_CTRL"]
        for lipc in lipcorners:
            side = lipc.split("_")[0]
            nostril_buff = side+"_nostril_macro_GRP"
            mult = cmds.shadingNode("multiplyDivide", 
                                    n = lipc.replace("CTRL", "nostrilMacro_MULT"), 
                                    au = True)
            cmds.connectAttr(lipc+".t", mult+".input1")
            cmds.setAttr("FACE_TUNING.lipcorner_follow", 0.05) # 5 % default
            cmds.connectAttr("FACE_TUNING.lipcorner_follow", mult+".input2X")
            cmds.connectAttr("FACE_TUNING.lipcorner_follow", mult+".input2Y")
            cmds.connectAttr("FACE_TUNING.lipcorner_follow", mult+".input2Z")
            cmds.connectAttr(mult+".output", nostril_buff+".t")
            
    ### clean up attributes - lock & hide
        util.lock(self.nostril, ["rx","ry","rz","sx","sy","sz"], rsidetoo = True)
        util.lock(self.tip, ["rx","ry","rz","sx","sy","sz"])

### missing:
    ### columella ctrl

if __name__ == "__main__":
    
    test = Nose()
    test.build_rig(
        joint_socket = "head_JNT", 
        ctrl_socket = "head_CTRL",
        lipcorners = ["L_lipcorner_macroOut_GRP", 
                      "R_lipcorner_macroOut_GRP"])
    cmds.hide("proxy_test_GRP")
    pass