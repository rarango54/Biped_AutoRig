import maya.cmds as cmds

from body_proxies.proxyspine import ProxySpine

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig


class Module(object):
    
    def __init__(self):
        
        self.module_name = "spine"
        
        self.joint1_jnt = "joint1_JNT"
        self.joint2_jnt = "joint2_JNT"
        
        self.control1_ctrl = "control2_CTRL"
        self.control1_sub_ctrl = "control1_sub_CTRL"
        self.control2_ctrl = "control2_CTRL"
        
    
        
    def skeleton(self, joint_socket):
        pmodule = ProxyModule()
        rig.make_joints(list(self.proxy_dict)[1:], "zxy", 4)
        cmds.joint(
            self.hip_jnt, e=True,
            orientJoint = "yxz", secondaryAxisOrient = "xup", children = True)
        cmds.parent(self.hip_jnt, joint_socket)

    def controls(self, ctrl_socket, ik_ctrlparent):
        # create L_ctrls, mirror
        FK_ctrls = []
        IK_ctrls = []
        Switcher = []
        # R_ctrls & mirroring
        rig.mirror_ctrls([FK_ctrls], "R_armFK", ctrl_socket)
        rig.mirror_ctrls([IK_ctrls], "R_armIK", ik_ctrlparent)
        rig.mirror_ctrls([Switcher], "R_armSwitch", ik_ctrlparent)
        

    def build_rig(self, joint_socket, ctrl_socket, spaces):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket)
        # create all rig connections



if __name__ == "__main__":
    
    test2 = Module()
        
    pass