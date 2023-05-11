import maya.cmds as cmds
import sys

from utils import ctrl_library
from utils import util


class Spine(object):
    
    def __init__(self, joint_socket, ctrl_socket):

        # downstream output
        self.breath_jnt = None
        # joint sockets
        self.hip_jnt = None
        self.up_chest_jnt = None
        # ctrl sockets / spaces
        self.body_ctrl = None
        self.hip_ctrl = None
        self.chest_ctrl = None
        self.up_chest_ctrl = None
        
        # internal vars
        self.name = "spine"
        
        self.waist_jnt = None
        self.chest_jnt = None
        self.spine_end_jnt = None
        
        self.waist_ctrl = None
        self.hip_sub_ctrl = None
        self.chest_sub_ctrl = None
        
        self.proxy_dict = {
            "hip"       :   [0, 1, 0],
            "waist"     :   [0, 1.15, 0],
            "chest"     :   [0, 1.3, 0],
            "upChest"   :   [0, 1.5, 0]
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
        
    #for i in sys.path:
        #print(i)