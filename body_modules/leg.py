import maya.cmds as cmds

from body_proxies.proxyleg import ProxyLeg

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig
from utils import bendy


class Legs(object):
    
    def __init__(self):
        
        self.module_name = "L_leg"
        
        self.upleg_jnt = "L_upleg_JNT"
        self.knee_jnt = "L_knee_JNT"
        self.lowleg_jnt = "L_lowleg_JNT"
        self.foot_jnt = "L_foot_JNT"
        self.toes_jnt = "L_toes_JNT"
        self.toes_end_jnt = "L_toes_end_JNT"
        
        self.upleg_fk = "L_upleg_FK_CTRL"
        self.knee_fk = "L_knee_FK_CTRL"
        self.lowleg_fk = "L_lowleg_FK_CTRL"
        self.foot_fk = "L_foot_FK_CTRL"
        self.toes_fk = "L_toes_FK_CTRL"
        
        self.upleg_b = "L_upleg_bendy_CTRL"
        self.lowleg_b = "L_lowleg_bendy_CTRL"
        self.knee_b = "L_knee_bendy_CTRL"
        
        self.foot_ik = "L_foot_IK_CTRL"
        self.ankle_ik = "L_ankle_IK_CTRL"
        self.hipjoint_ik = "L_hipjoint_IK_CTRL"
        self.polevector = "L_leg_polevector_IK_CTRL"
        self.switch = "L_leg_switcher_CTRL"
        
        self.outpiv_loc = "L_outroll_IK_LOC"
        self.inpiv_loc = "L_inroll_IK_LOC"
        self.heelpiv_loc = "L_heelroll_IK_LOC"
        self.toepiv_loc = "L_toeroll_IK_LOC"
        self.bswiv_loc = "L_ballswivel_IK_LOC"
        self.toes_loc = "L_toewiggle_IK_LOC"
        self.ball_loc = "L_ball_IK_LOC"
        
        self.heeloff_loc_grp = "L_toeroll_IK_heeloffset_loc_GRP"
        self.heeloff_ctrl_grp = "L_toeroll_IK_heeloffset_ctrl_GRP"
         
    def skeleton(self, joint_socket):
        pleg = ProxyLeg()
        leg_jnts = rig.make_joints(list(pleg.proxy_dict)[:6], "zyx", 3)
        foot = self.foot_jnt
        toe = self.toes_jnt
        end = self.toes_end_jnt
        cmds.joint(
            self.upleg_jnt, e = True,
            orientJoint = "yxz", secondaryAxisOrient = "xup", children = True)
        cmds.parent(self.upleg_jnt, joint_socket)
        
        # orient foot & toes to world
        cmds.parent(foot, world = True)
        cmds.joint(foot, e = True, orientJoint = "none", children = True)
        cmds.parent([toe, end], world = True)
        for j in [foot, toe, end]:
            # make Y axis point downwards like rest of leg
            cmds.setAttr(f"{j}.jointOrientX", 180)
        cmds.parent(foot, self.lowleg_jnt)
        cmds.parent(toe, foot)
        cmds.parent(end, toe)
        
        mirr_jnts = cmds.mirrorJoint(
                self.upleg_jnt, 
                mirrorYZ = True, 
                mirrorBehavior = True, 
                searchReplace = ["L_", "R_"])
        # except end_JNT
        cmds.sets(leg_jnts[:-1], add = "bind_joints")
        cmds.sets(mirr_jnts[:-1], add = "bind_joints")

    def controls(self, ctrl_socket):
        ikctrl_grp = cmds.group(
                n = "L_leg_IKctrls_GRP", empty = True, parent = "global_sub_CTRL")
        pleg = ProxyLeg()
        fk = [self.upleg_jnt,self.knee_jnt, self.lowleg_jnt, self.foot_jnt, 
             self.toes_jnt, self.toes_end_jnt]
        fk_ro = "zyx"
        scl = util.get_distance(self.upleg_jnt, self.lowleg_jnt)/5
        
        # FK ctrls
        dist = util.get_distance(self.upleg_jnt, self.knee_jnt)
        fk_upleg = Nurbs.fk_box(self.upleg_fk, scl, dist*0.75, "blue", fk_ro)
        fk_knee = cmds.group(n = self.knee_fk, empty = True)
        fk_lowleg = Nurbs.fk_box(self.lowleg_fk,scl, dist*0.6, "blue", fk_ro)
        fk_foot = Nurbs.box(self.foot_fk, scl, scl, scl/3, "blue", fk_ro)
        fk_toes = Nurbs.box(self.toes_fk, scl, scl/1.5, scl/3, "blue", fk_ro)
        Nurbs.flip_shape(fk_upleg, "y")
        Nurbs.flip_shape(fk_lowleg, "y")
        Nurbs.flip_shape(fk_foot, "y")
        
        # IK ctrls
        ik_foot = Nurbs.cube(self.foot_ik, scl*1.2, "blue", "zxy")
        ik_ankle = Nurbs.square(self.ankle_ik, scl*1.4, "sky", "zxy")
        ik_pv = Nurbs.octahedron(self.polevector, scl/3, "blue")
        ik_hipj = Nurbs.square(self.hipjoint_ik, scl*2.5, "blue")
        
        # bendies
        upleg_b = Nurbs.double_lolli(self.upleg_b, dist/4, "sky", "zyx")
        lowleg_b = Nurbs.double_lolli(self.lowleg_b, dist/4, "sky", "zyx")
        knee_b = Nurbs.double_lolli(self.knee_b, dist/4, "sky", "zyx")
        Nurbs.flip_shape(upleg_b, "-y")
        Nurbs.flip_shape(lowleg_b, "-y")
        Nurbs.flip_shape(knee_b, "-y")
            
        # switcher
        switch = Nurbs.switcher(self.switch, dist/9)
        Nurbs.flip_shape(switch, "-x")
        
        # expose rotateOrder
        for ro in [fk_upleg, fk_foot, ik_foot, ik_hipj]:
            cmds.setAttr(f"{ro}.rotateOrder", keyable = True)
        
        # ik foot roll locators
        out_loc = cmds.spaceLocator(n = self.outpiv_loc)[0]
        in_loc = cmds.spaceLocator(n = self.inpiv_loc)[0]
        heel_loc = cmds.spaceLocator(n = self.heelpiv_loc)[0]
        toepiv_loc = cmds.spaceLocator(n = self.toepiv_loc)[0]
        bswiv_loc = cmds.spaceLocator(n = self.bswiv_loc)[0]
        toes_loc = cmds.spaceLocator(n = self.toes_loc)[0]
        ball_loc = cmds.spaceLocator(n = self.ball_loc)[0]
        roll_locs_grp = cmds.group(n = "L_roll_locs_GRP", empty = True)
        
        # ctrl : position & parent
        relations = {
            fk_upleg :  (self.upleg_jnt,        ctrl_socket),
            fk_knee :   (self.knee_jnt,         fk_upleg),
            fk_lowleg : (self.lowleg_jnt,       fk_knee),
            fk_foot :   (self.foot_jnt,         fk_lowleg),
            fk_toes :   (self.toes_jnt,         fk_foot),
            ik_foot :   (self.foot_jnt,         ikctrl_grp),
            ik_ankle :  (self.foot_jnt,         ik_foot),
            ik_pv :     (pleg.polev,            ikctrl_grp),
            upleg_b :   (self.upleg_jnt,        ikctrl_grp),
            lowleg_b :  (self.lowleg_jnt,       ikctrl_grp),
            knee_b :    (self.knee_jnt,         ikctrl_grp),
            ik_hipj :   (self.upleg_jnt,        ctrl_socket),
            switch :    (self.foot_jnt,         ikctrl_grp),
            roll_locs_grp :  (self.toes_jnt,    ikctrl_grp),
            out_loc :   (pleg.outpiv,           roll_locs_grp),
            in_loc :    (pleg.inpiv,            out_loc),
            heel_loc :  (pleg.heelpiv,          in_loc),
            toepiv_loc :(pleg.toespiv,          heel_loc),
            bswiv_loc : (self.toes_jnt,         toepiv_loc),
            ball_loc :  (self.toes_jnt,         bswiv_loc),
            toes_loc :  (self.toes_jnt,         bswiv_loc),
        }
        
        for ctrl in list(relations):
        # some ctrls in world orientations instead of matching joint
        # + ik foot roll locators
            if ctrl in [ik_foot, ik_ankle, ik_hipj, switch,
                        bswiv_loc, ball_loc, toes_loc, roll_locs_grp]:
                cmds.matchTransform(ctrl, relations[ctrl][0], pos = True, rot = False)
            else:
                cmds.matchTransform(ctrl, relations[ctrl][0], pos = True, rot = True)
            cmds.parent(ctrl, relations[ctrl][1])
    # position bendies
        upleg_pc = cmds.pointConstraint(
                (self.upleg_jnt, self.lowleg_jnt), upleg_b, 
                offset = (0,0,0), weight = 0.5)[0]
        lowleg_pc = cmds.pointConstraint(
                (self.lowleg_jnt, self.foot_jnt), lowleg_b, 
                offset = (0,0,0), weight = 0.5)[0]
        knee_pc = cmds.pointConstraint(
                (self.knee_jnt, self.lowleg_jnt), knee_b, 
                offset = (0,0,0), weight = 0.5)[0]
        cmds.delete((upleg_pc, lowleg_pc, knee_pc))
    # offset switch_ctrl to side of ankle
        cmds.move(dist/2, 0, 0, switch, relative = True)
        
    # add attributes
        util.attr_separator([fk_upleg, ik_foot, ik_ankle, ik_hipj])
        cmds.addAttr(ik_foot, longName = "upleg_length", attributeType = "double", 
                     min = 0, defaultValue = 1)
        cmds.setAttr(f"{ik_foot}.upleg_length", e = True, keyable = True)
        cmds.addAttr(ik_foot, longName = "lowleg_length", attributeType = "double", 
                     min = 0, defaultValue = 1)
        cmds.setAttr(f"{ik_foot}.lowleg_length", e = True, keyable = True)
        cmds.addAttr(ik_foot, longName = "ball_roll", attributeType = "double", 
                     defaultValue = 0)
        cmds.setAttr(f"{ik_foot}.ball_roll", e = True, keyable = True)
        cmds.addAttr(ik_foot, longName = "ball_swivel", attributeType = "double", 
                     defaultValue = 0)
        cmds.setAttr(f"{ik_foot}.ball_swivel", e = True, keyable = True)
        cmds.addAttr(ik_foot, longName = "toes_UD", attributeType = "double", 
                     defaultValue = 0)
        cmds.setAttr(f"{ik_foot}.toes_UD", e = True, keyable = True)
        cmds.addAttr(ik_foot, longName = "toes_LR", attributeType = "double", 
                     defaultValue = 0)
        cmds.setAttr(f"{ik_foot}.toes_LR", e = True, keyable = True)
        # cmds.addAttr(ik_foot, longName = "toe_heel_roll", attributeType = "double", 
        #              defaultValue = 0)
        # cmds.setAttr(f"{ik_foot}.toe_heel_roll", e = True, keyable = True)
        # cmds.addAttr(ik_foot, longName = "in_out_roll", attributeType = "double", 
        #              defaultValue = 0)
        # cmds.setAttr(f"{ik_foot}.in_out_roll", e = True, keyable = True)
        
    # foot roll ctrls
        roll_locs = [heel_loc, out_loc, in_loc, toepiv_loc, ball_loc, toes_loc]
        roll_ctrls = []
        for loc in roll_locs:
            roll_ctrl = Nurbs.sphere(loc.replace("_LOC", "_CTRL"), scl/8, "blue", "xyz")
            roll_ctrls.append(roll_ctrl)
            cmds.matchTransform(roll_ctrl, loc, position = True)
        roll_ctrls_grp = cmds.group(n = "L_roll_ctrls_GRP", em = True)
        cmds.parent(roll_ctrls, roll_ctrls_grp)
        cmds.parent(roll_ctrls_grp, ik_ankle)
        util.mtx_zero(roll_ctrls_grp)
        util.mtx_zero(roll_locs_grp)
        
    #### MIRROR CTRLS TO THE RIGHT SIDE ####
        ikctrl_mirror_grp = cmds.group(
                n = "R_leg_IKctrls_mirror_GRP", empty = True, parent = "global_sub_CTRL")
        cmds.setAttr(f"{ikctrl_mirror_grp}.sx", -1)
        fkctrl_mirror_grp = cmds.group(
                n = "R_leg_FKctrls_mirror_GRP", empty = True, parent = ctrl_socket)
        cmds.setAttr(f"{fkctrl_mirror_grp}.sx", -1)
        rig.mirror_ctrls([fk_upleg], fkctrl_mirror_grp)
        rig.mirror_ctrls([ik_foot, ik_pv, ik_hipj, roll_locs_grp], ikctrl_mirror_grp)
        rig.mirror_ctrls([switch], ikctrl_mirror_grp)
        rig.mirror_ctrls([upleg_b, lowleg_b, knee_b], ikctrl_mirror_grp)
        
    # scale invert joints for FK ctrls
        sclinv_jnts = [fk_upleg, fk_knee, fk_lowleg]
        util.insert_scaleInvJoint(sclinv_jnts)
        util.insert_scaleInvJoint([x.replace("L_", "R_") for x in sclinv_jnts])
        
    # selection sets
        l_ctrls = [fk_upleg, fk_lowleg, fk_foot, fk_toes, 
                   ik_foot, ik_ankle, ik_pv, ik_hipj, 
                   upleg_b, knee_b, lowleg_b, switch]
        l_ctrls.extend(roll_ctrls)
        r_ctrls = [x.replace("L_", "R_") for x in l_ctrls]
        cmds.sets(l_ctrls, add = "L_leg")
        cmds.sets(r_ctrls, add = "R_leg")
        
        l_ctrls.insert(1, fk_knee)
        l_ctrls.extend(roll_locs)
        
    # cleanup
        util.mtx_zero(l_ctrls, rsidetoo = True)
        util.lock(switch, rsidetoo = True)
        util.lock(fk_lowleg, channels = ["tx","ty","tz","ry","rz"], rsidetoo = True)
        util.lock([fk_foot, fk_toes], channels = ["tx","ty","tz"], rsidetoo = True)
        

    def build_rig(self, joint_socket, ctrl_socket, spaces):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket)
        
    # create IK and FK joint chains
        L_jnts = [self.upleg_jnt, self.knee_jnt, self.lowleg_jnt, 
                  self.foot_jnt, self.toes_jnt, self.toes_end_jnt]
        L_switch = self.switch
        R_jnts = [x.replace("L_", "R_") for x in L_jnts]
        R_switch = self.switch.replace("L_", "R_")
        rig.ikfk_chains(L_jnts, L_switch)
        rig.ikfk_chains(R_jnts, R_switch)
        
    # connect rotateOrders from FK ctrls to FK joints
        for s in ["L_", "R_"]:
            ro_ctrls = [f"{s}upleg_FK_CTRL", f"{s}knee_FK_CTRL", f"{s}lowleg_FK_CTRL",
                        f"{s}foot_FK_CTRL", f"{s}toes_FK_CTRL"]
            for ro_ctrl in ro_ctrls:
                jnt = ro_ctrl.replace("_CTRL", "_JNT")
                cmds.connectAttr(f"{ro_ctrl}.rotateOrder", f"{jnt}.rotateOrder")
        
    # double knee ctrl setup: -0.5rx counter on lowleg buffer + 0.5rx on knee
        for s in ["L_", "R_"]:
            k_mult = cmds.shadingNode(
                    "multDoubleLinear", n = f"{s}knee_halfRot_MULT", asUtility = True)
            k_negmult  = cmds.shadingNode(
                    "multDoubleLinear", n = f"{s}knee_halfCounterRot_MULT", asUtility = True)
            cmds.setAttr(f"{k_mult}.input2", 0.5)
            cmds.setAttr(f"{k_negmult}.input2", -0.5)
            cmds.connectAttr(f"{s}lowleg_FK_CTRL.rotateX", f"{k_mult}.input1")
            cmds.connectAttr(f"{s}lowleg_FK_CTRL.rotateX", f"{k_negmult}.input1")
            kbuff = util.buffer(f"{s}lowleg_FK_CTRL", new_suffix = "counterRot_GRP")
            util.mtx_zero([kbuff, f"{s}lowleg_FK_CTRL"])
            cmds.connectAttr(f"{k_mult}.output", f"{s}knee_FK_CTRL.rotateX")
            cmds.connectAttr(f"{k_negmult}.output", f"{kbuff}.rotateX")
        
    ### FK setup
        # upleg_jnt with constraint to make space switches work
            cmds.parentConstraint(
                f"{s}upleg_FK_CTRL", f"{s}upleg_FK_JNT", mo = True, weight = 1)
            cmds.scaleConstraint(
                f"{s}upleg_FK_CTRL", f"{s}upleg_FK_JNT", mo = True, weight = 1)
            cmds.connectAttr(f"{s}knee_FK_CTRL.rotate", f"{s}knee_FK_JNT.rotate")
        # half rotX for lowLeg
            cmds.connectAttr(f"{k_mult}.output", f"{s}lowleg_FK_JNT.rotateX")
            cmds.scaleConstraint(
                f"{s}knee_FK_CTRL", f"{s}knee_FK_JNT", mo = True, weight = 1)
            cmds.scaleConstraint(
                f"{s}lowleg_FK_CTRL", f"{s}lowleg_FK_JNT", mo = True, weight = 1)
        # foot
            cmds.connectAttr(f"{s}foot_FK_CTRL.rotate", f"{s}foot_FK_JNT.rotate")
            cmds.connectAttr(f"{s}toes_FK_CTRL.rotate", f"{s}toes_FK_JNT.rotate")
            cmds.scaleConstraint(
                f"{s}foot_FK_CTRL", f"{s}foot_FK_JNT", mo = True, weight = 1)
            cmds.scaleConstraint(
                f"{s}toes_FK_CTRL", f"{s}toes_FK_JNT", mo = True, weight = 1)
                
    ### IK Setup
        for s in ["L_", "R_"]:
            # switcher follows deform skeleton
            util.mtx_hook(f"{s}lowleg_JNT", f"{s}leg_switcher_CTRL")
        # leg (Rotate Plane)
            leg_IKargs = {
                "name" : f"{s}leg_IKR",
                "startJoint" : f"{s}upleg_IK_JNT",
                "endEffector" : f"{s}foot_IK_JNT",
                "solver" : "ikRPsolver"}
            ikh = cmds.ikHandle(**leg_IKargs)
            cmds.parent(ikh[0], "misc_GRP")
            cmds.rename(ikh[1], f"{s}leg_IK_EFF")
            cmds.poleVectorConstraint(f"{s}leg_polevector_IK_CTRL",ikh[0])
            util.mtx_hook(f"{s}ball_IK_LOC", ikh[0])
        # foot (single chain)
            foot_IKargs = {
                'name' : f'{s}foot_IKS',
                'startJoint' : f"{s}foot_IK_JNT",
                'endEffector' : f"{s}toes_IK_JNT",
                'solver' : 'ikSCsolver'}
            ikh_foot = cmds.ikHandle(**foot_IKargs)
            cmds.parent(f'{s}foot_IKS', 'misc_GRP')
            cmds.rename(ikh_foot[1], f"{s}foot_IK_EFF")
            util.mtx_hook(f"{s}ball_IK_LOC", ikh_foot[0])
        # toes (single chain)
            toes_IKargs = {
                'name' : f'{s}toes_IKS',
                'startJoint' : f"{s}toes_IK_JNT",
                'endEffector' : f"{s}toes_end_IK_JNT",
                'solver' : 'ikSCsolver'}
            ikh_toes = cmds.ikHandle(**toes_IKargs)
            cmds.parent(f'{s}toes_IKS', 'misc_GRP')
            cmds.rename(ikh_toes[1], f"{s}toes_IK_EFF")
            util.mtx_hook(f"{s}toewiggle_IK_LOC", ikh_toes[0])
            
    ### stretchy IK and scale setup
        # current length
            
    ### Shoe Offset Setup
        cmds.addAttr(
            "RIG_TUNING_PANEL", longName = "shoes_heel_offset",
            niceName = "Shoes Heel Offset", attributeType = "double", 
            min = 0, defaultValue = 0)
        cmds.setAttr("RIG_TUNING_PANEL.shoes_heel_offset", e = True, channelBox = True)
        cmds.addAttr(
            "RIG_TUNING_PANEL", longName = "shoes_sole_offset",
            niceName = "Shoes Sole Offset", attributeType = "double", 
            min = 0, defaultValue = 0)
        cmds.setAttr("RIG_TUNING_PANEL.shoes_sole_offset", e = True, channelBox = True)
        cmds.addAttr(
            "RIG_TUNING_PANEL", longName = "shoes_toes_offset",
            niceName = "Shoes Toes Offset", attributeType = "double", defaultValue = 0)
        cmds.setAttr("RIG_TUNING_PANEL.shoes_toes_offset", e = True, channelBox = True)
    # FK - heel & toes offset
        for s in ["L_", "R_"]:
            pmas = []
            for n in ["heelOffset_foot", "heelOffset_toes", "toesOffset"]:
                pma = cmds.shadingNode(
                        "plusMinusAverage", n = f"{s}{n}_PMA", asUtility = True)
                pmas.append(pma)
        # fk foot_jnt.r = foot_ctrl.r + heel off
            cmds.connectAttr(f"{s}foot_FK_CTRL.r", f"{pmas[0]}.input3D[0]")
            cmds.connectAttr("RIG_TUNING_PANEL.shoes_heel_offset", 
                             f"{pmas[0]}.input3D[1].input3Dx")
            cmds.connectAttr(f"{pmas[0]}.output3D", f"{s}foot_FK_JNT.r", force = True)
        # fk toes_jnt.r = toes_ctrl.r - heel off + toe off
            cmds.setAttr(f"{pmas[1]}.operation", 2) # subtract
            cmds.connectAttr(f"{s}toes_FK_CTRL.r", f"{pmas[1]}.input3D[0]")
            cmds.connectAttr("RIG_TUNING_PANEL.shoes_heel_offset", 
                             f"{pmas[1]}.input3D[1].input3Dx")
            cmds.connectAttr(f"{pmas[1]}.output3D", f"{pmas[2]}.input3D[0]")
            cmds.connectAttr("RIG_TUNING_PANEL.shoes_toes_offset", 
                             f"{pmas[2]}.input3D[1].input3Dx")
            cmds.connectAttr(f"{pmas[2]}.output3D", f"{s}toes_FK_JNT.r", force = True)
        
        # hidden DRIVER setup for heel height offset from shoes
        # ankle rx + ball ty & tz as inputs for locs and ctrls to adjust accordingly
