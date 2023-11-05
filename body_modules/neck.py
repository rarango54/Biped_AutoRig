import maya.cmds as cmds

from body_proxies.proxyneck import ProxyNeck

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig
from utils import bendy


class Neck(object):
    
    def __init__(self):
        
        self.module_name = "neck"
        
        self.neck_1_jnt = "neck_1_JNT"
        self.neck_2_jnt = "neck_2_JNT"
        self.neck_3_jnt = "neck_3_JNT"
        self.neck_4_jnt = "neck_4_JNT"
        self.neck_5_jnt = "neck_5_JNT"
        # 5 joints in a straight line
        self.twist_jnt = "neck_twist_JNT"
        self.twist_end_jnt = "neck_twist_end_JNT"
        
        self.head_jnt = "head_JNT"
        self.head_end_jnt = "head_end_JNT"
        
        
        self.neck_ctrl = "neck_CTRL"
        self.neck_sub_ctrl = "neck_sub_CTRL"
        self.neckmid_ctrl = "neckmid_CTRL"
        self.head_ctrl = "head_CTRL"
        self.head_sub_ctrl = "head_sub_CTRL"
        
    
        
    def skeleton(self, joint_socket):
        pneck = ProxyNeck()
        neckchain = bendy.jointchain(
                mod_name = "neck", 
                number = 5, 
                start_obj = pneck.neck, 
                end_obj = pneck.head, 
                radius = 2, 
                rotord = "zyx", 
                orient = "vertical")
        cmds.sets(neckchain, add = "bind_joints")
        # add head_end_JNT
        he_pos = cmds.xform(pneck.head_end, q = True, 
                            translation = True, worldSpace = True)
        he = cmds.joint(
                n = self.head_end_jnt, position = he_pos, 
                radius = 2, rotationOrder = "zyx")
        cmds.sets(he, add = "joints")
        # last joint in chain = head joint -> reorient to world
        cmds.joint(
            neckchain[-1], e = True, 
            orientJoint = "yxz", secondaryAxisOrient = "xup", 
            children = False, zeroScaleOrient = False, radius = 4)
        # orient head_end to world
        cmds.joint(
            he, e = True, orientJoint = "none", 
            children = False, zeroScaleOrient = False)
        cmds.rename(neckchain[-1], self.head_jnt) # rename to head_jnt
        cmds.parent(neckchain[0], joint_socket)
        

    def controls(self, ctrl_socket):
        nsize = util.get_distance(self.neck_1_jnt, self.head_jnt)
        hsize = util.get_distance(self.head_jnt, self.head_end_jnt)
        # ctrl shapes
        neck = Nurbs.swoop_circle(self.neck_ctrl, nsize/3)
        neck_sub = Nurbs.swoop_circle(self.neck_sub_ctrl, nsize/3.5, "orange")
        neck_mid = Nurbs.double_circle(self.neckmid_ctrl, nsize/4)
        head = Nurbs.box(self.head_ctrl, hsize, hsize*1.5, hsize,
        "yellow", "xzy")
        head_sub = Nurbs.box(self.head_sub_ctrl, hsize/2.2, hsize/1.1, hsize/2.2,
        "orange", "xzy")
        
        relations = {
            neck :      (self.neck_1_jnt, ctrl_socket),
            neck_sub :  (self.neck_1_jnt, neck),
            neck_mid :  (self.neck_3_jnt, neck_sub),
            head :      (self.head_jnt, neck_sub),
            head_sub :  (self.head_jnt, head)
        }
        
        for ctrl in list(relations):
            cmds.matchTransform(ctrl, relations[ctrl][0], pos = True, rot = True)
            cmds.parent(ctrl, relations[ctrl][1])
        util.zero_transforms(list(relations))
        util.attr_separator([self.neck_ctrl, self.head_ctrl])
        rig.sub_ctrl_vis(self.neck_sub_ctrl)
        rig.sub_ctrl_vis(self.head_sub_ctrl)
        
        cmds.sets(neck, neck_sub, neck_mid, head, head_sub,
                  add = "neck_head")

    def build_rig(self, joint_socket, ctrl_socket, spaces):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket)
        
        # twistj = bendy.twist_setup(
        #         module_name = self.module_name,
        #         start = self.neck_1_jnt, 
        #         end = self.head_jnt, 
        #         driver = self.head_ctrl)
        bendy.ikspline(
            mod_name = self.module_name, 
            start = self.neck_1_jnt, 
            mid = self.neckmid_ctrl, 
            end = self.head_jnt, 
            forwardaxis = "y", 
            upaxis = "-z",
            base_ctrl = self.neck_sub_ctrl, 
            mid_ctrl = self.neckmid_ctrl, 
            end_ctrl = self.head_sub_ctrl)
        
        head_ikh = cmds.ikHandle(
                self.head_jnt,
                solver = "ikSCsolver",
                startJoint = self.head_jnt,
                endEffector = self.head_end_jnt,
                n = "head_IKH")
        cmds.rename(head_ikh[1], f"head_end_EFF")
        cmds.parent(head_ikh[0], self.head_ctrl)
        
        # point and aim for mid neck ctrl
        # head scale constraint or direct connect? if direct then global scl needs to be plugged in
        # head squetch? multiply dived node so that normal scale channels still work?
        # neck scl shouldn't affect head
        
        # add jaw joint temporarily for testing?
        
        # mid twist from mid_ctrl Ry possible?



if __name__ == "__main__":
    
    test2 = Module()
        
    pass