import maya.cmds as cmds

from utils import ctrl_library
from utils import util


class Base(object):
    """
    Naming Convention: {side}_{component}_#_{obj type}
    e.g. L_index_3_JNT
    
    Class attrs should provide downstream with sockets (connection points), parents and spaces
    """
    
    def __init__(self, character_name):

        self.ctrls_grp = None
        self.joints_grp = None
        self.misc_grp = None
        self.base_jnt = None
        self.global_ctrl = None
        
        
        self.name = None
        self.geo_grp = None
        self.main_grp = None
        self.skeleton_grp = None

        
    
    def setup(self, name):
        self.name = name
        # initial outliner group hierarchy
        self.main_grp = cmds.group(n=f"{self.name}_GRP", em=True)
        self.skeleton_grp = cmds.group(n="skeleton_GRP", p=self.main_grp, em=True)
        self.ctrls_grp = cmds.group(n="ctrls_GRP", p= self.skeleton_grp, em=True)
        self.joints_grp = cmds.group(n="joints_GRP", p=self.skeleton_grp, em=True)
        self.misc_grp = cmds.group(n="misc_GRP", p=self.skeleton_grp, em=True)
        
        # sets for bind joints, ctrls

    def build_proxy(self):
        pass
    
    def build_rig(self):
        pass
    

if __name__ == "__main__":
    
    sp = spine.Spine()
    print(sp.hip_jnt)
    print(sp.main_grp)
    
    pass