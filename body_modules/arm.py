import maya.cmds as cmds

from utils.ctrl_library import Control
from utils import util
from utils import rig


class Arms(object):
    
    def __init__(self):

        self.module_name = "L_arm"
        
        self.clavicle_jnt = "L_clavicle_JNT"
        self.shoulder_jnt = "L_shoulder_JNT"
        self.elbow_jnt = "L_elbow_JNT"
        self.hand_jnt = "L_hand_JNT"
        self.hand_end_jnt = "L_handEnd_JNT"

        self.clavicle_ctrl = "L_clavicle_CTRL"
        self.shoulderFK_ctrl = "L_shoulderFK_CTRL"
        self.elbowFK_ctrl = "L_elbowFK_CTRL"
        self.handFK_ctrl = "L_handFK_CTRL"
        self.handIK_ctrl = "L_handIK_CTRL"
        self.wristIK_ctrl = "L_wristIK_CTRL"
        self.pole_vector_ctrl = "L_armIK_PV_CTRL"
        self.switcher_ctrl = "L_arm_switcher_CTRL"
        
        self.finger_socket_prx = "L_hand_Apose_PRX"
        self.pole_vector_prx = "L_poleVector_PRX"
        
        self.proxy_dict = {
            "L_clavicle_PRX" : (
                [3, 145, 10], "sphere", 1, "green", 
                ["r","s"]),
            "L_shoulder_PRX" : (
                [15, 150, 0], "cube", 1, "grass", 
                ["t","r","s"]),
            "L_elbow_PRX" : (
                [45, 150, -5], "sphere", 0.5, "grass", 
                ["t","r","s"]),
            "L_hand_PRX" : (
                [75, 150, 0], "octahedron", 0.5, "grass", 
                ["t", "r", "s"]),
            "L_handEnd_PRX" : (
                [85, 150, 0], "sphere", 0.5, "grass", 
                ["t","r","s"]),
            "L_poleVector_PRX" : (
                [45, 150, -65], "arrow", 1.5, "grass", 
                ["t","r","s"]),
                
            "L_shoulder_Apose_PRX" : (
                [15, 150, 0], "cube", 2.5, "green", 
                ["r","s"]),
            "L_elbow_Apose_PRX" : (
                [45, 150, -5], "sphere", 1.5, "green", 
                ["ty","r","s"]),
            "L_hand_Apose_PRX" : (
                [75, 150, 0], "octahedron", 1.5, "green", 
                ["s"]),
            "L_poleVector_Apose_PRX" : (
                [45, 150, -65], "arrow", 3, "green", 
                ["t","r","s"]),
        }


    def build_proxy(self, proxy_socket):
        proxies = rig.make_proxies(self.proxy_dict, 
            proxy_socket, self.module_name)
        # A Pose drivers:
        Ashoulder = proxies[6]
        Aelbow = proxies[7]
        Ahand = proxies[8]
        Apv = proxies[9]
        # T Pose targets for skeleton build:
        shoulder = proxies[1]
        elbow = proxies[2]
        hand = proxies[3]
        hand_end = proxies[4]
        pv = proxies[5]
        
        # match joints' future orientation
        for i in proxies:
            if i == pv or Apv:
                continue
            cmds.rotate(0,90,0, i)
        
        Aelbow_buff = util.buffer_grp(Aelbow)
        cmds.parent(Apv, Aelbow_buff)
        cmds.connectAttr(f"{Aelbow}.tx", f"{Apv}.tx")
        
        Ashould_aim = cmds.group(n=Ashoulder.replace("PRX", "handAim_GRP"),
            em=True, p=Ashoulder)
        cmds.parent(Ashould_aim, f"{self.module_name}_proxy_GRP")
        cmds.aimConstraint(Ahand, Ashould_aim, n=Ashould_aim.replace("GRP", "AIM"),
            aim=(0,0,1), u=(0,1,0), wut="scene")
        cmds.orientConstraint(Ashould_aim, Aelbow_buff, mo=True,
            n=Aelbow.replace("PRX", "ORIENT"))
        cmds.aimConstraint(Ahand, Aelbow, n=Aelbow.replace("PRX", "AIM"),
            aim=(0,0,1), u=(0,1,0), wut="scene")
        cmds.pointConstraint((Ahand, Ashoulder), Aelbow_buff, mo=True,
            n=Aelbow.replace("PRX", "POINT"))
        cmds.aimConstraint(Aelbow, Ashoulder, n=Ashoulder.replace("PRX", "AIM"),
            aim=(0,0,1), u=(0,1,0), wut="scene")
        cmds.orientConstraint(Ashould_aim, Ahand, mo=False,
            n=Ahand.replace("PRX", "ORIENT"))
        
        should_buff = util.buffer_grp(shoulder)
        cmds.pointConstraint(Ashoulder, should_buff, mo=False,
            n=shoulder.replace("PRX", "POINT"))
        
        
        elbow_buff = util.buffer_grp(elbow)
        cmds.pointConstraint((hand, shoulder), elbow_buff, mo=True,
                n=Aelbow.replace("PRX", "POINT"))[0]
        cmds.aimConstraint(elbow, shoulder, n=shoulder.replace("PRX", "AIM"),
            aim=(0,0,1), u=(0,1,0), wut="scene")
        cmds.aimConstraint(hand, elbow, n=elbow.replace("PRX", "AIM"),
            aim=(0,0,1), u=(0,1,0), wut="scene")
                
        cmds.parent(hand_end, hand)
        cmds.parent(hand, should_buff)
        cmds.parent(pv, elbow_buff)
        
        # Tpose should match Apose layout but in a straight line
        dist = cmds.shadingNode("distanceBetween", 
                n="L_armLen_DIST", au=True)
        cmds.connectAttr(
            f"{Ashoulder}.worldMatrix[0]", f"{dist}.inMatrix1")
        cmds.connectAttr(
            f"{Ahand}.worldMatrix[0]", f"{dist}.inMatrix2")
        cmds.connectAttr(f"{Aelbow}.tx", f"{elbow}.tx")
        cmds.connectAttr(f"{Aelbow}.tz", f"{elbow}.tz")
        
        # connect global scale
        mult = cmds.shadingNode("multDoubleLinear",
                n="L_armLen_MDL", au=True)
        inv = cmds.shadingNode("multiplyDivide",
                n="L_armLen_MD", au=True)
        cmds.setAttr(f"{inv}.input1X", 1)
        cmds.setAttr(f"{inv}.operation", 2)
        cmds.connectAttr(f"{proxy_socket}.sy", f"{inv}.input2X")
        cmds.connectAttr(f"{inv}.outputX", f"{mult}.input2")
        
        cmds.connectAttr(f"{dist}.distance", f"{mult}.input1")
        cmds.connectAttr(f"{mult}.output", f"{hand}.tx")
        
        rig.proxy_lock(self.proxy_dict)
        
        # could hide T pose proxies if stable?
        
    def skeleton(self, joint_socket):
        arm_jnts = rig.make_joints(list(self.proxy_dict)[0:5], "zxy", 1.5)
        # clavicle joint needs to have specific orient
        cmds.joint(self.clavicle_jnt, e=True, oj="none", zso=True)
        cmds.parent(self.shoulder_jnt, joint_socket)
        cmds.setAttr(f"{self.clavicle_jnt}.jointOrientY", 90)
        cmds.parent(self.shoulder_jnt, self.clavicle_jnt)
        # rest of arm joint orient
        cmds.joint(self.shoulder_jnt, e=True, 
                   oj="zyx", sao="yup", ch=True, zso=True)
        cmds.parent(self.clavicle_jnt, joint_socket)
        cmds.mirrorJoint(self.clavicle_jnt, myz=True, mb=True, sr=["L_", "R_"])

    def controls(self, ctrl_socket, ik_space):
        fk = [self.clavicle_jnt, self.shoulder_jnt, 
            self.elbow_jnt, self.hand_jnt, self.hand_end_jnt]
        fk_ro = "zyx"
        fk_size = util.get_distance(self.shoulder_jnt, self.elbow_jnt)/5
        
        # clavicle ctrl
        # is not in the fk hierarchy
        dist = util.get_distance(self.clavicle_jnt, self.shoulder_jnt)
        clav = Control.shoulder(self.clavicle_ctrl, dist, "blue", fk_ro)
        clav_driver = cmds.group(
            n=clav.replace("CTRL", "driver_GRP"), p=ctrl_socket, em=True)
        cmds.matchTransform(clav, self.clavicle_jnt, px=True, py=True)
        cmds.matchTransform(clav, self.shoulder_jnt, pz=True)
        cmds.rotate(0,90,0, clav, r=True)
        cmds.parent(clav, ctrl_socket)
        util.zero_transforms(clav)
        util.zero_transforms(clav_driver)
        
        # FK ctrls
        dist = util.get_distance(self.shoulder_jnt, self.elbow_jnt)
        fk_should = Control.fk_box(self.shoulderFK_ctrl,
            fk_size, dist*0.75, "blue", fk_ro)
        fk_elbow = Control.fk_box(self.elbowFK_ctrl,
            fk_size, dist*0.6, "blue", fk_ro)
        fk_hand = Control.box(self.handFK_ctrl,
            fk_size, fk_size, fk_size/3, "blue", fk_ro)
        
        # IK ctrls
        ik_hand = Control.cube(self.handIK_ctrl, fk_size*1.2, "blue", "zxy")
        ik_wrist = Control.square(self.wristIK_ctrl, fk_size*1.4, "sky", "zxy")
        Control.flip_shape(ik_wrist, "-y")
        ik_pv = Control.octahedron(self.pole_vector_ctrl, fk_size/3, "blue")
        
        # position & parent
        relations = {
            fk_should : (self.shoulder_jnt, clav_driver),
            fk_elbow : (self.elbow_jnt, self.shoulderFK_ctrl),
            fk_hand : (self.hand_jnt, self.elbowFK_ctrl),
            ik_hand : (self.hand_jnt, ik_space),
            ik_wrist : (self.hand_jnt, self.handIK_ctrl),
            ik_pv : ("L_poleVector_PRX", ik_space),
        }
        
        for ctrl in list(relations):
            cmds.matchTransform(ctrl, relations[ctrl][0], pos=True, rot=True)
            cmds.parent(ctrl, relations[ctrl][1])
        util.zero_transforms(list(relations))
        
        # switcher
        switch = Control.switcher(self.switcher_ctrl, dist/6)
        Control.flip_shape(switch, "-x")
        cmds.parent(switch, ik_space)
        cmds.matchTransform(switch, self.hand_jnt, pos=True, rot=True)
        cmds.move(0, 0, -dist/2, switch, r=True)
        
        
        # R_ctrls & mirroring
        rig.mirror_ctrls([clav, clav_driver], "R_armFK", ctrl_socket)
        rig.mirror_ctrls([ik_hand, ik_pv], "R_armIK", ik_space)
        rig.mirror_ctrls([switch], "R_armSwitch", ik_space)
        
        # switcher ctrls follow skeleton
        cmds.parentConstraint(
            self.elbow_jnt, switch, mo=True, w=1)
        cmds.parentConstraint(
            self.elbow_jnt.replace("L_", "R_"), 
            switch.replace("L_", "R_"), mo=True, w=1)
        cmds.scaleConstraint(
            self.elbow_jnt, switch, o=(1,1,1), w=1)
        cmds.scaleConstraint(
            self.elbow_jnt.replace("L_", "R_"), 
            switch.replace("L_", "R_"), o=(1,1,1), w=1)
        
        l_ctrls = [clav, fk_should, fk_elbow, fk_hand,
            ik_hand, ik_wrist, ik_pv]
        r_ctrls = [x.replace("L_", "R_") for x in l_ctrls]
        cmds.sets(l_ctrls, add="L_arm")
        cmds.sets(r_ctrls, add="R_arm")
        
    def build_rig(self, joint_socket, ctrl_socket, ik_space, spaces):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket, ik_space)
        
        rig.ikfk(self.shoulder_jnt,
                 self.elbow_jnt,
                 self.hand_jnt,
                 self.hand_end_jnt,
                 self.switcher_ctrl)
        
        # create all rig connections



if __name__ == "__main__":
    
    
    # L_arm = Arm('L')
    # L_arm.build_proxy("global_PRX")
    # L_arm.build_rig("chest_up_JNT", "chest_up_CTRL", 
    #     ["cog_sub_CTRL", "chest_up_CTRL"])\
    for i in ["L_shoulder_Apose_PRX", "L_elbow_Apose_PRX", "L_hand_Apose_PRX"]:
        rot = cmds.xform(i, q=True, ro=True, ws=True)
        pos = cmds.xform(i, q=True, t=True, ws=True)
        jnt = i.replace("Apose_PRX", "JNT")
        cmds.xform(jnt, ro=rot, t=pos, ws=True)
    
    pass