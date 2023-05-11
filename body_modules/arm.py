import maya.cmds as cmds

from utils import util
from utils import ctrl_library


class Arm(object):
    
    def __init__(self, joint_socket, ctrl_socket):
        
        # downstream output
        # joint sockets
        self.up_arm_jnt = None
        self.elbow_jnt = None
        self.wrist_jnt = None
        # ctrl sockets / spaces
        self.up_armFK_ctrl = None
        self.elbowFK_ctrl = None
        self.handFK_ctrl = None
        self.handIK_ctrl = None
        self.up_chest_ctrl = None
        # scale inversion?
        
        # internal vars
        self.name = "module name"
        
        self.waist_jnt = None
        self.chest_jnt = None
        self.spine_end_jnt = None
        
        self.waist_ctrl = None
        
        self.proxy_dict = {
            "clavicle"  :   [0.02, 1.6, 0.05],
            "upArm"     :   [0.2, 1.6, 0],
            "elbow"     :   [0.4, 1.6, 0],
            "wrist"     :   [0.6, 1.6, 0]
        }
        
        # __init__ functions
        self.build_proxy()


    def build_proxy():
        
        pass
    
    def skeleton():
        
        pass
    
    def controls():
        
        pass

    def rig():
        
        pass



if __name__ == "__main__":
    
    
    
    pass