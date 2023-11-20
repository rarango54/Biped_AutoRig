import maya.cmds as cmds

from body_proxies.proxyarm import ProxyArm

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig
from utils import bendy


class Arms(object):
    
    def __init__(self):

        self.module_name = "L_arm"
        
        self.clavicle_jnt = "L_clavicle_JNT"
        self.uparm_jnt = "L_uparm_JNT"
        self.lowarm_jnt = "L_lowarm_JNT"
        self.hand_jnt = "L_hand_JNT"
        self.hand_end_jnt = "L_hand_end_JNT"

        self.clavicle_fk = "L_clavicle_CTRL"
        self.uparm_fk = "L_uparm_FK_CTRL"
        self.lowarm_fk = "L_lowarm_FK_CTRL"
        self.hand_fk = "L_hand_FK_CTRL"
        
        self.uparm_b = "L_uparm_bendy_CTRL"
        self.lowarm_b = "L_lowarm_bendy_CTRL"
        self.elbow_b = "L_elbow_bendy_CTRL"
        
        self.hand_ik = "L_hand_IK_CTRL"
        self.wrist_ik = "L_wrist_IK_CTRL"
        self.shoulder_ik = "L_shoulder_IK_CTRL"
        self.polevector = "L_arm_polevector_IK_CTRL"
        self.switch = "L_arm_switcher_CTRL"
                
    def skeleton(self, joint_socket):
        parm = ProxyArm()
        arm_jnts = rig.make_joints(
                proxies_list = list(parm.proxy_dict)[:5],
                rot_order = "xzy", 
                radius = 1.5)
        # clavicle specific orient Z pointing to side
        cmds.joint(self.clavicle_jnt, e = True, 
                   orientJoint = "none", 
                   zeroScaleOrient = True)
        cmds.parent(self.uparm_jnt, joint_socket)
        cmds.setAttr(f"{self.clavicle_jnt}.jointOrientY", 90)
        cmds.parent(self.uparm_jnt, self.clavicle_jnt)
        # rest of arm joint orient
        cmds.joint(self.uparm_jnt, e = True, 
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
        
        # only clavicle & hand joint (arms are skinned to bendy jnts
        cmds.sets((arm_jnts[0], arm_jnts[-2]), add = "bind_joints")
        cmds.sets((mirr_jnts[0], mirr_jnts[-2]), add = "bind_joints")

    def controls(self, ctrl_socket):
        ikctrl_grp = cmds.group(
                n = "L_arm_IKctrls_GRP", empty = True, parent = "global_sub_CTRL")
        parm = ProxyArm()
        fk = [self.clavicle_jnt, self.uparm_jnt, 
            self.lowarm_jnt, self.hand_jnt, self.hand_end_jnt]
        fk_ro = "xzy"
        fk_size = util.get_distance(self.uparm_jnt, self.lowarm_jnt)/5
        
        # clavicle ctrl
        dist = util.get_distance(self.clavicle_jnt, self.uparm_jnt)
        clav = Nurbs.shoulder(self.clavicle_fk, dist, "blue", fk_ro)
                
        # FK ctrls
        dist = util.get_distance(self.uparm_jnt, self.lowarm_jnt)
        fk_uparm = Nurbs.fk_box(self.uparm_fk,
            fk_size, dist*0.75, "blue", fk_ro)
        fk_lowarm = Nurbs.fk_box(self.lowarm_fk,
            fk_size, dist*0.6, "blue", fk_ro)
        fk_hand = Nurbs.box(self.hand_fk,
            fk_size, fk_size, fk_size/3, "blue", fk_ro)
        # IK ctrls
        ik_hand = Nurbs.cube(self.hand_ik, fk_size*1.2, "blue", "zxy")
        ik_wrist = Nurbs.square(self.wrist_ik, fk_size*1.4, "sky", "zxy")
        Nurbs.flip_shape(ik_wrist, "-y")
        ik_pv = Nurbs.octahedron(self.polevector, fk_size/3, "blue")
        ik_should = Nurbs.square(self.shoulder_ik, fk_size*2.5, "blue")
        Nurbs.flip_shape(ik_should, "-y")
        
        # bendies
        uparm_b = Nurbs.double_lolli(self.uparm_b, dist/4, "sky", "zyx")
        lowarm_b = Nurbs.double_lolli(self.lowarm_b, dist/4, "sky", "zyx")
        elbow_b = Nurbs.double_lolli(self.elbow_b, dist/4, "sky", "zyx")
        elbow_buff = util.buffer(elbow_b)
        
        # switcher
        switch = Nurbs.switcher(self.switch, dist/6)
        Nurbs.flip_shape(switch, "-x")
        
        # expose rotateOrder
        for ro in [fk_uparm, fk_hand, ik_hand, ik_should]:
            cmds.setAttr(f"{ro}.rotateOrder", keyable = True)
        
        # position & parent
        relations = {
            clav :      (self.clavicle_jnt,     ctrl_socket),
            fk_uparm :  (self.uparm_jnt,        clav),
            fk_lowarm : (self.lowarm_jnt,       fk_uparm),
            fk_hand :   (self.hand_jnt,         fk_lowarm),
            ik_hand :   (self.hand_jnt,         ikctrl_grp),
            ik_wrist :  (self.hand_jnt,         ik_hand),
            ik_pv :     (list(parm.proxy_dict)[5], ikctrl_grp),
            uparm_b :   (self.uparm_jnt,        ikctrl_grp),
            lowarm_b :  (self.lowarm_jnt,       ikctrl_grp),
            elbow_buff :(self.lowarm_jnt,       ikctrl_grp),
            ik_should : (self.uparm_jnt,        clav),
            switch :    (self.hand_jnt,         ikctrl_grp)
        }
        
        for ctrl in list(relations):
            cmds.matchTransform(ctrl, relations[ctrl][0], pos = True, rot = True)
            cmds.parent(ctrl, relations[ctrl][1])
        # position bendies
        uparm_pc = cmds.pointConstraint(
                (self.uparm_jnt, self.lowarm_jnt), uparm_b, 
                offset = (0,0,0), weight = 0.5)[0]
        lowarm_pc = cmds.pointConstraint(
                (self.lowarm_jnt, self.hand_jnt), lowarm_b, 
                offset = (0,0,0), weight = 0.5)[0]
        cmds.delete((uparm_pc, lowarm_pc))
        # make sure elbow bendy is in the middle of angle betw uparm & lowarm_jnts
        elbow_ori = cmds.getAttr(f"{elbow_buff}.rotateY")
        elbow_jori = cmds.getAttr(f"{self.lowarm_jnt}.jointOrientY")
        cmds.setAttr(f"{elbow_buff}.rotateY", (elbow_ori - elbow_jori/2))
        # offset switch ctrl from arm
        cmds.move(0, 0, -dist/2, switch, relative = True)
        
        # add attributes
        util.attr_separator([fk_uparm, ik_hand, ik_wrist, ik_should, clav])
        cmds.addAttr(ik_hand, longName = "uparm_length", attributeType = "double", 
                     min = 0, defaultValue = 1)
        cmds.setAttr(f"{ik_hand}.uparm_length", e = True, keyable = True)
        cmds.addAttr(ik_hand, longName = "lowarm_length", attributeType = "double", 
                     min = 0, defaultValue = 1)
        cmds.setAttr(f"{ik_hand}.lowarm_length", e = True, keyable = True)
        cmds.addAttr(clav, longName = "deltoid_twist", attributeType = "double")
        cmds.setAttr(f"{clav}.deltoid_twist", e = True, keyable = True)
        
        # R_ctrls & mirroring
        ikctrl_mirror_grp = cmds.group(
                n = "R_arm_IKctrls_mirror_GRP", empty = True, parent = "global_sub_CTRL")
        cmds.setAttr(f"{ikctrl_mirror_grp}.sx", -1)
        fkctrl_mirror_grp = cmds.group(
                n = "R_arm_FKctrls_mirror_GRP", empty = True, parent = ctrl_socket)
        cmds.setAttr(f"{fkctrl_mirror_grp}.sx", -1)
        rig.mirror_ctrls([clav], fkctrl_mirror_grp)
        rig.mirror_ctrls([ik_hand, ik_pv], ikctrl_mirror_grp)
        rig.mirror_ctrls([switch], ikctrl_mirror_grp)
        rig.mirror_ctrls([uparm_b, lowarm_b, elbow_buff], ikctrl_mirror_grp)
        
        # scale invert joints for FK ctrls
        sclinv_jnts = [clav, fk_uparm, fk_lowarm]
        util.insert_scaleInvJoint(sclinv_jnts)
        util.insert_scaleInvJoint([x.replace("L_", "R_") for x in sclinv_jnts])
        
        # selection sets
        l_ctrls = [clav, fk_uparm, fk_lowarm, fk_hand, 
                   ik_hand, ik_wrist, ik_pv, ik_should, 
                   uparm_b, elbow_b, lowarm_b, switch]
        r_ctrls = [x.replace("L_", "R_") for x in l_ctrls]
        cmds.sets(l_ctrls, add = "L_arm")
        cmds.sets(r_ctrls, add = "R_arm")
        
        util.mtx_zero(l_ctrls)
        util.mtx_zero(r_ctrls)
        
        util.lock(switch, rsidetoo = True)
        
    def build_rig(self, joint_socket, ctrl_socket, spaces):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket)
        
        # create IK and FK joint chains
        L_jnts = [self.uparm_jnt, self.lowarm_jnt, self.hand_jnt, self.hand_end_jnt]
        L_switch = self.switch
        R_jnts = [x.replace("L_", "R_") for x in L_jnts]
        R_switch = self.switch.replace("L_", "R_")
        rig.ikfk_chains(L_jnts, L_switch)
        rig.ikfk_chains(R_jnts, R_switch)
        
        # connect rotateOrders from FK ctrls to FK joints
        for s in ["L_", "R_"]:
            ro_ctrls = [f"{s}uparm_FK_CTRL", f"{s}lowarm_FK_CTRL", f"{s}hand_FK_CTRL"]
            for ro_ctrl in ro_ctrls:
                jnt = ro_ctrl.replace("_CTRL", "_JNT")
                cmds.connectAttr(f"{ro_ctrl}.rotateOrder", f"{jnt}.rotateOrder")
            cmds.connectAttr(
                f"{s}clavicle_CTRL.rotateOrder", f"{s}clavicle_JNT.rotateOrder")
        
    ### FK setup
        for s in ["L_", "R_"]:
        # clavicle
            cmds.parentConstraint(
                f"{s}clavicle_CTRL", f"{s}clavicle_JNT", mo = True, weight = 1)
            cmds.scaleConstraint(
                f"{s}clavicle_CTRL", f"{s}clavicle_JNT", mo = True, weight = 1)
        # uparm_jnt with constraint to make space switches work
            cmds.parentConstraint(
                f"{s}uparm_FK_CTRL", f"{s}uparm_FK_JNT", mo = True, weight = 1)
            cmds.scaleConstraint(
                f"{s}uparm_FK_CTRL", f"{s}uparm_FK_JNT", mo = True, weight = 1)
            
            cmds.connectAttr(f"{s}lowarm_FK_CTRL.rotate", f"{s}lowarm_FK_JNT.rotate")
            cmds.connectAttr(f"{s}hand_FK_CTRL.rotate", f"{s}hand_FK_JNT.rotate")
            cmds.scaleConstraint(
                f"{s}lowarm_FK_CTRL", f"{s}lowarm_FK_JNT", mo = True, weight = 1)
            cmds.scaleConstraint(
                f"{s}hand_FK_CTRL", f"{s}hand_FK_JNT", mo = True, weight = 1)
        
    ### IK setup
        for s in ["L_", "R_"]: 
            arm_IKargs = {
                "name" : f"{s}arm_IKR",
                "startJoint" : f"{s}uparm_IK_JNT",
                "endEffector" : f"{s}hand_IK_JNT",
                "solver" : "ikRPsolver"
            }
            ikh = cmds.ikHandle(**arm_IKargs)
            cmds.parent(ikh[0], "misc_GRP")
            cmds.rename(ikh[1], f"{s}arm_IK_EFF")
            
            cmds.poleVectorConstraint(f"{s}arm_polevector_IK_CTRL",ikh[0])
            util.mtx_hook(f"{s}wrist_IK_CTRL", ikh[0])
        # hand
            hand_IKargs = {
                'name' : f'{s}hand_IKS',
                'startJoint' : f"{s}hand_IK_JNT",
                'endEffector' : f"{s}hand_end_IK_JNT",
                'solver' : 'ikSCsolver'
            }
            ikh_hand = cmds.ikHandle(**hand_IKargs)
            cmds.parent(f'{s}hand_IKS', 'misc_GRP')
            cmds.rename(ikh_hand[1], f"{s}hand_IK_EFF")
            util.mtx_hook(f"{s}wrist_IK_CTRL", ikh_hand[0])
            
    ### stretchy IK and scale setup
        # current length
            armlen = cmds.shadingNode(
                    "distanceBetween", n = f"{s}arm_stretchylength_DBTW", asUtility = True)
            cmds.connectAttr(f"{s}shoulder_IK_CTRL.worldMatrix[0]", f"{armlen}.inMatrix1")
            cmds.connectAttr(f"{s}hand_IK_CTRL.worldMatrix[0]", f"{armlen}.inMatrix2")
        # src_armlen = uparm + lowarm lengths
            uparmlen = util.get_distance(f"{s}uparm_JNT", f"{s}lowarm_JNT")
            lowarmlen = util.get_distance(f"{s}lowarm_JNT", f"{s}hand_JNT")
        # MD up/lowarmlen by attr from hand_IK_CTRL
            ikctrl_len = cmds.shadingNode(
                    "multiplyDivide", n = f"{s}arm_ikctrlattr_MULT", asUtility = True)
            cmds.setAttr(f"{ikctrl_len}.input1X", uparmlen)
            cmds.setAttr(f"{ikctrl_len}.input1Y", lowarmlen)
            cmds.connectAttr(f"{s}hand_IK_CTRL.uparm_length", f"{ikctrl_len}.input2X")
            cmds.connectAttr(f"{s}hand_IK_CTRL.lowarm_length", f"{ikctrl_len}.input2Y")
        # ADD src_armlen = uparmlen + lowarmlen
            src_armlen = cmds.shadingNode(
                    "plusMinusAverage", n = f"{s}arm_srclength_ADD", asUtility = True)
            cmds.connectAttr(f"{ikctrl_len}.outputX", f"{src_armlen}.input1D[0]")
            cmds.connectAttr(f"{ikctrl_len}.outputY", f"{src_armlen}.input1D[1]")
        # DIV by global scale
            glob_inv = cmds.shadingNode(
                    "multiplyDivide", n = F"{s}arm_stretchyglobalScl_DIV", asUtility = True)
            cmds.setAttr(f"{glob_inv}.operation", 2) # divide
            cmds.connectAttr(f"{armlen}.distance", f"{glob_inv}.input1Z")
            cmds.connectAttr("global_CTRL.scale", f"{glob_inv}.input2")
        # DIV normalize -> current length / source length
            norm = cmds.shadingNode(
                    "multiplyDivide", n = F"{s}arm_stretchy_NORM", asUtility = True)
            cmds.setAttr(f"{norm}.operation", 2) # divide
            cmds.connectAttr(f"{glob_inv}.outputZ", f"{norm}.input1Z")
            cmds.connectAttr(f"{src_armlen}.output1D", f"{norm}.input2Z")
        # CONDITION -> prevent shrinking arm by setting a minimum scale Z = 1
            con = cmds.shadingNode(
                        "condition", n = f"{s}arm_stretchy_CON", asUtility = True)
            cmds.setAttr(f"{con}.operation", 5) # <= less or equal than
            cmds.connectAttr(f"{norm}.outputZ", f"{con}.firstTerm") # stretch value
            cmds.setAttr(f"{con}.secondTerm", 1) # minimum
            cmds.setAttr(f"{con}.colorIfTrueR", 1) # output when bending limb
        # output when stretching limb
            cmds.connectAttr(f"{norm}.outputZ", f"{con}.colorIfFalseR")
            
        # connect ctrl scale with globalScl
            for n, ik_jnt in enumerate(
                    [f"{s}uparm_IK_JNT", f"{s}lowarm_IK_JNT", f"{s}hand_IK_JNT"]
                    ):
                scl_md = cmds.shadingNode(
                        "multiplyDivide", n = ik_jnt.replace("_JNT", "_scale_MULT"), 
                        asUtility = True)
                sz_md = cmds.shadingNode(
                        "multiplyDivide", n = ik_jnt.replace("_JNT", "_stretchySz_MULT"), 
                        asUtility = True)
                cmds.connectAttr("global_CTRL.scale", f"{scl_md}.input1")
                if n == 0:
                    cmds.connectAttr(f"{s}hand_IK_CTRL.uparm_length",
                                     f"{scl_md}.input2Z")
                    cmds.connectAttr(f"{scl_md}.output", f"{sz_md}.input1")
                    cmds.connectAttr(f"{con}.outColorR", f"{sz_md}.input2Z")
                    cmds.connectAttr(f"{sz_md}.output", f"{ik_jnt}.scale")
