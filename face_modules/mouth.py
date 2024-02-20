import maya.cmds as cmds

from face_proxies.proxymouth import ProxyMouth

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig

class Mouth(object):
    
    def __init__(self):
### attachment point for teeth in jawrig? __init__ attribute
        self.module_name = "mouth"
        
        
        self.jaw_jnt = "jaw_JNT"
        self.mouth_jnt = "mouth_pivot_JNT"
        self.chin_jnt = "chin_JNT"
        
        self.L_corner_jnt = "L_lipcorner_main_JNT"
        self.R_corner_jnt = "R_lipcorner_main_JNT"
        
        self.invjaw = "jaw_inverse_CTRL"
        self.jaw = "jaw_aim_CTRL"
        self.jawnorm = "jaw_FK_CTRL"
        self.mouth = "mouth_CTRL"
        self.mdrive = "mouth_driver_GRP"
        self.mdrive_buff = "mouth_driver_buffer_GRP"
        
        self.corner = "L_lipcorner_CTRL"
        self.corner_buff = "L_lipcorner_buffer_GRP"
        self.corner_off = "L_lipcorner_offset_CTRL"
        
        self.uplip = "uplip_CTRL"
        self.lowlip = "lowlip_CTRL"
        self.uplip_buff = "uplip_buffer_GRP"
        self.lowlip_buff = "lowlip_buffer_GRP"
        
        self.upcenter = "uplip_center_CTRL"
        self.upsneer = "L_uplip_sneer_CTRL"
        self.upout = "L_uplip_out_CTRL"
        self.uppinch = "L_uplip_pinch_CTRL"
        
        self.lowcenter = "lowlip_center_CTRL"
        self.lowsneer = "L_lowlip_sneer_CTRL"
        self.lowout = "L_lowlip_out_CTRL"
        self.lowpinch = "L_lowlip_pinch_CTRL"
    
    def jawjoints(self, joint_socket):
        pmouth = ProxyMouth()
        rad = cmds.getAttr(joint_socket+".radius")/3
        jaw_jnts = rig.make_joints(
                proxies_list = pmouth.proxies[:3], # skip jaw ctrls
                rot_order = "xyz", 
                radius = rad,
                set = "fjoints")
        cmds.parent(self.mouth_jnt, self.jaw_jnt, noInvScale = True)
        cmds.parent(jaw_jnts[0], joint_socket, noInvScale = True)
        cmds.disconnectAttr(self.jaw_jnt+".s", self.chin_jnt+".inverseScale")
        cmds.sets(jaw_jnts[0], add = "fbind_joints") # just jaw
        cmds.sets(jaw_jnts, add = "fjoints")
        return jaw_jnts
        
    def lipjoints(self):
        L_corner = "L_lipcorner_loop_LOC"
        R_corner = "R_lipcorner_loop_LOC"
        up_loops = cmds.ls("uplip_*_loop_LOC")
        low_loops = cmds.ls("lowlip_*_loop_LOC")
        all_locs = [L_corner]
        all_locs.extend(up_loops)
        all_locs.append(R_corner)
        all_locs.extend(low_loops)
        uplip_jnts = []
        lowlip_jnts = []
        corner_jnts = []
        rad = cmds.getAttr(self.jaw_jnt+".radius")
        for loc in all_locs:
            cmds.select(clear = True)
            pos = cmds.xform(loc, q = True, t = True, ws = True)
            name = loc.replace("loop_LOC", "JNT")
            jnt = cmds.joint(
                n = name, 
                p = pos, rad = rad/3)
            cmds.parent(jnt, self.mouth_jnt, noInvScale = True)
            if "uplip" in jnt:
                uplip_jnts.append(jnt)
            elif "lowlip" in jnt:
                lowlip_jnts.append(jnt)
            elif "corner" in jnt:
                corner_jnts.append(jnt)
### noInvScale = True ???
        corner_jnts.reverse()
### 2 main lipcorner joints
        for loc in [L_corner, R_corner]:
            cmds.select(clear = True)
            pos = cmds.xform(loc, q = True, t = True, ws = True)
            name = loc.replace("loop_LOC", "main_JNT")
            jnt = cmds.joint(
                n = name, 
                p = pos, rad = rad/1.5)
            cmds.parent(jnt, self.mouth_jnt, noInvScale = True)
    # set
        set_jnts = uplip_jnts.copy()
        set_jnts.extend(lowlip_jnts)
        set_jnts.extend(corner_jnts)
        cmds.sets(set_jnts, add = "fbind_joints")
        cmds.sets(set_jnts, add = "fjoints")
        return [uplip_jnts, lowlip_jnts, corner_jnts]
    
