import maya.cmds as cmds

from utils import util
from misc import module_template as mt

from body_modules.base import Base
from body_modules.spine import Spine
from body_modules.arm import Arms


class BaseRig(object):
    
    def __init__(self, char_name):
        
        self.char_name = char_name


    def construct_proxy(self):
        base = Base(self.char_name)
        spine = Spine()
        arms = Arms()
        # module = mt.Module()
        
        base.setup()
        base.build_proxy()
        spine.build_proxy(base.base_prx)
        arms.build_proxy(base.base_prx)
        # module.build_proxy(base.base_prx)
    
    def construct_rig(self):
        base = Base(self.char_name)
        spine = Spine()
        arms = Arms()
        
        base.build_rig()
        spine.build_rig(
            base.root_jnt, base.global_sub_ctrl, 
            [base.global_sub_ctrl])
        arms.build_rig(
            spine.chest_up_jnt, spine.chest_up_ctrl, base.global_sub_ctrl, 
            [base.global_sub_ctrl, spine.cog_sub_ctrl, spine.chest_up_ctrl])
            
        cmds.hide(base.base_prx)


if __name__ == "__main__":
    
    Apollo = BaseRig("Apollo")
    Apollo.construct_proxy()
    Apollo.construct_rig()
    
    base.root_jnt
    pass