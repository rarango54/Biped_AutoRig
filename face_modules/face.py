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
    
    def __init__(self, rignode, joint_socket, ctrl_socket):
        self.rignode = rignode
        self.joint_socket = joint_socket
        self.ctrl_socket = ctrl_socket
        
        self.main = "face_GRP"
        self.ctrls_grp = "faceCtrls_GRP"
        self.misc = "fmisc_GRP"

        self.tuning_panel = "FACE_TUNING"
        
        self.setup()
        
    def setup(self):
        if cmds.objExists(self.main):
            return
        # initial outliner group hierarchy
        cmds.group(n = self.main, p = self.rignode, em = True)
        cmds.group(n = self.tuning_panel, p = self.rignode, em = True)
        cmds.reorder(self.tuning_panel, front = True)
        cmds.group(n = self.ctrls_grp, p = self.main, em = True)
        cmds.group(n = self.misc, p = self.main, em = True)
        
        self.attach_ctrls()
        
        all_grps = [self.main, self.ctrls_grp,
                    self.misc, self.tuning_panel]
        for node in all_grps:
            util.lock(node)
        
        cmds.select(cl=True)
        bj = cmds.sets(n = "fbind_joints")
        hj = cmds.sets(n = "fhelper_joints") # last skinning polish layer
        js = cmds.sets(n = "fjoints")
        br = cmds.sets(n = "brows")
        li = cmds.sets(n = "lids")
        ey = cmds.sets(n = "eyes")
        ch = cmds.sets(n = "cheeks")
        mo = cmds.sets(n = "mouth") # includes teeth & tongue
        ns = cmds.sets(n = "nose")

        cmds.sets([br, li, ey, ch, mo, ns], n = "face_ctrls")
    
    def attach_ctrls(self):
        cmds.matchTransform(self.ctrl_socket, self.joint_socket, pos = True)
        util.mtx_zero(self.ctrl_socket)
        cmds.parentConstraint(self.ctrl_socket, self.ctrls_grp,
                              mo = True, w = 1)
        cmds.scaleConstraint(self.ctrl_socket, self.ctrls_grp,
                            offset = (1,1,1), w = 1)
        

if __name__ == "__main__":
    
    test = Face()
    test.setup()
    # test.build_proxy()
    
    # test.build_rig()
    
    
    pass