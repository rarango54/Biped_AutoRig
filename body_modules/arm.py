import maya.cmds as cmds

from body_proxies.proxyarm import ProxyArm

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig
from utils import bendy


class Arms(object):
    
    def __init__(self, joint_socket, ctrl_socket, spaces):

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
        self.hand_sub_ik = "L_hand_IK_sub_CTRL"
        self.hand_align = "L_hand_align_IK_CTRL"
        self.shoulder_ik = "L_shoulder_IK_CTRL"
        self.polevector = "L_arm_polevector_IK_CTRL"
        self.switch = "L_arm_switcher_CTRL"
        
        self.L_ik_vis = [self.hand_ik, self.polevector, self.shoulder_ik]
        self.L_fk_vis = [self.uparm_fk, self.lowarm_fk, self.hand_fk]
        self.L_bendies = [self.uparm_b, self.elbow_b, self.lowarm_b]
        self.R_ik_vis = [x.replace("L_", "R_") for x in self.L_ik_vis]
        self.R_fk_vis = [x.replace("L_", "R_") for x in self.L_fk_vis]
        self.R_bendies = [x.replace("L_", "R_") for x in self.L_bendies]
        
        spaces.append(self.shoulder_ik)
        self.build_rig(joint_socket, ctrl_socket, spaces)
                
    def skeleton(self, joint_socket):
        parm = ProxyArm()
        arm_jnts = rig.make_joints(
                proxies_list = list(parm.proxy_dict)[:5],
                rot_order = "xzy", 
                radius = 1.5)
        # clavicle specific orient Z pointing to side
        cmds.joint(self.clavicle_jnt, e = True, 
                   orientJoint = "zxy",
                   secondaryAxisOrient = "zdown",
                   children = True,
                   zeroScaleOrient = True)
        cmds.parent(self.clavicle_jnt, joint_socket)
        mirr_jnts = cmds.mirrorJoint(
                self.clavicle_jnt, 
                mirrorYZ = True, 
                mirrorBehavior = True, 
                searchReplace = ["L_", "R_"])
        
        # only clavicle & hand joint (arms are skinned to bendy jnts)
        cmds.sets((arm_jnts[0], arm_jnts[-2]), add = "bind_joints")
        cmds.sets((mirr_jnts[0], mirr_jnts[-2]), add = "bind_joints")