##### CONTROLS #####################################################################
    def controls(self, ctrl_socket):
        # Setup
        pmouth = ProxyMouth()
        ctrl_grp = cmds.group(n = "mouth_ctrls_GRP", em = True, p = ctrl_socket)
    ### ctrl shapes
        cdist = cmds.getAttr(self.chin_jnt+".tz")/20
        # jaw
        invjaw = cmds.group(n = self.invjaw, em = True)
        jaw = Nurbs.sphere(self.jaw, cdist, "yellow")
        jawnorm = Nurbs.sphere(self.jawnorm, cdist*1.5, "yellow", "zyx")
        mouth = Nurbs.sphere(self.mouth, cdist/3, "yellow")
        mdrive = cmds.group(n = self.mdrive, em = True)
        # main lip
        lipc = Nurbs.cube(self.corner, cdist*2, "green")
        lipc_off = Nurbs.triangle(self.corner_off, cdist/2, cdist/2, "grass")
        # uplip
        uplip = Nurbs.box(self.uplip, cdist*4, cdist*0.8, cdist/10, "red")
        upc = Nurbs.triangle(self.upcenter, cdist/1.5, cdist/1.5, "pink")
        ups = Nurbs.triangle(self.upsneer, cdist, cdist, "red")
        upo = Nurbs.triangle(self.upout, cdist, cdist, "pink")
        upp = Nurbs.triangle(self.uppinch, cdist/2, cdist/2, "pink")
        # lowlip
        lowlip = Nurbs.box(self.lowlip, cdist*4, cdist*0.8, cdist/10, "blue")
        lowc = Nurbs.triangle(self.lowcenter, cdist/1.5, cdist/1.5, "sky")
        lows = Nurbs.triangle(self.lowsneer, cdist, cdist, "blue")
        lowo = Nurbs.triangle(self.lowout, cdist, cdist, "sky")
        lowp = Nurbs.triangle(self.lowpinch, cdist/2, cdist/2, "sky")
        
        # offset shapes a bit forward
        triangles = [upc, ups, upo, upp, lowc, lows, lowo, lowp, lipc_off]
        boxes = [uplip, lowlip, lipc]
        for c in triangles:
            cmds.move(0, 0, cdist*2, c+".cv[0:3]", r = True, localSpace = True)
        for b in boxes:
            if b == uplip:
                y = cdist*1.3
            elif b == lipc:
                y = 0
            else:
                y = cdist*-1.3
            cmds.move(0, y, cdist*1.2, b+".cv[0:15]", 
                      r = True, localSpace = True)
            
        mirr_grp = [ups, upo, upp, lipc, lows, lowo, lowp]
    # see through geo like xRay
        for xray in [jawnorm]:
            shapes = cmds.listRelatives(xray, children = True, shapes = True)
            for s in shapes:
                cmds.setAttr(f"{s}.alwaysDrawOnTop", 1)
        
    # position & parent
        relations = {
            invjaw :    (pmouth.jawctrl,    ctrl_grp),
            jaw :       (pmouth.jawctrl,    ctrl_grp),
            jawnorm :   (pmouth.jaw,        ctrl_grp),
            mdrive :    (pmouth.mpivot,    ctrl_grp),
            mouth :     (pmouth.mouthctrl,  ctrl_grp),
            uplip :     (pmouth.upcenter,   mdrive),
            upc :       (pmouth.upcenter,   uplip),
            ups :       (pmouth.upsneer,    mdrive),
            upo :       (pmouth.upout,      mdrive),
            upp :       (pmouth.uppinch,    mdrive),
            lowlip :    (pmouth.lowcenter,  mdrive),
            lowc :      (pmouth.lowcenter,  lowlip),
            lows :      (pmouth.lowsneer,   mdrive),
            lowo :      (pmouth.lowout,     mdrive),
            lowp :      (pmouth.lowpinch,   mdrive),
            lipc :      (pmouth.corner,     mdrive),
            lipc_off :  (pmouth.corner,     lipc)}
        
        for ctrl in list(relations):
            cmds.matchTransform(ctrl, relations[ctrl][0], pos = True, rot = True)
            cmds.parent(ctrl, relations[ctrl][1])
        
        # aim buffer for normal jaw
        jawbuff = util.buffer(jawnorm, "aim_GRP")
        cmds.setAttr(jawbuff+".rotateOrder", 5) # "zyx"
        # buffers for main lip drivers:
        lipc_buff = util.buffer(lipc)
        uplip_buff = util.buffer(uplip)
        lowlip_buff = util.buffer(lowlip)
        mdrive_buff = util.buffer(mdrive)
        cmds.parent(mouth, mdrive_buff)
        
####### Attributes
        # Z pre separator
        for zctrl in [lipc]:
            cmds.addAttr(zctrl, longName = "Z", attributeType = "double")
            cmds.setAttr(f"{zctrl}.Z", e = True, keyable = True)
        util.attr_separator([uplip, lowlip, mouth, lipc, jaw])
        attr_dict = {
            uplip : ["roll", "squetch"],
            lowlip : ["roll", "squetch"],
            lipc : ["zip", "zip_falloff"],
            mouth : ["seal"]}
        for ctrl in attr_dict.keys():
            for attr in attr_dict[ctrl]:
                cmds.addAttr(ctrl, longName = attr, attributeType = "double")
                cmds.setAttr(f"{ctrl}.{attr}", e = True, keyable = True)
        # FACE TUNING
        util.attr_separator("FACE_TUNING")
        for faceattr in ["jaw_aim_factor", "jaw_z_follow", "jaw_y_follow"]:
            cmds.addAttr(
                "FACE_TUNING", longName = faceattr, attributeType = "double")
            cmds.setAttr(f"FACE_TUNING.{faceattr}", e = True, keyable = True)
        
    ### R_ctrls & Mirroring
        lipctrl_mirror_grp = cmds.group(
                n = "R_lip_ctrls_mirror_GRP", empty = True, parent = mdrive)
        cmds.setAttr(f"{lipctrl_mirror_grp}.sx", -1)
        rig.mirror_ctrls([ups, upo, upp, lipc_buff, lows, lowo, lowp], 
                         lipctrl_mirror_grp, colors = False)
    
    # selection sets
        set_grp = [jaw, jawnorm, mouth, 
                   uplip, lowlip,
                   upc, ups, upo, upp,
                   lowc, lows, lowo, lowp]
        for ctrl in set_grp:
            if ctrl.startswith("L_"):
                set_grp.append(ctrl.replace("L_", "R_"))
        cmds.sets(set_grp, add = "mouth")
        
    # cleanup
        zero_grp = [invjaw, jaw, jawbuff, jawnorm, mdrive_buff, mdrive, mouth, 
                    uplip, upc, ups, upo, upp, 
                    lipc, lipc_off, 
                    lowlip, lowc, lows, lowo, lowp,
                    lipc_buff, uplip_buff, lowlip_buff]
        for z in zero_grp:
            if z.startswith("L_"):
                zero_grp.append(z.replace("L_", "R_"))
        util.mtx_zero(zero_grp)

