import maya.cmds as cmds

from body_proxies.proxyleg import ProxyLeg

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig


class Legs(object):
    
    def __init__(self):
        
        self.module_name = "L_leg"
        
        self.upleg_jnt = "L_upleg_JNT"
        self.knee_jnt = "L_knee_JNT"
        self.lowleg_jnt = "L_lowleg_JNT"
        self.foot_jnt = "L_foot_JNT"
        self.toes_jnt = "L_toes_JNT"
        self.toes_end_jnt = "L_toes_end_JNT"
        
        self.upleg_FK_ctrl = "L_upleg_FK_CTRL"
        self.knee_FK_grp = "L_knee_FK_GRP"
        self.lowleg_FK_ctrl = "L_lowleg_FK_CTRL"
        self.foot_FK_ctrl = "L_foot_FK_CTRL"
        self.toes_FK_ctrl = "L_toes_FK_CTRL"
        
        self.foot_IK_ctrl = "L_foot_IK_CTRL"
        self.pole_vector_ctrl = "L_legIK_PV_CTRL"
        
        self.switcher_ctrl = "L_leg_switcher_CTRL"
    
        
    def skeleton(self, joint_socket):
        pleg = ProxyLeg()
        leg_jnts = rig.make_joints(list(pleg.proxy_dict)[:-2], "yxz", 3)
        cmds.joint(
            self.upleg_jnt, e=True,
            orientJoint = "yxz", secondaryAxisOrient = "xup", children = True)
        cmds.parent(self.upleg_jnt, joint_socket)
        
        mirr_jnts = cmds.mirrorJoint(
                self.upleg_jnt, 
                mirrorYZ = True, 
                mirrorBehavior = True, 
                searchReplace = ["L_", "R_"])
        # except end_JNT
        cmds.sets(leg_jnts[:-1], add = "bind_joints")
        cmds.sets(mirr_jnts[:-1], add = "bind_joints")

    def controls(self, ctrl_socket, ik_ctrlparent):
        # create L_ctrls, mirror
        # FK_ctrls = []
        # IK_ctrls = []
        # Switcher = []
        # R_ctrls & mirroring
        # rig.mirror_ctrls([FK_ctrls], "R_armFK", ctrl_socket)
        # rig.mirror_ctrls([IK_ctrls], "R_armIK", ik_ctrlparent)
        # rig.mirror_ctrls([Switcher], "R_armSwitch", ik_ctrlparent)
        pass
        

    def build_rig(self, joint_socket, ctrl_socket, ik_ctrlparent, spaces):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket, ik_ctrlparent)
        # create all rig connections



if __name__ == "__main__":
    
    test2 = Module()
        
    pass