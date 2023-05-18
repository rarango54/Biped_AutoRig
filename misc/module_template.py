import maya.cmds as cmds

from utils.ctrl_library import Control
from utils import util
from utils import rig


class Module(object):
    
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
                [0, 112.5, 0], "sphere", 3, "sky", 
                ["tx","r","s"]),
            "chest_PRX" : (
                [0, 125, 0], "sphere", 3, "sky", 
                ["tx","r","s"]),
            "chest_up_PRX" : (
                [0, 140, 0], "sphere", 3, "sky", 
                ["tx","r","s"]),
            "spine_end_PRX" : (
                [0, 155, 0], "cube", 3, "sky", 
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
            buff = util.buffer_grp(i)
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
        # create L_ctrls, mirror
        pass

    def build_rig(self, joint_socket, ctrl_socket, spaces):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket)
        # create all rig connections



if __name__ == "__main__":
    
    
    test2 = Module()
    
    test2.build_proxy("global_PRX")
    # list(test2.proxy_dict)[2:]
    # test2.build_rig("root_JNT", "global_sub_CTRL", "global_sub_CTRL")
    
    pass