###### RIGGING ####################################################################
    def build_rig(self, joint_socket, ctrl_socket):
        jaw_jnts = self.jawjoints(joint_socket)
        lip_jnts = self.lipjoints()
        self.controls(ctrl_socket)
        self.jawrig()
        self.lipstojaw()
    # lips setup
        mouth_grp = cmds.group(n = "mouth_GRP", em = True, p = "fmisc_GRP")
        crv_grp = cmds.group(n = "lipcurves_GRP", em = True, p = mouth_grp)
        up_pose_locs = cmds.group(
                n = "uplip_poselocators_GRP", em = True, p = mouth_grp)
        low_pose_locs = cmds.group(
                n = "lowlip_poselocators_GRP", em = True, p = mouth_grp)
    # up lip curves
        up_crv_jnts = lip_jnts[0].copy() # right to left joints
        up_crv_jnts.insert(0, lip_jnts[-1][0]) # R_corner
        up_crv_jnts.append(lip_jnts[-1][1]) # L_corner
        uplip = self.locatorcurve(
                up_crv_jnts, "uplip_locators_CRV", corners = True)
        cmds.parent(uplip[0], crv_grp) # curve
        cmds.parent(uplip[1], up_pose_locs) # locators !! WITH CORNERS !!
        up_curves = self.rebuildcrvlayers(uplip[0], crv_grp)
    # low lip curves
        low_crv_jnts = lip_jnts[1].copy() # right to left joints
        low_crv_jnts.insert(0, lip_jnts[-1][0]) # R_corner
        low_crv_jnts.append(lip_jnts[-1][1]) # L_corner
        lowlip = self.locatorcurve(
                low_crv_jnts, "lowlip_locators_CRV", corners = False)
        cmds.parent(lowlip[0], crv_grp) # curve
        cmds.parent(lowlip[1], low_pose_locs) # locators
        low_curves = self.rebuildcrvlayers(lowlip[0], crv_grp)
        self.lipjointattach(up_crv_jnts, uplip[1])
        self.lipjointattach(low_crv_jnts[1:-1], lowlip[1]) # without corner joints!
        
        # attach corner_main_jnts
        for s in ["L_", "R_"]:
            pc = cmds.parentConstraint(
                    f"{s}lipcorner_CTRL", f"{s}lipcorner_main_JNT", mo = True, w = 1)[0]
            cmds.setAttr(pc+".interpType", 2)
        self.curvedrivers("uplip")
        self.curvedrivers("lowlip")
        self.orientjoints(up_crv_jnts[1:-1])
        self.orientjoints(low_crv_jnts[1:-1])
        # corner joints orient
        for s in ["L_", "R_"]:
            ori = cmds.orientConstraint(f"{s}lipcorner_CTRL", f"{s}lipcorner_JNT", 
                                        mo = True, w = 1, n = f"{s}lipcorner_ORI")
        
        
        
### extra joint curves for up & lowlip = seal blend targets
    # seal curve
        seal = self.seal(up_curves[2], low_curves[2]) # both highres curves
        cmds.parent(seal[0], crv_grp)

        
        self.macro_out(ctrl_socket)
    # cleanup
        cmds.hide([crv_grp, up_pose_locs, low_pose_locs])
        # Z attrs
        z_grp = [self.corner, self.corner.replace("L_", "R_")]
        for z in z_grp:
            mult = cmds.shadingNode(
                    "multDoubleLinear", n = z.replace("CTRL", "zattr_MULT"), au = True)
            cmds.setAttr(mult+".input2", 0.1)
            cmds.connectAttr(z+".Z", mult+".input1")
            cmds.connectAttr(mult+".output", z+".tz")
            util.lock(z, ["tz"])

        util.lock(self.jaw, ["rx","ry","sx","sy","sz"]) # with scales??
        util.lock(self.mouth, ["rx","ry","sz"])
        util.lock([self.uplip, self.lowlip], ["rx","sx","sy","sz"])
        util.lock([self.corner, self.corner.replace("L_", "R_")], 
                  ["rx","ry","rz","sx","sy","sz"])
        lip_shapers = []
        for s in ["L_", "R_"]:
            for part in ["uplip", "lowlip"]:
                lip_shapers.extend([f"{s}{part}_sneer_CTRL", f"{s}{part}_out_CTRL", f"{s}{part}_pinch_CTRL"])
            lip_shapers.append(f"{s}lipcorner_offset_CTRL")
        util.lock(lip_shapers, ["rx","sx","sy","sz"])
        util.lock(["uplip_center_CTRL", "lowlip_center_CTRL"], ["rx","sy","sz"])
        cmds.setAttr(self.mouth_jnt+".drawStyle", 2) # None
            
    def jawrig(self):
    # default jaw tuning values based on dist betw jaw and chin
        aim_factor = "FACE_TUNING.jaw_aim_factor"
        tz_factor = "FACE_TUNING.jaw_z_follow"
        ty_factor = "FACE_TUNING.jaw_y_follow"
        dist = util.distance(self.jaw_jnt, self.chin_jnt)
        cmds.setAttr(tz_factor, dist/4)
        cmds.setAttr(aim_factor, dist/1.6)
    # jaw aim & joint connection
        jaw_aim = cmds.listRelatives(self.jawnorm, parent = True)[0]
        cmds.parentConstraint(self.jawnorm, self.jaw_jnt, mo = True, w = 1)
        cmds.scaleConstraint(self.jawnorm, self.jaw_jnt, offset = (1,1,1), w = 1)
    # aim without constraint - jaw -> jaw_aim - only x & y
        # invert ty from ctrl to rx
        yinv = cmds.shadingNode(
                "multDoubleLinear", n = "invert_jawctrl_ty_MULT", au = True)
        cmds.connectAttr(self.jaw+".ty", yinv+".input1")
        cmds.setAttr(yinv+".input2", -1)
        aim_mult = cmds.shadingNode("multiplyDivide", n = "jaw_aim_MULT", au = True)
        cmds.connectAttr(aim_factor, aim_mult+".input2X")
        cmds.connectAttr(aim_factor, aim_mult+".input2Y")
        cmds.connectAttr(yinv+".output", aim_mult+".input1X")
        cmds.connectAttr(self.jaw+".tx", aim_mult+".input1Y")
        cmds.connectAttr(aim_mult+".outputX", jaw_aim+".rx")
        cmds.connectAttr(aim_mult+".outputY", jaw_aim+".ry")
    # jaw rz
        cmds.connectAttr(self.jaw+".rz", jaw_aim+".rz")
    # MACRO: jaw rx drive tz * tuning
        # jaw rx = jaw_aim.rx + jawnorm.rx
        rx_add = cmds.shadingNode("plusMinusAverage", n = "jaw_rxtotz_ADD", au = True)
        cmds.connectAttr(jaw_aim+".rx", rx_add+".input1D[0]")
        cmds.connectAttr(self.jawnorm+".rx", rx_add+".input1D[1]")
        rx_attr = rx_add+".output1D"
        # remap rotation into forward range
        z_rmv = util.remap("jaw_tz_follow_RMV", rx_attr, 
                           min = 0, max = 60, outmin = 0, outmax = 0)
        cmds.connectAttr(tz_factor, z_rmv+".outputMax")
        y_rmv = util.remap("jaw_ty_follow_RMV", rx_attr, 
                           min = 0, max = 60, outmin = 0, outmax = 0)
        cmds.connectAttr(ty_factor, y_rmv+".outputMax")
        cmds.connectAttr(y_rmv+".outValue", jaw_aim+".ty")
    # MACRO: jaw z/y follow + ctrl tz
        jaw_add = cmds.shadingNode("plusMinusAverage", n = "jaw_tz_ADD", au = True)
        cmds.connectAttr(self.jaw+".tz", jaw_add+".input1D[0]")
        cmds.connectAttr(z_rmv+".outValue", jaw_add+".input1D[1]")
        cmds.connectAttr(jaw_add+".output1D", jaw_aim+".tz")
    # sub ctrl
        rig.sub_ctrl_vis(self.jawnorm, self.jaw)
        
    # mouth follow 50%
        mouth_pc = cmds.parentConstraint(
                [self.invjaw, self.jawnorm], self.mdrive_buff, mo = True,
                w = 1, n = self.mdrive.replace("GRP", "jaw_PC"))[0]
        cmds.parentConstraint(self.mdrive, self.mouth_jnt, mo = True, w = 1)
        cmds.scaleConstraint(self.mdrive, self.mouth_jnt, offset = (1,1,1), w = 1)
