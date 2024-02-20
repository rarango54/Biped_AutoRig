import maya.cmds as cmds

from face_proxies.proxymouth_fail import ProxyMouth

from utils.ctrl_library import Nurbs
from utils import util
from utils import rig

class Mouth(object):
    
### number of edgeloops uplip, lowlip
### position of ctrls
    ### e.g. uplip - 8 vtx (without center or lipcorner)
    ### uplip ctrls at [4, 6, 7] (starting from 1!!)
    
    def __init__(self):

        self.module_name = "mouth"
        
        
        self.jaw_jnt = "jaw_JNT"
        self.jawb_jnt = "jaw_break_JNT"
        self.mouth_jnt = "mouth_pivot_JNT"
        self.chin_jnt = "chin_JNT"
        
        self.invjaw = "jaw_inverse_CTRL"
        self.jaw = "jaw_aim_CTRL"
        self.jawnorm = "jaw_FK_CTRL"
        self.jawb = "jaw_break_CTRL"
        self.mouth = "mouth_CTRL"
        
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
    
    def skeleton(self, joint_socket):
        pmouth = ProxyMouth()
        rad = cmds.getAttr(joint_socket+".radius")/3
        jaw_jnts = rig.make_joints(
                proxies_list = pmouth.proxies[:4], # skip jaw ctrls
                rot_order = "xyz", 
                radius = rad,
                set = "fjoints")
        cmds.joint(self.jawb_jnt, e = True, 
                   orientJoint = "zxy",
                   secondaryAxisOrient = "xup",
                   children = False)
        cmds.parent(self.mouth_jnt, self.jawb_jnt)
### cmds.parent(jaw_jnts[0], joint_socket)
        
    # lips
        corner = ["lipcorner_vtx_LOC"]
        up_center = ["uplipcenter_vtx_LOC"]
        low_center = ["lowlipcenter_vtx_LOC"]
        up_vtx = cmds.ls("uplip_*_LOC")
        low_vtx = cmds.ls("lowlip_*_LOC")
        # setup
        for section in [up_center, up_vtx, corner, low_center, low_vtx]:
            for loc in section:
                cmds.select(clear = True)
                pos = cmds.xform(loc, q = True, t = True, ws = True)
                if section != up_center and section != low_center:
                    name = "L_"+loc.replace("vtx_LOC", "JNT")
                else:
                    name = loc.replace("vtx_LOC", "JNT")
                jnt = cmds.joint(
                    n = name, 
                    p = pos, rad = rad/3)
                cmds.parent(jnt, self.mouth_jnt)
            # mirror
                if section != up_center and section != low_center:
                    mirr_jnt = cmds.mirrorJoint(
                        jnt, 
                        mirrorYZ = True, 
                        mirrorBehavior = True, 
                        searchReplace = ["L_", "R_"])[0]

### noInvScale = True ???
    