#### need global scale??
        ankle = cmds.spaceLocator(n = "ankle_driver_LOC")[0]
        ball = cmds.spaceLocator(n = "ball_driver_LOC")[0]
        heeloff_grp = cmds.group(
                [ankle, ball], n = "shoe_heel_offset_driver_GRP", 
                parent = "misc_GRP")
        cmds.matchTransform(ankle, self.foot_jnt, position = True)
        cmds.matchTransform(ball, self.toes_jnt, position = True)
        util.mtx_zero([ankle, ball])
        cmds.parentConstraint(
                ankle, ball, mo = True, skipRotate = ("x", "y", "z"), 
                weight = 1, n = "shoe_heel_offset_driver_PC")
        cmds.connectAttr("RIG_TUNING_PANEL.shoes_heel_offset", f"{ankle}.rx")
        cmds.setAttr(f"{heeloff_grp}.v", 0)
        
    ### foot roll setup
        # rotatePivot connections
        locs = [self.outpiv_loc, self.inpiv_loc, self.toepiv_loc, self.heelpiv_loc,
                self.ball_loc, self.toes_loc]
        r_locs = [x.replace("L_", "R_") for x in locs]
        locs.extend(r_locs)
        for loc in locs:
            roll_ctrl = loc.replace("_LOC", "_CTRL")