### just simply connect all transforms??
    # connect mouth ctrls channels
        channels = {"ty":"ty", "tz":"tz", "rz":"rz", "s":"s"}
        for driver in channels.keys():
            attr = channels[driver]
            cmds.connectAttr(self.mouth+"."+driver, self.mdrive+"."+attr)
        # tx to ry unitconv
        unit = cmds.shadingNode("unitConversion", n = "mouth_tx_ty_UNIT", au = True)
        cmds.setAttr(unit+".conversionFactor", 0.2)
        cmds.connectAttr(self.mouth+".tx", unit+".input")
        cmds.connectAttr(unit+".output", self.mdrive+".ry")
        
        
### attachment point for teeth in jawrig? __init__ attribute

    def lipstojaw(self):
    # 4 empty transforms under self.mdrive_BUFF! to be driven by jaws
        maindrivers = []
        maindriven = [self.uplip_buff, self.lowlip_buff, self.corner_buff, 
                     self.corner_buff.replace("L_", "R_")]
        for main in maindriven:
            jawdriv = cmds.group(n = main.replace("buffer_GRP", "jawfollow_driver_GRP"), 
                                 em = True, p = self.mdrive_buff)
            cmds.matchTransform(jawdriv, main, pos = True, rot = True, scl = True)
            util.mtx_zero(jawdriv)
            maindrivers.append(jawdriv)
    # drive transform channels on main_buffers as a layer on top of mouth ctrl 
        for index, driver in enumerate(maindrivers):
            driven = maindriven[index]
            util.connect_transforms(driver, driven)
        for corner in [maindrivers[-2], maindrivers[-1]]:
            cpc = cmds.parentConstraint(
                    [self.invjaw, self.jawnorm], corner, mo = True,
                    w = 0.5, n = corner.replace("GRP", "jaw_PC"))[0]
            cmds.setAttr(cpc+".interpType", 2) # shortest
        uplip_pc = cmds.parentConstraint(
                [self.invjaw, self.jawnorm], maindrivers[0], mo = True,
                w = 1, n = maindrivers[0].replace("GRP", "jaw_PC"))[0]
        lowlip_pc = cmds.parentConstraint(
                [self.invjaw, self.jawnorm], maindrivers[1], mo = True,
                w = 1, n = maindrivers[1].replace("GRP", "jaw_PC"))[0]
        cmds.setAttr(f"{uplip_pc}.{self.invjaw}W0", 0.96)
        cmds.setAttr(f"{uplip_pc}.{self.jawnorm}W1", 0.04)
        cmds.setAttr(f"{lowlip_pc}.{self.invjaw}W0", 0.04)
        cmds.setAttr(f"{lowlip_pc}.{self.jawnorm}W1", 0.96)
        cmds.setAttr(uplip_pc+".interpType", 2) # shortest
        cmds.setAttr(lowlip_pc+".interpType", 2) # shortest
    # jaw rx driver ADD
        add = cmds.shadingNode("addDoubleLinear", n = "jaw_rx_squash_ADD", au = True)
        jawaim = cmds.listRelatives(self.jawnorm, parent = True)[0]
        cmds.connectAttr(self.jawnorm+".rx", add+".input1")
        cmds.connectAttr(jawaim+".rx", add+".input2")
    ### MACRO corners ### 
        # lipcorners go in with jaw opening (default based on mouth width)
        mwidth = util.distance(self.corner, self.corner.replace("L_", "R_"))
    # 2 tuning attrs for tz & tx
        for faceattr in ["mouthcorners_tz", "mouthcorners_tx"]:
            cmds.addAttr(
                "FACE_TUNING", longName = faceattr, attributeType = "double", min = 0)
            cmds.setAttr(f"FACE_TUNING.{faceattr}", e = True, keyable = True)
        cmds.setAttr("FACE_TUNING.mouthcorners_tx", mwidth / 5) # default
    # new macro buffer for lipcorner ctrls
        for corner in [self.corner, self.corner.replace("L_", "R_")]:
            # buffer
            macro = util.buffer(corner, "MACRO_mouthopen_GRP")
            # remap with tuner driving maxOut & minOut per axis
            for tuner in ["FACE_TUNING.mouthcorners_tz", "FACE_TUNING.mouthcorners_tx"]:
                name = macro.replace("GRP", "")
                axis = tuner.split("_")[-1]
                inv = cmds.shadingNode("multDoubleLinear", n = f"{name}{axis}_MULT", au = True)
                cmds.connectAttr(tuner, inv+".input1")
                cmds.setAttr(inv+".input2", -1)
                rmv = util.remap(
                        f"{name}{axis}_RMV", add+".output", -60, 60, 0, 0)
                cmds.connectAttr(tuner, rmv+".outputMin")
                cmds.connectAttr(inv+".output", rmv+".outputMax")
                cmds.connectAttr(rmv+".outValue", f"{macro}.{axis}")
    ### JAW SQUASH ###
    # counter animate lowlip going up at neg jaw.rx (only ty & tz)
        # clamp at rx = 0 with condition
        con = cmds.shadingNode("condition", n = "jaw_squash_CON", au = True)
        cmds.setAttr(con+".operation", 4) # less than 0
        cmds.connectAttr(add+".output", con+".firstTerm")
    # blend half.t with jawfollow.t (except tx)
        for name in ["uplip", "lowlip", "R_lipcorner", "L_lipcorner"]:
            jawfollow = name+"_jawfollow_driver_GRP"
            ctrlbuff = name+"_buffer_GRP"
            blend = cmds.shadingNode(
                    "blendColors", n = name+"_jaw_squash_BLEND", au = True)
            cmds.connectAttr(con+".outColorR", blend+".blender")
            cmds.connectAttr(jawfollow+".t", blend+".color1")
            cmds.connectAttr(jawfollow+".tx", blend+".color2R") # tx unaffected by squash
            cmds.connectAttr(jawfollow+".tz", blend+".color2B") # tz unaffected by squash
            # jawfollow.t * 0.5
            half = cmds.shadingNode(
                    "multiplyDivide", n = f"jaw_squash_{name}_MULT", au = True)
            cmds.setAttr(half+".input2", 0.5, 0.5, 0.5)
            cmds.connectAttr(f"{name}_jawfollow_driver_GRP.t", half+".input1")
            cmds.connectAttr(half+".outputY", blend+".color2G") # ty
            # cmds.connectAttr(half+".outputZ", blend+".color2B") # tz
            cmds.connectAttr(blend+".output", ctrlbuff+".t", force = True)
    
    def macro_out(self, ctrl_socket):
        """translation output to plug into macro behaviour of other modules
        e.g. nose, nostrils, cheeks, lowOrbs"""
        # list of drivers (lipcorners, uplips)
        macro_grp = cmds.group(n = "mouth_macroOut_GRP", em = True, p = ctrl_socket)
        macro_drivers = {"L_lipcorner_CTRL" : "L_lipcorner_macroOut_GRP",
                         "uplip_9_JNT" : "uplip_macroOut_GRP",
                         "lowlip_8_JNT" : "lowlip_macroOut_GRP"}
