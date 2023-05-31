import maya.cmds as cmds

from utils.ctrl_library import Control
from utils import util
from utils import rig


class Spine(object):
    
    def __init__(self):
        
        self.module_name = "spine"
        
        self.hip_jnt = "hip_JNT"
        self.waist_jnt = "waist_JNT"
        self.chest_jnt = "chest_JNT"
        self.chest_up_jnt = "chest_up_JNT"
        
        self.cog_ctrl = "cog_CTRL"
        self.cog_sub_ctrl = "cog_sub_CTRL"
        self.hip_ctrl = "hip_CTRL"
        self.hip_sub_ctrl = "hip_sub_CTRL"
        self.waist_ctrl = "waist_CTRL"
        self.chest_ctrl = "chest_CTRL"
        self.chest_sub_ctrl = "chest_sub_CTRL"
        self.chest_up_ctrl = "chest_up_CTRL"
        
        self.proxy_dict = {
            "cog_PRX" : (
                [0, 100, 0], "cube", 10, "yellow", 
                ["tx","ry","rz","s"]),
            "hip_PRX" : (
                [0, 100, 0], "cube", 5, "sky", 
                ["tx","r","s"]),
            "waist_PRX" : (
                [0, 112.5, 0], "sphere", 2, "sky", 
                ["tx","r","s"]),
            "chest_PRX" : (
                [0, 125, 0], "sphere", 2, "sky", 
                ["tx","r","s"]),
            "chest_up_PRX" : (
                [0, 140, 0], "sphere", 2, "sky", 
                ["tx","r","s"]),
            "spine_end_PRX" : (
                [0, 155, 0], "octahedron", 2, "sky", 
                ["tx","r","s"])
        }
    
    def build_proxy(self, proxy_socket):
        proxies = rig.make_proxies(self.proxy_dict, 
            proxy_socket, self.module_name)
        # hip & spine end drive the 3 middle spine proxies
        hip = proxies[1]
        end = proxies[-1]
        for nr, i in enumerate(proxies[2:-1]):
            cmds.parent(i, hip)
            buff = util.buffer_grp(i, "buffer_prx_GRP")
            pc = cmds.pointConstraint((end, hip), buff, 
                n=i.replace("PRX", "POINT"))[0]
            w0 = (nr+1)*0.25
            w1 = 1-w0
            cmds.setAttr(f"{pc}.{end}W0", w0)
            cmds.setAttr(f"{pc}.{hip}W1", w1)
        cmds.parent((hip, end), proxies[0])
        
        rig.proxy_lock(self.proxy_dict)
        
    def skeleton(self, joint_socket):
        rig.make_joints(list(self.proxy_dict)[1:], "zxy", 4)
        cmds.joint(self.hip_jnt, 
            e=True, oj="yxz", sao="xup", ch=True, zso=True)
        cmds.parent(self.hip_jnt, joint_socket)

    def controls(self, ctrl_socket):
        size = util.get_distance(self.hip_jnt, self.chest_up_jnt)/2
        cog = Control.box(self.cog_ctrl, 
                size*1.5, size/2, size*1.2, "yellow", "zxy")
        cog_sub = Control.box(self.cog_sub_ctrl,
                size*1.8, size/4, size*1.5, "pink", "zxy")
        # cmds.matchTransform([cog, cog_sub], "cog_PRX", pos=True)
        # cmds.parent(cog_sub, cog)
        
        hip = Control.swoop_circle(self.hip_ctrl, size*0.75, "brown", "yzx")
        waist = Control.stack_circles(self.waist_ctrl, size, "brown", "zxy")
        chest = Control.swoop_circle(self.chest_ctrl, size, "yellow", "zyx")
        chest_sub = Control.swoop_circle(self.chest_sub_ctrl, size*0.9, "pink", "zyx")
        chest_up = Control.swoop_circle(self.chest_up_ctrl, size*0.75, "brown", "zyx")
        
        relations = {
            cog : ("cog_PRX", ctrl_socket),
            cog_sub : ("cog_PRX", self.cog_ctrl),
            hip : ("hip_PRX", self.cog_sub_ctrl),
            waist : ("waist_PRX", self.cog_sub_ctrl),
            chest: ("chest_PRX", self.cog_sub_ctrl),
            chest_sub : ("chest_PRX", self.chest_ctrl),
            chest_up : ("chest_up_PRX", self.chest_sub_ctrl)
        }
        
        for ctrl in list(relations):
            cmds.matchTransform(ctrl, relations[ctrl][0], pos=True)
            cmds.parent(ctrl, relations[ctrl][1])
        util.zero_transforms(list(relations))
        
        # separators?
        rig.sub_ctrl_vis(self.cog_sub_ctrl)
        rig.sub_ctrl_vis(self.chest_sub_ctrl)
        
        cmds.sets(cog, cog_sub, hip, waist, 
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