### add thickness driver into scl_md.inputs 2X and 2Y
                if n == 1:
                    cmds.connectAttr(f"{s}hand_IK_CTRL.lowarm_length",
                                     f"{scl_md}.input2Z")
                    cmds.connectAttr(f"{scl_md}.output", f"{sz_md}.input1")
                    cmds.connectAttr(f"{con}.outColorR", f"{sz_md}.input2Z")
                    cmds.connectAttr(f"{sz_md}.output", f"{ik_jnt}.scale")
### add thickness driver into scl_md.inputs 2X and 2Y
                if n == 2:
                    cmds.connectAttr(f"{s}hand_IK_CTRL.scale",
                                     f"{scl_md}.input2")
                    cmds.connectAttr(f"{scl_md}.output", f"{ik_jnt}.scale")
            
### can this be before the IK or FK Setup?        
        # switcher & elbow_bendy_buffer follow deform skeleton
            util.mtx_hook(f"{s}lowarm_JNT", f"{s}arm_switcher_CTRL")
            util.mtx_hook(f"{s}uparm_JNT", f"{s}elbow_bendy_buffer_GRP")
        # elbow bendy: 0.5 x elbow_JNT rot
            half_rot = cmds.shadingNode(
                        "multiplyDivide", n = f"{s}elbow_bendy_halfrot_MULT", 
                        asUtility = True)
            cmds.setAttr(f"{half_rot}.input2", 0.5, 0.5, 0.5)
            cmds.connectAttr(f"{s}lowarm_JNT.rotate", f"{half_rot}.input1")
            cmds.connectAttr(f"{half_rot}.output", f"{s}elbow_bendy_buffer_GRP.rotate")
            