### could also parentCon en empty transf. to driver (or to joint??)
### if it's parented in the ctrl_socket, maybe that would give correct results?
### including seal for mid lips
        # mirror setup
        mirr = cmds.group(n = "mouth_macroOut_mirror_GRP", em = True, p = macro_grp)
        cmds.setAttr(mirr+".sx", -1)
        for driv in macro_drivers.keys():
            suffix = driv.split("_")[-1]
            output = cmds.group(n = macro_drivers[driv], 
                                em = True, p = macro_grp)
            cmds.matchTransform(output, driv, pos = True, rot = True)
            if driv.startswith("L_"):
                rig.mirror_ctrls(output, mirr, colors = False)
                r_output = output.replace("L_", "R_")
                util.mtx_zero(r_output)
                cmds.parentConstraint(driv.replace("L_", "R_"), r_output, 
                                      mo = True, w = 1,
                                      n = r_output.replace("GRP", "PC"))
            util.mtx_zero(output)
            cmds.parentConstraint(driv, output, mo = True, w = 1,
                                  n = output.replace("GRP", "PC"))
        return macro_grp
        
        
##### LIP SHAPER RIG #####
    def locatorcurve(self, jointlist, name, corners = True):
        """creates and attaches 1 locator per joint to a linear curve
        name needs to be e.g. "uplip_locators_CRV"
        no corner_locs for lowerlip, but curve needs to start at corners!
        return: [curve, locator_list]"""
        size = cmds.getAttr(self.jaw_jnt+".radius")/10
        locs = []
        for jnt in jointlist:
            locname = jnt.replace("_JNT", "_pose_LOC")
            if cmds.objExists(locname):
                locname = jnt.replace("_JNT", "_temp_LOC")
            loc = cmds.spaceLocator(n = locname)[0]
            if loc.startswith("up"):
                color = 20 # pink
                size  = size
            elif loc.startswith("low"):
                color = 18 # sky
                size = size
            else:
                color = 13 # red
                size = size*2
            cmds.setAttr(loc+".localScale", size, size, size)
            cmds.setAttr(f"{loc}.overrideEnabled", 1)
            cmds.setAttr(f"{loc}.overrideColor", color)
            cmds.matchTransform(loc, jnt, pos = True)
            locs.append(loc)
        crv = util.pointcurve(name, locs, 1)
        for nr, loc in enumerate(locs):
            pci = cmds.createNode("pointOnCurveInfo", n = loc.replace("_LOC", "_PCI"))
            cmds.connectAttr(crv+"Shape.worldSpace[0]", pci+".inputCurve")
            cmds.setAttr(pci+".parameter", nr)
            cmds.connectAttr(pci+".position", loc+".translate")
        if corners == False: # don't need corner locs for lower lip
            cmds.delete([locs[0], locs[-1]])
            locs.remove(locs[0])
            locs.remove(locs[-1])
        return [crv, locs]

    def rebuildcrvlayers(self, locatorcurve, parent_grp):
        """rebuild locatorcurve 3 times with 6, 8, 14 spans
        keep history to attach mid to low & high to mid (no wire needed yet)
        wire deform locatorcurve to highres curve
        return: [lowres, midres, highres]"""
        prefix = locatorcurve.split("_")[0] # uplip or lowlip
        # duplicate & replace with rebuild
        lowres = cmds.duplicate(locatorcurve, n = prefix+"_lowres_CRV")[0]
        cmds.rebuildCurve(lowres, replaceOriginal = 1, rebuildType = 0, keepRange = 0,
                          spans = 6, degree = 3, constructionHistory = 0)
        # new curves with rebuilds
        midres = cmds.rebuildCurve(
                lowres, n = prefix+"_midres_CRV", replaceOriginal = 0, 
                rebuildType = 0, keepRange = 0,
                spans = 8, degree = 3, constructionHistory = 0)[0]
        highres = cmds.rebuildCurve(
                midres, n = prefix+"_highres_CRV", replaceOriginal = 0, 
                rebuildType = 0, keepRange = 0,
                spans = 14, degree = 3, constructionHistory = 0)[0]
        # parent new curves (lowres already parented)
        cmds.parent([midres, highres], parent_grp)
        # 3 wire deformers
        wires = {locatorcurve : highres}
        # wires = {midres : lowres, highres : midres, locatorcurve : highres}
        for driven in wires.keys():
            driver = wires[driven]
            wire = cmds.wire(
                    driven, n = driven.replace("_CRV", "_follow_WIRE"),
                    envelope = 1, wire = driver)[0]
            cmds.setAttr(wire+".dropoffDistance[0]", 100)
        # purple, grass, pink, white
        colors = {lowres : 9, midres : 27, highres : 20, locatorcurve : 16}
        for curve in colors.keys():
            cmds.setAttr(f"{curve}Shape.overrideEnabled", 1)
            cmds.setAttr(f"{curve}Shape.overrideColor", colors[curve])
