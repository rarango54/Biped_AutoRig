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
        self.foot_sub_ik = "L_foot_IK_sub_CTRL"
        self.foot_align = "L_foot_align_IK_CTRL"
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
        
        self.outpiv = "L_outroll_IK_CTRL"
        self.inpiv = "L_inroll_IK_CTRL"
        self.heelpiv = "L_heelroll_IK_CTRL"
        self.toepiv = "L_toeroll_IK_CTRL"
        self.bswiv = "L_ballswivel_IK_CTRL"
        self.toes = "L_toewiggle_IK_CTRL"
        self.ball = "L_ball_IK_CTRL"
        
        self.heeloff_loc_grp = "L_toeroll_IK_heeloffset_loc_GRP"
        self.heeloff_ctrl_grp = "L_toeroll_IK_heeloffset_ctrl_GRP"
        
        self.L_ik_vis = [self.foot_ik, self.polevector, 
                           self.hipjoint_ik, self.outpiv, self.inpiv, self.heelpiv,
                           self.toepiv, self.toes, self.ball]
        self.L_fk_ctrls = [self.upleg_fk, self.lowleg_fk, self.foot_fk, self.toes_fk]
        self.L_bendies = [self.upleg_b, self.knee_b, self.lowleg_b]
        self.R_ik_vis = [x.replace("L_", "R_") for x in self.L_ik_vis]
        self.R_fk_ctrls = [x.replace("L_", "R_") for x in self.L_fk_ctrls]
        self.R_bendies = [x.replace("L_", "R_") for x in self.L_bendies]
         
    def skeleton(self, joint_socket):
        pleg = ProxyLeg()
        leg_jnts = rig.make_joints(list(pleg.proxy_dict)[:6], "zyx", 1.5)
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
        # only foot & toe jnt (rest of leg is skinned to bendy jnts)
        cmds.sets(leg_jnts[3:-1], add = "bind_joints")
        cmds.sets(mirr_jnts[3:-1], add = "bind_joints")

