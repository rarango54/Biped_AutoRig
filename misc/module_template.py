import maya.cmds as cmds

from utils import ctrl_library
from utils import util


class Module(object):
    
    def __init__(self):
        
        self.name = "spine"
        
        self.hip_jnt = "hip_JNT"
        self.joint2_jnt = None
        self.joint3_jnt = None
        self.joint4_up_jnt = None
        
        self.hip_ctrl = "hip_CTRL"
        self.hip_sub_ctrl = "hip_sub_CTRL"
        self.ctrl2_ctrl = None
        self.ctrl3_ctrl = None
        self.ctrl4_ctrl = None
        self.ctrl4_sub_ctrl = None
        
        self.proxy_dict = {
            "hip_PRX":   [0, 100, 0],
            "loc2":   [0, 110, 0],
            "loc3":   [0, 120, 0],
            "loc4":   [0, 140, 0],
        }
    
    def proxy_rig(self):
        group = cmds.group(n=f"{self.name}_proxy_GRP", em=True)
        proxy = util.make_proxies(self.proxy_dict, group)
        # create a hacky rig with limited transforms, make buffer grps, constraints, etc.
        cmds.pointConstraint([proxy[0], proxy[-1]], proxy[1], mo=True, w=1)
    
    def skeleton(self, joint_socket):
        cmds.select(cl=True)
        for key in self.proxy_dict:
            fitted_pos = cmds.xform(key, q=True, t=True, ws=True)
            cmds.joint(n=key.replace("PRX", "JNT"), p=fitted_pos, roo="zxy")
            
            
        pass
    
    def controls(self, ctrl_socket):
        # create L_ctrls, mirror
        pass

    def rig(self, joint_socket, ctrl_socket, spaces):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket)
        # create all rig connections



if __name__ == "__main__":
    
    test = Module()

    test.proxy_rig()
    test.rig("joint1", "nurbsCircle1", "nurbsCircle1")
            
    
    pass