### could be connected to head scale
        # cmds.setAttr(wire+".dropoffDistance[0]", 100)
        return [lowres, midres, highres]
        
# seal curve = rebuild with same (14) spans + blendshape 0.5 to lowerlip 14 spanner
    def seal(self, up_highres, low_highres):
        """create seal line that sticks halfway between up and lowlip lines
        return: [seal_curve, blendshape node]"""
        seal_crv = cmds.rebuildCurve(
                low_highres, n = "lips_seal_CRV", replaceOriginal = 0, rebuildType = 0,
                spans = 14, degree = 3, constructionHistory = 1)[0]
        blend = cmds.blendShape(seal_crv, n = "lips_seal_BLSH")
        cmds.blendShape(blend, e = True, target = (seal_crv, 1, up_highres, 1), weight = [1, 0.5])
### attach lowlip locatorcurve_COPY with locators
    # -> set blendshape target to 1
        # -> attach uplip locatorcurve_COPY with locators
### 2 extra arguments for those 2 locatorcurves??
        # cmds.blendShape(blend, e = True, weight = [(0, 0.5)] ) # seal height
        cmds.setAttr(seal_crv+"Shape.overrideEnabled", 1)
        cmds.setAttr(seal_crv+"Shape.overrideColor", 24) # brown
        return [seal_crv, blend]

    # attach joints to highres curve until seal is set up
    def lipjointattach(self, joints, pose_locs):
        for index, jnt in enumerate(joints):
            loc = pose_locs[index]
            cmds.pointConstraint(loc, jnt, mo = True, w = 1,
                                  n = jnt.replace("JNT", "curveFollow_POINT"))
### add seal_locs as driver to constraints & return PCs?

    def curvedrivers(self, name):
        """name needs to be uplip or lowlip"""
        size = cmds.getAttr(self.jaw_jnt+".radius")/6
        lowres = name+"_lowres_CRV"
        midres = name+"_midres_CRV"
        highres = name+"_highres_CRV"
        rad = cmds.getAttr(self.jaw_jnt+".radius")/2
        grp = cmds.group(n = name+"_curvedrivers_GRP", em = True, p = "mouth_GRP")
    ### LOWRES driving setup
        # position at lip center
            # get from pci node
        temp_pci = cmds.createNode("pointOnCurveInfo", n = "temp_PCI")
        cmds.connectAttr(lowres+".worldSpace[0]", temp_pci+".inputCurve")
        cmds.setAttr(temp_pci+".parameter", 0.5)
        midpos = cmds.getAttr(temp_pci+".position")[0]
        cmds.delete(temp_pci)
        # add joint for main_lip ctrl
        cmds.select(clear = True)
        main_jnt = cmds.joint(n = name+"_main_crvJNT", position = midpos, rad = rad*1.5)
        cmds.setAttr(main_jnt+".overrideEnabled", 1)
        cmds.setAttr(main_jnt+".overrideColor", 9) # purple like lowres curve
        cmds.parent(main_jnt, grp)
        # connect joint to ctrl -> point + orient + scaleConstraint
        cmds.pointConstraint(name+"_CTRL", main_jnt, mo = True, 
                             w = 1, n = name+"_main_crvjnt_POINT")
        cmds.orientConstraint(name+"_CTRL", main_jnt, mo = True, 
                             w = 1, n = name+"_main_crvjnt_ORI")
        cmds.scaleConstraint(name+"_CTRL", main_jnt, offset = (1,1,1), 
                             w = 1, n = name+"_main_crvjnt_SCL")
        low_skin = cmds.skinCluster(
                [self.L_corner_jnt, main_jnt, self.R_corner_jnt],
                lowres,
                name = name+"_lowres_crv_SKIN",
                toSelectedBones = True,
                bindMethod = 0,
                skinMethod = 0,
                normalizeWeights = 1,
                maximumInfluences = 2)[0]
        low_weights = {0.20 : ["cv[1]", "cv[7]"], 
                       0.60 : ["cv[2]", "cv[6]"],
                       0.90 : ["cv[3]", "cv[5]"]}
        for w in low_weights.keys():
            for cv in low_weights[w]:
                cmds.skinPercent(low_skin, f"{lowres}.{cv}", 
                                 transformValue = (main_jnt, w))
    ### MIDRES driving setup
        # 3 locs on lowres -> center & sneer ctrls
        lowres_ctrls = [f"R_{name}_sneer_CTRL", 
                        f"{name}_center_CTRL", 
                        f"L_{name}_sneer_CTRL"]
        midres_drive_jnts = [self.L_corner_jnt, self.R_corner_jnt]
        for index, param in enumerate([0.25, 0.5, 0.75]):
            ctrl = lowres_ctrls[index]
            pci = cmds.createNode("pointOnCurveInfo",
                                  n = f"{lowres}_{index+1}_driver_PCI")
            cmds.connectAttr(lowres+".worldSpace[0]", pci+".inputCurve")
            cmds.setAttr(pci+".parameter", param)
            loc = cmds.spaceLocator(n = f"{lowres}_{index+1}_driver_LOC")[0]
            cmds.setAttr(loc+".localScale", size, size, size)
            cmds.setAttr(loc+".overrideEnabled", 1)
            cmds.setAttr(loc+".overrideColor", 9) # purple like lowres
            cmds.parent(loc, grp)
            cmds.connectAttr(pci+".position", loc+".t")
        # attach ctrls for each with buffer
            buff = util.buffer(ctrl)
            util.mtx_zero([buff, ctrl])
            cmds.pointConstraint(loc, buff, mo = True, w = 1, 
                                 n = loc.replace("LOC", "POINT"))
        # add joint for each
            cmds.select(clear = True)
            jnt = cmds.joint(n = ctrl.replace("CTRL", "crvJNT"), rad = rad)
            # special buffer because of R_side
            crv_jnt_buff = cmds.duplicate(ctrl, parentOnly = True, 
                                          n = jnt.replace("JNT", "buffer_GRP"))[0]
            cmds.matchTransform([jnt, crv_jnt_buff], loc, pos = True)
            cmds.setAttr(jnt+".overrideEnabled", 1)
            cmds.setAttr(jnt+".overrideColor", 27) # grass like midres curve
            cmds.parent(crv_jnt_buff, loc)
            util.mtx_zero(crv_jnt_buff)
            cmds.parent(jnt, crv_jnt_buff)
        # constrain joint to ctrl
            cmds.connectAttr(ctrl+".t", crv_jnt_buff+".t")
            cmds.connectAttr(ctrl+".s", crv_jnt_buff+".s")
            cmds.orientConstraint(ctrl, crv_jnt_buff, mo = True, 
                                  w = 1, n = jnt.replace("JNT", "ORI"))
        # bind midres to joints
            midres_drive_jnts.append(jnt)
        mid_skin = cmds.skinCluster(
                midres_drive_jnts,
                midres,
                name = name+"_midres_crv_SKIN",
                toSelectedBones = True,
                bindMethod = 0,
                skinMethod = 0,
                normalizeWeights = 1,
                maximumInfluences = 2)[0]
        mid_weights = {0.20 : ["cv[1]", "cv[9]"], 
                       0.60 : ["cv[2]", "cv[8]"]}
        for w in mid_weights.keys():
            R_cv = mid_weights[w][0]
            L_cv = mid_weights[w][1]
            cmds.skinPercent(mid_skin, f"{midres}.{L_cv}", 
                             transformValue = (f"L_{name}_sneer_crvJNT", w))
            cmds.skinPercent(mid_skin, f"{midres}.{R_cv}", 
                             transformValue = (f"R_{name}_sneer_crvJNT", w))
