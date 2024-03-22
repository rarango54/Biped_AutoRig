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
    
    def __init__(self):
        
        # self.char_name = char_name
        # self.char_height = None
        
        self.main_grp = "rig_GRP"
        self.geo_grp = "geo_GRP"
        self.skeleton_grp = "skeleton_GRP"
        self.ctrls_grp = "bodyCtrls_GRP"
        self.joints_grp = "joints_GRP"
        self.misc_grp = "misc_GRP"
        self.corr_grp = "correctiveDrivers_GRP"
        self.other_grp = "other_ctrls_GRP"

        self.root_jnt = "root_JNT"
        self.global_ctrl = "global_CTRL"
        self.global_sub = "global_sub_CTRL"
        
        self.tuning_panel = "BODY_TUNING"
        
        self.setup()
        self.build_rig()
        
    def setup(self):
        if cmds.objExists(self.main_grp):
            return
        # initial outliner group hierarchy
        cmds.group(n = self.main_grp, em = True)
        cmds.group(n = self.tuning_panel, p = self.main_grp, em = True)
        cmds.group(n = self.geo_grp, p = self.main_grp, em = True)
        cmds.group(n = self.skeleton_grp, p = self.main_grp, em = True)
        cmds.group(n = self.ctrls_grp, p = self.skeleton_grp, em = True)
        cmds.group(n = self.joints_grp, p = self.skeleton_grp, em = True)
        cmds.group(n = self.misc_grp, p = self.skeleton_grp, em = True)
        cmds.group(n = self.corr_grp, p = self.misc_grp, em = True)
        
        all_grps = [self.main_grp, self.geo_grp, self.skeleton_grp, self.ctrls_grp,
                    self.joints_grp, self.misc_grp, self.tuning_panel]
        for node in all_grps:
            util.lock(node)
        
        cmds.select(cl=True)
        bj = cmds.sets(n = "bind_joints")
        hj = cmds.sets(n = "helper_joints") # last skinning polish layer
        js = cmds.sets(n = "joints")
        sp = cmds.sets(n = "spine")
        hn = cmds.sets(n = "neck_head")
        la = cmds.sets(n = "L_arm")
        ra = cmds.sets(n = "R_arm")
        lf = cmds.sets(n = "L_fingers")
        rf = cmds.sets(n = "R_fingers")
        ll = cmds.sets(n = "L_leg")
        rl = cmds.sets(n = "R_leg")
        cmds.sets([sp,hn,la,ra,lf,rf,ll,rl], n = "body_ctrls")
        
    
    def build_rig(self):
        # joint
        cmds.select(cl=True)
        cmds.joint(n=self.root_jnt, rad=4)
        cmds.parent(self.root_jnt, self.joints_grp)
        
        # ctrls
        Nurbs.double_circle(self.global_ctrl, 100)
        sub = Nurbs.arrow(self.global_sub, 80, "grass")
        sub_shape = cmds.listRelatives(sub, c=True, s=True)[0]
        cmds.parent(self.global_ctrl, self.ctrls_grp)
        cmds.parent(self.global_sub, self.global_ctrl)

        rig.sub_ctrl_vis(self.global_sub)
        
        # connections
        cmds.parentConstraint(
            self.global_sub, self.root_jnt, 
            w=1)
        cmds.scaleConstraint(
            self.global_sub, self.root_jnt, 
            o=(1,1,1), w=1)
        cmds.connectAttr(f"{self.global_ctrl}.scaleY", f"{self.global_ctrl}.scaleX")
        cmds.connectAttr(f"{self.global_ctrl}.scaleY", f"{self.global_ctrl}.scaleZ")
        cmds.setAttr(
            f"{self.global_ctrl}.scaleX", e = True, 
            lock = True, keyable = False, channelBox = False)
        cmds.setAttr(
            f"{self.global_ctrl}.scaleZ", e = True, 
            lock = True, keyable = False, channelBox = False)
        
        cmds.group(n = self.other_grp, em = True, parent = self.global_sub)
        
        # sets
        cmds.sets(self.root_jnt, add="joints")
        cmds.sets(self.global_ctrl, self.global_sub, add="body_ctrls")
        
        util.lock(self.global_sub, ["sx","sy","sz"])

if __name__ == "__main__":
    
    test = Base()
    
    pass