#### could plug in SOLE THICKNESS offset in ty here
            cmds.connectAttr(f"{roll_ctrl}.t", f"{loc}.rotatePivot")
        for s in ["L_", "R_"]:
            util.mtx_hook(f"{s}ankle_IK_CTRL", f"{s}roll_locs_GRP")
        # IK - heel offset groups
            loc_heeloff = cmds.group(
                    f"{s}toeroll_IK_LOC", 
                    n = f"{s}heeloffset_loc_GRP", parent = f"{s}heelroll_IK_LOC")
            ctrl_heeloff = cmds.group(
                    [f"{s}toeroll_IK_CTRL", f"{s}ball_IK_CTRL", f"{s}toewiggle_IK_CTRL"], 
                    n = f"{s}heeloffset_ctrl_GRP", parent = f"{s}roll_ctrls_GRP")
        # IK - heel offset connections
            cmds.connectAttr(f"{ball}.ty", f"{s}roll_locs_GRP.ty")
            cmds.connectAttr(f"{ball}.ty", f"{s}roll_ctrls_GRP.ty")
            cmds.connectAttr(f"{ball}.tz", f"{loc_heeloff}.tz")
            cmds.connectAttr(f"{ball}.tz", f"{ctrl_heeloff}.tz")
        # ball roll = ctrl.r + attr.rx + heeloffset.rx
            br_plus = cmds.shadingNode(
                    "plusMinusAverage", n = f"{s}ballRoll_PLUS", asUtility = True)
            cmds.connectAttr(f"{s}ball_IK_CTRL.r", f"{br_plus}.input3D[0]")
            cmds.connectAttr(f"{s}foot_IK_CTRL.ball_roll", 
                             f"{br_plus}.input3D[1].input3Dx")
            cmds.connectAttr(f"{ankle}.rx", f"{br_plus}.input3D[2].input3Dx")
            cmds.connectAttr(f"{br_plus}.output3D", f"{s}ball_IK_LOC.r")
        # ball swivel
            cmds.connectAttr(
                    f"{s}foot_IK_CTRL.ball_swivel", f"{s}ballswivel_IK_LOC.rotateY")
        # toewiggle = ctrl.r + attr.rx/ry + toeoffset.rx
            toewig_plus = cmds.shadingNode(
                    "plusMinusAverage", n = f"{s}toeWiggle_PLUS", asUtility = True)
            cmds.connectAttr(f"{s}toewiggle_IK_CTRL.r", f"{toewig_plus}.input3D[0]")
            cmds.connectAttr(f"{s}foot_IK_CTRL.toes_UD", 
                             f"{toewig_plus}.input3D[1].input3Dx")
            cmds.connectAttr(f"{s}foot_IK_CTRL.toes_LR", 
                             f"{toewig_plus}.input3D[1].input3Dy")
            cmds.connectAttr(f"{toewig_plus}.output3D", f"{s}toewiggle_IK_LOC.r")
        # clamped attrs: toe/heel & in/out roll
### fuck it! do those later maybe. Just straight connections from ctrls for now
            cmds.connectAttr(f"{s}toeroll_IK_CTRL.r", f"{s}toeroll_IK_LOC.r")
            cmds.connectAttr(f"{s}heelroll_IK_CTRL.r", f"{s}heelroll_IK_LOC.r")
            cmds.connectAttr(f"{s}inroll_IK_CTRL.r", f"{s}inroll_IK_LOC.r")
            cmds.connectAttr(f"{s}outroll_IK_CTRL.r", f"{s}outroll_IK_LOC.r")
        
        

if __name__ == "__main__":
    
    test2 = Module()
        
    pass