##### CONTROLS #####################################################################
    def controls(self, ctrl_socket, spaces):
    # Setup
        ikctrl_grp = cmds.group(
                n = "L_arm_IKctrls_GRP", empty = True, parent = "global_sub_CTRL")
        parm = ProxyArm()
        fk = [self.clavicle_jnt, self.uparm_jnt, 
            self.lowarm_jnt, self.hand_jnt, self.hand_end_jnt]
        fk_ro = "xzy"
        leng = util.distance(self.uparm_jnt, self.lowarm_jnt)
        wid = leng / 5
      
    # FK ctrls
        cdist = util.distance(self.clavicle_jnt, self.uparm_jnt)
        clav = Nurbs.fk_box(self.clavicle_fk, 
            wid/8, cdist*0.9, "blue", fk_ro)
        # clav = Nurbs.shoulder(self.clavicle_fk, cdist, "blue", fk_ro)
        fk_uparm = Nurbs.fk_box(self.uparm_fk,
            wid/8, leng*0.9, "blue", fk_ro)
        fk_lowarm = Nurbs.fk_box(self.lowarm_fk,
            wid/8, leng*0.8, "blue", fk_ro)
        fk_hand = Nurbs.box(self.hand_fk,
            wid, wid, wid/3, "blue", fk_ro)
        
    # IK ctrls
        ik_hand = Nurbs.cube(self.hand_ik, wid*1.2, "blue", "zxy")
        ik_hand_sub = Nurbs.square(self.hand_sub_ik, wid*1.4, "sky", "zxy")
        Nurbs.flip_shape(ik_hand_sub, "-y")
        ik_align = Nurbs.box(self.hand_align, wid/6, wid*1.4, wid/6, "sky", "zxy")
        ik_pv = Nurbs.octahedron(self.polevector, leng/12, "blue")
        ik_should = Nurbs.square(self.shoulder_ik, wid*2.5, "blue")
        Nurbs.flip_shape(ik_should, "-y")
    # bendies
        uparm_b = Nurbs.sphere(self.uparm_b, leng/20, "sky", "zyx")
        lowarm_b = Nurbs.sphere(self.lowarm_b, leng/20, "sky", "zyx")
        elbow_b = Nurbs.sphere(self.elbow_b, leng/20, "sky", "zyx")
        elbow_buff = util.buffer(elbow_b)
    # switcher
        switch = Nurbs.switcher(self.switch, leng/8)
        Nurbs.flip_shape(switch, "-x")
        
    # see through geo like xRay
        for xray in [clav, fk_uparm, fk_lowarm, uparm_b, lowarm_b, elbow_b]:
            shapes = cmds.listRelatives(xray, children = True, shapes = True)
            for s in shapes:
                cmds.setAttr(f"{s}.alwaysDrawOnTop", 1)
    # expose rotateOrder
        for ro in [fk_uparm, fk_hand, ik_hand, ik_should]:
            cmds.setAttr(f"{ro}.rotateOrder", channelBox = True)
        
    # position & parent
        relations = {
            clav :      (self.clavicle_jnt,     ctrl_socket),
            fk_uparm :  (self.uparm_jnt,        clav),
            fk_lowarm : (self.lowarm_jnt,       fk_uparm),
            fk_hand :   (self.hand_jnt,         fk_lowarm),
            ik_hand :   (self.hand_jnt,         ikctrl_grp),
            ik_hand_sub :  (self.hand_jnt,         ik_hand),
            ik_align :  (self.hand_jnt,         ik_hand_sub),
            ik_pv :     (list(parm.proxy_dict)[5], ikctrl_grp),
            uparm_b :   (self.uparm_jnt,        ikctrl_grp),
            lowarm_b :  (self.lowarm_jnt,       ikctrl_grp),
            elbow_buff :(self.lowarm_jnt,       ikctrl_grp),
            ik_should : (self.uparm_jnt,        clav),
            switch :    (self.hand_jnt,         ikctrl_grp)}
        
        for ctrl in list(relations):
            cmds.matchTransform(ctrl, relations[ctrl][0], pos = True, rot = True)
            cmds.parent(ctrl, relations[ctrl][1])
    # remove rot on polevector
        cmds.rotate(0,0,0, self.polevector, worldSpace = True)
    # position bendies
        uparm_pc = cmds.pointConstraint(
                (self.uparm_jnt, self.lowarm_jnt), uparm_b, 
                offset = (0,0,0), weight = 0.5)[0]
        lowarm_pc = cmds.pointConstraint(
                (self.lowarm_jnt, self.hand_jnt), lowarm_b, 
                offset = (0,0,0), weight = 0.5)[0]
        cmds.delete((uparm_pc, lowarm_pc))
    # elbow bendy in middle (angle) betw uparm & lowarm_jnts
        elbow_ori = cmds.getAttr(f"{elbow_buff}.rotateY")
        elbow_jori = cmds.getAttr(f"{self.lowarm_jnt}.jointOrientY")
        cmds.setAttr(f"{elbow_buff}.rotateY", (elbow_ori - elbow_jori/2))
    # offset switcher ctrl from arm
        cmds.move(0, 0, -leng/2, switch, relative = True)
    # add buffer to ik_align for wrist_align attr
        util.buffer(ik_align)
        
    ### Flatten orientation of ik_hand & fk_uparm for A pose
        cmds.rotate(0, 90, 0, ik_hand, worldSpace = True)
        cmds.rotate(0, 0, 0, fk_uparm, worldSpace = True)
        
