import maya.cmds as cmds

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig



class Base(object):
    """
    Naming Convention: {side}_{component}_#_{obj type}
    e.g. L_index_3_JNT
    
    Class attrs should provide downstream with 
    sockets (connection points), parents and spaces
    """
    
    def __init__(self, char_name):
        
        self.char_name = char_name
        self.char_height = None
        
        self.main_grp = f"{self.char_name}_GRP"
        self.geo_grp = "geo_GRP"
        self.skeleton_grp = "skeleton_GRP"
        self.ctrls_grp = "ctrls_GRP"
        self.joints_grp = "joints_GRP"
        self.misc_grp = "misc_GRP"

        self.root_jnt = "root_JNT"
        self.global_ctrl = "global_CTRL"
        self.global_sub_ctrl = "global_sub_CTRL"
                
        
    def setup(self):
        if cmds.objExists(self.main_grp):
            return
        # initial outliner group hierarchy
        cmds.group(n=self.main_grp, em=True)
        cmds.group(n=self.geo_grp, p=self.main_grp, em=True)
        cmds.group(n=self.skeleton_grp, p=self.main_grp, em=True)
        cmds.group(n=self.ctrls_grp, p= self.skeleton_grp, em=True)
        cmds.group(n=self.joints_grp, p=self.skeleton_grp, em=True)
        cmds.group(n=self.misc_grp, p=self.skeleton_grp, em=True)
        
        cmds.select(cl=True)
        bj = cmds.sets(n="bind_joints")
        js = cmds.sets(n="joints")
        sp = cmds.sets(n="spine")
        hn = cmds.sets(n="neck_head")
        la = cmds.sets(n="L_arm")
        ra = cmds.sets(n="R_arm")
        lf = cmds.sets(n="L_fingers")
        rf = cmds.sets(n="R_fingers")
        ll = cmds.sets(n="L_leg")
        rl = cmds.sets(n="R_leg")
        cmds.sets([sp,hn,la,ra,lf,rf,ll,rl], n="body_ctrls")
        
    
    def build_rig(self):
        # joint
        cmds.select(cl=True)
        cmds.joint(n=self.root_jnt, rad=4)
        cmds.parent(self.root_jnt, self.joints_grp)
        
        # ctrls
        Nurbs.double_circle(self.global_ctrl, 100)
        sub = Nurbs.arrow(self.global_sub_ctrl, 80, "grass")
        sub_shape = cmds.listRelatives(sub, c=True, s=True)[0]
        cmds.parent(self.global_ctrl, self.ctrls_grp)
        cmds.parent(self.global_sub_ctrl, self.global_ctrl)

        rig.sub_ctrl_vis(self.global_sub_ctrl)
        
        # connections
        cmds.parentConstraint(
            self.global_sub_ctrl, self.root_jnt, 
            w=1)
        cmds.scaleConstraint(
            self.global_sub_ctrl, self.root_jnt, 
            o=(1,1,1), w=1)
        cmds.connectAttr(f"{self.global_ctrl}.scaleY", f"{self.global_ctrl}.scaleX")
        cmds.connectAttr(f"{self.global_ctrl}.scaleY", f"{self.global_ctrl}.scaleZ")
        cmds.setAttr(
            f"{self.global_ctrl}.scaleX", e = True, 
            lock = True, keyable = False, channelBox = False)
        cmds.setAttr(
            f"{self.global_ctrl}.scaleZ", e = True, 
            lock = True, keyable = False, channelBox = False)
        
        # sets
        cmds.sets(self.root_jnt, add="joints")
        cmds.sets(self.global_ctrl, self.global_sub_ctrl, add="body_ctrls")

if __name__ == "__main__":
    
    test = Base("Apollo")
    test.setup()
    # test.build_proxy()
    
    # test.build_rig()
    
    
    pass