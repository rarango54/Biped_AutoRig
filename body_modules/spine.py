import maya.cmds as cmds

from body_proxies.proxyspine import ProxySpine

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig


class Spine(object):
    
    def __init__(self):
        
        self.module_name = "spine"
        
        self.hip_jnt = "hip_JNT"
        self.waist_jnt = "waist_JNT"
        self.chest_jnt = "chest_JNT"
        self.chest_up_jnt = "chest_up_JNT"
        
        self.fly_ctrl = "fly_CTRL"
        self.cog_ctrl = "cog_CTRL"
        self.body_ctrl = "body_CTRL"
        self.body_sub_ctrl = "body_sub_CTRL"
        self.hip_ctrl = "hip_CTRL"
        self.hip_sub_ctrl = "hip_sub_CTRL"
        self.waist_ctrl = "waist_CTRL"
        self.chest_ctrl = "chest_CTRL"
        self.chest_sub_ctrl = "chest_sub_CTRL"
        self.chest_up_ctrl = "chest_up_CTRL"
        self.spine_end_jnt = "spine_end_JNT"
        
        
    def skeleton(self, joint_socket):
        pspine = ProxySpine()
        spine_jnts = rig.make_joints(list(pspine.proxy_dict)[3:], "zxy", 4)
        cmds.joint(
            self.hip_jnt, e = True, 
            orientJoint = "yxz", secondaryAxisOrient = "xup", children = True)
        cmds.parent(self.hip_jnt, joint_socket)
        
        cmds.sets(spine_jnts, add = "bind_joints")

    def controls(self, ctrl_socket):
        size = util.get_distance(self.hip_jnt, self.chest_up_jnt)/2
        body = Nurbs.box(self.body_ctrl, 
                size*1.5, size/2, size*1.2, "yellow", "zxy")
        body_sub = Nurbs.box(self.body_sub_ctrl,
                size*1.8, size/4, size*1.5, "pink", "zxy")
        # cmds.matchTransform([body, body_sub], "body_PRX", pos=True)
        # cmds.parent(body_sub, body)
        
        hip = Nurbs.swoop_circle(self.hip_ctrl, size*0.75, "brown", "yzx")
        waist = Nurbs.stack_circles(self.waist_ctrl, size, "brown", "zxy")
        chest = Nurbs.swoop_circle(self.chest_ctrl, size, "yellow", "zyx")
        chest_sub = Nurbs.swoop_circle(self.chest_sub_ctrl, size*0.9, "pink", "zyx")
        chest_up = Nurbs.swoop_circle(self.chest_up_ctrl, size*0.75, "brown", "zyx")
        
        relations = {
            body : ("body_PRX", ctrl_socket),
            body_sub : ("body_PRX", self.body_ctrl),
            hip : ("hip_PRX", self.body_sub_ctrl),
            waist : ("waist_PRX", self.body_sub_ctrl),
            chest: ("chest_PRX", self.body_sub_ctrl),
            chest_sub : ("chest_PRX", self.chest_ctrl),
            chest_up : ("chest_up_PRX", self.chest_sub_ctrl)
        }
        
        for ctrl in list(relations):
            cmds.matchTransform(ctrl, relations[ctrl][0], pos=True)
            cmds.parent(ctrl, relations[ctrl][1])
        util.zero_transforms(list(relations))
        
        # separators?
        rig.sub_ctrl_vis(self.body_sub_ctrl)
        rig.sub_ctrl_vis(self.chest_sub_ctrl)
        
        cmds.sets(body, body_sub, hip, waist, 
                chest, chest_sub, chest_up,
                add="spine")

    def build_rig(self, joint_socket, ctrl_socket, spaces):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket)
        
        waist_buff = util.buffer_grp(self.waist_ctrl)
        cmds.orientConstraint(
            [self.chest_sub_ctrl, self.hip_ctrl], waist_buff,
            o=(0,0,0), sk=("x", "z"), w=1)
        util.zero_transforms(self.waist_ctrl)
        
        connections = {
            self.hip_ctrl : self.hip_jnt,
            self.waist_ctrl : self.waist_jnt,
            self.chest_sub_ctrl : self.chest_jnt,
            self.chest_up_ctrl : self.chest_up_jnt
        }
        
        for ctrl in list(connections):
            jnt = connections[ctrl]
            cmds.parentConstraint(ctrl, jnt, w=1)
            cmds.scaleConstraint(ctrl, jnt, o=(1,1,1), w=1)



if __name__ == "__main__":
    
    
    test2 = Spine()
    
    test2.build_proxy("global_PRX")
    test2.build_rig("root_JNT", "global_sub_CTRL", "global_sub_CTRL")
    
    pass