####### Attributes
        util.attr_separator([fk_uparm, ik_hand, ik_hand_sub, ik_should, clav, ik_pv])
        for attr in ["uparm_length", "lowarm_length", 
                     "up_thickX", "up_thickY", 
                     "low_thickX", "low_thickY"]:
            cmds.addAttr(ik_hand, longName = attr, attributeType = "double", 
                         min = 0.05, defaultValue = 1)
            cmds.setAttr(f"{ik_hand}.{attr}", e = True, keyable = True)
        cmds.addAttr(ik_hand, longName = "stretch_toggle", at = "double", 
                     min = 0, max = 1, dv = 1)
        cmds.setAttr(f"{ik_hand}.stretch_toggle", e = True, keyable = True)
        cmds.addAttr(clav, longName = "deltoid_twist", attributeType = "double")
        cmds.setAttr(f"{clav}.deltoid_twist", e = True, keyable = True)
        # BODY TUNING
        util.attr_separator("BODY_TUNING", name = "Arms")
        cmds.addAttr("BODY_TUNING", longName = "elbow_offset", at = "double")
        cmds.setAttr("BODY_TUNING.elbow_offset", e = True, keyable = True)
        cmds.addAttr("BODY_TUNING", ln = "e_start_angle", at = "double", dv = -90)
        cmds.setAttr("BODY_TUNING.e_start_angle", e = True, keyable = True)
        cmds.addAttr("BODY_TUNING", ln = "e_end_angle", at = "double", dv = -160)
        cmds.setAttr("BODY_TUNING.e_end_angle", e = True, keyable = True)
        
    ### R_ctrls & Mirroring
        ikctrl_mirror_grp = cmds.group(
                n = "R_arm_IKctrls_mirror_GRP", em = True, parent = "global_sub_CTRL")
        cmds.setAttr(f"{ikctrl_mirror_grp}.sx", -1)
        fkctrl_mirror_grp = cmds.group(
                n = "R_arm_FKctrls_mirror_GRP", em = True, parent = ctrl_socket)
        cmds.setAttr(f"{fkctrl_mirror_grp}.sx", -1)
        rig.mirror_ctrls([clav], fkctrl_mirror_grp)
        rig.mirror_ctrls([ik_hand, ik_pv], ikctrl_mirror_grp)
        rig.mirror_ctrls([switch], ikctrl_mirror_grp)
        rig.mirror_ctrls([uparm_b, lowarm_b, elbow_buff], ikctrl_mirror_grp)
        
    ### Spaces
        uparm_space = rig.spaces(spaces[:-1], fk_uparm, r_only = True)
        rig.spaces(spaces[:-1], fk_uparm.replace("L_", "R_"), r_only = True)
        rig.spaces(spaces, ik_hand)
        rig.spaces(spaces, ik_hand.replace("L_", "R_"), rside = True)
        spaces.append(ik_hand)
        rig.spaces(spaces, ik_pv)
        rig.spaces(spaces, ik_pv.replace("L_", "R_"), rside = True)
    
    # polevector line connecting with knee
        for s in ["L_", "R_"]:
            pole_crv = Nurbs.lineconnect(
                    f"{s}armPole", [f"{s}elbow_bendy_CTRL", f"{s}arm_polevector_IK_CTRL"],
                    proxy = False)
            cmds.parent(pole_crv, "other_ctrls_GRP")
    
    # selection sets
        l_ctrls = [clav, fk_uparm, fk_lowarm, fk_hand, 
                   ik_hand, ik_hand_sub, ik_align, ik_pv, ik_should, 
                   uparm_b, elbow_b, lowarm_b, switch]
        r_ctrls = [x.replace("L_", "R_") for x in l_ctrls]
        cmds.sets(l_ctrls, add = "L_arm")
        cmds.sets(r_ctrls, add = "R_arm")
        
    # cleanup
        util.mtx_zero(l_ctrls)
        util.mtx_zero(r_ctrls)
        rig.fk_sclinvert([uparm_space[0], fk_lowarm, fk_hand], rsidetoo = True)
        
    # rotate ik_hand & fk_uparm into place (will have rot values in bind pose)
        for s in ["L_", "R_"]:
            cmds.matchTransform(f"{s}hand_IK_CTRL", f"{s}hand_JNT", rot = True)
            cmds.matchTransform(f"{s}uparm_FK_CTRL", f"{s}uparm_JNT", rot = True)
        