##### CONTROLS #####################################################################
    def controls(self, ctrl_socket, spaces):
        ikctrl_grp = cmds.group(
                n = "L_leg_IKctrls_GRP", empty = True, parent = "global_sub_CTRL")
        pleg = ProxyLeg()
        fk = [self.upleg_jnt,self.knee_jnt, self.lowleg_jnt, self.foot_jnt, 
             self.toes_jnt, self.toes_end_jnt]
        fk_ro = "zyx"
        scl = util.distance(self.upleg_jnt, self.lowleg_jnt)/5
        
    # FK ctrls
        dist = util.distance(self.upleg_jnt, self.knee_jnt)
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
        ik_foot_sub = Nurbs.square(self.foot_sub_ik, scl*1.4, "sky", "zxy")
        # ik_align = Nurbs.box(self.foot_align, scl*1.6, scl/6, scl/6, "sky", "zxy")
        ik_pv = Nurbs.octahedron(self.polevector, scl/3, "blue")
        ik_hipj = Nurbs.square(self.hipjoint_ik, scl*2.5, "blue", "zxy")
        
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
            cmds.setAttr(f"{ro}.rotateOrder", channelBox = True)
        
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
            ik_foot_sub :  (self.foot_jnt,         ik_foot),
            # ik_align :  (self.foot_jnt,         ik_foot_sub),
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
            if ctrl in [ik_foot, ik_foot_sub, ik_hipj, switch,
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
    # add buffer to lowleg_FK_CTRL
        kbuff = util.buffer(fk_lowleg, new_suffix = "counterRot_GRP")
    # add buffer to ik_align and knee_bendy for ankle_align attr
        # align_buff = util.buffer(ik_align)
        knee_b_buff = util.buffer(knee_b)
        util.mtx_zero(knee_b_buff)

    # knee aim targets for bendy setup
        aim1 = cmds.group(n = "L_knee_bendy_kneeaim_GRP", em = True, parent = knee_b)
        aim2 = cmds.group(n = "L_knee_bendy_lowlegaim_GRP", em = True, parent = knee_b)
        cmds.matchTransform(aim1, self.knee_jnt, position = True)
        cmds.matchTransform(aim2, self.lowleg_jnt, position = True)
        util.mtx_zero([aim1, aim2])
        util.lock([aim1, aim2])
    # offset switch_ctrl to side of ankle
        cmds.move(dist/2, 0, 0, switch, relative = True)
        
####### Attributes
        util.attr_separator([fk_upleg, ik_foot, ik_hipj, ik_pv])
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
        cmds.addAttr(ik_foot, longName = "toe_heel_roll", attributeType = "double", 
                     defaultValue = 0)
        cmds.setAttr(f"{ik_foot}.toe_heel_roll", e = True, keyable = True)
        cmds.addAttr(ik_foot, longName = "in_out_roll", attributeType = "double", 
                     defaultValue = 0)
        cmds.setAttr(f"{ik_foot}.in_out_roll", e = True, keyable = True)
        util.attr_separator(ik_foot, 2)
        cmds.addAttr(ik_foot, longName = "upleg_length", attributeType = "double", 
                     min = 0, defaultValue = 1)
        cmds.setAttr(f"{ik_foot}.upleg_length", e = True, keyable = True)
        cmds.addAttr(ik_foot, longName = "lowleg_length", attributeType = "double", 
                     min = 0, defaultValue = 1)
        cmds.setAttr(f"{ik_foot}.lowleg_length", e = True, keyable = True)
        
    # foot roll ctrls
        roll_locs = [heel_loc, out_loc, in_loc, toepiv_loc, ball_loc, toes_loc]
        roll_ctrls = []
        for loc in roll_locs:
            offdist = util.distance(self.toes_jnt, self.toes_end_jnt)
            if loc == roll_locs[-2]: # ball
                roll_ctrl = Nurbs.halfcircle(
                    loc.replace("_LOC", "_CTRL"), scl, "blue", "xyz")
            elif loc == roll_locs[-1]: # toes
                roll_ctrl = Nurbs.halfcircle(
                    loc.replace("_LOC", "_CTRL"), scl, "blue", "xyz")
                Nurbs.flip_shape(roll_ctrl, "-y")
                cmds.move(0,0,offdist, roll_ctrl+".cv[0:5]", relative = True)
            else:
                roll_ctrl = Nurbs.sphere(
                        loc.replace("_LOC", "_CTRL"), scl/8, "blue", "xyz")
            roll_ctrls.append(roll_ctrl)
            cmds.matchTransform(roll_ctrl, loc, position = True)
        roll_ctrls_grp = cmds.group(n = "L_roll_ctrls_GRP", em = True)
        cmds.parent(roll_ctrls, roll_ctrls_grp)
        cmds.parent(roll_ctrls_grp, ik_foot_sub)
        util.mtx_zero(roll_ctrls_grp)
        util.mtx_zero(roll_locs_grp)
        
    #### MIRROR CTRLS TO THE RIGHT SIDE ####
        ikctrl_mirror_grp = cmds.group(
                n = "R_leg_IKctrls_mirror_GRP", em = True, parent = "global_sub_CTRL")
        cmds.setAttr(f"{ikctrl_mirror_grp}.sx", -1)
        fkctrl_mirror_grp = cmds.group(
                n = "R_leg_FKctrls_mirror_GRP", em = True, parent = ctrl_socket)
        cmds.setAttr(f"{fkctrl_mirror_grp}.sx", -1)
        rig.mirror_ctrls([fk_upleg, ik_hipj], fkctrl_mirror_grp)
        rig.mirror_ctrls([ik_foot, ik_pv, roll_locs_grp], ikctrl_mirror_grp)
        rig.mirror_ctrls([switch], ikctrl_mirror_grp)
        rig.mirror_ctrls([upleg_b, lowleg_b, knee_b_buff], ikctrl_mirror_grp)
    
    ### Spaces
        upleg_space = rig.spaces(spaces[:-1], fk_upleg, r_only = True)
        rig.spaces(spaces[:-1], fk_upleg.replace("L_", "R_"), r_only = True)
        rig.spaces(spaces, ik_foot)
        rig.spaces(spaces, ik_foot.replace("L_", "R_"), rside = True)
        rig.spaces(spaces, ik_pv)
        rig.spaces(spaces, ik_pv.replace("L_", "R_"), rside = True)
        rig.spaces(spaces[:-1], ik_hipj, r_only = True)
        rig.spaces(spaces[:-1], ik_hipj.replace("L_", "R_"), r_only = True)
    
    # polevector line connecting with knee
        for s in ["L_", "R_"]:
            pole_crv = Nurbs.lineconnect(
                    f"{s}legPole", [f"{s}knee_bendy_CTRL", f"{s}leg_polevector_IK_CTRL"],
                    proxy = False)
            cmds.parent(pole_crv, "other_ctrls_GRP")
        
    # selection sets
#### ik_align ctrl missing
        l_ctrls = [fk_upleg, fk_lowleg, fk_foot, fk_toes, 
                   ik_foot, ik_foot_sub, ik_pv, ik_hipj, 
                   upleg_b, knee_b, lowleg_b, switch]
        l_ctrls.extend(roll_ctrls)
        r_ctrls = [x.replace("L_", "R_") for x in l_ctrls]
        cmds.sets(l_ctrls, add = "L_leg")
        cmds.sets(r_ctrls, add = "R_leg")
        
    # cleanup
        l_ctrls.insert(1, fk_knee)
        l_ctrls.extend(roll_locs)
        
        util.mtx_zero(l_ctrls, rsidetoo = True)
        
        rig.fk_sclinvert([upleg_space[0], fk_knee, fk_foot, fk_toes], rsidetoo = True)
        # for R_upleg need to rewire because of mirror_GRP betw hip and upleg ctrls
        upleg_p = fkctrl_mirror_grp.replace("_GRP", "_scl_COMP")
        cmds.connectAttr(f"{ctrl_socket}.s", f"{upleg_p}.inputScale", f = True)
        
###### RIGGING ####################################################################
    def build_rig(self, joint_socket, ctrl_socket, spaces):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket, spaces)
        
    # create IK and FK joint chains
        L_jnts = [self.upleg_jnt, self.knee_jnt, self.lowleg_jnt, 
                  self.foot_jnt, self.toes_jnt, self.toes_end_jnt]
        L_switch = self.switch
        R_jnts = [x.replace("L_", "R_") for x in L_jnts]
        R_switch = self.switch.replace("L_", "R_")
        rig.ikfk_chains(L_jnts, L_switch, 1)
        rig.ikfk_chains(R_jnts, R_switch, 1)
        rig.ikfk_ctrlvis(self.L_ik_vis, self.L_fk_ctrls, self.L_bendies, L_switch)
        rig.ikfk_ctrlvis(self.R_ik_vis, self.R_fk_ctrls, self.R_bendies, R_switch)
        
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
            util.mtx_zero([f"{s}lowleg_FK_counterRot_GRP", f"{s}lowleg_FK_CTRL"])
            cmds.connectAttr(f"{k_mult}.output", f"{s}knee_FK_CTRL.rotateX")
            cmds.connectAttr(f"{k_negmult}.output", f"{s}lowleg_FK_counterRot_GRP.rotateX")
        # switcher & knee bendy follow deform skeleton
            util.mtx_hook(f"{s}lowleg_JNT", f"{s}leg_switcher_CTRL")
            util.mtx_hook(f"{s}knee_JNT", f"{s}knee_bendy_buffer_GRP")
        
    ### FK setup
        # upleg_jnt with constraints to make space switches work later
            cmds.pointConstraint(
                f"{s}upleg_FK_CTRL", f"{s}upleg_FK_JNT", mo = False, weight = 1)
            cmds.orientConstraint(
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
            rig.sub_ctrl_vis(f"{s}foot_IK_sub_CTRL")
            cmds.connectAttr(f"{s}leg_switcher_CTRL.ikfk",
                             f"{s}legPole_line_CRVShape.v")
            cmds.pointConstraint(
                f"{s}hipjoint_IK_CTRL", f"{s}upleg_IK_JNT", offset = (0,0,0), weight = 1)
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
            livelength = cmds.shadingNode(
                    "distanceBetween", n = f"{s}leg_stretchylength_DBTW", au = True)
            cmds.connectAttr(
                    f"{s}hipjoint_IK_CTRL.worldMatrix[0]", f"{livelength}.inMatrix1")
            cmds.connectAttr(
                    f"{s}foot_IK_sub_CTRL.worldMatrix[0]", f"{livelength}.inMatrix2")
        # src_length = upleg + lowleg + knee lengths
            uplength = util.distance(f"{s}upleg_JNT", f"{s}knee_JNT")
            lowlength = util.distance(f"{s}lowleg_JNT", f"{s}foot_JNT")
            kneelength = util.distance(f"{s}knee_JNT", f"{s}lowleg_JNT")
        # MD up/lowlength by attr from foot_IK_CTRL
            ikctrl_len = cmds.shadingNode(
                    "multiplyDivide", n = f"{s}leg_ikctrlattr_MULT", asUtility = True)
            cmds.setAttr(f"{ikctrl_len}.input1X", uplength)
            cmds.setAttr(f"{ikctrl_len}.input1Y", lowlength)
            cmds.setAttr(f"{ikctrl_len}.input1Z", kneelength)
            cmds.connectAttr(f"{s}foot_IK_CTRL.upleg_length", f"{ikctrl_len}.input2X")
            cmds.connectAttr(f"{s}foot_IK_CTRL.lowleg_length", f"{ikctrl_len}.input2Y")
        # ADD src_length = uplength + lowlength + kneelength!!
            src_length = cmds.shadingNode(
                    "plusMinusAverage", n = f"{s}leg_srclength_ADD", asUtility = True)
            cmds.connectAttr(f"{ikctrl_len}.outputX", f"{src_length}.input1D[0]")
            cmds.connectAttr(f"{ikctrl_len}.outputY", f"{src_length}.input1D[1]")
            cmds.connectAttr(f"{ikctrl_len}.outputZ", f"{src_length}.input1D[2]")
        # DIV livelength by global scale
            glob_inv = cmds.shadingNode(
                    "multiplyDivide", n = f"{s}leg_stretchyglobalScl_DIV", au = True)
            cmds.setAttr(f"{glob_inv}.operation", 2) # divide
            cmds.connectAttr(f"{livelength}.distance", f"{glob_inv}.input1Y")
            cmds.connectAttr("global_CTRL.scale", f"{glob_inv}.input2")
        # DIV normalize -> current length / source length
            norm = cmds.shadingNode(
                    "multiplyDivide", n = F"{s}leg_stretchy_NORM", asUtility = True)
            cmds.setAttr(f"{norm}.operation", 2) # divide
            cmds.connectAttr(f"{glob_inv}.outputY", f"{norm}.input1Y")
            cmds.connectAttr(f"{src_length}.output1D", f"{norm}.input2Y")
        # CONDITION -> prevent shrinking leg by setting a minimum scale Z = 1
            con = cmds.shadingNode(
                        "condition", n = f"{s}leg_stretchy_CON", asUtility = True)
            cmds.setAttr(f"{con}.operation", 5) # <= less or equal than
            cmds.connectAttr(f"{norm}.outputY", f"{con}.firstTerm") # stretch value
            cmds.setAttr(f"{con}.secondTerm", 1) # minimum
            cmds.setAttr(f"{con}.colorIfTrueR", 1) # output when bending limb
        # output when stretching limb {con}.outColorR
            cmds.connectAttr(f"{norm}.outputY", f"{con}.colorIfFalseR")
            
        # connect ctrl scale with globalScl
            for n, ik_jnt in enumerate([f"{s}upleg_IK_JNT", 
                                        f"{s}lowleg_IK_JNT", 
                                        f"{s}foot_IK_JNT"]):
                uniscl = cmds.shadingNode(
                        "multiplyDivide", n = ik_jnt.replace("_JNT", "_uniscale_MULT"), 
                        asUtility = True)
                stretchY = cmds.shadingNode(
                        "multiplyDivide", n = ik_jnt.replace("_JNT", "_stretchSy_MULT"), 
                        asUtility = True)
                cmds.connectAttr("global_CTRL.scale", f"{uniscl}.input1")
                if n == 0: # upleg
                    cmds.connectAttr(f"{s}foot_IK_CTRL.upleg_length",
                                     f"{uniscl}.input2Y")
                    cmds.connectAttr(f"{uniscl}.output", f"{stretchY}.input1")
                    cmds.connectAttr(f"{con}.outColorR", f"{stretchY}.input2Y")
                    cmds.connectAttr(f"{stretchY}.output", f"{ik_jnt}.scale")
### add thickness driver into uniscl.inputs 2X and 2Y
                if n == 1: # lowleg
                    cmds.connectAttr(f"{s}foot_IK_CTRL.lowleg_length",
                                     f"{uniscl}.input2Y")
                    cmds.connectAttr(f"{uniscl}.output", f"{stretchY}.input1")
                    cmds.connectAttr(f"{con}.outColorR", f"{stretchY}.input2Y")
                    cmds.connectAttr(f"{stretchY}.output", f"{ik_jnt}.scale")
### add thickness driver into uniscl.inputs 2X and 2Y
                if n == 2: # foot
                    cmds.connectAttr(f"{s}foot_IK_CTRL.scale",
                                     f"{uniscl}.input2")
                    cmds.connectAttr(f"{uniscl}.output", f"{ik_jnt}.scale")
                    cmds.connectAttr(f"{uniscl}.output", f"{s}toes_IK_JNT.scale")
        # IK knee sx & sz = average betw upleg & lowleg scales
        # IK knee sy = globalScl
            avg = cmds.shadingNode("plusMinusAverage", n = f"{s}knee_IK_scale_AVG", 
                        asUtility = True)
            cmds.setAttr(f"{avg}.operation", 3) # average
            cmds.connectAttr(f"{s}upleg_IK_JNT.scale", f"{avg}.input3D[0]")
            cmds.connectAttr(f"{s}lowleg_IK_JNT.scale", f"{avg}.input3D[1]")
            cmds.connectAttr(f"{avg}.output3D", f"{s}knee_IK_JNT.s")
        
        # add knee_bendy_jnt
        for s in ["L_", "R_"]:
            knee_b_jnt = cmds.duplicate(
                    f"{s}knee_JNT", n = f"{s}knee_bendy_JNT", parentOnly = True)[0]
            rad = cmds.getAttr(f"{knee_b_jnt}.radius")
            cmds.setAttr(f"{knee_b_jnt}.radius", rad * 1.5)
            cmds.parent(knee_b_jnt, f"{s}knee_JNT")
            snap = cmds.pointConstraint(
                    [f"{s}knee_JNT", f"{s}lowleg_JNT"], knee_b_jnt, 
                    mo = False, weight = 1)
            cmds.delete(snap)
            cmds.parentConstraint(
                    f"{s}knee_bendy_CTRL", knee_b_jnt, mo = True, weight = 1)
            cmds.scaleConstraint(
                    f"{s}knee_bendy_CTRL", knee_b_jnt, mo = True, weight = 1)
            cmds.sets(knee_b_jnt, add = "bind_joints")
            cmds.sets(knee_b_jnt, add = "joints")
        # & knee_pin target
            knee_pin_grp = cmds.group(
                    n = f"{s}knee_pin_target_GRP", em = True, parent = "misc_GRP")
            snap2 = cmds.pointConstraint(
                    [f"{s}knee_JNT", f"{s}lowleg_JNT"], knee_pin_grp, 
                    mo = False, weight = 1)
            cmds.delete(snap2)
            util.mtx_hook(f"{s}knee_IK_JNT", knee_pin_grp)
            
    # ankle align
        for s in ["L_", "R_"]:
            # rig.spaceblend(
            #         f"{s}foot_IK_sub_CTRL", f"{s}lowleg_IK_JNT", 
            #         f"{s}foot_align_IK_buffer_GRP",
            #         f"{s}foot_IK_CTRL", "ankle_align", r_only = True)
            # shapes = cmds.listRelatives(
            #         f"{s}foot_align_IK_CTRL", children = True, shapes = True)
            # for sh in shapes:
            #     cmds.connectAttr(f"{s}foot_IK_CTRL.ankle_align", sh+".v")
    # knee pin
            rig.spaceblend(
                    f"{s}knee_pin_target_GRP", f"{s}leg_polevector_IK_CTRL", 
                    f"{s}knee_bendy_buffer_GRP",
                    f"{s}leg_polevector_IK_CTRL", "pin_knee", t_only = True)
    
###### missing:
    # thickness ctrl (with falloffs?
    
    ### Bendies
        for s in ["L_", "R_"]:
            upax = "x" if s == "L_" else "-x"
            bendy.setup(
                mod_name = f"{s}upleg", 
                base_driver = f"{s}upleg_JNT", 
                head_driver = f"{s}knee_JNT",
                forwardaxis = "y", 
                upaxis = upax,
                mid_ctrl = f"{s}upleg_bendy_CTRL", 
                twistInvDriver = "hip_JNT",
                elbow_bendy_ctrl = f"{s}knee_bendy_CTRL")
            bendy.setup(
                mod_name = f"{s}lowleg", 
                base_driver = f"{s}lowleg_JNT", 
                head_driver = f"{s}foot_JNT",
                forwardaxis = "y", 
                upaxis = upax,
                mid_ctrl = f"{s}lowleg_bendy_CTRL",
                elbow_bendy_ctrl = f"{s}knee_bendy_CTRL")
        # to avoid unnatural lowleg twisting
            cmds.delete(f"{s}lowleg_twist_driverMtx_MM")
            util.mtx_hook(f"{s}lowleg_JNT", f"{s}lowleg_endTwist_LOC", force = True)
        # upleg & lowleg bendy ctrls both aim to knee_bendy and squetch
        # added aim targets matching knee & lowleg jnt pivots under knee_bendy_ctrl
            bendy.aim(
                bendy = f"{s}upleg_bendy_CTRL",
                aimtarget = f"{s}knee_bendy_kneeaim_GRP", 
                uptarget = f"{s}upleg_baseTwist_LOC",
                root = f"{s}upleg_JNT",
                vaim = (0,1,0),
                vup = (1,0,0))
            bendy.aim(
                bendy = f"{s}lowleg_bendy_CTRL",
                aimtarget = f"{s}knee_bendy_lowlegaim_GRP", 
                uptarget = f"{s}lowleg_endTwist_LOC",
                root = f"{s}foot_JNT",
                vaim = (0,-1,0),
                vup = (1,0,0),
                scldriver = f"{s}lowleg_JNT")
            
    ### Shoe Offset Setup
        cmds.addAttr(
            "BODY_TUNING", longName = "shoes_heel_offset",
            niceName = "Shoes Heel Offset", attributeType = "double", 
            min = 0, defaultValue = 0)
        cmds.setAttr("BODY_TUNING.shoes_heel_offset", e = True, channelBox = True)
        cmds.addAttr(
            "BODY_TUNING", longName = "shoes_sole_offset",
            niceName = "Shoes Sole Offset", attributeType = "double", 
            min = 0, defaultValue = 0)
        cmds.setAttr("BODY_TUNING.shoes_sole_offset", e = True, channelBox = True)
        cmds.addAttr(
            "BODY_TUNING", longName = "shoes_toes_offset",
            niceName = "Shoes Toes Offset", attributeType = "double", defaultValue = 0)
        cmds.setAttr("BODY_TUNING.shoes_toes_offset", e = True, channelBox = True)
    # FK - heel & toes offset
        for s in ["L_", "R_"]:
            pmas = []
            for n in ["heelOffset_foot", "heelOffset_toes", "toesOffset"]:
                pma = cmds.shadingNode(
                        "plusMinusAverage", n = f"{s}{n}_PMA", asUtility = True)
                pmas.append(pma)
        # fk foot_jnt.r = foot_ctrl.r + heel off
            cmds.connectAttr(f"{s}foot_FK_CTRL.r", f"{pmas[0]}.input3D[0]")
            cmds.connectAttr("BODY_TUNING.shoes_heel_offset", 
                             f"{pmas[0]}.input3D[1].input3Dx")
            cmds.connectAttr(f"{pmas[0]}.output3D", f"{s}foot_FK_JNT.r", force = True)
        # fk toes_jnt.r = toes_ctrl.r - heel off + toe off
            cmds.setAttr(f"{pmas[1]}.operation", 2) # subtract
            cmds.connectAttr(f"{s}toes_FK_CTRL.r", f"{pmas[1]}.input3D[0]")
            cmds.connectAttr("BODY_TUNING.shoes_heel_offset", 
                             f"{pmas[1]}.input3D[1].input3Dx")
            cmds.connectAttr(f"{pmas[1]}.output3D", f"{pmas[2]}.input3D[0]")
            cmds.connectAttr("BODY_TUNING.shoes_toes_offset", 
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
        cmds.connectAttr("BODY_TUNING.shoes_heel_offset", f"{ankle}.rx")
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
            util.mtx_hook(f"{s}foot_IK_sub_CTRL", f"{s}roll_locs_GRP")
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
        # in_out_roll = ctrl.r + attr.rz (in -> positive, out -> negative)
            io_clamp = cmds.shadingNode("clamp", n = s+"inoutroll_CLAMP", au = True)
            # in -> R, out -> G
            cmds.setAttr(io_clamp+".maxR", 180)
            cmds.setAttr(io_clamp+".minG", -180)
            cmds.connectAttr(s+"foot_IK_CTRL.in_out_roll", io_clamp+".inputR")
            cmds.connectAttr(s+"foot_IK_CTRL.in_out_roll", io_clamp+".inputG")
            # ADD output R + inroll.rz
            in_add = cmds.shadingNode(
                    "plusMinusAverage", n = s+"inroll_ADD", au = True)
            cmds.connectAttr(io_clamp+".outputR", in_add+".input3D[0].input3Dz")
            cmds.connectAttr(s+"inroll_IK_CTRL.r", in_add+".input3D[1]")
            cmds.connectAttr(in_add+".output3D", s+"inroll_IK_LOC.r")
            # ADD output G + outroll.rz
            out_add = cmds.shadingNode(
                    "plusMinusAverage", n = s+"outroll_ADD", au = True)
            cmds.connectAttr(io_clamp+".outputG", out_add+".input3D[0].input3Dz")
            cmds.connectAttr(s+"outroll_IK_CTRL.r", out_add+".input3D[1]")
            cmds.connectAttr(out_add+".output3D", s+"outroll_IK_LOC.r")
        # toe_heel_roll = ctrl.r + attr.rx (toe -> pos, heel -> neg)
            th_clamp = cmds.shadingNode("clamp", n = s+"toeheelroll_CLAMP", au = True)
            # toe -> R, heel -> G
            cmds.setAttr(th_clamp+".maxR", 180)
            cmds.setAttr(th_clamp+".minG", -180)
            cmds.connectAttr(s+"foot_IK_CTRL.toe_heel_roll", th_clamp+".inputR")
            cmds.connectAttr(s+"foot_IK_CTRL.toe_heel_roll", th_clamp+".inputG")
            # ADD output R + toeroll.rx
            toe_add = cmds.shadingNode(
                    "plusMinusAverage", n = s+"toeroll_ADD", au = True)
            cmds.connectAttr(th_clamp+".outputR", toe_add+".input3D[0].input3Dx")
            cmds.connectAttr(s+"toeroll_IK_CTRL.r", toe_add+".input3D[1]")
            cmds.connectAttr(toe_add+".output3D", s+"toeroll_IK_LOC.r")
            # ADD output G + heelroll.rx
            heel_add = cmds.shadingNode(
                    "plusMinusAverage", n = s+"heelroll_ADD", au = True)
            cmds.connectAttr(th_clamp+".outputG", heel_add+".input3D[0].input3Dx")
            cmds.connectAttr(s+"heelroll_IK_CTRL.r", heel_add+".input3D[1]")
            cmds.connectAttr(heel_add+".output3D", s+"heelroll_IK_LOC.r")
        
    ### clean up attributes - lock & hide
        util.lock(self.switch, rsidetoo = True)
        util.lock(self.lowleg_fk, ["tx","ty","tz","ry","rz"], rsidetoo = True)
        util.lock([self.knee_fk, self.foot_fk, self.toes_fk], 
                  ["tx","ty","tz"], rsidetoo = True)
        util.lock([self.inpiv, self.outpiv, self.heelpiv, self.toepiv, self.ball, 
                  self.toes], ["sx","sy","sz"], rsidetoo = True)
        util.lock(self.polevector, ["rx","ry","rz","sx","sy","sz"], rsidetoo = True)
        util.lock(self.hipjoint_ik, ["sx","sz"], rsidetoo = True)
        # util.lock(self.foot_align, ["tx","ty","tz","sx","sy","sz"], rsidetoo = True)
        
    # hide IK & FK joint chains
        for s in ["L_", "R_"]:
            cmds.hide(f"{s}upleg_FK_JNT", f"{s}upleg_IK_JNT")
        

if __name__ == "__main__":
    
    test2 = Module()
        
    pass