### need to set weights for rest of cvs too?
    ### HIGHRES driving setup
        # 5 locs on midres -> out_ctrl + center & sneer joints
        midres_ctrls = [f"R_{name}_pinch_CTRL", 
                        f"R_{name}_out_CTRL", 
                        f"L_{name}_out_CTRL", 
                        f"L_{name}_pinch_CTRL"]
        parameters = [0.0625, 0.125, 0.875, 0.9375]
### could add xtra ctrl betw. sneer and center?
        if name == "uplip": # include corners
            midres_ctrls.insert(0, "R_lipcorner_offset_CTRL")
            midres_ctrls.append("L_lipcorner_offset_CTRL")
            parameters.insert(0, 0)
            parameters.append(1)
        highres_drive_jnts = []
        for index, param in enumerate(parameters):
            ctrl = midres_ctrls[index]
            pci = cmds.createNode("pointOnCurveInfo",
                                  n = f"{midres}_{index+1}_driver_PCI")
            cmds.connectAttr(midres+".worldSpace[0]", pci+".inputCurve")
            cmds.setAttr(pci+".parameter", param)
            loc = cmds.spaceLocator(n = f"{midres}_{index+1}_driver_LOC")[0]
            cmds.setAttr(loc+".localScale", size, size, size)
            cmds.setAttr(loc+".overrideEnabled", 1)
            cmds.setAttr(loc+".overrideColor", 27) # purple like lowres
            cmds.parent(loc, grp)
            cmds.connectAttr(pci+".position", loc+".t")
        # attach ctrls for each with buffer
            buff = util.buffer(ctrl)
            util.mtx_zero([buff, ctrl])
            cmds.pointConstraint(loc, buff, mo = True, w = 1, 
                                 n = loc.replace("LOC", "POINT"))
        # add joint for each
            cmds.select(clear = True)
            jnt = cmds.joint(n = ctrl.replace("CTRL", "crvJNT"), rad = rad)
            # special buffer because of R_side
            crv_jnt_buff = cmds.duplicate(ctrl, parentOnly = True, 
                                          n = jnt.replace("JNT", "buffer_GRP"))[0]
            cmds.matchTransform([jnt, crv_jnt_buff], loc, pos = True)
            cmds.setAttr(jnt+".overrideEnabled", 1)
            cmds.setAttr(jnt+".overrideColor", 20) # pink like highres curve
            cmds.parent(crv_jnt_buff, loc)
            util.mtx_zero(crv_jnt_buff)
            cmds.parent(jnt, crv_jnt_buff)
        # constrain joint to ctrl
            cmds.connectAttr(ctrl+".t", crv_jnt_buff+".t")
            cmds.connectAttr(ctrl+".s", crv_jnt_buff+".s")
            cmds.orientConstraint(ctrl, crv_jnt_buff, mo = True, 
                                  w = 1, n = jnt.replace("JNT", "ORI"))
        # bind highres to joints
            highres_drive_jnts.append(jnt)
        highres_drive_jnts.extend(midres_drive_jnts[2:]) # without corner_main_JNTs
        if name == "lowlip":
            highres_drive_jnts.extend(
                ["R_lipcorner_offset_crvJNT", "L_lipcorner_offset_crvJNT"])
        high_skin = cmds.skinCluster(
                highres_drive_jnts,
                highres,
                name = name+"_highres_crv_SKIN",
                toSelectedBones = True,
                bindMethod = 0,
                skinMethod = 0,
                normalizeWeights = 1,
                maximumInfluences = 2)[0]
        high_weights = {0.15 : ["cv[5]", "cv[11]"], 
                        0.55 : ["cv[6]", "cv[10]"],
                        0.85 : ["cv[7]", "cv[9]"]}
        for w in high_weights.keys():
            for cv in high_weights[w]:
                cmds.skinPercent(high_skin, f"{highres}.{cv}", 
                                 transformValue = (f"{name}_center_crvJNT", w))
        high_corner_weights = {
            "R_lipcorner_offset_crvJNT" : {"cv[1]" : 0.6},
            f"R_{name}_pinch_crvJNT" : {"cv[2]" : 0.8, "cv[3]" : 0},
            f"R_{name}_out_crvJNT" : {"cv[3]" : 1, "cv[4]" : 0.3},
            f"R_{name}_sneer_crvJNT" : {"cv[3]" : 0.15},
            "L_lipcorner_offset_crvJNT" : {"cv[15]" : 0.6},
            f"L_{name}_pinch_crvJNT" : {"cv[14]" : 0.8, "cv[13]" : 0},
            f"L_{name}_out_crvJNT" : {"cv[13]" : 1, "cv[12]" : 0.3},
            f"L_{name}_sneer_crvJNT" : {"cv[13]" : 0.15}
            }
        for joint in high_corner_weights.keys():
            for cv in high_corner_weights[joint].keys():
                w = high_corner_weights[joint][cv]
                cmds.skinPercent(high_skin, f"{highres}.{cv}", 
                                 transformValue = (joint, w))
    # make pinch follow out_ctrl 90%
        for s in ["L_", "R_"]:
            pinch = f"{s}{name}_pinch"
            pinch_ctrl = pinch+"_CTRL"
            pinch_buff = pinch+"_crvbuffer_GRP"
            out_ctrl = f"{s}{name}_out_CTRL"
            # out_ctrl.t * 0.9 -> newbuffer for pinch ctrl
            new_buff = util.buffer(pinch_ctrl, "outctrl_follow_GRP")
            ctrl_mult = cmds.shadingNode(
                    "multiplyDivide", n = pinch+"_ctrl_outfollow_MULT", au = True)
            cmds.connectAttr(out_ctrl+".t", ctrl_mult+".input1")
            cmds.setAttr(ctrl_mult+".input2", 0.9, 0.9, 0.9) # 90 %
            cmds.connectAttr(ctrl_mult+".output", new_buff+".t")
            # out_ctrl.t * 0.9 + pinch_ctrl.t -> pinch_buff.t, force = True
            pinch_mult = cmds.shadingNode(
                    "multiplyDivide", n = pinch+"_jnt_outfollow_MULT", au = True)
            pinch_add = cmds.shadingNode(
                    "plusMinusAverage", n = pinch+"_jnt_outfollow_ADD", au = True)
            cmds.connectAttr(out_ctrl+".t", pinch_mult+".input1")
            cmds.setAttr(pinch_mult+".input2", 0.9, 0.9, 0.9) # 90 %
            cmds.connectAttr(pinch_mult+".output", pinch_add+".input3D[0]")
            cmds.connectAttr(pinch_ctrl+".t", pinch_add+".input3D[1]")
            cmds.connectAttr(pinch_add+".output3D", pinch_buff+".t", force = True)
            
            
    # cleanup 
        cmds.hide(grp)