###### RIGGING ####################################################################
    def build_rig(self, joint_socket, ctrl_socket, spaces):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket, spaces)
        
        # create IK and FK joint chains
        L_jnts = [self.uparm_jnt, self.lowarm_jnt, self.hand_jnt, self.hand_end_jnt]
        L_switch = self.switch
        R_jnts = [x.replace("L_", "R_") for x in L_jnts]
        R_switch = self.switch.replace("L_", "R_")
        rig.ikfk_chains(L_jnts, L_switch)
        rig.ikfk_chains(R_jnts, R_switch)
        rig.ikfk_ctrlvis(self.L_ik_vis, self.L_fk_vis, self.L_bendies, L_switch)
        rig.ikfk_ctrlvis(self.R_ik_vis, self.R_fk_vis, self.R_bendies, R_switch)
        # shoulder ctrl vis
        for s in ["L_", "R_"]:
            switch = f"{s}arm_switcher_CTRL"
            cmds.addAttr(switch, longName = "shoulder_ctrl", at = "double", 
                         min = 0, max = 1, dv = 0)
            cmds.setAttr(switch+".shoulder_ctrl", e = True, keyable = False, cb = True)
            shoulder_mult = cmds.shadingNode(
                    "multDoubleLinear", n = f"{s}shoulderctrl_vis_MULT", au = True)
            cmds.connectAttr(switch+".shoulder_ctrl", shoulder_mult+".input1")
            cmds.connectAttr(switch+".ikfk", shoulder_mult+".input2")
            cmds.connectAttr(
                    shoulder_mult+".output", f"{s}shoulder_IK_CTRLShape.v", force = True)
        
        # connect rotateOrders from FK ctrls to FK joints
        for s in ["L_", "R_"]:
            ro_ctrls = [f"{s}uparm_FK_CTRL", f"{s}lowarm_FK_CTRL", f"{s}hand_FK_CTRL"]
            for ro_ctrl in ro_ctrls:
                jnt = ro_ctrl.replace("_CTRL", "_JNT")
                cmds.connectAttr(f"{ro_ctrl}.rotateOrder", f"{jnt}.rotateOrder")
            cmds.connectAttr(
                f"{s}clavicle_CTRL.rotateOrder", f"{s}clavicle_JNT.rotateOrder")
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
        
        ### OFFSET locator for bending beyond 90 degr
            elbow_b = f"{s}elbow_bendy_CTRL"
            elbow_off = cmds.spaceLocator(n = f"{s}elbow_offset_LOC")[0]
            cmds.matchTransform(elbow_off, elbow_b, pos = True, rot = True, scl = True)
            cmds.parent(elbow_off, "misc_GRP")
            util.mtx_hook(elbow_b, elbow_off)
        # forearm rot angle drives offset
            off_rmv = util.remap(
                    f"{s}elbow_offset_RMV", f"{s}lowarm_JNT.ry", 
                    min = "BODY_TUNING.e_start_angle", 
                    max = "BODY_TUNING.e_end_angle", 
                    outmin = 0, outmax = "BODY_TUNING.elbow_offset")
            cmds.connectAttr(off_rmv+".outValue", elbow_off+".tz")
        # duplicate forearm JNT / rename to elbow JNT
            elbow_jnt = cmds.duplicate(
                    f"{s}lowarm_JNT", parentOnly = True, n = f"{s}elbow_JNT")[0]
            rad = cmds.getAttr(elbow_jnt+".radius")
            cmds.setAttr(elbow_jnt+".radius", rad*2)
            cmds.sets(elbow_jnt, add = "bind_joints")
            cmds.orientConstraint(elbow_b, elbow_jnt, mo = True, w = 1,
                                  n = f"{s}elbow_ORI")
            cmds.pointConstraint([elbow_b, elbow_off], elbow_jnt, mo = True, w = 0.5,
                                  n = f"{s}elbow_POINT")
            cmds.scaleConstraint(elbow_b, elbow_jnt, mo = True, w = 1,
                                  n = f"{s}elbow_SCL")
        
    ### FK setup
        for s in ["L_", "R_"]:
        # clavicle
            clav = s+"clavicle_CTRL"
            cmds.parentConstraint(clav, f"{s}clavicle_JNT", mo = True, w = 1,
                                  n = clav.replace("CTRL", "PC"))
            cmds.scaleConstraint(clav, f"{s}clavicle_JNT", mo = True, w = 1,
                                 n = clav.replace("CTRL", "SCL"))
            # lock rz and add twist attr instead
            cmds.addAttr(clav, longName = "twist", attributeType = "double", 
                         defaultValue = 0)
            cmds.setAttr(clav+".twist", e = True, keyable = True)
            cmds.connectAttr(clav+".twist", clav+".rz")
            cmds.setAttr(clav+".rz", lock = True, k = False, cb = False)
        # uparm_jnt with constraint to make space switches work later
            cmds.pointConstraint(f"{s}uparm_FK_CTRL", f"{s}uparm_FK_JNT", mo = False,
                                 w = 1, n = f"{s}uparm_FK_POINT")
            cmds.orientConstraint(f"{s}uparm_FK_CTRL", f"{s}uparm_FK_JNT", mo = True,
                                  w = 1, n = f"{s}uparm_FK_ORI")
            cmds.scaleConstraint(f"{s}uparm_FK_CTRL", f"{s}uparm_FK_JNT", mo = True,
                                 w = 1, n = f"{s}uparm_FK_SCL")
            
            cmds.connectAttr(f"{s}lowarm_FK_CTRL.rotate", f"{s}lowarm_FK_JNT.rotate")
            cmds.connectAttr(f"{s}hand_FK_CTRL.rotate", f"{s}hand_FK_JNT.rotate")
            cmds.scaleConstraint(f"{s}lowarm_FK_CTRL", f"{s}lowarm_FK_JNT", mo = True,
                                 w = 1, n = f"{s}lowarm_FK_SCL")
            cmds.scaleConstraint(f"{s}hand_FK_CTRL", f"{s}hand_FK_JNT", mo = True,
                                 w = 1, n = f"{s}hand_FK_SCL")
        
    ### IK setup
        for s in ["L_", "R_"]:
            # variables
            ikhand = f"{s}hand_IK_CTRL"
            rig.sub_ctrl_vis(f"{s}hand_IK_sub_CTRL")
            cmds.connectAttr(f"{s}arm_switcher_CTRL.ikfk",
                             f"{s}armPole_line_CRVShape.v")
            arm_IKargs = {
                "name" : f"{s}arm_IKR",
                "startJoint" : f"{s}uparm_IK_JNT",
                "endEffector" : f"{s}hand_IK_JNT",
                "solver" : "ikRPsolver"
            }
            ikh = cmds.ikHandle(**arm_IKargs)
            cmds.parent(ikh[0], "misc_GRP")
            cmds.rename(ikh[1], f"{s}arm_IK_EFF")
            
            cmds.poleVectorConstraint(f"{s}arm_polevector_IK_CTRL",ikh[0], 
                                      n = f"{s}arm_polevector_IK_POL")
            util.mtx_hook(f"{s}hand_IK_sub_CTRL", ikh[0])
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
            util.mtx_hook(f"{s}hand_align_IK_CTRL", ikh_hand[0])
            
    ### stretchy IK and scale setup
        # current length = distance between shoulder and wrist
            armlen = cmds.shadingNode(
                    "distanceBetween", n = f"{s}arm_stretchylength_DBTW", au = True)
            cmds.connectAttr(f"{s}shoulder_IK_CTRL.worldMatrix[0]", 
                             f"{armlen}.inMatrix1")
            cmds.connectAttr(f"{s}hand_IK_sub_CTRL.worldMatrix[0]", 
                             f"{armlen}.inMatrix2")
        # orig_armlen = uparm + lowarm lengths
            uparmlen = util.distance(f"{s}uparm_JNT", f"{s}lowarm_JNT")
            lowarmlen = util.distance(f"{s}lowarm_JNT", f"{s}hand_JNT")
        # MD up/lowarmlen by attr from hand_IK_CTRL
            ikctrl_len = cmds.shadingNode(
                    "multiplyDivide", n = f"{s}arm_ikctrlattr_MULT", au = True)
            cmds.setAttr(f"{ikctrl_len}.input1X", uparmlen)
            cmds.setAttr(f"{ikctrl_len}.input1Y", lowarmlen)
            cmds.connectAttr(ikhand+".uparm_length", 
                             f"{ikctrl_len}.input2X")
            cmds.connectAttr(ikhand+".lowarm_length", 
                             f"{ikctrl_len}.input2Y")
        # ADD src_armlen = uparmlen + lowarmlen
            src_armlen = cmds.shadingNode(
                    "plusMinusAverage", n = f"{s}arm_srclength_ADD", au = True)
            cmds.connectAttr(f"{ikctrl_len}.outputX", f"{src_armlen}.input1D[0]")
            cmds.connectAttr(f"{ikctrl_len}.outputY", f"{src_armlen}.input1D[1]")
        # DIV by global scale
            glob_inv = cmds.shadingNode(
                    "multiplyDivide", n = f"{s}arm_stretchyglobalScl_DIV", au = True)
            cmds.setAttr(f"{glob_inv}.operation", 2) # divide
            cmds.connectAttr(f"{armlen}.distance", f"{glob_inv}.input1Z")
            cmds.connectAttr("global_CTRL.scale", f"{glob_inv}.input2")
        # TOGGLE blend betw orig length vs live-measured distance
            togg = cmds.shadingNode(
                    "blendColors", n = f"{s}stretch_toggle_BLEND", au = True)
            cmds.connectAttr(ikhand+".stretch_toggle",
                             togg+".blender")
            cmds.connectAttr(glob_inv+".outputZ",
                             togg+".color1B")
            cmds.setAttr(togg+".color2B", uparmlen + lowarmlen)
        # DIV normalize -> current length / source length
            norm = cmds.shadingNode(
                    "multiplyDivide", n = F"{s}arm_stretchy_NORM", au = True)
            cmds.setAttr(norm+".operation", 2) # divide
            cmds.connectAttr(togg+".outputB", norm+".input1Z")
            # cmds.connectAttr(glob_inv+".outputZ", norm+".input1Z")
            cmds.connectAttr(f"{src_armlen}.output1D", norm+".input2Z")
        # CONDITION -> prevent shrinking arm by setting a minimum scale Z = 1
            con = cmds.shadingNode(
                        "condition", n = f"{s}arm_stretchy_CON", asUtility = True)
            cmds.setAttr(f"{con}.operation", 5) # <= less or equal than
            cmds.connectAttr(norm+".outputZ", f"{con}.firstTerm") # stretch value
            cmds.setAttr(f"{con}.secondTerm", 1) # minimum
            cmds.setAttr(f"{con}.colorIfTrueR", 1) # output when bending limb
        # output when stretching limb {con}.outColorR
            cmds.connectAttr(norm+".outputZ", f"{con}.colorIfFalseR")
            
        # connect ctrl scale with globalScl
            for n, ik_jnt in enumerate(
                    [f"{s}uparm_IK_JNT", f"{s}lowarm_IK_JNT", f"{s}hand_IK_JNT"]
                    ):
                uniscl = cmds.shadingNode(
                        "multiplyDivide", n = ik_jnt.replace("_JNT", "_uniscale_MULT"), 
                        asUtility = True)
                stretchz = cmds.shadingNode(
                        "multiplyDivide", n = ik_jnt.replace("_JNT", "_stretchSz_MULT"), 
                        asUtility = True)
                cmds.connectAttr("global_CTRL.scale", f"{uniscl}.input1")
                if n == 0: # uparm
                    cmds.connectAttr(ikhand+".uparm_length",
                                     f"{uniscl}.input2Z")
                    cmds.connectAttr(f"{uniscl}.output", f"{stretchz}.input1")
                    cmds.connectAttr(f"{con}.outColorR", f"{stretchz}.input2Z")
                    cmds.connectAttr(f"{stretchz}.output", f"{ik_jnt}.scale")