###### missing:
    # wrist align
    # ik shoulder space (Noah's setup)
    # spaces
    # thickness ctrl (with falloffs?
        
        for s in ["L_", "R_"]:
            bendy.setup(
                mod_name = f"{s}uparm", 
                base_driver = f"{s}uparm_JNT", 
                head_driver = f"{s}lowarm_JNT",
                forwardaxis = "z", 
                upaxis = "-x",
                mid_ctrl = f"{s}uparm_bendy_CTRL", 
                twistInvDriver = f"{s}clavicle_JNT",
                elbow_bendy_ctrl = f"{s}elbow_bendy_CTRL")
            bendy.setup(
                mod_name = f"{s}lowarm", 
                base_driver = f"{s}lowarm_JNT", 
                head_driver = f"{s}hand_JNT",
                forwardaxis = "z", 
                upaxis = "-x",
                mid_ctrl = f"{s}lowarm_bendy_CTRL",
                elbow_bendy_ctrl = f"{s}elbow_bendy_CTRL")
        # uparm & lowarm bendy ctrls both aim to elbow_bendy and squetch
            bendy.aim(
                bendy = f"{s}uparm_bendy_CTRL",
                aimtarget = f"{s}elbow_bendy_CTRL", 
                uptarget = f"{s}uparm_baseTwist_LOC",
                root = f"{s}uparm_bendy_1_JNT",
                vaim = (0,0,1),
                vup = (1,0,0))
            bendy.aim(
                bendy = f"{s}lowarm_bendy_CTRL",
                aimtarget = f"{s}elbow_bendy_CTRL", 
                uptarget = f"{s}lowarm_endTwist_LOC",
                root = f"{s}lowarm_twist_end_JNT",
                vaim = (0,0,-1),
                vup = (1,0,0),
                scldriver = f"{s}lowarm_JNT")
                
    # deltoid twist(asymmetric) = IKS.roll - IKS.twist
        delt_inv = cmds.shadingNode(
                "multiplyDivide", n = "deltoidInv_MULT", asUtility = True)
        cmds.setAttr(f"{delt_inv}.input2", -1, -1, -1)
        
        cmds.connectAttr("L_clavicle_CTRL.deltoid_twist", "L_uparm_IKS.roll")
        cmds.connectAttr("L_clavicle_CTRL.deltoid_twist", f"{delt_inv}.input1X")
        cmds.connectAttr(f"{delt_inv}.outputX", "L_uparm_IKS.twist")
        
        cmds.connectAttr("R_clavicle_CTRL.deltoid_twist", f"{delt_inv}.input1Y")
        cmds.connectAttr(f"{delt_inv}.outputY", "R_uparm_IKS.roll")
        cmds.connectAttr("R_clavicle_CTRL.deltoid_twist", "R_uparm_IKS.twist")
            

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