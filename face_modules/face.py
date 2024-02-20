import maya.cmds as cmds

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig



class Face(object):
    """
    Naming Convention: {side}_{component}_#_{obj type}
    e.g. L_index_3_JNT
    
    Class attrs should provide downstream with 
    sockets (connection points), parents and spaces
    """
    
    def __init__(self):
        
        # self.char_name = char_name
        # self.char_height = None
        
        self.main_grp = "face_GRP"
        self.skeleton_grp = "fskeleton_GRP"
        self.ctrls_grp = "faceCtrls_GRP"
        self.joints_grp = "fjoints_GRP"
        self.misc_grp = "fmisc_GRP"

        self.root_jnt = "root_JNT"
        
        self.tuning_panel = "FACE_TUNING"
                
        
    def setup(self):
        if cmds.objExists(self.main_grp):
            return
        # initial outliner group hierarchy
        cmds.group(n = self.main_grp, em = True)
        cmds.group(n = self.tuning_panel, p = self.main_grp, em = True)
        cmds.group(n = self.skeleton_grp, p = self.main_grp, em = True)
        cmds.group(n = self.ctrls_grp, p = self.skeleton_grp, em = True)
        cmds.group(n = self.joints_grp, p = self.skeleton_grp, em = True)
        cmds.group(n = self.misc_grp, p = self.skeleton_grp, em = True)
        
        all_grps = [self.main_grp, self.skeleton_grp, self.ctrls_grp,
                    self.joints_grp, self.misc_grp, self.tuning_panel]
        for node in all_grps:
            util.lock(node)
        
        cmds.select(cl=True)
        bj = cmds.sets(n = "fbind_joints")
        hj = cmds.sets(n = "fhelper_joints") # last skinning polish layer
        js = cmds.sets(n = "fjoints")
        br = cmds.sets(n = "brows")
        li = cmds.sets(n = "lids")
        ch = cmds.sets(n = "cheeks")
        mo = cmds.sets(n = "mouth") # includes teeth & tongue
        ns = cmds.sets(n = "nose")

        cmds.sets([br, li, ch, mo, ns], n = "face_ctrls")
        

if __name__ == "__main__":
    
    test = Face()
    test.setup()
    # test.build_proxy()
    
    # test.build_rig()
    
    
    pass