### add thickness driver into uniscl.inputs 2X and 2Y
                if n == 1: # lowarm
                    cmds.connectAttr(ikhand+".lowarm_length",
                                     f"{uniscl}.input2Z")
                    cmds.connectAttr(f"{uniscl}.output", f"{stretchz}.input1")
                    cmds.connectAttr(f"{con}.outColorR", f"{stretchz}.input2Z")
                    cmds.connectAttr(f"{stretchz}.output", f"{ik_jnt}.scale")
### add thickness driver into uniscl.inputs 2X and 2Y
                if n == 2: # hand
                    cmds.connectAttr(ikhand+".scale",
                                     f"{uniscl}.input2")
                    cmds.connectAttr(f"{uniscl}.output", f"{ik_jnt}.scale")
    # wrist align
        for s in ["L_", "R_"]:
            rig.spaceblend(
                    f"{s}hand_IK_sub_CTRL", f"{s}lowarm_IK_JNT", 
                    f"{s}hand_align_IK_buffer_GRP",
                    f"{s}hand_IK_CTRL", "wrist_align", r_only = True)
            shapes = cmds.listRelatives(
                    f"{s}hand_align_IK_CTRL", children = True, shapes = True)
            for sh in shapes:
                cmds.connectAttr(f"{s}hand_IK_CTRL.wrist_align", sh+".v")
    # elbow pin
            rig.spaceblend(
                    f"{s}lowarm_JNT", f"{s}arm_polevector_IK_CTRL", 
                    f"{s}elbow_bendy_buffer_GRP",
                    f"{s}arm_polevector_IK_CTRL", "pin_elbow", t_only = True)
    
    ### Bendies
        for s in ["L_", "R_"]:
            uparm_bendy_joints = bendy.setup(
                mod_name = f"{s}uparm", 
                base_driver = f"{s}uparm_JNT", 
                head_driver = f"{s}lowarm_JNT",
                forwardaxis = "z", 
                upaxis = "-x",
                mid_ctrl = f"{s}uparm_bendy_CTRL", 
                twistInvDriver = f"{s}clavicle_JNT",
                elbow_bendy_ctrl = f"{s}elbow_bendy_CTRL")
            lowarm_bendy_joints = bendy.setup(
                mod_name = f"{s}lowarm", 
                base_driver = f"{s}lowarm_JNT", 
                head_driver = f"{s}hand_JNT",
                forwardaxis = "z", 
                upaxis = "-x",
                mid_ctrl = f"{s}lowarm_bendy_CTRL",
                elbow_bendy_ctrl = f"{s}elbow_bendy_CTRL",
                offset_driver = f"{s}elbow_offset_LOC")
        # uparm & lowarm bendy ctrls both aim to elbow_bendy and squetch
            bendy.aim(
                bendy = f"{s}uparm_bendy_CTRL",
                aimtarget = f"{s}elbow_bendy_CTRL", 
                uptarget = f"{s}uparm_baseTwist_LOC",
                root = f"{s}uparm_bendy_1_JNT",
                vaim = (0,0,1),
                vup = (1,0,0),
                scldriver = f"{s}uparm_JNT")
            bendy.aim(
                bendy = f"{s}lowarm_bendy_CTRL",
                aimtarget = f"{s}elbow_offset_LOC", 
                uptarget = f"{s}lowarm_endTwist_LOC",
                root = f"{s}lowarm_twist_end_JNT",
                vaim = (0,0,-1),
                vup = (1,0,0),
                scldriver = f"{s}lowarm_JNT")
            
    ### THICKNESS setup for bendies
            upthick = bendy.chainthick(f"{s}uparm_thickness_channels_GRP", 
                                       ["sx", "sy"], uparm_bendy_joints)
            lowthick = bendy.chainthick(f"{s}lowarm_thickness_channels_GRP", 
                                        ["sx", "sy"], lowarm_bendy_joints)
            cmds.parent([upthick, lowthick], "misc_GRP")
            switcher = f"{s}arm_switcher_CTRL"
        # UP START
        # ikfk blend betw uparm_FK_CTRL & hand_IK_CTRL attrs
            upstartblend = cmds.shadingNode(
                    "blendColors", n = f"{s}uparm_thickstart_ikfk_BLEND", au = True)
            cmds.connectAttr(switcher+".ikfk", upstartblend+".blender")
            cmds.connectAttr(f"{s}hand_IK_CTRL.up_thickX", upstartblend+".color1R")
            cmds.connectAttr(f"{s}hand_IK_CTRL.up_thickY", upstartblend+".color1G")
            cmds.connectAttr(f"{s}uparm_FK_CTRL.s", upstartblend+".color2")
            # into upthick node
            cmds.connectAttr(upstartblend+".outputR", upthick+".start_sx")
            cmds.connectAttr(upstartblend+".outputG", upthick+".start_sy")
        # UP MID
        # uparm bendy directly into upthick.mid (no global scl)
            cmds.connectAttr(f"{s}uparm_bendy_CTRL.sx", upthick+".mid_sx")
            cmds.connectAttr(f"{s}uparm_bendy_CTRL.sy", upthick+".mid_sy")
        # ELBOW = UP END & LOW START
        # ikfk blend betw lowarm_FK_CTRL & hand_IK_CTRL attrs
            upendblend = cmds.shadingNode(
                    "blendColors", n = f"{s}uparm_thickend_ikfk_BLEND", au = True)
            cmds.connectAttr(switcher+".ikfk", upendblend+".blender")
            cmds.connectAttr(f"{s}hand_IK_CTRL.low_thickX", upendblend+".color1R")
            cmds.connectAttr(f"{s}hand_IK_CTRL.low_thickY", upendblend+".color1G")
            cmds.connectAttr(f"{s}lowarm_FK_CTRL.s", upendblend+".color2")
            # mult with elbow bendy scl
            elbowthick = cmds.shadingNode("multiplyDivide", 
                                            n = f"{s}elbow_thick_MULT", 
                                            au = True)
            cmds.connectAttr(upendblend+".output", elbowthick+".input1")
            cmds.connectAttr(f"{s}elbow_bendy_CTRL.s", elbowthick+".input2")
            # into upthick node
            cmds.connectAttr(elbowthick+".outputX", upthick+".end_sx")
            cmds.connectAttr(elbowthick+".outputY", upthick+".end_sy")
            # also into lowthick.start
            cmds.connectAttr(elbowthick+".outputX", lowthick+".start_sx")
            cmds.connectAttr(elbowthick+".outputY", lowthick+".start_sy")
        # LOW MID
        # lowarm bendy direct into lowthick.mid (no global scale)
            cmds.connectAttr(f"{s}lowarm_bendy_CTRL.sx", lowthick+".mid_sx")
            cmds.connectAttr(f"{s}lowarm_bendy_CTRL.sy", lowthick+".mid_sy")
        # LOW END
        # blend betw hand_FK_CTRL & hand_IK_CTRL
            lowendblend = cmds.shadingNode(
                    "blendColors", n = f"{s}lowarm_thickend_ikfk_BLEND", au = True)
            cmds.connectAttr(switcher+".ikfk", lowendblend+".blender")
            cmds.connectAttr(f"{s}hand_IK_CTRL.s", lowendblend+".color1")
            cmds.connectAttr(f"{s}hand_FK_CTRL.s", lowendblend+".color2")
            # into lowthick node
            cmds.connectAttr(lowendblend+".outputR", lowthick+".end_sx")
            cmds.connectAttr(lowendblend+".outputG", lowthick+".end_sy")
                
    ### DELTOID twist(asymmetric) = IKS.roll - IKS.twist
        delt_inv = cmds.shadingNode(
                "multiplyDivide", n = "deltoidInv_MULT", asUtility = True)
        cmds.setAttr(f"{delt_inv}.input2", -1, -1, -1)
        
        cmds.connectAttr("L_clavicle_CTRL.deltoid_twist", "L_uparm_IKS.roll")
        cmds.connectAttr("L_clavicle_CTRL.deltoid_twist", f"{delt_inv}.input1X")
        cmds.connectAttr(f"{delt_inv}.outputX", "L_uparm_IKS.twist")
        
        cmds.connectAttr("R_clavicle_CTRL.deltoid_twist", f"{delt_inv}.input1Y")
        cmds.connectAttr(f"{delt_inv}.outputY", "R_uparm_IKS.roll")
        cmds.connectAttr("R_clavicle_CTRL.deltoid_twist", "R_uparm_IKS.twist")
        
    ### CLEAN UP attributes - lock & hide
        util.lock([self.lowarm_fk, self.hand_fk], ["tx","ty","tz"], rsidetoo = True)
        util.lock(self.switch, rsidetoo = True)
        util.lock(self.lowarm_fk, ["tx","ty","tz","rx","rz"], rsidetoo = True)
        util.lock(self.hand_fk, ["tx","ty","tz"], rsidetoo = True)
        util.lock(self.polevector, ["rx","ry","rz","sx","sy","sz"], rsidetoo = True)
        util.lock(self.shoulder_ik, ["sx","sy"], rsidetoo = True)
        util.lock(self.clavicle_fk, ["sx","sy"], rsidetoo = True)
        util.lock(self.hand_align, ["tx","ty","tz","sx","sy","sz"], rsidetoo = True)
        util.lock(self.elbow_b, ["rx","ry","sz"], rsidetoo = True)
        util.lock([self.uparm_b, self.lowarm_b], ["rz"], rsidetoo = True)
        
    # hide IK & FK joint chains
        for s in ["L_", "R_"]:
            cmds.hide(f"{s}uparm_FK_JNT", f"{s}uparm_IK_JNT")

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