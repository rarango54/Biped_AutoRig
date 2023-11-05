import maya.cmds as cmds

from body_proxies.proxyarm import ProxyArm

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig


class Arms(object):
    
    def __init__(self):

        self.module_name = "L_arm"
        
        self.clavicle_jnt = "L_clavicle_JNT"
        self.uparm_jnt = "L_uparm_JNT"
        self.elbow_jnt = "L_elbow_JNT"
        self.hand_jnt = "L_hand_JNT"
        self.hand_end_jnt = "L_hand_end_JNT"

        self.clavicle_ctrl = "L_clavicle_CTRL"
        self.clavicle_driver_grp = "L_clavicle_driver_GRP"
        self.uparm_FK_ctrl = "L_uparm_FK_CTRL"
        self.elbow_FK_ctrl = "L_elbow_FK_CTRL"
        self.hand_FK_ctrl = "L_hand_FK_CTRL"
        
        self.hand_IK_ctrl = "L_hand_IK_CTRL"
        self.wrist_IK_ctrl = "L_wrist_IK_CTRL"
        self.pole_vector_ctrl = "L_armIK_PV_CTRL"
        self.switcher_ctrl = "L_arm_switcher_CTRL"
        
        self.finger_socket_prx = "L_hand_PRX"
        self.pole_vector_prx = "L_poleVector_PRX"
        
    def skeleton(self, joint_socket):
        parm = ProxyArm()
        arm_jnts = rig.make_joints(
                proxies_list = list(parm.proxy_dict)[:5],
                rot_order = "zxy", 
                radius = 1.5)
        # clavicle joint needs to have specific orient
        cmds.joint(self.clavicle_jnt, e = True, 
                   orientJoint = "none", 
                   zeroScaleOrient = True)
        cmds.parent(self.uparm_jnt, joint_socket)
        cmds.setAttr(f"{self.clavicle_jnt}.jointOrientY", 90)
        cmds.parent(self.uparm_jnt, self.clavicle_jnt)
        # rest of arm joint orient
        cmds.joint(
                self.uparm_jnt, e = True, 
                orientJoint = "zyx", 
                secondaryAxisOrient = "yup", 
                children = True, 
                zeroScaleOrient = True)
        cmds.parent(self.clavicle_jnt, joint_socket)
        mirr_jnts = cmds.mirrorJoint(
                self.clavicle_jnt, 
                mirrorYZ = True, 
                mirrorBehavior = True, 
                searchReplace = ["L_", "R_"])
        
        cmds.sets(arm_jnts[:-1], add = "bind_joints") # except hand_end_JNT
        cmds.sets(mirr_jnts[:-1], add = "bind_joints") # except hand_end_JNT

    def controls(self, ctrl_socket, ik_ctrlparent):
        parm = ProxyArm()
        fk = [self.clavicle_jnt, self.uparm_jnt, 
            self.elbow_jnt, self.hand_jnt, self.hand_end_jnt]
        fk_ro = "zyx"
        fk_size = util.get_distance(self.uparm_jnt, self.elbow_jnt)/5
        
        # clavicle ctrl
        # is not in the fk hierarchy
        dist = util.get_distance(self.clavicle_jnt, self.uparm_jnt)
        clav = Nurbs.shoulder(self.clavicle_ctrl, dist, "blue", fk_ro)
        clav_driver = cmds.group(
            n=clav.replace("CTRL", "driver_GRP"), p=ctrl_socket, em=True)
        cmds.matchTransform(clav_driver, self.clavicle_jnt, pos=True, rot=True)
        cmds.matchTransform(clav, self.clavicle_jnt, px=True, py=True, rot=True)
        cmds.matchTransform(clav, self.uparm_jnt, pz=True)
        cmds.parent(clav, ctrl_socket)
        util.zero_transforms(clav)
        util.zero_transforms(clav_driver)
                
        # FK ctrls
        dist = util.get_distance(self.uparm_jnt, self.elbow_jnt)
        fk_uparm = Nurbs.fk_box(self.uparm_FK_ctrl,
            fk_size, dist*0.75, "blue", fk_ro)
        fk_elbow = Nurbs.fk_box(self.elbow_FK_ctrl,
            fk_size, dist*0.6, "blue", fk_ro)
        fk_hand = Nurbs.box(self.hand_FK_ctrl,
            fk_size, fk_size, fk_size/3, "blue", fk_ro)
        
        # IK ctrls
        ik_hand = Nurbs.cube(self.hand_IK_ctrl, fk_size*1.2, "blue", "zxy")
        ik_wrist = Nurbs.square(self.wrist_IK_ctrl, fk_size*1.4, "sky", "zxy")
        Nurbs.flip_shape(ik_wrist, "-y")
        ik_pv = Nurbs.octahedron(self.pole_vector_ctrl, fk_size/3, "blue")
        
        # position & parent
        relations = {
            fk_uparm : (self.uparm_jnt, clav_driver),
            fk_elbow : (self.elbow_jnt, self.uparm_FK_ctrl),
            fk_hand : (self.hand_jnt, self.elbow_FK_ctrl),
            ik_hand : (self.hand_jnt, ik_ctrlparent),
            ik_wrist : (self.hand_jnt, self.hand_IK_ctrl),
            ik_pv : (list(parm.proxy_dict)[5], ik_ctrlparent),
        }
        
        for ctrl in list(relations):
            cmds.matchTransform(ctrl, relations[ctrl][0], pos=True, rot=True)
            cmds.parent(ctrl, relations[ctrl][1])
        util.zero_transforms(list(relations))
        
        # switcher
        switch = Nurbs.switcher(self.switcher_ctrl, dist/6)
        Nurbs.flip_shape(switch, "-x")
        cmds.parent(switch, ik_ctrlparent)
        cmds.matchTransform(switch, self.hand_jnt, pos=True, rot=True)
        cmds.move(0, 0, -dist/2, switch, r=True)
        
        
        # R_ctrls & mirroring
        rig.mirror_ctrls([clav, clav_driver], "R_armFK", ctrl_socket)
        rig.mirror_ctrls([ik_hand, ik_pv], "R_armIK", ik_ctrlparent)
        rig.mirror_ctrls([switch], "R_armSwitch", ik_ctrlparent)
        
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
                    
        l_ctrls = [clav, fk_uparm, fk_elbow, fk_hand,
            ik_hand, ik_wrist, ik_pv]
        r_ctrls = [x.replace("L_", "R_") for x in l_ctrls]
        cmds.sets(l_ctrls, add = "L_arm")
        cmds.sets(r_ctrls, add = "R_arm")
        
    def build_rig(self, joint_socket, ctrl_socket, ik_ctrlparent, spaces):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket, ik_ctrlparent)
        
        # create IK and FK joint chains
        left_jnts = [self.uparm_jnt, self.elbow_jnt, self.hand_jnt, self.hand_end_jnt]
        left_switch = self.switcher_ctrl
        right_jnts = [x.replace("L_", "R_") for x in left_jnts]
        right_switch = self.switcher_ctrl.replace("L_", "R_")
        rig.ikfk_chains(left_jnts, left_switch)
        rig.ikfk_chains(right_jnts, right_switch)
        for s in ["L_", "R_"]:
            # clavicle
            util.connect_transforms(f"{s}clavicle_CTRL", f"{s}clavicle_driver_GRP")
            cmds.parentConstraint(
                f"{s}clavicle_driver_GRP", f"{s}clavicle_JNT", mo=True, w=1)
            cmds.scaleConstraint(
                f"{s}clavicle_driver_GRP", f"{s}clavicle_JNT", 
                mo=True, w=1)
        # FK setup
        fk_ctrls = [self.uparm_FK_ctrl,
                    self.elbow_FK_ctrl,
                    self.hand_FK_ctrl]
        for fk in fk_ctrls:
            util.connect_transforms(fk, fk.replace("CTRL", "JNT"), t=False)
            r_fk = fk.replace("L_", "R_")
            util.connect_transforms(r_fk, r_fk.replace("CTRL", "JNT"), t=False)
        
        # IK setup
        for s in ["L_", "R_"]:
            ikh_arm = f"{s}arm_IKR"
            arm_IKargs = {
                "name" : ikh_arm,
                "startJoint" : f"{s}uparm_IK_JNT",
                "endEffector" : f"{s}hand_IK_JNT",
                "solver" : "ikRPsolver"
            }
            cmds.ikHandle(**arm_IKargs)
            cmds.parent(f"{s}arm_IKR", "misc_GRP")
            # cmds.connectAttr(f"{s}hand_IK_CTRL.worldMatrix[0]", f"{s}arm_IKR.offsetParentMatrix")
            # cmds.xform(f"{s}arm_IKR", translation=[0, 0, 0], rotation=[0, 0, 0], scale=[1, 1, 1])
            ee = cmds.ikHandle(ikh_arm, q=True, ee=True) # get effector
            cmds.rename(ee, f"{s}arm_IK_EFF")
            
            cmds.poleVectorConstraint(f"{s}armIK_PV_CTRL",f"{s}arm_IKR")
            cmds.parentConstraint(f"{s}wrist_IK_CTRL", ikh_arm, mo=True, w=1)
            # hand follow
            ikh_hand = f'{s}hand_IKS'
            hand_IKargs = {
                'name' : ikh_hand,
                'startJoint' : f"{s}hand_IK_JNT",
                'endEffector' : f"{s}hand_end_IK_JNT",
                'solver' : 'ikSCsolver'
            }
            cmds.ikHandle(**hand_IKargs)
            cmds.parent(f'{s}hand_IKS', 'misc_GRP')
            cmds.parentConstraint(f"{s}wrist_IK_CTRL", ikh_hand, mo=True, w=1)
            cmds.scaleConstraint(
                f"{s}wrist_IK_CTRL", f"{s}hand_IK_JNT", mo=True, w=1)
            

if __name__ == "__main__":
    
    socket = cmds.group(n="proxies_GRP", em=True, w=True)
    socket1 = cmds.group(n="testjoint_GRP", em=True, w=True)
    socket2 = cmds.group(n="testctrl_GRP", em=True, w=True)
    socket3 = cmds.group(n="testikspace_GRP", em=True, w=True)
    parm = ProxyArm()
    parm.build_proxy(socket)
    arm = Arms()
    arm.build_rig(socket1, socket2, socket3, [socket])
    help(rig.ikfk)
    
    pass