##### CONTROLS #####################################################################
    def controls(self, ctrl_socket):
        # Setup
        pmouth = ProxyMouth()
      
    ### ctrl shapes
        cdist = cmds.getAttr(self.chin_jnt+".tz")/20
        # jaw
        invjaw = cmds.group(n = self.invjaw, em = True)
        jaw = Nurbs.sphere(self.jaw, cdist, "yellow")
        jawnorm = Nurbs.sphere(self.jawnorm, cdist*1.3, "yellow", "zyx")
        # jawb = Nurbs.circle(self.jawb, cdist*1.2, "brown")
        mouth = Nurbs.sphere(self.mouth, cdist/1.5, "yellow")
        # main lip
        lipc = Nurbs.cube(self.corner, cdist*2, "red")
        lipc_off = Nurbs.triangle(self.corner_off, cdist, cdist, "pink")
        # uplip
        uplip = Nurbs.box(self.uplip, cdist*4, cdist*0.8, cdist/10, "yellow")
        upc = Nurbs.triangle(self.upcenter, cdist, cdist, "pink")
        ups = Nurbs.triangle(self.upsneer, cdist, cdist, "red")
        upo = Nurbs.triangle(self.upout, cdist, cdist, "red")
        upp = Nurbs.triangle(self.uppinch, cdist, cdist, "pink")
        # lowlip
        lowlip = Nurbs.box(self.lowlip, cdist*4, cdist*0.8, cdist/10, "yellow")
        lowc = Nurbs.triangle(self.lowcenter, cdist, cdist, "pink")
        lows = Nurbs.triangle(self.lowsneer, cdist, cdist, "red")
        lowo = Nurbs.triangle(self.lowout, cdist, cdist, "red")
        lowp = Nurbs.triangle(self.lowpinch, cdist, cdist, "pink")
        
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
        
        uplip_jnts = cmds.ls("L_uplip*_JNT")
        uplip_jnts.insert(0, "uplipcenter_JNT")
        lowlip_jnts = cmds.ls("L_lowlip*_JNT")
        lowlip_jnts.insert(0, "lowlipcenter_JNT")
        lipcorner_jnt = "L_lipcorner_JNT"
    # position & parent
        relations = {
            invjaw :       (pmouth.jawctrl,    ctrl_socket),
            jaw :       (pmouth.jawctrl,    ctrl_socket),
            # jawb :      (pmouth.jawctrl,    jaw),
            jawnorm :   (pmouth.jaw,        ctrl_socket),
            mouth :     (pmouth.mouthctrl,  ctrl_socket),
            uplip :     (pmouth.upcenter,   mouth),
            upc :       (pmouth.upcenter,     uplip),
            ups :       (pmouth.upsneer,     mouth),
            upo :       (pmouth.upout,     mouth),
            upp :       (pmouth.uppinch,     mouth),
            lowlip :    (pmouth.lowcenter,    mouth),
            lowc :      (pmouth.lowcenter,    lowlip),
            lows :      (pmouth.lowsneer,    mouth),
            lowo :      (pmouth.lowout,    mouth),
            lowp :      (pmouth.lowpinch,    mouth),
            lipc :      (pmouth.corner,     mouth),
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
        
####### Attributes
        # Z
        cmds.addAttr(lipc, longName = "Z", attributeType = "double")
        cmds.setAttr(f"{lipc}.Z", e = True, keyable = True)
        cmds.addAttr(jaw, longName = "Z", attributeType = "double")
        cmds.setAttr(f"{jaw}.Z", e = True, keyable = True)
### Z on main lips, mouth
        util.attr_separator([uplip, lowlip, mouth, lipc, jaw])
        cmds.addAttr(uplip, longName = "roll", attributeType = "double")
        cmds.setAttr(f"{uplip}.roll", e = True, keyable = True)
        cmds.addAttr(uplip, longName = "squetch", attributeType = "double")
        cmds.setAttr(f"{uplip}.squetch", e = True, keyable = True)
        cmds.addAttr(lowlip, longName = "roll", attributeType = "double")
        cmds.setAttr(f"{lowlip}.roll", e = True, keyable = True)
        cmds.addAttr(lowlip, longName = "squetch", attributeType = "double")
        cmds.setAttr(f"{lowlip}.squetch", e = True, keyable = True)
        cmds.addAttr(lipc, longName = "zip", attributeType = "double")
        cmds.setAttr(f"{lipc}.zip", e = True, keyable = True)
        cmds.addAttr(lipc, longName = "zip_falloff", attributeType = "double")
        cmds.setAttr(f"{lipc}.zip_falloff", e = True, keyable = True)
        # jaw attrs to break
        cmds.addAttr(jaw, longName = "bend", attributeType = "double")
        cmds.setAttr(f"{jaw}.bend", e = True, keyable = True)
        cmds.addAttr(jaw, longName = "skew", attributeType = "double")
        cmds.setAttr(f"{jaw}.skew", e = True, keyable = True)
        cmds.addAttr(jaw, longName = "twist", attributeType = "double")
        cmds.setAttr(f"{jaw}.twist", e = True, keyable = True)
        # mouth
        cmds.addAttr(mouth, longName = "seal", attributeType = "double")
        cmds.setAttr(f"{mouth}.seal", e = True, keyable = True)
        
        
    ### R_ctrls & Mirroring
        lipctrl_mirror_grp = cmds.group(
                n = "R_lip_ctrls_mirror_GRP", empty = True, parent = mouth)
        cmds.setAttr(f"{lipctrl_mirror_grp}.sx", -1)
        rig.mirror_ctrls([ups, upo, upp, lipc_buff, lows, lowo, lowp], lipctrl_mirror_grp)
    
    # selection sets
        # l_ctrls = [clav, fk_uparm, fk_lowarm, fk_hand, 
        #            ik_hand, ik_hand_sub, ik_align, ik_pv, ik_should, 
        #            uparm_b, elbow_b, lowarm_b, switch]
        # r_ctrls = [x.replace("L_", "R_") for x in l_ctrls]
        # cmds.sets(l_ctrls, add = "L_arm")
        # cmds.sets(r_ctrls, add = "R_arm")
        
        zero_grp = [invjaw, jaw, jawbuff, jawnorm, mouth, 
                    uplip, upc, ups, upo, upp, 
                    lipc, lipc_off, 
                    lowlip, lowc, lows, lowo, lowp,
                    lipc_buff, uplip_buff, lowlip_buff]
        for z in zero_grp:
            if z.startswith("L_"):
                zero_grp.append(z.replace("L_", "R_"))
    # cleanup
        util.mtx_zero(zero_grp)

    def lipctrlconnect(self):
### create LIP_CTRL_TUNING grp
### attr for each parent constraint def weights
### buffers for main drivers
        main_drivers = [self.uplip, self.lowlip, self.corner, self.corner.replace("L_", "R_")]
        # uplip follow invjaw 98%
        uplip_follow = cmds.parentConstraint(
                [self.invjaw, self.jawb_jnt], self.uplip_buff, mo = True, w = 1,
                n = self.uplip.replace("CTRL", "jawfollow_PC"))[0]
        cmds.setAttr(uplip_follow+"."+self.invjaw+"W0", 0.98)
        cmds.setAttr(uplip_follow+"."+self.jawb_jnt+"W1", 0.02)
        # lowlip follow jawbreak 98%
        lowlip_follow = cmds.parentConstraint(
                [self.invjaw, self.jawb_jnt], self.lowlip_buff, mo = True, w = 1,
                n = self.lowlip.replace("CTRL", "jawfollow_PC"))[0]
        cmds.setAttr(lowlip_follow+"."+self.invjaw+"W0", 0.02)
        cmds.setAttr(lowlip_follow+"."+self.jawb_jnt+"W1", 0.98)
        cmds.setAttr(uplip_follow+".interpType", 2) # "shortest" to avoid flipping
        cmds.setAttr(lowlip_follow+".interpType", 2) # "shortest" to avoid flipping
        # corners follow jaw 50%
        for s in ["L_", "R_"]:
            corner_follow = cmds.parentConstraint(
                    [self.invjaw, self.jawb_jnt], f"{s}lipcorner_buffer_GRP", mo = True, w = 1,
                    n = f"{s}lipcorner_jawfollow_PC")[0]
            cmds.setAttr(corner_follow+"."+self.invjaw+"W0", 0.5)
            cmds.setAttr(corner_follow+"."+self.jawb_jnt+"W1", 0.5)
            cmds.setAttr(corner_follow+".interpType", 2) # "shortest" to avoid flipping

        for s in ["L_", "R_"]:
            corner_drive = f"{s}lipcorner_CTRL"
            corn = f"{s}lipcorner_offset_CTRL"
            for v in ["up", "low"]:
                center_drive = f"{v}lip_CTRL"
                sneer = f"{s}{v}lip_sneer_CTRL"
                out = f"{s}{v}lip_out_CTRL"
                pinch = f"{s}{v}lip_pinch_CTRL"
                sneer_buff = util.buffer(sneer)
                out_buff = util.buffer(out)
                pinch_buff = util.buffer(pinch)
                util.mtx_zero([sneer, out, pinch, sneer_buff, out_buff, pinch_buff])
                # 3 constraints for [sneer, out, pinch]
                sneer_con = cmds.parentConstraint(
                    (center_drive, corner_drive), sneer_buff,
                    n = f"{s}{v}lip_sneer_ctrl_PC", mo = True, w = 1)[0]
                cmds.setAttr(sneer_con+f".{center_drive}W0", 0.75)
                cmds.setAttr(sneer_con+f".{corner_drive}W1", 0.25)
                out_con = cmds.parentConstraint(
                    (sneer, corner_drive), out_buff,
                    n = f"{s}{v}lip_out_ctrl_PC", mo = True, w = 1)[0]
                cmds.setAttr(out_con+f".{sneer}W0", 0.6)
                cmds.setAttr(out_con+f".{corner_drive}W1", 0.4)
                pinch_con = cmds.parentConstraint(
                    (out, corn), pinch_buff,
                    n = f"{s}{v}lip_pinch_ctrl_PC", mo = True, w = 1)[0]
                cmds.setAttr(pinch_con+f".{out}W0", 0.6)
                cmds.setAttr(pinch_con+f".{corn}W1", 0.4)
                for con in [sneer_con, out_con, pinch_con]:
                    cmds.setAttr(con+".interpType", 2) # "shortest" to avoid flipping
### arguments specifying ctrl nodes
### that way, can reuse for replicating on seal grps?

    def seals(self):
        lipjoints = cmds.ls("*lip_*_JNT")
        seal_grp = cmds.group(n = "lip_seal_GRP", em = True, p = "fmisc_GRP")
        center_seal = cmds.group(n = "center_SEAL", em = True)
        cmds.parent(center_seal, seal_grp)
        seals = []
        seals.append(center_seal)
        cpc = cmds.parentConstraint(
                ["uplip_CTRL", "lowlip_CTRL"],
                center_seal, mo = False, w = 0.5, 
                n = center_seal.replace("SEAL", "seal_PC"))[0]
        cmds.setAttr(cpc+".interpType", 2) # "shortest" to avoid flipping
        for s in ["L_", "R_"]:
            sneer_seal = cmds.group(n = f"{s}sneer_SEAL", em = True)
            out_seal = cmds.group(n = f"{s}out_SEAL", em = True)
            pinch_seal = cmds.group(n = f"{s}pinch_SEAL", em = True)
            for seal_driver in [sneer_seal, out_seal, pinch_seal]:
                upc = s+"uplip_"+seal_driver[2:].replace("SEAL", "CTRL")
                lowc = s+"lowlip_"+seal_driver[2:].replace("SEAL", "CTRL")
                pc = cmds.parentConstraint([upc, lowc], seal_driver, mo = False, w = 0.5,
                                      n = seal_driver.replace("SEAL", "seal_PC"))[0]
                cmds.setAttr(pc+".interpType", 2) # "shortest" to avoid flipping
### 1 grp per joint needed? could have only seal drivers, same number as ctrls
### mo = True would then lead to indiv. joint drivers to stay in correct place
### offset from both ctrls and seals
        for j in lipjoints:
            seal = cmds.group(n = j.replace("_JNT", "_SEAL"), em = True)
            cmds.matchTransform(seal, j, pos = True)
            cmds.parent(seal, seal_grp)
            seals.append(seal)
        for s in ["L_", "R_"]:
            corner = f"{s}lipcorner_offset_CTRL"
            for v in ["up", "low"]:
                joints = cmds.ls(f"{s}{v}lip_*_JNT")
                seal_side = [x.replace("_JNT", "_SEAL") for x in joints]
                # follow with linear falloff
                for i, seal in  enumerate(seal_side):
                    w = (i+1) / (len(seal_side) + 2) # +2 because corner and center are not in seals
                    invw = 1 - w
                    con = cmds.parentConstraint([center_seal, corner], seal, mo = True, w = 1,
                                                n = s.replace("SEAL", "seal_PC"))[0]
                    cmds.setAttr(con+f".{center_seal}W0", invw)
                    cmds.setAttr(con+f".{corner}W1", w)
### make the seal transforms stay in the middle of posed lips at all times
### seal vs zip behaviour??
        return seals
    def lipjointsconnect(self, part = "up", ctrl_pos = [3, 5, 6]):
        # LIP_JOINT_TUNING
        # attr for each joint's constr. weight to inner ctrl
        lip_tuning = cmds.group(n = f"{part}lips_weights", em = True, p = "face_GRP")
        util.lock(lip_tuning, vis = True)
        lip_joints = cmds.ls(f"L_{part}lip_*_JNT")
        # predefined sections
        sect1 = lip_joints[:ctrl_pos[0]]
        sneer = lip_joints[ctrl_pos[0]] # 3
        sect2 = lip_joints[ctrl_pos[0]+1]
        out = lip_joints[ctrl_pos[1]] # 5
        pinch = lip_joints[ctrl_pos[2]] # 6
        sectend = lip_joints[(ctrl_pos[2]+1):] # end
        for index, joint in enumerate(lip_joints):
            if joint in sect1:
                # only first section has multiple joints
                if len(sect1) == 3:
                    def_weights = [0.9, 0.7, 0.5]
                elif len(sect1) == 2:
                    def_weights = [0.7, 0.4]
                dv = def_weights[index]
            elif joint in [sneer, out, pinch]:
                dv = 1
            else:
                dv = 0.6
            attr_name = joint[2:-4]
            cmds.addAttr(lip_tuning, longName = attr_name, attributeType = "double", 
                         defaultValue = dv, min = 0, max = 1)
            cmds.setAttr(lip_tuning+"."+attr_name, e = True, keyable = True)
        # [section of joints] per pair of ctrls
        return
###### RIGGING ####################################################################
    def build_rig(self, joint_socket, ctrl_socket):
        self.skeleton(joint_socket)
        self.controls(ctrl_socket)
    # setup
        # jaw aim & connect attrs to jaw_break
        jaw_aim = cmds.listRelatives(self.jawnorm, parent = True)[0]
        cmds.parentConstraint(self.jawnorm, self.jaw_jnt, mo = True, w = 1)
        cmds.scaleConstraint(self.jawnorm, self.jaw_jnt, offset = (1,1,1), w = 1)
        cmds.connectAttr(self.jaw+".tz", jaw_aim+".tz")
        # cmds.connectAttr(self.jaw+".s", jaw_aim+".s")
        jaimc = cmds.aimConstraint(
            self.jaw, jaw_aim, n = "jaw_AIM", mo = True, w = 1, aimVector = (0,0,1),
            upVector = (0,1,0), worldUpType = "objectRotation", 
            worldUpVector = (0,1,0), worldUpObject = self.jaw)
        cmds.connectAttr(self.jaw+".bend", self.jawb_jnt+".rx")
        cmds.connectAttr(self.jaw+".skew", self.jawb_jnt+".ry")
        cmds.connectAttr(self.jaw+".twist", self.jawb_jnt+".rz")
        rig.sub_ctrl_vis(self.jawnorm, self.jaw)
        # mouth follow 50%
        cmds.parentConstraint(self.mouth, self.mouth_jnt, mo = True, w = 1)
        cmds.scaleConstraint(self.mouth, self.mouth_jnt, offset = (1,1,1), w = 1)
        
        self.lipctrlconnect()
        self.seals()
        self.lipjointsconnect(part = "up", ctrl_pos = [3, 5, 6])
        self.lipjointsconnect(part = "low", ctrl_pos = [2, 4, 5])
        
    # cleanup
        # Z attrs
        z_grp = [self.jaw, self.corner, self.corner.replace("L_", "R_")]
        for z in z_grp:
            cmds.connectAttr(z+".Z", z+".tz")
            util.lock(z, ["tz"])

        util.lock(self.jaw, ["rx","ry","sx","sy","sz"]) # with scales??
        cmds.setAttr(self.mouth_jnt+".drawStyle", 2) # None
        return

if __name__ == "__main__":
    
    test = Mouth()
    test.build_rig(
        joint_socket = "head_JNT", 
        ctrl_socket = "head_CTRL")
    cmds.hide("proxy_test_GRP")
    cmds.setAttr("head_JNT.drawStyle", 2) # None
    pass