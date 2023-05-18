import maya.cmds as cmds

from utils.ctrl_library import Control
from utils import util
from utils import rig


class Arm(object):
    
    def __init__(self, side):
        
        self.side = side
        self.module_name = f"{self.side}_arm"
        
        self.clavicle_jnt = f"{self.side}_clavicle_JNT"
        self.up_arm_jnt = f"{self.side}_upArm_JNT"
        self.elbow_jnt = f"{self.side}_elbow_JNT"
        self.hand_jnt = f"{self.side}_hand_JNT"
        self.hand_end_jnt = f"{self.side}_handEnd_JNT"

        self.clavicle_ctrl = f"{self.side}_clavicle_CTRL"
        self.up_armFK_ctrl = f"{self.side}_upArmFK_CTRL"
        self.elbowFK_ctrl = f"{self.side}_elbowFK_CTRL"
        self.handFK_ctrl = f"{self.side}_handFK_CTRL"
        self.handIK_ctrl = f"{self.side}_handIK_CTRL"
        self.pole_vector_ctrl = f"{self.side}_armIK_PV_CTRL"
        
        self.proxy_dict = {
            f"{self.side}_clavicle_PRX" : (
                [3, 145, 10], "sphere", 1.5, "green", 
                ["r","s"]),
            f"{self.side}_up_arm_PRX" : (
                [15, 150, 0], "cube", 5, "grass", 
                ["rx","s"]),
            f"{self.side}_elbow_PRX" : (
                [45, 150, -5], "sphere", 2, "grass", 
                ["ty","r","s"]),
            f"{self.side}_hand_PRX" : (
                [75, 150, 0], "sphere", 3, "grass", 
                ["s"]),
            f"{self.side}_handEnd_PRX" : (
                [85, 150, 0], "sphere", 1.2, "grass", 
                ["tx","ty","r","s"]),
            f"{self.side}_poleVector_PRX" : (
                [45, 150, -65], "arrow", 4, "grass", 
                ["t","r","s"])
        }


    def build_proxy(self, proxy_socket):
        proxies = rig.make_proxies(self.proxy_dict, 
            proxy_socket, self.module_name)
        up_arm = proxies[1]
        elbow = proxies[2]
        hand = proxies[3]
        hand_end = proxies[4]
        pv = proxies[-1]
        cmds.parent(hand_end, hand)
        cmds.parent(pv, elbow)
        elbow_buff = util.buffer_grp(proxies[2])
        
        pc = cmds.pointConstraint((hand, up_arm), elbow_buff, mo=True,
                n=elbow.replace("PRX", "POINT"))[0]
        oc = cmds.orientConstraint(up_arm, elbow_buff, mo=True,
                n=elbow.replace("PRX", "ORIENT"))[0]
        ac = cmds.aimConstraint(hand, up_arm, aim=(1,0,0), u=(0,1,0), wut="scene")
        
        hand_end_ori = cmds.group(n=hand.replace("PRX", "Ori_GRP"), 
                            p=hand, r=True, em=True)
        hoc = cmds.orientConstraint(up_arm, hand_end_ori, mo=True,
                n=hand_end.replace("PRX", "ORIENT"))[0]
        cmds.parent(hand_end, hand_end_ori)
                
        rig.proxy_lock(self.proxy_dict)
        
    def skeleton(self, joint_socket):
        rig.make_joints(list(self.proxy_dict)[0:-1], "zxy", 3)
        cmds.joint(self.clavicle_jnt, 
            e=True, oj="zyx", sao="yup", ch=True, zso=True)
        cmds.parent(self.clavicle_jnt, joint_socket)

    def controls(self, ctrl_socket):
        # create L_ctrls, mirror
        pass

    def build_rig(self, joint_socket, ctrl_socket, spaces):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket)
        # create all rig connections



if __name__ == "__main__":
    
    
    L_arm = Arm('L')
    L_arm.build_proxy("global_PRX")
    L_arm.build_rig("chest_up_JNT", "chest_up_CTRL", 
        ["cog_sub_CTRL", "chest_up_CTRL"])