### Rotations ###
    def orientjoints(self, lipjoints):
        """lipjoints do NOT include corner joints (they stay oriented to corner_ctrls
        """
        name = lipjoints[0].split("_")[0] # uplip or lowlip prefix
        # make new group node "uplip_tuning"
        attr_t = cmds.group(n = name+"_tuning", em = True, p = "mouth_GRP")
        util.lock(attr_t, vis = True)
        util.attr_separator(attr_t, "center")
### better place to parent than face_GRP?
        # add one attr per joint (just one side)
        mid_index = int((len(lipjoints)-1)/2)
        center_joint = lipjoints[mid_index]
        # middle driver under midlip ctrl
        mid_ctrl = name+"_CTRL"
        middle = cmds.group(n = name+"_orient_DRIVER", em = True, p = mid_ctrl)
        if name == "uplip": # inverted lip roll
            roll_inv = cmds.shadingNode(
                    "multDoubleLinear", n = "uplip_roll_inv_MULT", au = True)
            cmds.connectAttr(mid_ctrl+".roll", roll_inv+".input1")
            cmds.setAttr(roll_inv+".input2", -1)
            cmds.connectAttr(roll_inv+".output", middle+".rx")
        else:
            cmds.connectAttr(mid_ctrl+".roll", middle+".rx")
        util.lock(middle)
        # center joint
        cori = cmds.orientConstraint(middle, center_joint, mo = True, w = 1,
                                     n = center_joint.replace("JNT", "ORI"))[0]
        left_joints = lipjoints[mid_index+1:]
        right_joints = lipjoints[0:mid_index]
        right_joints.reverse()
        for nr, j in enumerate(left_joints):
            attr = f"joint{nr+1}"
            cmds.addAttr(attr_t, longName = attr, attributeType = "double",
                         min = 0, max = 1, dv = 0)
            cmds.setAttr(f"{attr_t}.{attr}", e = True, keyable = True)
            tuner = f"{attr_t}.{attr}"
### initial values for orient weight (falloff from middle to corner)
            length = float(len(left_joints))
            degree = 1.3
            linear_value = float(nr) / (length - 1)
            div_value = linear_value / degree
            final_value = div_value * linear_value
            cmds.setAttr(tuner, final_value)
            # create reverse node per attr
            rev = cmds.shadingNode("reverse", n = f"{name}_joint{nr}_REV", au = True)
            cmds.connectAttr(tuner, rev+".inputX")
            for s in ["L_", "R_"]:
                # naming on joints without side prefix
                joint = j if s == "L_" else right_joints[nr]
                corner = f"{s}lipcorner_main_JNT"
                ori = cmds.orientConstraint([corner, middle], joint, mo = True, w = 1,
                                            n = joint.replace("JNT", "ORI"))[0]
        # attrs + reverse into constraint W0, W1
                cmds.connectAttr(tuner, f"{ori}.{corner}W0")
                cmds.connectAttr(rev+".outputX", f"{ori}.{middle}W1")
        util.attr_separator(attr_t, "corner")
### replace joint target with group node? to work with seal?

### jaw tuner for "openMouth" pose to make lipcorners go in a bit (squetch)
    # drive with rx from jaw or from same setup as tz follow?
### seal blending setup oioiioioioi
### add "squetch " attr
### lip volume tuner by curvelength * head.sx -> drive same shape as "squetch"
if __name__ == "__main__":
    
    test = Mouth()
    test.build_rig(
        joint_socket = "head_JNT", 
        ctrl_socket = "head_CTRL")
    cmds.hide("proxy_test_GRP")
    cmds.setAttr("head_JNT.drawStyle", 2) # None
    pass