import maya.cmds as cmds

from utils import util
from misc import module_template as mt

from body_modules.base import Base
from body_modules.spine import Spine
from body_modules.arm import Arm


class BaseRig(object):
    
    def __init__(self, character_name):
        
        self.name = character_name


    def construct_proxy(self):
        module = mt.Module()
        module.proxy_rig()
    
    def delete_proxy(self):
        pass
    
    def construct_rig(self):
        module = mt.Module()
        module.rig("joint1", "nurbsCircle1", "nurbsCircle1")
    
    def delete_rig(self):
        pass


if __name__ == "__main__":
    
    BaseRig("Apollo").construct_proxy()
    Apollo.construct_proxy()
    Apollo.construct_rig()
    
    pass